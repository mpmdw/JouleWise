"""S5 finalization structural archive probes and pinned GAMMA CLI path checks."""
import contextlib
import copy
from dataclasses import replace
import io
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from joulewise import analysis_manifest_v3 as mv3,whole_window as ww
from joulewise.analysis_engine import inputs
from joulewise.cli import _cmd_analyze_claims
from tests.b5_analysis import fixtures_s5 as fx,fixtures_s3 as s3

class FinalizationBlock5Tests(unittest.TestCase):
    def args(self,fixture,**overrides):
        values=dict(manifest_dir=fixture['prospective_path'].parent,custody_root=fixture['root'],runs_root=fixture['runs_root'],
            whole_window_verdict_path=fixture['verdict_path'],bracket_binding_path=fixture['bracket_path'],
            calibration_ledger_path=fixture['ledger_path'],aggregate_floor_artifact_path=fixture['floor_path'],
            acceptance_bound_path=fixture['acceptance_path'],block5_inputs=fixture['block5_inputs'])
        values.update(overrides);return values

    def test_t10_claim_licensing_false_with_and_without_context(self):
        with fx.finalization_case() as f:
            row=json.loads(f['verdict_path'].read_bytes());row['claim_licensing']=False
            f['verdict_path'].write_text(json.dumps(row))
            for context in (f['block5_inputs'],None):
                with self.subTest(context=context is not None),self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,'^analysis_finalization_verdict_not_passed:'):
                    mv3._authenticate_finalization_inputs(f['prospective'],**self.args(f,block5_inputs=context))

    def test_r5_stored_failed_without_window_index(self):
        with fx.finalization_case() as f:
            row=json.loads(f['verdict_path'].read_bytes());row['status']='failed'
            f['verdict_path'].write_text(json.dumps(row))
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,'^analysis_finalization_verdict_not_passed:'):
                mv3._authenticate_finalization_inputs(f['prospective'],**self.args(f,block5_inputs=None))

    def test_r6_ledger_must_equal_archive_prefix(self):
        with fx.finalization_case() as f:
            original=f['ledger_path'].read_bytes()
            for raw in (original+b'{}\n',b' '+original):
                with self.subTest(kind='append' if raw.startswith(original) else 'changed'):
                    f['ledger_path'].write_bytes(raw)
                    with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,'^analysis_finalization_ledger_head_mismatch: ledger_not_the_archive_prefix$'):
                        mv3._authenticate_finalization_inputs(f['prospective'],**self.args(f))

    def test_bracket_bytes_must_equal_archive(self):
        with fx.finalization_case() as f:
            f['bracket_path'].write_bytes(f['bracket_path'].read_bytes()+b' ')
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,'^analysis_finalization_bracket_binding_mismatch: bracket_not_the_archive_binding$'):
                mv3._authenticate_finalization_inputs(f['prospective'],**self.args(f))

    def test_r1_removed_member_paths_not_opened_by_basis_and_identity(self):
        """S5-only passes: removed members are in stored row.bundle_ids; validator is not invoked."""
        with fx.finalization_case() as f:
            units=f['units'];kept=frozenset(run for cid in units.cells for run in units.kept_run_ids(cid))
            for run in units.removed_run_ids():shutil.rmtree(f['runs_root']/run,ignore_errors=True)
            row=json.loads(f['verdict_path'].read_bytes())
            basis,paths=mv3._verify_basis_members(f['prospective'],row,manifest_dir=f['prospective_path'].parent,
                runs_root=f['runs_root'],kept_run_ids=kept)
            self.assertEqual(set(paths),kept)
            arms,entries,blocks=mv3._derive_arms_and_entries(f['prospective'],manifest_dir=f['prospective_path'].parent,
                runs_root=f['runs_root'],bundle_paths=paths,removed_run_ids=units.removed_run_ids())
            self.assertTrue(all(entry['bundle_path'] is None for entry in entries if entry['run_id'] in units.removed_run_ids()))
            self.assertEqual(len(entries),80)

    def test_r10_finalizer_index_on_non_block5_root(self):
        with mock.patch.object(mv3,'is_hazard_runs_root',return_value=False),self.assertRaisesRegex(
                mv3.AnalysisManifestFinalizationError,'^analysis_finalization_attachment_invalid: window_index_not_a_block5_root$'):
            mv3.finalize_prospective_analysis_manifest_v3(Path('unopened'),plan_tree_path=Path('unopened'),
                custody_root=Path('unopened'),runs_root=Path('runs'),whole_window_verdict_path=Path('unopened'),
                bracket_binding_path=Path('unopened'),calibration_ledger_path=Path('unopened'),
                aggregate_floor_artifact_path=Path('unopened'),output_dir=Path('unopened'),window_index=Path('index'))

    def test_t8_semantics_hash_ignores_all_three_roles(self):
        with fx.finalization_case() as f:
            row=json.loads(f['verdict_path'].read_bytes());paths={m['run_id']:f['runs_root']/m['run_id'] for c in f['prospective']['contrasts'] for m in c['members']}
            # Members removed by the earlier no-read probe may have no bundle. Derive
            # the same frozen projection using the real kept-only identity seam.
            removed=f['units'].removed_run_ids();paths={run:path for run,path in paths.items() if run not in removed}
            arms,entries,blocks=mv3._derive_arms_and_entries(f['prospective'],manifest_dir=f['prospective_path'].parent,
                runs_root=f['runs_root'],bundle_paths=paths,removed_run_ids=removed)
            attachments={'arms':arms,'entries':entries,'blocks':blocks,**{role:{} for role in mv3._REQUIRED_ATTACHMENT_ROLES}}
            kwargs=dict(prospective_relative=f['prospective_path'].relative_to(f['root']).as_posix(),prospective_sha256='1'*64,
                plan_tree_relative=f['plan_tree_path'].relative_to(f['root']).as_posix(),plan_tree_sha256='2'*64)
            bare=mv3._build_finalized_manifest(f['prospective'],attachments=attachments,**kwargs)
            for role in mv3._BLOCK5_ROLES:attachments[role]={'synthetic_role_digest':'3'*64}
            enriched=mv3._build_finalized_manifest(f['prospective'],attachments=attachments,**kwargs)
            self.assertEqual(mv3.analysis_semantics_sha256_v1(bare),mv3.analysis_semantics_sha256_v1(enriched))
            self.assertEqual(mv3.analysis_semantics_sha256_v1(enriched),mv3.analysis_semantics_sha256_v1(f['prospective']))

    def test_rendered_manifest_bytes_do_not_follow_the_hash_seed(self):
        # S10 joined run: two dry runs into two custody roots wrote finalized
        # manifests with the same id and different bytes, because the block-5 roles
        # were inserted in frozenset iteration order (the per-process hash seed).
        class Ordered(frozenset):
            order = ()
            def __iter__(self):
                return iter(self.order)
        with fx.finalization_case() as f:
            removed=f['units'].removed_run_ids()
            paths={m['run_id']:f['runs_root']/m['run_id'] for c in f['prospective']['contrasts'] for m in c['members']
                   if m['run_id'] not in removed}
            arms,entries,blocks=mv3._derive_arms_and_entries(f['prospective'],manifest_dir=f['prospective_path'].parent,
                runs_root=f['runs_root'],bundle_paths=paths,removed_run_ids=removed)
            attachments={'arms':arms,'entries':entries,'blocks':blocks,**{role:{} for role in mv3._REQUIRED_ATTACHMENT_ROLES},
                         **{role:{'synthetic_role_digest':'3'*64} for role in mv3._BLOCK5_ROLES}}
            kwargs=dict(prospective_relative=f['prospective_path'].relative_to(f['root']).as_posix(),prospective_sha256='1'*64,
                plan_tree_relative=f['plan_tree_path'].relative_to(f['root']).as_posix(),plan_tree_sha256='2'*64)
            rendered=[]
            for order in (sorted(mv3._BLOCK5_ROLES),sorted(mv3._BLOCK5_ROLES,reverse=True)):
                roles=Ordered(mv3._BLOCK5_ROLES);roles.order=tuple(order)
                with mock.patch.object(mv3,'_BLOCK5_ROLES',roles):
                    rendered.append(mv3.render_manifest(mv3._build_finalized_manifest(f['prospective'],attachments=attachments,**kwargs)))
            self.assertEqual(rendered[0],rendered[1])


