"""Independent sensitivity packs retain project/check/extract refusal order."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from joulewise import analysis_run_cache as arc
from joulewise.b5_analysis import pack_parallel as pp
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from joulewise.b5_analysis.sensitivity import SensitivityConsumers
from joulewise.b5_analysis.sensitivity_parallel import derive_pack
from joulewise.b5_analysis.windows import AnalysisRefusal


def project_fixture(spec, kept, **kwargs):
    pack, mode = spec['pack'], spec['mode']
    if mode == 'overlap':
        marker = Path(spec['barrier']) / pack
        marker.touch()
        sibling = Path(spec['barrier']) / ('beta' if pack == 'alpha' else 'alpha')
        import time
        deadline = time.monotonic() + 5
        while not sibling.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        if not sibling.exists():
            raise AnalysisRefusal('sensitivity_packs_did_not_overlap')
    if mode == 'project_both' or (mode == 'alpha_check_beta_project' and pack == 'beta'):
        raise AnalysisRefusal('sensitivity_' + pack + '_project_refused')
    value = deepcopy(spec['projection'])
    if mode == 'alpha_check_beta_project':
        value['cells'][0]['mean_j'] += 1
    return value


def extract_fixture(root, spec, **kwargs):
    if spec['mode'] == 'extract_both':
        raise AnalysisRefusal('sensitivity_' + spec['pack'] + '_extract_refused')
    return {'pack': spec['pack'], 'bound': kwargs['archive_context'].sensitivity_bound_s}


def strict_fixture(*args, **kwargs):
    return []


def unused_contrasts(**kwargs):
    raise AssertionError('pack derivations never run contrasts')


class SensitivityParallelTests(unittest.TestCase):
    def calls(self, root, mode, **spec_fields):
        calls = []
        for pack in ('alpha', 'beta'):
            cell = {'cell_id': pack + '-cell', 'mean_j': 3., 'lower_j': 1., 'upper_j': 5.,
                    'interval': {'h_j': .1, 'B_j': 2.}, 'attribution_floor': {'value_j': 2.},
                    'binding': dict(selection_sha256='a' * 64, prompt_pin_sha256='b' * 64,
                                    whole_window_basis_sha256='c' * 64)}
            projection = {'cells': [cell], 'refused_cells': []}
            spec = dict(reported_energy_cells=[{'cell_id': cell['cell_id']}],
                        pack=pack, mode=mode, projection=projection, **spec_fields)
            args = (pack, SimpleNamespace(claim_runs_root=root / pack), None,
                    SimpleNamespace(sources_replay=None, sensitivity_bound_s=.04), spec, projection,
                    {'manifest_id': 'synthetic'}, True, strict_fixture,
                    SensitivityConsumers(project_fixture, extract_fixture, unused_contrasts))
            calls.append((args, {}))
        return calls

    def test_pack_refusals_and_primary_equality_checks_precede_later_pack_errors(self):
        with tempfile.TemporaryDirectory(prefix='sensitivity-order-') as tmp:
            for mode in ('ok', 'project_both', 'extract_both', 'alpha_check_beta_project'):
                results = []
                for workers in (1, 3):
                    calls = self.calls(Path(tmp), mode)
                    with arc.analysis_run_caches({}, workers=workers) as caches:
                        caches.deadline = DeadlineObserver()
                        outcomes = pp.pack_map(derive_pack, calls)
                        if mode == 'ok' and workers == 3:
                            self.assertTrue(all(outcome.ok for outcome in outcomes))
                        values = []
                        try:
                            for (args, kwargs), outcome in zip(calls, outcomes or [None, None]):
                                values.append(pp.consume(outcome, lambda: derive_pack(*args, **kwargs)))
                        except AnalysisRefusal as exc:
                            results.append(('refused', exc.code, values))
                        else:
                            results.append(('ok', values))
                self.assertEqual(*results)
                if mode in ('project_both', 'extract_both'):
                    self.assertIn('alpha', results[0][1])
                elif mode == 'alpha_check_beta_project':
                    self.assertEqual(results[0][1], 'sensitivity_differs_at_primary_bound')

    def test_parallel_pack_results_are_byte_equal_at_both_step_11_bounds(self):
        """The equality gate and wider pass have identical serial/parallel pack bytes."""
        with tempfile.TemporaryDirectory(prefix='sensitivity-equality-') as tmp:
            root = Path(tmp)
            for bound in (.03, .05):
                encoded = []
                for workers in (1, 3):
                    calls = self.calls(root, 'ok')
                    # Model the two driver calls by changing only their fresh
                    # sensitivity contexts; all authenticated primary inputs remain shared.
                    calls = [((*(args[:3]), SimpleNamespace(
                        sources_replay=None, sensitivity_bound_s=bound), *args[4:]), kwargs)
                             for args, kwargs in calls]
                    with arc.analysis_run_caches({}, workers=workers) as caches:
                        caches.deadline = DeadlineObserver()
                        outcomes = pp.pack_map(derive_pack, calls)
                        values = [pp.consume(outcome, lambda a=args, k=kwargs: derive_pack(*a, **k))
                                  for (args, kwargs), outcome in zip(calls, outcomes or [None, None])]
                    encoded.append(json.dumps(values, sort_keys=True, separators=(',', ':'),
                                              ensure_ascii=False, allow_nan=False).encode())
                self.assertEqual(encoded[0], encoded[1], f'bound {bound} changed bytes')

    def test_alpha_and_beta_pack_kernels_really_overlap(self):
        """A two-party barrier can complete only when both isolated workers run."""
        with tempfile.TemporaryDirectory(prefix='sensitivity-overlap-') as tmp:
            root = Path(tmp)
            barrier = root / 'barrier'
            barrier.mkdir()
            calls = self.calls(root, 'overlap', barrier=str(barrier))
            with arc.analysis_run_caches({}, workers=3) as caches:
                caches.deadline = DeadlineObserver()
                outcomes = pp.pack_map(derive_pack, calls)
                self.assertIsNotNone(outcomes)
                self.assertTrue(all(outcome.ok for outcome in outcomes))
                values = [pp.consume(outcome, lambda a=args, k=kwargs: derive_pack(*a, **k))
                          for (args, kwargs), outcome in zip(calls, outcomes)]
            self.assertEqual([value[0][0]['pack'] for value in values], ['alpha', 'beta'])


if __name__ == '__main__':
    unittest.main()
