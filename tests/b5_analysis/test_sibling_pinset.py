"""S5 sibling custody probes; hand-built two-producer synthetic mint fixture."""
import atexit
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from joulewise.analysis_engine import inputs
from tests.test_mint_floor_artifact_generalized import freeze_synthetic_v2_pinset
from scripts import mint_floor_artifact_generalized as mint
from tests.b5_analysis import fixtures_s5 as fx

_CACHE=None

def minted():
    global _CACHE
    if _CACHE is None:
        tmp=tempfile.TemporaryDirectory(prefix='s5-pinset-base-');atexit.register(tmp.cleanup)
        root=Path(tmp.name)
        path,digest,producers,snapshot=freeze_synthetic_v2_pinset(root)
        value=mint.mint_multi_cell_authenticated_artifact(pinset_path=path,pinset_sha256=digest,
            producer_inputs=producers,calibration_ledger_snapshot=snapshot,project_commit='0'*40,project_tree_state='clean')
        _CACHE=(value,path.read_bytes())
    return copy.deepcopy(_CACHE)

class SiblingPinsetTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix='s5-sibling-');self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        self.value,self.pinbytes=minted()
        self.floor=self.root/'floor.json'
        self.sibling=self.root/self.value['provenance']['calibration_plan']['relative_path']
        self.sibling.write_bytes(self.pinbytes);self.write_floor()
    def write_floor(self):self.floor.write_text(json.dumps(self.value)+'\n')
    def test_r9_sibling_two_producer_authentication(self):
        self.assertEqual(inputs.sibling_floor_pinset(self.floor),self.sibling)
        loaded=inputs.load_floor_artifact(self.floor,require_sibling_pinset=True)
        self.assertEqual(loaded.value,self.value)
        self.assertEqual(len(loaded.value['provenance']['producer_calibration_plans']),2)
    def test_r9_absent_sibling_never_uses_repository(self):
        self.sibling.unlink()
        repository=self.root/'repository';repository.mkdir()
        (repository/self.sibling.name).write_bytes(self.pinbytes)
        with mock.patch('joulewise.detection_floor._FLOOR_MINT_PINSET_DIRECTORY',repository), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^floor_pinset_not_beside_floor:'):
            inputs.load_floor_artifact(self.floor,require_sibling_pinset=True)
    def test_r9_directory_component(self):
        self.value['provenance']['calibration_plan']['relative_path']='sub/pinset.json';self.write_floor()
        with self.assertRaisesRegex(inputs.AnalysisInputError,'^floor_pinset_not_beside_floor:'):
            inputs.sibling_floor_pinset(self.floor)
    def test_r9_symlink(self):
        target=self.root/'actual.json';self.sibling.rename(target);self.sibling.symlink_to(target)
        with self.assertRaisesRegex(inputs.AnalysisInputError,'^floor_pinset_not_beside_floor:'):
            inputs.sibling_floor_pinset(self.floor)

class FloorContextTests(unittest.TestCase):
    def test_a1_lazy_exports_are_the_sealed_consumer(self):
        from joulewise.b5_analysis.kept_units import KeptUnits,load_kept_units
        self.assertIs(inputs.KeptUnits,KeptUnits)
        self.assertIs(inputs.load_kept_units,load_kept_units)
        self.assertIn('KeptUnits',inputs.__all__);self.assertIn('load_kept_units',inputs.__all__)
    def test_floor_context_required_before_ledger(self):
        with tempfile.TemporaryDirectory(prefix='s5-floor-context-') as temporary:
            root=Path(temporary)
            with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
                 mock.patch.object(inputs,'load_calibration_ledger_snapshot',side_effect=AssertionError('live ledger read')), \
                 self.assertRaisesRegex(inputs.AnalysisInputError,'^archive_context_required: alpha$'):
                inputs.bind_floor_artifact_evidence({},root/'floor.json',{'alpha':root},strict_validator=lambda *_:[])
    def test_floor_context_never_reads_live_ledger(self):
        from joulewise.whole_window import ArchiveContext
        from types import SimpleNamespace
        value,raw=minted()
        with tempfile.TemporaryDirectory(prefix='s5-floor-bind-') as temporary:
            root=Path(temporary);floor=root/'floor.json';floor.write_text(json.dumps(value))
            ids={cell['provenance'][kind]['evidence_root_id'] for cell in value['cells'] for kind in ('absolute','comparative')}
            roots={rid:root/rid for rid in ids}
            for path in roots.values():path.mkdir()
            contexts={str(path.resolve()):ArchiveContext(root/'archive',window_bracket={'status':'passed','b_fiducial_s':.04}) for path in roots.values()}
            cap=inputs.AuthenticatedFloorArtifact(value,floor.read_bytes(),'a'*64,frozenset(ids))
            with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
                 mock.patch.object(inputs,'load_calibration_ledger_snapshot',side_effect=AssertionError('live ledger read')), \
                 mock.patch.object(inputs,'_floor_producer_plans',return_value=({},())), \
                 mock.patch.object(inputs,'_campaign_order_binding_problems',return_value=()), \
                 mock.patch.object(inputs,'AuthenticatedConsumptionSession',return_value=SimpleNamespace(ready=False)), \
                 mock.patch.object(inputs,'whole_window_refusal_reasons',return_value=()), \
                 self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                inputs.bind_floor_artifact_evidence(value,floor,roots,strict_validator=lambda *_:[],
                    _authenticated_floor=cap,archive_contexts=contexts)