class ClaimCommandTests(unittest.TestCase):
    def args(self,**changes):
        value=dict(analysis_manifest='manifest',runs_root='runs',floor_artifact='floor',evidence_roots=None,output='output.json',
            legacy_l1_mechanics=False,neg8_harvest_archive='archive',window_index='index')
        value.update(changes);return SimpleNamespace(**value)
    def test_r4_no_window_index(self):
        error=io.StringIO()
        with mock.patch('joulewise.window_lineage.is_hazard_runs_root',return_value=True),contextlib.redirect_stderr(error):
            self.assertEqual(_cmd_analyze_claims(self.args(window_index=None)),2)
        self.assertEqual(error.getvalue(),'error: window_index_required\n')
    def test_r10_index_off_block5(self):
        error=io.StringIO()
        with mock.patch('joulewise.window_lineage.is_hazard_runs_root',return_value=False),contextlib.redirect_stderr(error):
            self.assertEqual(_cmd_analyze_claims(self.args()),2)
        self.assertEqual(error.getvalue(),'error: kept_units_not_a_block5_root\n')
    def test_t9_archive_path_agrees_with_pinned_gamma(self):
        # The exact archive is S0's real pinned-harvest GAMMA_STD. The builder
        # is a named handoff double; CLI path enforcement is the real call site.
        archive=fx.pinned_handle('GAMMA_STD')
        built={'gamma_archive':archive,'kept_units':object(),'archive_contexts':{}}
        result={'claim_verdicts_id':'synthetic','contrasts':[]}
        for path,expected in ((archive.window.archive_root,0),(archive.window.archive_root.parent,2)):
            error=io.StringIO()
            with mock.patch('joulewise.window_lineage.is_hazard_runs_root',return_value=True), \
                 mock.patch.object(inputs,'block5_claim_gate_inputs',return_value=built), \
                 mock.patch('joulewise.analysis_engine.analyze_claims',return_value=result), \
                 contextlib.redirect_stderr(error),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(_cmd_analyze_claims(self.args(neg8_harvest_archive=str(path))),expected)
            if expected:self.assertEqual(error.getvalue(),'error: neg8_archive_differs_from_window_index\n')

class LoaderBoundaryTests(unittest.TestCase):
    def test_r1_loader_never_opens_removed_directories(self):
        """Writer-excluded removed members absent from row.bundle_ids; directories deleted."""
        with fx.loader_case() as case:
            for run in case.units.removed_run_ids():shutil.rmtree(case.runs/run)
            loaded=case.call()
            self.assertFalse(case.units.removed_run_ids() & set(case.reader_calls))
            self.assertEqual(len(case.reader_calls),72)
            for row in loaded.registered.values():
                if row.bundle_id in case.units.removed_run_ids():
                    self.assertIsNone(row.summary);self.assertEqual(row.base_reason_codes,('unit_removed_by_exclusion_function',))
    def test_r2_loader_deleted_kept_bundle(self):
        with fx.loader_case() as case:
            run=next(iter(case.units.kept_run_ids('decode')));shutil.rmtree(case.runs/run)
            with self.assertRaisesRegex(inputs.AnalysisInputError,'^member_code_on_kept_unit$'):case.call()
    def test_r6_loader_never_reads_live_ledger(self):
        with fx.loader_case() as case,mock.patch.object(inputs,'load_calibration_ledger_snapshot',side_effect=AssertionError('live ledger read')):
            case.call()
    def test_window_refusal_keeps_validator_reason(self):
        with fx.loader_case(reasons=('cpu_admission_core_failed',)) as case, \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^cpu_admission_core_failed: cpu_admission_core_failed$'):
            case.call()
    def test_r3_finalized_exclusions_digest_mismatch(self):
        with fx.loader_case() as case:
            manifest=case.loaded.manifest
            manifest['schema_version']='joulewise.analysis_manifest.v3.finalized'
            manifest.setdefault('evidence',{})['analysed_attempt_exclusions']={'sha256':'f'*64,'catalog_sha256':case.units.catalog_sha256,
                'harvest_pin':case.units.window.harvest_pin,'harvest_record':{'sha256':case.units.window.harvest_record_sha256}}
            with self.assertRaisesRegex(inputs.AnalysisInputError,'^exclusions_differ_from_finalized_manifest$'):case.call()

class AdditionalGuardsTests(unittest.TestCase):
    def test_index_builder_requires_block5_root(self):
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=False), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^kept_units_not_a_block5_root$'):
            inputs.block5_claim_gate_inputs(Path('unopened'),Path('unopened'),Path('runs'))
    def test_index_builder_requires_gamma_runs_root(self):
        gamma=fx.pinned_handle('GAMMA_STD')
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
             mock.patch('joulewise.b5_analysis.windows.load_window_index',return_value=SimpleNamespace(entries=())), \
             mock.patch('joulewise.b5_analysis.windows.select_analysed_attempts',return_value={'gamma':gamma.window}), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^runs_root_differs_from_window_index$'):
            inputs.block5_claim_gate_inputs(Path('unopened'),Path('unopened'),Path('different-runs'))
    def test_analysis_uses_gamma_pack_only(self):
        context=ww.ArchiveContext(Path('archive'))
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^exclusions_plan_mismatch$'):
            inputs.load_analysis_inputs(Path('unopened'),Path('runs'),Path('floor'),strict_validator=lambda *_:[],
                kept_units=SimpleNamespace(window=SimpleNamespace(pack='alpha')),
                archive_contexts={str(Path('runs').resolve()):context})
    def test_gamma_archive_required_before_member_read(self):
        context=ww.ArchiveContext(Path('archive'))
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^archive_context_required: GAMMA archive$'):
            inputs.load_analysis_inputs(Path('unopened'),Path('runs'),Path('floor'),strict_validator=lambda *_:[],
                kept_units=SimpleNamespace(window=SimpleNamespace(pack='gamma')),
                archive_contexts={str(Path('runs').resolve()):context})
    def test_finalized_manifest_requires_exclusions_role(self):
        with fx.loader_case() as case:
            case.loaded.manifest['schema_version']='joulewise.analysis_manifest.v3.finalized'
            with self.assertRaisesRegex(inputs.AnalysisInputError,'^analysed_attempt_exclusions_role_missing$'):case.call()
    def test_r3_each_exclusions_binding_is_checked(self):
        for key in ('sha256','catalog_sha256','harvest_pin','harvest_record'):
            with self.subTest(key=key),fx.loader_case() as case:
                manifest=case.loaded.manifest;manifest['schema_version']='joulewise.analysis_manifest.v3.finalized'
                role={'sha256':case.units.exclusions_sha256,'catalog_sha256':case.units.catalog_sha256,
                      'harvest_pin':case.units.window.harvest_pin,'harvest_record':{'sha256':case.units.window.harvest_record_sha256}}
                role[key]={'sha256':'f'*64} if key=='harvest_record' else 'f'*64
                manifest.setdefault('evidence',{})['analysed_attempt_exclusions']=role
                with self.assertRaisesRegex(inputs.AnalysisInputError,'^exclusions_differ_from_finalized_manifest$'):case.call()
    def test_supersession_window_refusal_is_tooling(self):
        with fx.loader_case() as case,mock.patch.object(inputs,'supersession_visibility_scan',return_value={'status':'refused'}), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^whole_window_verdict_conflict:'):
            case.call()
    def test_r6_finalization_never_reads_live_ledger(self):
        with fx.finalization_case() as f, \
             mock.patch('joulewise.calibration_ledger.load_calibration_ledger_snapshot',side_effect=AssertionError('live ledger read')):
            # ledger_prefix is stage S2, the sole authorized ledger loader; stub
            # that already-authenticated cut while probing the S5 call sites.
            with mock.patch('joulewise.b5_analysis.bracket.ledger_prefix',return_value=f['ledger_path'].read_bytes()):
                try:
                    mv3._authenticate_finalization_inputs(f['prospective'],**FinalizationBlock5Tests().args(f))
                except mv3.AnalysisManifestFinalizationError as exc:
                    self.assertNotIn('live ledger read',str(exc))
    def test_acceptance_id_must_be_active(self):
        with fx.finalization_case() as f,mock.patch.object(mv3,'load_calibration_acceptance_bound',return_value={'acceptance_id':'wrong'}), \
             self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,'^analysis_finalization_attachment_invalid: acceptance_differs_from_active$'):
            mv3._authenticate_finalization_inputs(f['prospective'],**FinalizationBlock5Tests().args(f))
    def test_claim_licensing_cannot_replace_admitted(self):
        with fx.finalization_case() as f:
            session=SimpleNamespace(_prepare=lambda **kw:None,_basis_bracket_binding=lambda:json.loads(f['bracket_path'].read_bytes()))
            with mock.patch.object(ww,'AuthenticatedConsumptionSession',return_value=session), \
                 mock.patch.object(ww,'validate_whole_window_verdict_row',return_value=SimpleNamespace(admitted=False,reasons=('cpu_admission_core_failed',))), \
                 self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,'^analysis_finalization_verdict_not_passed: cpu_admission_core_failed$'):
                mv3._authenticate_finalization_inputs(f['prospective'],**FinalizationBlock5Tests().args(f))

