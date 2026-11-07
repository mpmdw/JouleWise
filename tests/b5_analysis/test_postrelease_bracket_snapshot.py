"""L4 key projection and bypass arguments, using empty synthetic snapshots."""
import contextlib
from dataclasses import replace
import inspect
from pathlib import Path
import pickle
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc, analysis_verified_store as vdl
from joulewise import calibration_bracketing as calibration, calibration_ledger as ledger
from joulewise.b5_analysis import bracket as br


class BracketSnapshotTests(unittest.TestCase):
    def setUp(self):
        # These are scalar spellings only. No operation opens or stats them.
        self.snapshot = ledger.CalibrationLedgerSnapshot(
            'synthetic', Path('/synthetic-a/ledger.jsonl'), 1, 'a'*64, (), (), ())
        self.kwargs = dict(mode='issuing', ledger_snapshot=self.snapshot, bracket_binding={},
                           bracket_window_id='w', bracket_plan_id='p', bracket_plan_sha256='b'*64,
                           bracket_evidence_root_id='e', trigger_scope='sealed')

    def test_original_snapshot_reaches_absent_off_and_unregistered_fallbacks(self):
        for mode in (None, vdl.OFF, vdl.ON):
            with self.subTest(mode=mode):
                context = contextlib.nullcontext() if mode is None else arc.analysis_run_caches({}, vdl_mode=mode)
                with context, mock.patch.object(calibration, 'calibration_bracket_for_bundles') as fn:
                    br._calibration_assessment('/synthetic-runs', [], None, **self.kwargs)
                fn.assert_called_once_with('/synthetic-runs', [], None, **self.kwargs)
                self.assertIs(fn.call_args.kwargs['ledger_snapshot'], self.snapshot)

    def test_nonservable_and_unreadable_hits_keep_the_original_snapshot(self):
        for payload in (pickle.dumps(({'status': 'failed'}, ())), b'invalid pickle'):
            with self.subTest(payload=payload):
                store = mock.Mock()
                store.probe.return_value = SimpleNamespace(entry=SimpleNamespace(value=payload))
                with mock.patch.object(vdl, 'active_store', return_value=store), \
                        mock.patch.object(calibration, 'calibration_bracket_for_bundles') as fn:
                    br._calibration_assessment('/synthetic-runs', [], None, **self.kwargs)
                store.call.assert_not_called()
                self.assertIs(fn.call_args.kwargs['ledger_snapshot'], self.snapshot)
                self.assertIs(store.probe.call_args.kwargs['ledger_snapshot'], self.snapshot)

    def arguments(self, snapshot):
        signature = inspect.signature(calibration.calibration_bracket_for_bundles)
        bound = signature.bind('/synthetic-runs', [], None,
                               **{**self.kwargs, 'ledger_snapshot': snapshot})
        bound.apply_defaults()
        return dict(bound.arguments)

    def test_only_ledger_parent_is_removed_from_the_scalar_key(self):
        spec = next(spec for spec in vdl.LEAVES if spec.leaf_id == br.L4)
        arguments = self.arguments(self.snapshot)
        key = vdl._scalar_bytes(spec, arguments)
        relocated = replace(self.snapshot, ledger_path=Path('/synthetic-b/ledger.jsonl'))
        self.assertEqual(key, vdl._scalar_bytes(spec, self.arguments(relocated)))
        for changed in (replace(self.snapshot, head_digest='c'*64),
                        replace(self.snapshot, ledger_path=Path('/synthetic-a/other.jsonl')),
                        replace(self.snapshot, head_sequence=2)):
            self.assertNotEqual(key, vdl._scalar_bytes(spec, self.arguments(changed)))
        self.assertIs(arguments['ledger_snapshot'], self.snapshot)
        self.assertEqual(key, vdl.canonical_bytes(tuple(
            (name, replace(self.snapshot, ledger_path=Path('ledger.jsonl')) if name == 'ledger_snapshot'
             else arguments[name]) for name, role in spec.params if role == vdl.SCALAR)))

    def test_genuine_leaf_still_does_not_read_the_projected_field(self):
        self.assertNotIn('ledger_path', inspect.getsource(calibration))
        self.assertEqual(inspect.getsource(ledger.CalibrationLedgerSnapshot).count('ledger_path'), 1)

    def test_store_prepares_the_same_key_but_forwards_the_original_snapshot(self):
        fn = calibration.calibration_bracket_for_bundles
        with arc.analysis_run_caches({}, vdl_mode=vdl.ON) as caches:
            with mock.patch.object(caches.vdl, '_fill', return_value=('synthetic', ())) as fill:
                caches.vdl.call(br.L4, fn, '/synthetic-runs', [], None, **self.kwargs)
            prepared, _, _, forwarded = fill.call_args.args
            self.assertIs(prepared.arguments['ledger_snapshot'], self.snapshot)
            self.assertIs(forwarded['ledger_snapshot'], self.snapshot)
            spec = next(spec for spec in vdl.LEAVES if spec.leaf_id == br.L4)
            relocated = replace(self.snapshot, ledger_path=Path('/synthetic-b/ledger.jsonl'))
            again = caches.vdl._prepare(spec, fn, ('/synthetic-runs', [], None),
                                        {**self.kwargs, 'ledger_snapshot': relocated})
            self.assertEqual(prepared.key, again.key)
