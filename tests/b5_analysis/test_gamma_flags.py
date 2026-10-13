"""S5 midpoint guards over S0's real pinned-harvest synthetic GAMMA bytes."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from joulewise.analysis_engine import inputs
from joulewise.b5_analysis.archive import ArchiveHandle
from joulewise import whole_window as ww
from tests.b5_analysis import fixtures_s5 as fx,fixtures_s3 as s3,fixtures_s3b as s3b

class GammaFlagsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.window=fx.pinned_window('GAMMA_MIDPOINT_LOST')
    def handle(self,counts_only=False):
        # A counterfactual authenticates exactly the changed output bytes.
        tmp=tempfile.TemporaryDirectory(prefix='s5-midpoint-');self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        harvest=json.loads((self.window.archive/'harvest.json').read_bytes())
        outputs={}
        for name in ('derived/exclusions.json','derived/flags.jsonl'):
            raw=(self.window.archive/name).read_bytes()
            if name.endswith('exclusions.json'):
                doc=json.loads(raw);doc['pack_id']='synthetic_non_gamma_pack'
                doc['claim_usable']=True;doc['reasons']=[]
                doc.setdefault('flag_counts',{}).setdefault('by_code',{})['neg8.midpoint_lost']=1 if counts_only else 0
                raw=json.dumps(doc).encode()
            elif counts_only:raw=b''
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
            import hashlib
            outputs[name]=hashlib.sha256(raw).hexdigest()
        harvest['outputs'].update(outputs)
        window=SimpleNamespace(archive_root=root,record=SimpleNamespace(record_shape='pin4'))
        return ArchiveHandle(window,harvest,{})
    def test_r7_authenticated_row_whatever_scope(self):
        archive=self.handle()
        with self.assertRaisesRegex(inputs.AnalysisInputError,'^analysed_attempt_carries_midpoint_lost$'):
            inputs.require_contrast_attempt_keeps_midpoint(archive)
    def test_r7_counts_without_row(self):
        with self.assertRaisesRegex(inputs.AnalysisInputError,'^analysed_attempt_carries_midpoint_lost$'):
            inputs.require_contrast_attempt_keeps_midpoint(self.handle(counts_only=True))
    def test_r7_loader_calls_guard_before_members(self):
        archive=self.handle()
        units=SimpleNamespace(window=SimpleNamespace(pack='gamma'))
        context=ww.ArchiveContext(archive.window.archive_root)
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
             mock.patch.object(inputs,'load_manifest',side_effect=AssertionError('member/manifest read')), \
             mock.patch.object(inputs,'_read_bundle',side_effect=AssertionError('member read')), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^analysed_attempt_carries_midpoint_lost$'):
            inputs.load_analysis_inputs(Path('unopened.json'),Path('runs'),Path('unopened-floor.json'),
                strict_validator=lambda *_:[],kept_units=units,
                archive_contexts={str(Path('runs').resolve()):context},gamma_archive=archive)

    def test_r4_loader_kept_units_required(self):
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^kept_quads_required$'):
            inputs.load_analysis_inputs(Path('unopened'),Path('runs'),Path('floor'),strict_validator=lambda *_:[])
    def test_context_required(self):
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=True), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^archive_context_required$'):
            inputs.load_analysis_inputs(Path('unopened'),Path('runs'),Path('floor'),strict_validator=lambda *_:[],
                kept_units=SimpleNamespace())
    def test_off_block5_refuses_arguments(self):
        with mock.patch.object(inputs,'is_hazard_runs_root',return_value=False), \
             self.assertRaisesRegex(inputs.AnalysisInputError,'^kept_units_not_a_block5_root$'):
            inputs.load_analysis_inputs(Path('unopened'),Path('runs'),Path('floor'),strict_validator=lambda *_:[],
                kept_units=SimpleNamespace())

class AlphaFlagTests(unittest.TestCase):
    def test_alpha_flag_kept_units_and_context_do_not_call_gamma_guard(self):
        # The real exclusion function applies ALPHA's rule to S0's pinned
        # ALPHA roster. Its small archive uses the named hand-built S3 context.
        from tests.b5_analysis import fixtures_s1 as s1
        from joulewise.flags.exclusions import compute
        from joulewise.b5_analysis.kept_units import load_kept_units
        snapshot=s1.cached()
        flag={'flag_id':'alpha-midpoint','code':'neg8.midpoint_lost','scope':{'level':'window',
            'plan_id':snapshot.roster['plan_id'],'attempt':snapshot.roster['attempt'],
            'run_id':None,'bundle_id':None,'stage_id':None},'interval':{'monotonic_ns':None}}
        snapshot.exclusions.clear();snapshot.exclusions.update(compute([flag],snapshot.roster,{},s1.CATALOG))
        case=s1.Case(snapshot);self.addCleanup(case.close)
        archive=case.handle();units=load_kept_units(archive,sealed_catalog_sha256=s1.PINS.sealed['catalog_sha256'],planned_units=case.planned)
        self.assertEqual(units.cell('df-b5t-family').n_b,10)
        context=ww.ArchiveContext(archive.window.archive_root,window_bracket={'status':'passed','b_fiducial_s':.02},
                                 governed_e3=False,removed_bundle_ids=units.removed_run_ids())
        self.assertIsInstance(context,ww.ArchiveContext)
        with fx.loader_case() as gamma,mock.patch.object(inputs,'require_contrast_attempt_keeps_midpoint',wraps=inputs.require_contrast_attempt_keeps_midpoint) as guard:
            gamma.call()
        guard.assert_called_once_with(gamma.archive)