class PinnedValidatorBoundaryTests(unittest.TestCase):
    def test_r8_real_pinned_gamma_cpu_disagreement_remains_window_refusal(self):
        case=s3.Case('GAMMA_STD');self.addCleanup(case.close)
        case.row['idle_admission_core']['members'][0]['cpu_admission']['sample_count']+=1
        case.bind_row()
        with s3.adapter_projection(case):
            result=ww.validate_whole_window_verdict_row(case.row,case.window.claim,set(case.row['bundle_ids']),
                consumption_session=case.session())
        self.assertIn('cpu_admission_core_failed',result.reasons)
        with fx.loader_case(reasons=result.reasons) as loaded_case:
            with self.assertRaises(inputs.AnalysisInputError) as raised:loaded_case.call()
            self.assertTrue(str(raised.exception).startswith(result.reasons[0]+': '))
            self.assertFalse(str(raised.exception).startswith('member_code_on_kept_unit'))
            self.assertFalse((loaded_case.root/'output.json').exists())

class RoleAttachmentTests(unittest.TestCase):
    def seams(self,f):
        stack=contextlib.ExitStack()
        session=SimpleNamespace(_prepare=lambda **kw:None,_basis_bracket_binding=lambda:json.loads(f['bracket_path'].read_bytes()))
        stack.enter_context(mock.patch.object(ww,'AuthenticatedConsumptionSession',return_value=session))
        stack.enter_context(mock.patch.object(ww,'validate_whole_window_verdict_row',return_value=SimpleNamespace(admitted=True,reasons=())))
        stack.enter_context(mock.patch.object(ww,'whole_window_refusal_reasons',return_value=()))
        stack.enter_context(mock.patch.object(inputs,'sibling_floor_pinset',return_value=f['acceptance_path']))
        # The legacy harness artifact was genuinely validated when built; this
        # adapter isolates attachment math from S6's novel two-producer pinset.
        stack.enter_context(mock.patch('joulewise.detection_floor.validate_floor_artifact',return_value=[]))
        stack.enter_context(mock.patch.object(mv3,'is_hazard_runs_root',return_value=True))
        return stack
    def build(self,f):
        row=json.loads(f['verdict_path'].read_bytes());row['status']='failed'
        raw=(json.dumps(row)+'\n').encode();f['verdict_path'].write_bytes(raw);(f['runs_root']/'campaign_log.jsonl').write_bytes(raw)
        with self.seams(f):
            attachments=mv3._authenticate_finalization_inputs(f['prospective'],**FinalizationBlock5Tests().args(f))
            mv3._write_append_only(f['root']/attachments['analysed_attempt_exclusions']['path'],attachments['_exclusions_bytes'])
            manifest=mv3._build_finalized_manifest(f['prospective'],attachments=attachments,
                prospective_relative=f['prospective_path'].relative_to(f['root']).as_posix(),
                prospective_sha256=__import__('hashlib').sha256(f['prospective_path'].read_bytes()).hexdigest(),
                plan_tree_relative=f['plan_tree_path'].relative_to(f['root']).as_posix(),
                plan_tree_sha256=__import__('hashlib').sha256(f['plan_tree_path'].read_bytes()).hexdigest())
        path=f['root']/(f['prospective']['manifest_id']+mv3.FINALIZED_BASENAME_SUFFIX)
        return manifest,path
    def test_c3_roles_and_c4_explicit_context_replay(self):
        with fx.finalization_case() as f:
            manifest,path=self.build(f)
            self.assertTrue(mv3._BLOCK5_ROLES.issubset(manifest['evidence']))
            self.assertEqual(manifest['evidence']['whole_window_verdict']['status'],'failed')
            self.assertEqual(manifest['evidence']['analysed_attempt_exclusions']['sha256'],f['units'].exclusions_sha256)
            self.assertNotIn('b_fiducial_s',manifest['evidence']['window_bracket'])
            with self.seams(f):
                self.assertEqual(mv3.validate_finalized_analysis_manifest_v3(manifest,manifest_path=path,custody_root=f['root'],
                    acceptance_bound_path=f['acceptance_path'],_block5_inputs=f['block5_inputs']),())
    def test_c4_digest_of_copied_exclusions_is_rechecked(self):
        with fx.finalization_case() as f:
            manifest,path=self.build(f);copied=f['root']/manifest['evidence']['analysed_attempt_exclusions']['path']
            original=copied.read_bytes();self.addCleanup(copied.write_bytes,original);copied.write_bytes(original+b' ')
            with self.seams(f):
                self.assertTrue(mv3.validate_finalized_analysis_manifest_v3(manifest,manifest_path=path,custody_root=f['root'],
                    acceptance_bound_path=f['acceptance_path'],_block5_inputs=f['block5_inputs']))
    def test_c4_new_roles_are_invalid_on_non_block5_root(self):
        with fx.finalization_case() as f:
            manifest,path=self.build(f)
            with self.seams(f),mock.patch.object(mv3,'is_hazard_runs_root',return_value=False):
                self.assertTrue(mv3.validate_finalized_analysis_manifest_v3(manifest,manifest_path=path,custody_root=f['root'],
                    acceptance_bound_path=f['acceptance_path'],_block5_inputs=f['block5_inputs']))
    def test_floor_consumer_identity_uses_kept_members(self):
        with fx.finalization_case() as f:
            paths={run:f['runs_root']/run for cid in f['units'].cells for run in f['units'].kept_run_ids(cid)}
            for run in f['units'].removed_run_ids():shutil.rmtree(f['runs_root']/run,ignore_errors=True)
            self.assertEqual(len(mv3._floor_consumer_contexts(f['prospective'],paths)),4)

