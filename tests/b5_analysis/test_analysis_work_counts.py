"""Work counters for repeated analysis-run derivations (L9-SPEEDUP-R2 item 5).

A regression guard without timing: on a small synthetic run (committed S10
ALPHA members, one analysis run, the serial path so every call is counted in
this process) count the strict validations and re-reductions per bundle and
the calibration physics refits, and require upper bounds. The run repeats the
block-5 driver's patterns: the bracket selection is recomputed (step 3b, then
again by a later step), a floor extraction validates members of two cells
(one bundle in both), and the bracket's candidate discovery loads the same
calibration candidate once per pack. If a run-scoped cache stops being shared
(the run physics store, the candidate-physics memo) or a loop starts validating
or re-reducing a bundle more often, a bound fails.
"""
import collections
import contextlib
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_run_cache as arc, calibration_bracketing as calibration, cli
from joulewise import floor_extraction as fe, powermetrics_fiducial as pf, reduce as reducer, whole_window as ww
from joulewise.b5_analysis import bracket
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from tests.b5_analysis.test_parallel_steps import GOOD, REFUSED, RUNS, _SelectionArchive
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE

# Upper bounds for the run below (the counts at L9-SPEEDUP-R2).
# Two selections and two cells: GOOD[0] is in both cells. REFUSED's summary is unreadable,
# so neither the selection nor the extraction may strict-validate it.
MAX_STRICT_VALIDATIONS = {GOOD[0]: 4, GOOD[1]: 3, GOOD[2]: 3, REFUSED: 0}
MAX_REDUCTIONS_PER_STRICT_VALIDATION = 1
# One shared fit for the members' reductions, one for the candidate's physics.
MAX_PHYSICS_REFITS = 2


class AnalysisWorkCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='work-counts-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        names = (*GOOD, REFUSED)
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(cls.root, members=[m for m in blob.getmembers()
                                               if m.name.startswith(tuple(RUNS + n + '/' for n in names))],
                            filter='data')
        cls.runs = cls.root / RUNS

    def name_of(self, path):
        return next((part for part in Path(path).parts if part in (*GOOD, REFUSED)), str(path))

    def run_counted(self):
        validations, reductions, refits = collections.Counter(), collections.Counter(), []
        real_validate, real_reduce, real_refit = cli.validate_bundle, reducer.reduce_bundle, \
            pf.rederive_detection_from_artifacts

        def validate(path, strict=False, **kwargs):
            if strict:
                validations[self.name_of(path)] += 1
            return real_validate(path, strict=strict, **kwargs)

        def reduce(path, *args, **kwargs):
            reductions[self.name_of(path)] += 1
            return real_reduce(path, *args, **kwargs)

        def refit(*args, **kwargs):
            refits.append(1)
            return real_refit(*args, **kwargs)
        store = {}
        with contextlib.ExitStack() as stack:
            for target, name, replacement in ((cli, 'validate_bundle', validate), (cli, 'reduce_bundle', reduce),
                                              (reducer, 'reduce_bundle', reduce),
                                              (pf, 'rederive_detection_from_artifacts', refit)):
                stack.enter_context(mock.patch.object(target, name, replacement))
            stack.enter_context(ww.shared_instrument_calibration_physics_cache(store))
            caches = stack.enter_context(arc.analysis_run_caches(store, workers=1))
            caches.deadline = DeadlineObserver()
            # Step 3b and a later step: the bracket selection, twice.
            names = tuple(sorted((*GOOD, REFUSED)))
            for _ in range(2):
                archive = _SelectionArchive(self.runs, names, GOOD)
                with tempfile.TemporaryDirectory(prefix='sel-', dir=self.root) as directory:
                    selected = bracket._window_inputs(archive, archive, Path(directory))
                self.assertEqual(len(selected), len(GOOD))
            # Step 4: a floor extraction over two cells sharing one member.
            runs_root = self.root / 'extraction'
            if not runs_root.exists():
                for name in (*GOOD, REFUSED):
                    shutil.copytree(self.runs / name, runs_root / name)
                from tests.test_floor_extraction import install_synthetic_recovered_manifest
                install_synthetic_recovered_manifest(runs_root, [*GOOD, REFUSED])
            cell = lambda cell_id, members: {'cell_id': cell_id, 'kind': 'absolute', 'metric': 'gross_energy_j',
                                             'window_class': 'request',
                                             'members': [{'slot': m, 'bundle_id': m} for m in members]}
            spec = {'schema_version': fe.EXTRACTION_SPEC_SCHEMA_VERSION,
                    'cells': [cell('W-A', (GOOD[0], REFUSED)), cell('W-B', (GOOD[0], GOOD[1], GOOD[2]))]}
            from joulewise.whole_window import WholeWindowDriftAllowanceResult
            with mock.patch.object(fe, '_whole_window_extraction_refusals', lambda *a, **k: ()), \
                    mock.patch.object(fe, 'whole_window_drift_allowances',
                                      lambda *a, **k: WholeWindowDriftAllowanceResult('legacy', {})):
                fe.extract_cells(runs_root, spec)
            # Candidate discovery: the same calibration candidate, once per pack.
            candidates = [calibration._load_calibration_candidate_unbounded(
                self.runs / GOOD[2] / 'instrument_calibration', runs_root=self.runs) for _ in range(3)]
            self.assertTrue(all(c == candidates[0] and c is not None for c in candidates))
            self.assertEqual(caches.deadline.firings, 0)
        return validations, reductions, len(refits)

    def test_strict_validations_reductions_and_refits_stay_bounded(self):
        validations, reductions, refits = self.run_counted()
        for name, bound in MAX_STRICT_VALIDATIONS.items():
            with self.subTest(bundle=name):
                self.assertLessEqual(validations[name], bound, 'strict validations of one bundle')
                if bound:
                    self.assertGreater(validations[name], 0, 'the bundle was validated')
                self.assertLessEqual(reductions[name], MAX_REDUCTIONS_PER_STRICT_VALIDATION * validations[name],
                                     're-reductions of one bundle')
        self.assertLessEqual(refits, MAX_PHYSICS_REFITS, 'calibration physics refits in one run')


if __name__ == '__main__':
    unittest.main()