class SerializedFloorPinsetTests(unittest.TestCase):
    def test_embedded_novel_floor_uses_explicit_sibling_pinset(self):
        import base64
        import hashlib
        from tests.test_analysis_integration import _v3_fixture_artifact
        from joulewise.analysis_engine.artifact import validate_claim_verdicts,calculate_claim_verdicts_id
        value,pinraw=minted();raw=(json.dumps(value)+'\n').encode()
        with tempfile.TemporaryDirectory(prefix='s5-embedded-') as temporary:
            root=Path(temporary);pin=root/value['provenance']['calibration_plan']['relative_path'];pin.write_bytes(pinraw)
            artifact=_v3_fixture_artifact()
            artifact['inputs']['floor_artifact'].update(artifact_id=value['artifact_id'],file_sha256=hashlib.sha256(raw).hexdigest(),
                embedded_bytes_base64=base64.b64encode(raw).decode())
            artifact['claim_verdicts_id']=calculate_claim_verdicts_id(artifact)
            prefix='artifact.inputs.floor_artifact.embedded_bytes_base64:'
            self.assertTrue(any(error.startswith(prefix) for error in validate_claim_verdicts(artifact)))
            self.assertFalse(any(error.startswith(prefix) for error in validate_claim_verdicts(artifact,floor_pinset_path=pin)))

class SeparationPinsetTests(unittest.TestCase):
    def test_output_separation_authenticates_sibling_without_repository_search(self):
        value,pinraw=minted()
        with tempfile.TemporaryDirectory(prefix='s5-separation-') as temporary:
            root=Path(temporary);floor=root/'floor.json';floor.write_text(json.dumps(value))
            (root/value['provenance']['calibration_plan']['relative_path']).write_bytes(pinraw)
            ids={cell['provenance'][kind]['evidence_root_id'] for cell in value['cells'] for kind in ('absolute','comparative')}
            mapping={rid:root/rid for rid in ids};mapping['extra']=root/'extra'
            with mock.patch('joulewise.detection_floor._repository_floor_mint_pinsets',side_effect=AssertionError('repository pinset search')):
                self.assertEqual(inputs.declared_evidence_roots(floor,mapping,require_sibling_pinset=True),
                                 {rid:root/rid for rid in ids})