class CommandMissingArchiveTests(unittest.TestCase):
    def test_neg8_archive_flag_required(self):
        error=io.StringIO()
        with mock.patch('joulewise.window_lineage.is_hazard_runs_root',return_value=True),contextlib.redirect_stderr(error):
            self.assertEqual(_cmd_analyze_claims(ClaimCommandTests().args(neg8_harvest_archive=None)),2)
        self.assertEqual(error.getvalue(),'error: neg8_harvest_archive_required\n')

class BracketMetadataTests(unittest.TestCase):
    def test_c4_bracket_metadata_is_rebound_to_archive_bytes(self):
        for field,value in (('terminal_sequence',999),('ledger_copy_sha256','f'*64),
                            ('sources_sha256sums_sha256','f'*64),('trigger_scope','wrong'),
                            ('compared_with_harvest','wrong')):
            with self.subTest(field=field),fx.finalization_case() as f:
                built={**f['block5_inputs'],'brackets':{'gamma':replace(f['block5_inputs']['brackets']['gamma'],**{field:value})}}
                with RoleAttachmentTests().seams(f),self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                        '^analysis_finalization_attachment_invalid: window_bracket_metadata_mismatch$'):
                    mv3._authenticate_finalization_inputs(f['prospective'],**FinalizationBlock5Tests().args(f,block5_inputs=built))

class SessionScopeTests(unittest.TestCase):
    def test_loader_session_gets_only_kept_members_and_context(self):
        with fx.loader_case() as case:
            case.call()
            args,kwargs=inputs.AuthenticatedConsumptionSession.call_args
            self.assertEqual(args[1],set().union(*(case.units.kept_run_ids(cid) for cid in case.units.cells)))
            self.assertIs(kwargs['archive_context'],case.context)
            self.assertEqual(kwargs['calibration_ledger_snapshot'].receipts,())

class ToolingExitTests(unittest.TestCase):
    def test_member_code_exit_2_no_artifact(self):self.check('member_code_on_kept_unit')
    def test_midpoint_lost_exit_2_no_artifact(self):self.check('analysed_attempt_carries_midpoint_lost')
    def check(self,code):
        import tempfile
        with tempfile.TemporaryDirectory(prefix='s5-cli-stop-') as temporary:
            output=Path(temporary)/'claim.json';archive=fx.pinned_handle('GAMMA_STD')
            built={'gamma_archive':archive,'kept_units':object(),'archive_contexts':{}}
            error=io.StringIO()
            with mock.patch('joulewise.window_lineage.is_hazard_runs_root',return_value=True), \
                 mock.patch.object(inputs,'block5_claim_gate_inputs',return_value=built), \
                 mock.patch('joulewise.analysis_engine.analyze_claims',side_effect=inputs.AnalysisInputError(code)), \
                 contextlib.redirect_stderr(error):
                self.assertEqual(_cmd_analyze_claims(ClaimCommandTests().args(output=str(output),neg8_harvest_archive=str(archive.window.archive_root))),2)
            self.assertEqual(error.getvalue(),'error: '+code+'\n');self.assertFalse(output.exists())

class ReboundExclusionsTests(unittest.TestCase):
    def test_r3_real_kept_units_reader_accepts_rebound_variant_then_loader_refuses(self):
        import hashlib
        from joulewise.b5_analysis.archive import ArchiveHandle
        from joulewise.b5_analysis.kept_units import load_kept_units
        with fx.finalization_case() as f:
            original=f['units'];archive=f['archive']
            manifest,manifest_path=RoleAttachmentTests().build(f)
            manifest_path.write_text(json.dumps(manifest))
            path=archive.window.archive_root/'derived/exclusions.json';raw=path.read_bytes()
            self.addCleanup(path.write_bytes,raw)
            doc=json.loads(raw);doc['s5_counterfactual']='changed bytes; unchanged units'
            changed=json.dumps(doc).encode();path.write_bytes(changed)
            record=ww._archive_thaw(archive.record);record['outputs']['derived/exclusions.json']=hashlib.sha256(changed).hexdigest()
            window=copy.copy(archive.window)
            record_path=window.archive_root/'harvest.json';saved=record_path.read_bytes();self.addCleanup(record_path.write_bytes,saved)
            record_raw=json.dumps(record).encode();record_path.write_bytes(record_raw)
            window.harvest_record_sha256=hashlib.sha256(record_raw).hexdigest()
            rebound=ArchiveHandle(window,record,{})
            units=load_kept_units(rebound,sealed_catalog_sha256=original.catalog_sha256,
                planned_units=inputs.planned_contrast_units(f['prospective']))
            self.assertNotEqual(units.exclusions_sha256,original.exclusions_sha256)
            context=ww.ArchiveContext(rebound.window.archive_root,
                window_bracket=f['block5_inputs']['archive_contexts'][str(f['runs_root'].resolve())].window_bracket,
                removed_bundle_ids=units.removed_run_ids())
            with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
                 mock.patch.object(inputs,'_read_bundle',side_effect=AssertionError('member read')), \
                 self.assertRaisesRegex(inputs.AnalysisInputError,'^exclusions_differ_from_finalized_manifest$'):
                inputs.load_analysis_inputs(manifest_path,f['runs_root'],f['floor_path'],strict_validator=lambda *_:[],
                    kept_units=units,gamma_archive=rebound,archive_contexts={str(f['runs_root'].resolve()):context})

class FinalizedMemberPreflightTests(unittest.TestCase):
    def test_r2_finalized_missing_kept_member_stops_before_manifest_replay(self):
        with fx.loader_case() as case:
            manifest=case.loaded.manifest;manifest['schema_version']='joulewise.analysis_manifest.v3.finalized'
            for row in manifest['entries']:row['bundle_path']=row['run_id']
            manifest.setdefault('evidence',{})['analysed_attempt_exclusions']={
                'sha256':case.units.exclusions_sha256,'catalog_sha256':case.units.catalog_sha256,
                'harvest_pin':case.units.window.harvest_pin,'harvest_record':{'sha256':case.units.window.harvest_record_sha256}}
            run=next(iter(case.units.kept_run_ids('decode')));shutil.rmtree(case.runs/run)
            with self.assertRaisesRegex(inputs.AnalysisInputError,'^member_code_on_kept_unit$'):case.call()


