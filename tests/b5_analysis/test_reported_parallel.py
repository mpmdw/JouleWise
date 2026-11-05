"""Step-10 staging, ordered publication and refusal identity on synthetic bytes."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise import analysis_run_cache as arc
from joulewise.b5_analysis import dry_run as d, pack_parallel as pp
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from joulewise.b5_analysis.steps import StepRecord
from joulewise.b5_analysis.windows import AnalysisRefusal
from scripts import issue_reported_energy as issuer


def issue_fixture(index, pack):
    mode = json.loads(Path(index).read_bytes())['mode']
    if mode == 'issuer_both':
        raise AnalysisRefusal('reported_energy_' + pack + '_refused')
    return dict(window={'harvest_pin': 'a' * 40}, exclusions_sha256='b' * 64,
                pack=pack, cells=[], refused_cells=[])


def open_fixture(state, pack):
    state.write('basis_' + pack, 'custody/' + pack + '-basis.json', {'pack': pack}, addressed=True)
    mode = state._synthetic_mode
    if mode == 'changed_input':
        state.output('extraction_' + pack).write_bytes(b'changed synthetic report')
    state.rehash()  # The production opener independently authenticates its inputs too.
    state.write('receipt_' + pack, 'custody/' + pack + '-receipt.json', {'receipt_pack': pack}, addressed=True)
    if mode == 'opener_both' or (mode == 'beta_opener' and pack == 'beta'):
        raise AnalysisRefusal('reported_energy_' + pack + '_opener_refused')
    return 0


def fixture_worker(task):
    with patch.object(issuer, 'issue_pack', issue_fixture), patch.object(d, '_reported_open', open_fixture):
        return pp.run_pack(task)


def failed_worker(task):
    return replace(fixture_worker(task), ok=False, value=None)


class ReportedParallelTests(unittest.TestCase):
    maxDiff = None
    def run_step(self, root, workers, mode, worker=fixture_worker):
        root.mkdir()
        index = root / 'index.json'
        index.write_text(json.dumps({'mode': mode}))
        artifacts = root / 'artifacts'
        artifacts.mkdir()
        state = d.RunState('blind-dry-run', index, artifacts, '0' * 40)
        state.workers = workers
        state._synthetic_mode = mode
        for pack in ('alpha', 'beta'):
            state.write('extraction_' + pack, 'mint/' + pack + '.json',
                        {'kept_units_binding': {'harvest_pin': 'a' * 40, 'exclusions_sha256': 'b' * 64}})
            state.step_records.append(StepRecord('4', pack, 'ok'))
        runner = d.StepRunner(artifacts)
        state._runner = runner
        with arc.analysis_run_caches({}, workers=workers) as caches, \
                patch.object(issuer, 'issue_pack', issue_fixture), \
                patch.object(d, '_reported_open', open_fixture), patch.object(pp, 'run_pack', worker):
            caches.deadline = DeadlineObserver()
            rows = d.step_10(state, runner)
        files = {p.relative_to(artifacts).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in artifacts.rglob('*') if p.is_file()}
        return ([r.as_dict() for r in rows], state.outputs, files, runner._counter,
                [code for _, code, _ in state._raw_codes])

    def test_every_published_byte_record_and_log_counter_matches_serial(self):
        with tempfile.TemporaryDirectory(prefix='reported-order-') as tmp:
            root = Path(tmp)
            for mode in ('ok', 'issuer_both', 'opener_both', 'beta_opener'):
                with self.subTest(mode=mode):
                    serial = self.run_step(root / (mode + '-serial'), 1, mode)
                    parallel = self.run_step(root / (mode + '-parallel'), 3, mode)
                    self.assertEqual(serial, parallel)
                    if mode != 'ok':
                        first = 'beta' if mode == 'beta_opener' else 'alpha'
                        self.assertEqual(serial[0][-1]['window'], first)
                        self.assertIn(first, serial[-1][-1])
                        if first == 'alpha':
                            self.assertFalse(any('beta' in name and not name.startswith('mint/')
                                                 for name in parallel[2]))

    def test_failed_staging_recomputes_at_original_serial_position(self):
        with tempfile.TemporaryDirectory(prefix='reported-fallback-') as tmp:
            root = Path(tmp)
            self.assertEqual(self.run_step(root / 'serial', 1, 'ok'),
                             self.run_step(root / 'parallel', 3, 'ok', worker=failed_worker))

    def test_opener_refuses_changed_report_bytes_in_its_own_staging(self):
        with tempfile.TemporaryDirectory(prefix='reported-reauth-') as tmp:
            for workers in (1, 3):
                rows, _, _, counter, codes = self.run_step(Path(tmp) / str(workers), workers, 'changed_input')
                self.assertEqual(codes, ['step_input_digest_mismatch'])
                self.assertEqual(rows[0]['window'], 'alpha')
                self.assertEqual(counter, 2)


if __name__ == '__main__':
    unittest.main()