class RemainingSiblingNameTests(unittest.TestCase):
    setUp = SiblingPinsetTests.setUp
    write_floor = SiblingPinsetTests.write_floor
    def test_empty_name_is_refused_before_path_checks(self):
        self.value['provenance']['calibration_plan']['relative_path'] = ''; self.write_floor()
        with self.assertRaisesRegex(inputs.AnalysisInputError, '^floor_pinset_not_beside_floor: invalid name$'):
            inputs.sibling_floor_pinset(self.floor)
    def test_backslash_name_is_refused_even_if_file_exists(self):
        name = 'nested\\pinset.json'
        (self.root / name).write_bytes(self.pinbytes)
        self.value['provenance']['calibration_plan']['relative_path'] = name; self.write_floor()
        with self.assertRaisesRegex(inputs.AnalysisInputError, '^floor_pinset_not_beside_floor: invalid name$'):
            inputs.sibling_floor_pinset(self.floor)
    def test_directory_name_is_refused_even_if_file_exists(self):
        sub = self.root / 'sub'; sub.mkdir(); (sub / 'pinset.json').write_bytes(self.pinbytes)
        self.value['provenance']['calibration_plan']['relative_path'] = 'sub/pinset.json'; self.write_floor()
        with self.assertRaisesRegex(inputs.AnalysisInputError, '^floor_pinset_not_beside_floor: invalid name$'):
            inputs.sibling_floor_pinset(self.floor)


class RemainingFloorDispatchTests(unittest.TestCase):
    def test_removed_floor_member_refuses_before_any_member_read(self):
        from tests.b5_analysis import fixtures_s5 as fx
        with fx.floor_dispatch_case(removed=True) as case:
            with self.assertRaisesRegex(inputs.AnalysisInputError, '^floor_artifact_invalid: removed floor member$'):
                case.call()
            case.readers.assert_not_called()
            self.assertEqual(case.sessions, {})
    def test_floor_context_selection_and_operative_summary_dispatch(self):
        from tests.b5_analysis import fixtures_s5 as fx
        with fx.floor_dispatch_case() as case:
            result = case.call()
            self.assertEqual(case.seen, [42., 99.])
            self.assertEqual(result.bound_cell_ids, frozenset({'first', 'second'}))
            for rid, (_, members, kwargs) in case.sessions.items():
                self.assertEqual(members, {'member-' + rid})
                self.assertIs(kwargs['archive_context'], case.contexts[str(case.roots[rid].resolve())])
                self.assertEqual(kwargs['calibration_ledger_snapshot'].receipts, ())


class FloorOperativeBoundFixTests(unittest.TestCase):
    """F2: floor dispatch consumes only each structural root's operative summaries."""
    def session_override(self, case, change):
        def session(path, members, **kwargs):
            rid = Path(path).name
            bound = case.contexts[str(Path(path).resolve())].window_bracket['b_fiducial_s']
            value = 42. if rid == 'first' else 99.
            result = SimpleNamespace(ready=True,
                summary_for=lambda bid: {'status': 'succeeded', 'value': value},
                provenance_for=lambda bid: {'operative_fiducial_bound_s': bound})
            change(result, rid)
            return result
        return mock.patch.object(inputs, 'AuthenticatedConsumptionSession', side_effect=session)

    def test_f2_not_ready_without_reasons_refuses_before_members(self):
        with fx.floor_dispatch_case() as case:
            with self.session_override(case, lambda session, rid: setattr(session, 'ready', False)), \
                 self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                case.call()
            case.readers.assert_not_called()

    def test_f2_missing_operative_summary_refuses(self):
        with fx.floor_dispatch_case() as case:
            def change(session, rid):
                if rid == 'first': session.summary_for = lambda bid: None
            with self.session_override(case, change), \
                 self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                case.call()
            self.assertEqual(case.seen, [])

    def test_f2_missing_or_other_root_bound_refuses(self):
        for provenance in (None, {}, {'operative_fiducial_bound_s': .04},
                           {'operative_fiducial_bound_s': .01}, {'operative_fiducial_bound_s': .06}):
            with self.subTest(provenance=provenance), fx.floor_dispatch_case() as case:
                def change(session, rid):
                    if rid == 'first': session.provenance_for = lambda bid: provenance
                with self.session_override(case, change), \
                     self.assertRaisesRegex(inputs.AnalysisInputError, '^operative_bound_not_the_window_bracket$'):
                    case.call()
                self.assertEqual(case.seen, [])

    def test_f2_own_bound_and_summary_do_not_read_stored_summary(self):
        with fx.floor_dispatch_case() as case:
            with mock.patch.object(inputs, 'BundleReader', return_value=SimpleNamespace(
                    raw_summary=mock.Mock(side_effect=AssertionError('stored summary read')),
                    raw_metadata=lambda: {}, raw_config=lambda: {})):
                case.call()
            self.assertEqual(case.seen, [42., 99.])

    def test_f2_pre_block5_root_keeps_stored_summary_behavior(self):
        with fx.floor_dispatch_case() as case, \
             mock.patch.object(inputs, 'is_hazard_runs_root', return_value=False), \
             mock.patch.object(inputs, 'load_calibration_ledger_snapshot', return_value=object()):
            inputs.bind_floor_artifact_evidence(case.artifact, case.floor, case.roots,
                strict_validator=lambda *_: [], _authenticated_floor=case.cap,
                calibration_ledger_snapshot=object())
            self.assertEqual(case.seen, [1., 1.])