class SessionPreparationIdentityTests(unittest.TestCase):
    def test_finalization_validator_prepares_full_stored_membership(self):
        """Removed members in row.bundle_ids remain on disk for row authentication."""
        real_session = ww.AuthenticatedConsumptionSession
        with fx.finalization_case(removed=(3,)) as f:
            row = json.loads(f['verdict_path'].read_bytes())
            full_paths = {bid: f['runs_root'] / bid for bid in row['bundle_ids']}
            captured = []
            def validate(row, root, referenced, *, consumption_session, **kwargs):
                captured.append(consumption_session)
                policy = ww.CampaignPolicy.from_mapping(dict(ww._registered_policy(row['campaign_policy']['sha256'])))
                consumption_session._prepare(bundle_paths=full_paths, policy=policy)
                return SimpleNamespace(admitted=consumption_session.ready, reasons=consumption_session.refusal_reasons)
            with RoleAttachmentTests().seams(f), \
                 mock.patch.object(ww, 'AuthenticatedConsumptionSession', real_session), \
                 mock.patch.object(ww, '_current_strict_summary', return_value=False), \
                 mock.patch.object(ww, 'capture_pipeline_refusal', return_value=None), \
                 mock.patch.object(ww, 'validate_whole_window_verdict_row', side_effect=validate):
                mv3._authenticate_finalization_inputs(f['prospective'], **FinalizationBlock5Tests().args(f))
            self.assertTrue(captured[0].ready)
            self.assertEqual(set(dict(captured[0]._preparation_identity)), set(row['bundle_ids']))
            self.assertEqual(captured[0].referenced_bundle_ids,
                frozenset().union(*(f['units'].kept_run_ids(cid) for cid in f['units'].cells)))

    def test_loader_leaves_preparation_to_validator(self):
        """S5 never pre-prepares; validator may authenticate removed row members."""
        real_session = ww.AuthenticatedConsumptionSession
        captured = []
        with fx.loader_case() as case:
            def validate(root, referenced, *, consumption_session, **kwargs):
                self.assertFalse(consumption_session._prepared)
                paths = {row.bundle_id: row.path for row in case.loaded.registered.values()}
                consumption_session._prepare(bundle_paths=paths, policy=SimpleNamespace())
                captured.append(consumption_session)
                return consumption_session.refusal_reasons
            with mock.patch.object(inputs, 'AuthenticatedConsumptionSession', real_session), \
                 mock.patch.object(ww, '_current_strict_summary', return_value=False), \
                 mock.patch.object(ww, 'capture_pipeline_refusal', return_value=None), \
                 mock.patch.object(real_session, 'provenance_for', return_value={'operative_fiducial_bound_s': .04}), \
                 mock.patch.object(inputs, 'whole_window_refusal_reasons', side_effect=validate):
                case.call()
            self.assertTrue(captured[0].ready)
            self.assertEqual(len(captured[0]._preparation_identity), 80)


class PublicFinalizedReplayTests(unittest.TestCase):
    def test_standalone_block5_replay_requires_and_uses_window_index(self):
        """Structural finalization harness; builder handoff isolated from replay."""
        with fx.finalization_case() as f:
            manifest, path = RoleAttachmentTests().build(f)
            index = f['root'] / 'window-index.json'
            with RoleAttachmentTests().seams(f), \
                 mock.patch.object(inputs, 'block5_claim_gate_inputs', return_value=f['block5_inputs']) as builder:
                refusals = mv3.validate_finalized_analysis_manifest_v3(manifest, manifest_path=path,
                    custody_root=f['root'], acceptance_bound_path=f['acceptance_path'])
                self.assertEqual(len(refusals), 1)
                self.assertEqual(refusals[0].reason_code, 'analysis_manifest_finalized_invalid')
                self.assertTrue(refusals[0].detail.startswith('window_index_required'))
                builder.assert_not_called()
                self.assertEqual(mv3.validate_finalized_analysis_manifest_v3(manifest, manifest_path=path,
                    custody_root=f['root'], acceptance_bound_path=f['acceptance_path'], window_index=index), ())
                builder.assert_called_once_with(index, f['prospective_path'], f['runs_root'])
                builder.reset_mock()
                self.assertEqual(mv3.validate_finalized_analysis_manifest_v3(manifest, manifest_path=path,
                    custody_root=f['root'], acceptance_bound_path=f['acceptance_path'], window_index=index,
                    _block5_inputs=f['block5_inputs']), ())
                builder.assert_not_called()


class IndexedExternalRunsRootTests(unittest.TestCase):
    """F1: reuse S5's structural fixture and its documented replay doubles."""

    @contextlib.contextmanager
    def custody(self, fixture):
        with tempfile.TemporaryDirectory(prefix='s10-finalize-custody-') as temporary:
            root = Path(temporary)
            for child in fixture['root'].iterdir():
                if child in (fixture['runs_root'], fixture['archive'].window.archive_root):
                    continue
                destination = root / child.name
                if child.is_dir():
                    shutil.copytree(child, destination)
                else:
                    shutil.copyfile(child, destination)
            yield root

    def args(self, fixture, custody, **overrides):
        values = {'custody_root': custody, 'output_dir': custody, 'runs_root': fixture['runs_root'],
                  'window_index': fixture['root'] / 'window-index.json',
                  'acceptance_bound_path': fixture['acceptance_path']}
        for argument, key in (('plan_tree_path', 'plan_tree_path'),
                              ('whole_window_verdict_path', 'verdict_path'),
                              ('bracket_binding_path', 'bracket_path'),
                              ('calibration_ledger_path', 'ledger_path'),
                              ('aggregate_floor_artifact_path', 'floor_path')):
            values[argument] = custody / fixture[key].relative_to(fixture['root'])
        values.update(overrides)
        return values

    def finalize(self, fixture, custody, **overrides):
        prospective = custody / fixture['prospective_path'].relative_to(fixture['root'])
        return mv3.finalize_prospective_analysis_manifest_v3(
            prospective, **self.args(fixture, custody, **overrides))

    def test_F1_a_indexed_external_root_finalizes_replays_and_is_custody_independent(self):
        with fx.finalization_case() as f, self.custody(f) as first, self.custody(f) as second, \
             RoleAttachmentTests().seams(f), \
             mock.patch.object(inputs, 'block5_claim_gate_inputs', return_value=f['block5_inputs']) as builder:
            self.assertFalse(f['runs_root'].is_relative_to(first))
            manifests = []
            for custody in (first, second):
                manifest = self.finalize(f, custody)
                path = custody / (f['prospective']['manifest_id'] + mv3.FINALIZED_BASENAME_SUFFIX)
                self.assertEqual(mv3.validate_finalized_analysis_manifest_v3(
                    manifest, manifest_path=path, custody_root=custody,
                    acceptance_bound_path=f['acceptance_path'], window_index=f['root'] / 'window-index.json'), ())
                for role in mv3._REQUIRED_ATTACHMENT_ROLES:
                    self.assertFalse(Path(manifest['evidence'][role]['path']).is_absolute())
                manifests.append(path.read_bytes())
            self.assertEqual(manifests[0], manifests[1])
            self.assertEqual(builder.call_count, 4)
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: whole-window verdict: path is outside custody$'):
                self.finalize(f, first, whole_window_verdict_path=f['verdict_path'])

    def test_F1_b_an_external_copy_is_not_the_indexed_window(self):
        with fx.finalization_case() as f, self.custody(f) as custody, \
             RoleAttachmentTests().seams(f), \
             mock.patch.object(inputs, 'block5_claim_gate_inputs', return_value=f['block5_inputs']):
            other = custody.parent / (custody.name + '-runs-copy')
            shutil.copytree(f['runs_root'], other)
            self.addCleanup(shutil.rmtree, other)
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: runs_root_not_the_indexed_window$'):
                mv3._finalization_runs_root(other, custody, 'runs root', f['block5_inputs'])
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: runs_root_not_the_indexed_window$'):
                self.finalize(f, custody, runs_root=other)

    def test_F1_c_no_index_keeps_the_original_containment_refusal(self):
        with fx.finalization_case() as f, self.custody(f) as custody:
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: runs root: path is outside custody$'):
                mv3._finalization_runs_root(f['runs_root'], custody, 'runs root', None)
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: runs root: path is outside custody$'):
                self.finalize(f, custody, window_index=None)

    def test_F1_d_bracket_root_must_be_the_indexed_window(self):
        with fx.finalization_case() as f, self.custody(f) as custody, \
             RoleAttachmentTests().seams(f), \
             mock.patch.object(inputs, 'block5_claim_gate_inputs', return_value=f['block5_inputs']):
            bracket_path = self.args(f, custody)['bracket_binding_path']
            bracket = json.loads(bracket_path.read_bytes())
            bracket['runs_root'] = str(custody)
            bracket_path.write_text(json.dumps(bracket))
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: runs_root_not_the_indexed_window$'):
                self.finalize(f, custody)

    def test_index_builder_mismatch_retains_the_F1_detail(self):
        with fx.finalization_case() as f, self.custody(f) as custody, \
             RoleAttachmentTests().seams(f), \
             mock.patch.object(inputs, 'block5_claim_gate_inputs',
                               side_effect=inputs.AnalysisInputError('runs_root_differs_from_window_index')):
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_attachment_invalid: runs_root_not_the_indexed_window$'):
                self.finalize(f, custody)


