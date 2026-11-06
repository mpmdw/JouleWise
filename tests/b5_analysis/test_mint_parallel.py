"""Small synthetic MINT inputs: ordered refusals, transport and read replay."""
from contextlib import contextmanager
from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import analysis_run_cache as arc
from joulewise.authentication_io import V2AuthenticationReadSession, read_authentication_input
from joulewise.b5_analysis import mint_parallel as mp, pack_parallel as pp
from joulewise.b5_analysis.archive import ArchiveHandle
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from joulewise.cli import validate_bundle
from scripts import mint_floor_artifact_generalized as mint


_FRESH_CORE = mint._fresh_original_core


def evidence_core():
    core = _FRESH_CORE()
    core.load_calibration_acceptance_bound = lambda path: json.loads(
        read_authentication_input(path, grammar='json', label='synthetic acceptance'))
    return core


def configured_core(*args, **kwargs):
    core = evidence_core()

    def authenticate(paths, **kwargs):
        for path in (paths.report_path, paths.spec_path, paths.order_manifest_path, paths.spec_path):
            read_authentication_input(path, grammar='json', label='synthetic component')
        member = core.AuthenticatedMember(
            bundle_id='synthetic', bundle_sha256='b' * 64, config_sha256='c' * 64,
            metric_value_j=1.25, raw_config={}, metadata={}, summary={},
            admissible_half_width_j=0.125)
        values = {field.name: None for field in fields(core.AuthenticatedComponent)}
        values.update(kind=paths.expected_kind, cell={}, spec_cell={}, widths_j=(), members=(member,),
                      calibration_cell_id=paths.calibration_cell_id, spec_sha256='a' * 64)
        return core.AuthenticatedComponent(**values)

    core._authenticate_component = authenticate
    core._verify_report_widths = lambda *args: None
    return core


@contextmanager
def synthetic_authentication():
    # Keep producer control flow, archive authentication, plan/sidecar pins and
    # session behavior real; replace only expensive component/bracket science.
    with patch.object(mint, '_fresh_original_core', evidence_core), \
            patch.object(mint, '_configured_core', configured_core), \
            patch.object(mint, '_v2_mint_pinset', lambda *args: None), \
            patch.object(mint, '_pre_admit_legacy_report', mint._strict_json_file), \
            patch.object(mint, '_v2_authenticate_bracket_binding',
                         lambda **kwargs: ({'pre': 1}, {'post': 2}, {'allowance': '0.1'})):
        yield


def synthetic_worker(task):
    with synthetic_authentication():
        return pp.run_pack(task)


def failed_result_transport_worker(task):
    with synthetic_authentication(), patch.object(mp, '_portable_component',
                                                  side_effect=TypeError('synthetic result transport')):
        return pp.run_pack(task)


def fixture(root):
    from tests.b5_analysis.test_producer_parallel import entries

    registered = entries(root)
    producers, rows = [], []
    for pack, entry in registered.items():
        source = entry.window.archive_root / 'sources/inputs/acceptance.json'
        bracket = entry.window.archive_root / 'derived/bracket-binding.json'
        source.write_bytes(b'{}')
        bracket.write_bytes(b'{}')
        entry.producer_plan_id = pack
        entry.window.pack = pack
        entry.pack_path = root / (pack + '-pack')
        entry.pack_path.mkdir(exist_ok=True)
        entry.ledger_snapshot = {'valid': True, 'pack': pack}
        plan = entry.pack_path / 'calibration_plan.json'
        plan.write_text(json.dumps({'plan_id': pack}))
        digest = hashlib.sha256(plan.read_bytes()).hexdigest()
        sidecar = entry.pack_path / 'calibration_plan.sha256'
        sidecar.write_text(digest + '  ' + plan.name + '\n')
        paths = {'evidence_root': str(entry.window.claim_runs_root)}
        for field, name in (('report', 'report.json'), ('spec', 'extraction_spec.json'),
                            ('order_manifest', 'order_manifest.json')):
            path = entry.pack_path / name
            path.write_bytes(b'{}')
            paths[field] = str(path)
        cells, input_cells = [], []
        for role in ('decode', 'prefill'):
            pins = {'evidence_root_id': pack, 'calibration_cell_id': role,
                    'evaluation_basis_sha256': 'a' * 64, 'consumption_semantics_id': 'synthetic'}
            cells.append({'role': role, 'absolute': dict(pins), 'comparative': dict(pins)})
            input_cells.append({'role': role, 'absolute': dict(paths), 'comparative': dict(paths),
                                'allowed_consumer_condition_families': []})
        producers.append({'plan': {'plan_id': pack, 'sha256': digest, 'declared_sha256': digest,
                                   'sidecar_sha256': hashlib.sha256(sidecar.read_bytes()).hexdigest()},
                          'cells': cells})
        rows.append({'plan_id': pack, 'calibration_plan': str(plan),
                     'calibration_plan_sidecar': str(sidecar), 'bracket_binding': str(bracket),
                     'cells': input_cells})
    return SimpleNamespace(value={'producer_plans': producers}), rows, registered