class FloorWindowRefusalS5FixTests(unittest.TestCase):
    def test_tb_floor_row_refusal_stops_binding_before_members(self):
        with fx.floor_dispatch_case() as case, \
             mock.patch.object(inputs, 'whole_window_refusal_reasons',
                               return_value=('whole_window_neg8_verdict_failed',)), \
             self.assertRaisesRegex(inputs.AnalysisInputError,
                 '^whole_window_neg8_verdict_failed: whole_window_neg8_verdict_failed$'):
            case.call()
        case.readers.assert_not_called()


class SiblingWiringS5FixTests(unittest.TestCase):
    def test_te_e13_output_separation_requires_sibling_pinset(self):
        from joulewise import analysis_engine as engine
        loaded = fx.arithmetic_inputs([3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7])
        with fx.arithmetic_seams(loaded), \
             mock.patch.object(engine, 'is_hazard_runs_root', return_value=True), \
             mock.patch.object(engine, 'declared_evidence_roots', return_value={}) as declared, \
             mock.patch.object(engine, '_validate_output_separation'), \
             mock.patch.object(engine, 'write_claim_verdicts_atomic'):
            engine.analyze_claims(Path('manifest'), Path('runs'), Path('floor'),
                strict_validator=lambda *_: [], output_path=Path('output'))
        self.assertIs(declared.call_args.kwargs.get('require_sibling_pinset'), True)

    def test_te_e15_build_and_write_use_the_sibling_pinset(self):
        from joulewise import analysis_engine as engine
        loaded = fx.arithmetic_inputs([3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7])
        pinset = Path('synthetic-sibling-pinset.json')
        with fx.arithmetic_seams(loaded), \
             mock.patch.object(engine, 'declared_evidence_roots', return_value={}), \
             mock.patch.object(engine, '_validate_output_separation'), \
             mock.patch.object(engine, 'sibling_floor_pinset', return_value=pinset), \
             mock.patch.object(engine, 'finalize_claim_verdicts', side_effect=lambda body, **kw: body) as finalize, \
             mock.patch.object(engine, 'write_claim_verdicts_atomic') as write:
            engine.analyze_claims(Path('manifest'), Path('runs'), Path('floor'),
                strict_validator=lambda *_: [], output_path=Path('output'))
        self.assertEqual(finalize.call_args.kwargs.get('floor_pinset_path'), pinset)
        self.assertEqual(write.call_args.kwargs.get('floor_pinset_path'), pinset)

    def test_te_i19_loader_requires_sibling_pinset(self):
        with fx.loader_case() as case:
            loader = inputs.load_floor_artifact
            with mock.patch.object(inputs, 'load_floor_artifact', wraps=loader) as load:
                case.call()
            self.assertIs(load.call_args.kwargs.get('require_sibling_pinset'), True)

    def test_te_f18_finalization_passes_sibling_and_its_digest(self):
        import hashlib
        from joulewise import analysis_manifest_v3 as mv3
        from tests.b5_analysis.test_finalization_block5 import RoleAttachmentTests, FinalizationBlock5Tests
        with fx.finalization_case() as fixture, RoleAttachmentTests().seams(fixture):
            with mock.patch('joulewise.detection_floor.validate_floor_artifact', return_value=[]) as validate:
                mv3._authenticate_finalization_inputs(fixture['prospective'], **FinalizationBlock5Tests().args(fixture))
            self.assertEqual(validate.call_args.kwargs.get('pinset_path'), fixture['acceptance_path'])
            self.assertEqual(validate.call_args.kwargs.get('expected_pinset_sha256'),
                hashlib.sha256(fixture['acceptance_path'].read_bytes()).hexdigest())