class Block5ClosedSetScanTests(unittest.TestCase):
    def test_unregistered_matching_bundle_is_found_on_block5(self):
        """Real scan on a synthetic root; removed writer-included members stay unread by S5."""
        with fx.loader_case() as case:
            kept = {key: row for key, row in case.loaded.registered.items()
                    if row.bundle_id not in case.units.removed_run_ids()}
            target = next(iter(kept.values()))
            extra = case.runs / 'unregistered-matching'
            extra.mkdir()
            (extra / 'config.json').write_text(json.dumps(target.raw_config))
            # Reading a removed directory as a candidate would fail admission.
            for run in case.units.removed_run_ids():
                (case.runs / run / 'config.json').write_text('{invalid removed bytes')
            direct = inputs._scan_replacements_and_topups(case.loaded.manifest, case.manifest_path.parent,
                case.runs, lambda *_: [], kept, {}, {}, excluded_bundle_ids=case.units.removed_run_ids())
            self.assertEqual(direct[3][0]['bundle_id'], extra.name)
            loaded = case.call()
            self.assertEqual(loaded.unregistered_matching, tuple(direct[3]))
            self.assertEqual(loaded.top_up_entry_ids, frozenset(direct[4]))
            self.assertTrue(loaded.top_up_entry_ids)
            self.assertEqual(set(loaded.effective), set(case.loaded.registered))
            self.assertFalse(case.units.removed_run_ids() & set(case.reader_calls))


class RealIndexedBuilderTests(unittest.TestCase):
    def test_real_index_builder_refuses_a_floor_shaped_archive_as_gamma(self):
        """Pinned-harvest archives (S0), nothing replaced but S2's capture adapter.

        The real builder loads the index (a complete history: BETA's five earlier
        attempts are no-archive entries), opens every attempt record, selects the
        three analysed windows and opens GAMMA's archive. S0's synthetic GAMMA
        window is shaped like a floor pack (its one cell has a repeat stratum),
        so the kept-units reader refuses it against a contrast manifest. The
        positive run of the builder needs a GAMMA-shaped synthetic window, which
        stage S10's chain fixture owns.
        """
        from joulewise.b5_analysis.windows import AnalysisRefusal
        from joulewise.b5_analysis import archive as archive_module, kept_units as kept_module
        case = fx.indexed_gamma_case()
        attempts = json.loads(case.index.read_bytes())['attempts']
        self.assertIn(case.gamma.entry_data, attempts)
        self.assertEqual(sorted(row['attempt'] for row in attempts if row['pack'] == 'beta'), [1, 2, 3, 4, 5, 6])
        opened = []
        real_open, real_load = archive_module.open_archive, kept_module.load_kept_units
        def spy_open(window, **kwargs):
            opened.append(window.pack); return real_open(window, **kwargs)
        loads = []
        def spy_load(archive, **kwargs):
            loads.append(archive.window.pack); return real_load(archive, **kwargs)
        with mock.patch.object(archive_module, 'open_archive', side_effect=spy_open), \
             mock.patch.object(kept_module, 'load_kept_units', side_effect=spy_load), \
             self.assertRaisesRegex(AnalysisRefusal, '^exclusions_plan_mismatch$'):
            fx.real_indexed_gamma_inputs()
        self.assertEqual((opened, loads), (['gamma'], ['gamma']))


class OperativeWindowBoundTests(unittest.TestCase):
    def test_kept_members_carry_the_window_bracket_bound(self):
        """Synthetic loader handoff; kept members use the explicit context bound."""
        with fx.loader_case() as case:
            loaded = case.call()
            for row in loaded.effective.values():
                if row.included:
                    self.assertEqual(row.consumption_provenance['operative_fiducial_bound_s'],
                                     case.context.window_bracket['b_fiducial_s'])
    def test_another_windows_bound_is_refused(self):
        with fx.loader_case() as case:
            first = next(iter(case.units.kept_run_ids('decode')))
            case.session.provenance_for = lambda bid: {'operative_fiducial_bound_s': .05 if bid == first else .04}
            with self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                case.call()
    def test_missing_kept_provenance_is_refused(self):
        with fx.loader_case() as case:
            case.session.provenance_for = lambda bid: None
            with self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                case.call()
    def test_session_not_ready_is_refused_not_served_from_stored_summaries(self):
        """Hand-built loader boundary. A session that is not ready and reports no
        window refusal must not leave kept members on their stored summaries."""
        with fx.loader_case() as case:
            case.session.ready = False
            with self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                case.call()
    def test_kept_member_without_operative_summary_is_refused(self):
        """Hand-built loader boundary. One kept member for which the session has
        no re-reduced summary must stop the load, not fall back to the stored one."""
        with fx.loader_case() as case:
            first = next(iter(case.units.kept_run_ids('decode')))
            served = case.session.summary_for
            case.session.summary_for = lambda bid: None if bid == first else served(bid)
            with self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                case.call()


