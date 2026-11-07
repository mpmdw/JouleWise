"""Independent sensitivity packs retain project/check/extract refusal order."""
from copy import deepcopy
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
    def calls(self, root, mode):
        calls = []
        for pack in ('alpha', 'beta'):
            cell = {'cell_id': pack + '-cell', 'mean_j': 3., 'lower_j': 1., 'upper_j': 5.,
                    'interval': {'h_j': .1, 'B_j': 2.}, 'attribution_floor': {'value_j': 2.},
                    'binding': dict(selection_sha256='a' * 64, prompt_pin_sha256='b' * 64,
                                    whole_window_basis_sha256='c' * 64)}
            projection = {'cells': [cell], 'refused_cells': []}
            spec = dict(reported_energy_cells=[{'cell_id': cell['cell_id']}],
                        pack=pack, mode=mode, projection=projection)
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


if __name__ == '__main__':
    unittest.main()