class MintParallelTests(unittest.TestCase):
    def run_case(self, root, *, workers, failures=(), transport_failure=False,
                 result_transport_failure=False, validator=validate_bundle):
        pinset, rows, entries = fixture(root)
        for pack in failures:
            # Distinct later failures; alpha's must own both error and partial reads.
            path = entries[pack].pack_path / ('calibration_plan.sha256' if pack == 'alpha' else 'calibration_plan.json')
            path.write_bytes(b'{}')
        registry = {str(entry.window.claim_runs_root.resolve()): entry for entry in entries.values()}
        results, roots, outcomes = {}, {}, None
        with patch.dict(mint.BLOCK5_PRODUCERS, registry, clear=True), synthetic_authentication(), \
                patch.object(pp, 'run_pack', failed_result_transport_worker
                             if result_transport_failure else synthetic_worker), \
                patch.dict('os.environ', {pp.PACK_PARALLEL_ENV: 'on'}), \
                arc.analysis_run_caches({}, workers=workers) as caches, \
                V2AuthenticationReadSession() as session:
            caches.deadline = DeadlineObserver()
            common = dict(acceptance={}, acceptance_sha256='0' * 64, ledger_snapshot={},
                          pinset_path=root / 'pinset.json', pinset_sha256='0' * 64,
                          strict_validator=validator, consumption_semantics_id=None)
            calls = mp.authentication_calls(pinset, {row['plan_id']: row for row in rows}, block5=True, **common)
            if transport_failure:
                with patch.object(pp, 'dumps', side_effect=TypeError('synthetic transport failure')):
                    outcomes = pp.pack_map(mp.authenticate_producer, calls)
                self.assertIsNone(outcomes)
            elif calls is not None:
                outcomes = pp.pack_map(mp.authenticate_producer, calls)
            if workers > 1 and calls is not None and not transport_failure:
                self.assertIsNotNone(outcomes)
                self.assertEqual([o.ok for o in outcomes],
                                 [p not in failures and not result_transport_failure for p in entries])
                self.assertFalse(session.records)  # Compute-ahead admits nothing.
            error = None
            try:
                for i, (producer, row) in enumerate(zip(pinset.value['producer_plans'], rows)):
                    value, new_roots = mp.consume_authenticated(
                        None if outcomes is None else outcomes[i],
                        lambda: mint._authenticate_v2_producer(
                            producer, row, block5=True, evidence_roots=roots, **common))
                    results[row['plan_id']] = asdict(value)
                    roots.update(new_roots)
                    mint._allow_governed_extraction_spec(entries[row['plan_id']].pack_path / 'extraction_spec.json')
            except mint.MintError as exc:
                error = (type(exc), str(exc))
            return (results, roots, error, tuple(vars(r) for r in session.records.values()),
                    {pack: entry.archive.census() for pack, entry in entries.items()})

    def compare(self, **kwargs):
        with tempfile.TemporaryDirectory(prefix='mint-parallel-') as tmp:
            root = Path(tmp)
            serial = self.run_case(root, workers=1, **kwargs)
            parallel = self.run_case(root, workers=3, **kwargs)
            self.assertEqual(serial, parallel)
            return serial

    def test_success_matches_serial_inputs_roots_records_and_census(self):
        result = self.compare()
        self.assertEqual(list(result[0]), ['alpha', 'beta'])
        self.assertIsNone(result[2])

    def test_competing_failures_keep_first_refusal_and_partial_state(self):
        for failures in (('alpha', 'beta'), ('beta',)):
            with self.subTest(failures=failures):
                result = self.compare(failures=failures)
                self.assertIn("producer '" + failures[0] + "'", result[2][1])
                self.assertEqual(list(result[0]), [] if 'alpha' in failures else ['alpha'])

    def test_failed_transport_keeps_serial_path(self):
        result = self.compare(transport_failure=True)
        self.assertIsNone(result[2])

    def test_failed_result_transport_recomputes_at_serial_position(self):
        result = self.compare(result_transport_failure=True)
        self.assertIsNone(result[2])

    def test_caller_validator_seam_keeps_serial_path(self):
        self.compare(validator=lambda *args, **kwargs: [])

    def test_input_loop_schedules_only_with_a_fresh_session(self):
        with tempfile.TemporaryDirectory(prefix='mint-input-loop-') as tmp:
            root = Path(tmp)
            results = []
            for workers, earlier in ((1, False), (3, False), (3, True)):
                pinset, rows, entries = fixture(root)
                registry = {str(e.window.claim_runs_root.resolve()): e for e in entries.values()}
                acceptance = entries['alpha'].window.archive_root / 'sources/inputs/acceptance.json'
                manifest = {'producer_plans': rows, 'calibration_acceptance': str(acceptance),
                            'calibration_ledger': str(root / 'unused-ledger.jsonl'),
                            'calibration_ledger_head_pin': str(root / 'unused-head.json')}
                scheduled, pack_map = [], pp.pack_map

                def capture(function, calls):
                    outcomes = pack_map(function, calls)
                    scheduled.append(outcomes)
                    return outcomes

                with patch.dict(mint.BLOCK5_PRODUCERS, registry, clear=True), synthetic_authentication(), \
                        patch.object(mint, '_expand_block5_manifest', return_value=manifest), \
                        patch.object(pp, 'run_pack', synthetic_worker), \
                        patch.object(pp, 'pack_map', side_effect=capture), \
                        patch.dict('os.environ', {pp.PACK_PARALLEL_ENV: 'on'}), \
                        arc.analysis_run_caches({}, workers=workers) as caches, \
                        V2AuthenticationReadSession() as session:
                    caches.deadline = DeadlineObserver()
                    if earlier:
                        read_authentication_input(acceptance, grammar='json', label='caller earlier read')
                    inputs, roots, snapshots = mint._authenticate_v2_inputs(
                        pinset=pinset, pinset_path=root / 'pinset.json', pinset_sha256='0' * 64,
                        input_manifest_path=root / 'manifest.json',
                        input_manifest={'schema_version': mint.BLOCK5_INPUT_SCHEMA},
                        strict_validator=validate_bundle, consumption_semantics_id=None)
                    results.append(({k: asdict(v) for k, v in inputs.items()}, roots, snapshots,
                                    tuple(vars(r) for r in session.records.values()),
                                    {p: e.archive.census() for p, e in entries.items()}))
                if earlier:
                    self.assertFalse(scheduled)
                elif workers == 3:
                    self.assertTrue(all(o.ok for o in scheduled[0]))
            self.assertEqual(results[0], results[1])
            # The caller's extra acceptance read is the sole census difference.
            self.assertEqual(results[0][:3], results[2][:3])
            self.assertEqual(results[0][4], results[2][4])
            self.assertEqual(results[2][3][0]['read_count'], results[0][3][0]['read_count'] + 1)

    def test_shared_root_ids_disable_scheduling(self):
        with tempfile.TemporaryDirectory(prefix='mint-shared-root-') as tmp:
            root = Path(tmp)
            pinset, rows, entries = fixture(root)
            for cell in pinset.value['producer_plans'][1]['cells']:
                for name in ('absolute', 'comparative'):
                    cell[name]['evidence_root_id'] = 'alpha'
            registry = {str(e.window.claim_runs_root.resolve()): e for e in entries.values()}
            with patch.dict(mint.BLOCK5_PRODUCERS, registry, clear=True):
                calls = mp.authentication_calls(
                    pinset, {r['plan_id']: r for r in rows}, block5=True,
                    strict_validator=validate_bundle)
                self.assertIsNone(calls)


if __name__ == '__main__':
    unittest.main()