class RemainingFinalizedGuardsTests(unittest.TestCase):
    def test_exact_new_role_keys_before_attachment_replay(self):
        with fx.finalization_case() as f:
            manifest, path = RoleAttachmentTests().build(f)
            for role in mv3._BLOCK5_ROLES:
                with self.subTest(role=role):
                    changed = copy.deepcopy(manifest); changed['evidence'][role]['unexpected'] = True
                    with mock.patch.object(mv3, '_authenticate_finalization_inputs') as replay:
                        errors = mv3.validate_finalized_analysis_manifest_v3(changed, manifest_path=path,
                            custody_root=f['root'], _block5_inputs=f['block5_inputs'])
                    self.assertEqual(errors[0].reason_code, 'analysis_manifest_finalized_invalid')
                    self.assertIn('unexpected', errors[0].detail)
                    replay.assert_not_called()
    def test_exact_nested_harvest_keys_before_attachment_replay(self):
        with fx.finalization_case() as f:
            manifest, path = RoleAttachmentTests().build(f)
            manifest['evidence']['analysed_attempt_exclusions']['harvest_record']['unexpected'] = True
            with mock.patch.object(mv3, '_authenticate_finalization_inputs') as replay:
                errors = mv3.validate_finalized_analysis_manifest_v3(manifest, manifest_path=path,
                    custody_root=f['root'], _block5_inputs=f['block5_inputs'])
            self.assertEqual(errors[0].reason_code, 'analysis_manifest_finalized_invalid')
            self.assertIn('harvest_record', errors[0].detail)
            replay.assert_not_called()
    def test_harvest_record_bytes_digest_is_rechecked(self):
        with fx.finalization_case() as f:
            manifest, path = RoleAttachmentTests().build(f)
            harvest = Path(manifest['evidence']['analysed_attempt_exclusions']['harvest_record']['path'])
            original = harvest.read_bytes(); self.addCleanup(harvest.write_bytes, original)
            harvest.write_bytes(original + b' ')
            with RoleAttachmentTests().seams(f):
                errors = mv3.validate_finalized_analysis_manifest_v3(manifest, manifest_path=path,
                    custody_root=f['root'], acceptance_bound_path=f['acceptance_path'], _block5_inputs=f['block5_inputs'])
            self.assertEqual(errors[0].reason_code, 'analysis_manifest_lineage_mismatch')
            self.assertIn('harvest record digest mismatch', errors[0].detail)
    def test_unknown_kept_cell_becomes_plan_mismatch(self):
        loaded = fx.arithmetic_inputs([3.] * 10)
        units = replace(loaded.kept_units, cells={})
        with self.assertRaisesRegex(inputs.AnalysisInputError, '^exclusions_plan_mismatch$'):
            inputs._check_kept_plan(loaded.manifest, units)
    def test_later_loader_passes_include_only_kept_members(self):
        with fx.loader_case() as case:
            removed = case.units.removed_run_ids()
            def identity(manifest, evidence):
                self.assertFalse(removed & {row.bundle_id for row in evidence.values()})
                return {}
            def lineage(evidence):
                self.assertFalse(removed & {row.bundle_id for row in evidence})
            with mock.patch.object(inputs, '_enforce_registered_realized_identity', side_effect=identity), \
                 mock.patch.object(inputs, '_require_common_launch_lineage', side_effect=lineage):
                loaded = case.call()
            for row in loaded.registered.values():
                if row.bundle_id in removed:
                    self.assertIsNone(row.summary)
                    self.assertIsNone(row.consumption_provenance)
    def test_finalized_preflight_skips_writer_excluded_removed_members(self):
        """Removed members absent from row.bundle_ids (writer excluded_bundles); directories deleted."""
        with fx.loader_case() as case:
            manifest = case.loaded.manifest
            manifest['schema_version'] = mv3.FINALIZED_SCHEMA_VERSION
            for row in manifest['entries']: row['bundle_path'] = row['run_id']
            manifest.setdefault('evidence', {})['analysed_attempt_exclusions'] = {
                'sha256': case.units.exclusions_sha256, 'catalog_sha256': case.units.catalog_sha256,
                'harvest_pin': case.units.window.harvest_pin,
                'harvest_record': {'sha256': case.units.window.harvest_record_sha256}}
            for bid in case.units.removed_run_ids(): shutil.rmtree(case.runs / bid)
            case.units.window.governed_e3 = False
            case.archive.output_bytes = lambda name: b'{"sequence":1}'
            case.archive.source_bytes = lambda name: b''
            sources = case.units.window.archive_root / 'sources'; sources.mkdir()
            (sources / 'SHA256SUMS').write_bytes(b'')
            with mock.patch.object(inputs, 'load_manifest', side_effect=RuntimeError('manifest replay checkpoint')) as replay:
                with self.assertRaisesRegex(RuntimeError, '^manifest replay checkpoint$'):
                    case.call()
            replay.assert_called_once()
            self.assertFalse(case.units.removed_run_ids() & set(case.reader_calls))


class RemovedMemberSeamVariants(unittest.TestCase):
    def test_loader_leaves_writer_included_removed_members_unopened(self):
        """Removed members in row.bundle_ids stay on disk; row validator is a handoff double."""
        with fx.loader_case() as case:
            self.assertTrue(all((case.runs / bid).is_dir() for bid in case.units.removed_run_ids()))
            loaded = case.call()
            self.assertFalse(case.units.removed_run_ids() & set(case.reader_calls))
            self.assertTrue(all(row.summary is None for row in loaded.registered.values()
                                if row.bundle_id in case.units.removed_run_ids()))
    def test_basis_and_identity_skip_writer_excluded_removed_members(self):
        """Removed members absent from row.bundle_ids and in excluded_bundles; directories deleted."""
        with fx.finalization_case(removed=(7,)) as f:
            removed = f['units'].removed_run_ids()
            kept = frozenset().union(*(f['units'].kept_run_ids(cid) for cid in f['units'].cells))
            row = json.loads(f['verdict_path'].read_bytes())
            row['bundle_ids'] = [bid for bid in row['bundle_ids'] if bid not in removed]
            row['evaluation_basis']['member_occurrences'] = [m for m in row['evaluation_basis']['member_occurrences']
                                                              if m['bundle_id'] not in removed]
            basis = row['evaluation_basis']
            basis['sha256'] = mv3._canonical_sha({key: value for key, value in basis.items() if key != 'sha256'})
            row['excluded_bundles'] = [{'bundle_id': bid} for bid in sorted(removed)]
            for bid in removed: shutil.rmtree(f['runs_root'] / bid)
            _, paths = mv3._verify_basis_members(f['prospective'], row, manifest_dir=f['prospective_path'].parent,
                runs_root=f['runs_root'], kept_run_ids=kept)
            self.assertEqual(set(paths), kept)
            _, entries, _ = mv3._derive_arms_and_entries(f['prospective'], manifest_dir=f['prospective_path'].parent,
                runs_root=f['runs_root'], bundle_paths=paths, removed_run_ids=removed)
            self.assertTrue(all(entry['bundle_path'] is None for entry in entries if entry['run_id'] in removed))


class S5FixArchiveTests(unittest.TestCase):
    """F1 regressions at the loader and CLI, using structural synthetic windows."""
    def test_f1a_loader_uses_context_archive_for_equivalent_spelling(self):
        with fx.loader_case() as case:
            alias = case.root / 'extra' / '..' / 'archive'
            (case.root / 'extra').mkdir()
            result = SimpleNamespace(status='allowances', allowances={'synthetic': {'value': .1}})
            with mock.patch.object(inputs, 'whole_window_drift_allowances', return_value=result) as allowance:
                loaded = case.call(neg8_harvest_archive=alias)
            self.assertEqual(allowance.call_args.kwargs['neg8_harvest_archive'], case.context.neg8_harvest_archive)
            self.assertTrue(all(row.whole_window_drift_allowances == result.allowances
                                for row in loaded.effective.values() if row.summary is not None))

    def test_f1a_loader_refuses_different_archive(self):
        with fx.loader_case() as case, self.assertRaisesRegex(inputs.AnalysisInputError,
                '^neg8_archive_differs_from_window_index$'):
            case.call(neg8_harvest_archive=case.root / 'other-archive')

    def test_f1a_command_passes_index_archive(self):
        with fx.loader_case() as case:
            alias = case.root / 'extra' / '..' / 'archive'
            (case.root / 'extra').mkdir()
            args = ClaimCommandTests().args(neg8_harvest_archive=str(alias))
            built = {'gamma_archive': case.archive, 'kept_units': case.units, 'archive_contexts': {}}
            with mock.patch('joulewise.window_lineage.is_hazard_runs_root', return_value=True), \
                 mock.patch.object(inputs, 'block5_claim_gate_inputs', return_value=built), \
                 mock.patch('joulewise.analysis_engine.analyze_claims', return_value={
                     'claim_verdicts_id': 'synthetic', 'contrasts': []}) as analyze, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(_cmd_analyze_claims(args), 0)
            self.assertEqual(analyze.call_args.kwargs['neg8_harvest_archive'], case.archive.window.archive_root)

    def test_f1b_block5_requires_recorded_allowances(self):
        for status in ('absent', 'legacy'):
            with self.subTest(status=status), fx.loader_case() as case, \
                 mock.patch.object(inputs, 'whole_window_drift_allowances',
                                   return_value=SimpleNamespace(status=status, allowances={})), \
                 self.assertRaisesRegex(inputs.AnalysisInputError,
                     '^drift_allowance_not_recorded_on_block5_root: ' + status + '$'):
                case.call()

    def test_f1b_command_stops_without_artifact(self):
        for status in ('absent', 'legacy'):
            with self.subTest(status=status), fx.loader_case() as case:
                args = ClaimCommandTests().args(output=str(case.root / 'no-artifact.json'),
                    neg8_harvest_archive=str(case.archive.window.archive_root))
                built = {'gamma_archive': case.archive, 'kept_units': case.units, 'archive_contexts': {}}
                error = io.StringIO()
                with mock.patch('joulewise.window_lineage.is_hazard_runs_root', return_value=True), \
                     mock.patch.object(inputs, 'block5_claim_gate_inputs', return_value=built), \
                     mock.patch('joulewise.analysis_engine.analyze_claims', side_effect=lambda *a, **k: (case.call(), {'claim_verdicts_id': 'synthetic', 'contrasts': []})[1]), \
                     mock.patch.object(inputs, 'whole_window_drift_allowances',
                                       return_value=SimpleNamespace(status=status, allowances={})), \
                     contextlib.redirect_stderr(error):
                    self.assertEqual(_cmd_analyze_claims(args), 2)
                self.assertEqual(error.getvalue(), 'error: drift_allowance_not_recorded_on_block5_root: ' + status + '\n')
                self.assertFalse(Path(args.output).exists())


    def test_f1b_pre_block5_keeps_absent_and_legacy_behavior(self):
        for status in ('absent', 'legacy'):
            with self.subTest(status=status), fx.loader_case(removed=()) as case, \
                 mock.patch.object(inputs, 'is_hazard_runs_root', return_value=False), \
                 mock.patch.object(inputs, 'whole_window_drift_allowances',
                                   return_value=SimpleNamespace(status=status, allowances={})):
                loaded = case.call(kept_units=None, archive_contexts=None, gamma_archive=None,
                    calibration_ledger_snapshot=inputs.archive_snapshot(case.context))
                self.assertTrue(loaded.effective)
                self.assertTrue(all(row.whole_window_drift_allowance_required == (status != 'legacy')
                                    for row in loaded.effective.values()))
                self.assertIsNone(loaded.kept_quads)


class WindowAgreementFixTests(unittest.TestCase):
    """F3 regressions with distinct synthetic attempts and context removal sets."""
    def test_f3_archive_window_mismatch_precedes_midpoint_and_reads(self):
        with fx.loader_case() as case:
            wrong = copy.copy(case.archive.window)
            wrong.archive_root = case.root / 'another-attempt'
            wrong.harvest_pin = '7' * 40
            wrong.harvest_record_sha256 = '8' * 64
            archive = SimpleNamespace(window=wrong)
            with mock.patch.object(inputs, 'require_contrast_attempt_keeps_midpoint') as guard, \
                 mock.patch.object(inputs, 'load_manifest', side_effect=AssertionError('manifest opened')), \
                 self.assertRaisesRegex(inputs.AnalysisInputError, '^context_window_mismatch$'):
                case.call(gamma_archive=archive)
            guard.assert_not_called()
            self.assertEqual(case.reader_calls, [])

    def test_f3_context_archive_mismatch_precedes_midpoint_and_reads(self):
        with fx.loader_case() as case:
            context = ww.ArchiveContext(case.root / 'third-archive',
                window_bracket=case.context.window_bracket, removed_bundle_ids=frozenset())
            with mock.patch.object(inputs, 'require_contrast_attempt_keeps_midpoint') as guard, \
                 mock.patch.object(inputs, 'load_manifest', side_effect=AssertionError('manifest opened')), \
                 self.assertRaisesRegex(inputs.AnalysisInputError, '^context_window_mismatch$'):
                case.call(archive_contexts={str(case.runs.resolve()): context})
            guard.assert_not_called()
            self.assertEqual(case.reader_calls, [])

    def test_f3_registered_removed_set_must_agree_before_members(self):
        with fx.loader_case() as case:
            removed = case.units.removed_run_ids()
            kept = next(row['run_id'] for row in case.loaded.manifest['entries'] if row['run_id'] not in removed)
            for changed in (removed - {next(iter(removed))}, removed | {kept}):
                with self.subTest(removed=sorted(changed)):
                    context = ww.ArchiveContext(case.context.neg8_harvest_archive,
                        window_bracket=case.context.window_bracket, removed_bundle_ids=changed)
                    with self.assertRaisesRegex(inputs.AnalysisInputError, '^context_kept_units_mismatch$'):
                        case.call(archive_contexts={str(case.runs.resolve()): context})
                    self.assertEqual(case.reader_calls, [])

    def test_f3_removed_references_outside_manifest_are_allowed(self):
        with fx.loader_case() as case:
            context = ww.ArchiveContext(case.context.neg8_harvest_archive,
                window_bracket=case.context.window_bracket,
                removed_bundle_ids=case.units.removed_run_ids() | {'excluded-reference', 'absent-spare'})
            loaded = case.call(archive_contexts={str(case.runs.resolve()): context})
            self.assertEqual(set(case.reader_calls), {row['run_id'] for row in loaded.manifest['entries']}
                - case.units.removed_run_ids())


class LicensingAndScanS5FixTests(unittest.TestCase):
    def test_ta_only_literal_true_licenses_an_admitted_context_row(self):
        """Structural finalization; row validator explicitly admits the failed row."""
        with fx.finalization_case() as fixture:
            for licensing in (True, False, None, 'true', 1):
                with self.subTest(claim_licensing=licensing):
                    verdict = json.loads(fixture['verdict_path'].read_bytes())
                    verdict.update(status='failed', claim_licensing=licensing)
                    raw = (json.dumps(verdict) + '\n').encode()
                    fixture['verdict_path'].write_bytes(raw)
                    (fixture['runs_root'] / 'campaign_log.jsonl').write_bytes(raw)
                    with RoleAttachmentTests().seams(fixture):
                        if licensing is True:
                            mv3._authenticate_finalization_inputs(fixture['prospective'],
                                **FinalizationBlock5Tests().args(fixture))
                        else:
                            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                                    '^analysis_finalization_verdict_not_passed: whole-window verdict must be claim-licensing and passed$'):
                                mv3._authenticate_finalization_inputs(fixture['prospective'],
                                    **FinalizationBlock5Tests().args(fixture))

    def test_tc_loader_scan_hides_removed_bundles_on_disk(self):
        """Writer-included removed members have configs on disk; S5's scan hides them."""
        with fx.loader_case() as case:
            removed = case.units.removed_run_ids()
            by_id = {row.bundle_id: row for row in case.loaded.registered.values()}
            for run_id in removed:
                (case.runs / run_id / 'config.json').write_text(json.dumps(by_id[run_id].raw_config))
            loaded = case.call()
            self.assertEqual(loaded.unregistered_matching, ())
            self.assertEqual(loaded.top_up_entry_ids, frozenset())


class FinalizationCoverageS5FixTests(unittest.TestCase):
    def test_tf_kept_member_must_be_in_verdict_membership(self):
        with fx.finalization_case() as fixture:
            units = fixture['units']
            kept = frozenset(run_id for cid in units.cells for run_id in units.kept_run_ids(cid))
            verdict = json.loads(fixture['verdict_path'].read_bytes())
            missing = sorted(kept)[0]
            verdict['bundle_ids'] = [bid for bid in verdict['bundle_ids'] if bid != missing]
            with self.assertRaisesRegex(mv3.AnalysisManifestFinalizationError,
                    '^analysis_finalization_member_cover_mismatch:'):
                mv3._verify_basis_members(fixture['prospective'], verdict,
                    manifest_dir=fixture['prospective_path'].parent, runs_root=fixture['runs_root'], kept_run_ids=kept)

    def test_tg_exclusions_role_uses_kept_units_catalog_digest(self):
        with fx.finalization_case() as fixture, RoleAttachmentTests().seams(fixture):
            attachments = mv3._authenticate_finalization_inputs(fixture['prospective'],
                **FinalizationBlock5Tests().args(fixture))
            self.assertNotEqual(fixture['units'].catalog_sha256, '0' * 64)
            self.assertEqual(attachments['analysed_attempt_exclusions']['catalog_sha256'],
                fixture['units'].catalog_sha256)
