"""P2-B1 row 1: a HAZARD_PACK whole-window verdict validates members in a process pool.

Every member still gets ``cli.validate_bundle(path, strict=True)``; only the
wall clock changes (serially an ALPHA window's 107 claim-root bundles take
about 3,700 s, past the harvest's 1,800 s budget).  The per-member result is
the serial result, in membership order; other roots keep the serial loop.
"""

from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import Future
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path
from unittest.mock import patch

from joulewise import cli, whole_window
from scripts import run_campaign


class ParallelStrictValidationTests(unittest.TestCase):
    """Row 1: strict validation of every member, in a process pool on HAZARD roots."""

    def test_pool_results_equal_the_serial_results_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for index in range(5):
                path = Path(tmp) / f"bundle-{index}"
                if index % 2:
                    path.mkdir()
                    (path / "metadata.json").write_text("{not json\n")
                paths.append(path)
            serial = [cli.validate_bundle(path, strict=True) for path in paths]
            # The pool is started by "spawn". Under the whole-suite runner every worker died
            # while re-importing the runner's main module (tests/runner_isolation.py, item
            # 1), the in-process fallback produced the same answers, and this test passed
            # without a pool. Hide the main module so the workers start, and count the
            # fallback's calls in this process so a pool that did no work fails the test.
            from tests import runner_isolation
            in_process = whole_window._strict_validation_problems
            with runner_isolation.hide_main_from_spawned_children(), \
                    patch.object(whole_window, "_strict_validation_problems", side_effect=in_process) as fallback:
                pooled = whole_window.strict_validate_bundles(paths, workers=3)
        self.assertEqual(pooled, serial)
        self.assertTrue(all(problems for problems in pooled))
        self.assertEqual(fallback.call_count, 0, "the pool did not validate these bundles; the fallback did")

    def test_a_validator_exception_is_recorded_as_the_serial_path_records_it(self) -> None:
        def boom(_path, strict):
            raise RuntimeError("broken bundle")

        self.assertEqual(whole_window.strict_validate_bundles([Path("x")], workers=4, validator=boom),
                         [["strict validation raised RuntimeError: broken bundle"]])

    def test_physics_cache_is_shared_only_with_a_validator_that_accepts_it(self) -> None:
        caches = []

        def with_cache(path, strict, physics_cache=None):
            caches.append(physics_cache)
            return []

        def without_cache(path, strict):
            return []

        whole_window.strict_validate_bundles([Path("a"), Path("b")], workers=1, validator=with_cache)
        self.assertIsInstance(caches[0], dict)
        self.assertIs(caches[0], caches[1])
        self.assertEqual(whole_window.strict_validate_bundles(
            [Path("a"), Path("b")], workers=1, validator=without_cache), [[], []])

    def _with_fake_pool(self, pool_factory):
        """Run the pool path with a fake executor and an in-process validator."""

        def validator(path, strict):
            return [f"invalid {Path(path).name}"]

        with patch.object(cli, "validate_bundle", side_effect=validator), \
                patch("concurrent.futures.ProcessPoolExecutor", side_effect=pool_factory):
            return whole_window.strict_validate_bundles(
                [Path("b0"), Path("b1"), Path("b2")], workers=3)

    def test_a_dead_worker_leaves_its_bundles_to_be_validated_in_process(self) -> None:
        # Review F4: a worker that dies must never turn its bundles into an
        # empty (valid) problem list.
        class DyingPool:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def submit(self, _fn, path_text):
                future = Future()
                if path_text == "b1":
                    future.set_result(["pooled b1"])
                else:
                    future.set_exception(BrokenProcessPool("worker exited"))
                return future

        self.assertEqual(self._with_fake_pool(DyingPool),
                         [["invalid b0"], ["pooled b1"], ["invalid b2"]])

    def test_a_pool_that_cannot_start_validates_every_bundle_in_process(self) -> None:
        def no_pool(*args, **kwargs):
            raise OSError("cannot spawn")

        self.assertEqual(self._with_fake_pool(no_pool),
                         [["invalid b0"], ["invalid b1"], ["invalid b2"]])

    def test_a_single_hazard_member_takes_the_serial_path(self) -> None:
        # Review F6: one member gains nothing from a pool.
        calls = []

        def member(source, waivers, *, strict_problems=None):
            calls.append(strict_problems)
            return source.path.name

        with patch.object(run_campaign, "_whole_window_member", side_effect=member), \
                patch.object(run_campaign._window_lineage, "is_hazard_runs_root", return_value=True), \
                patch.object(run_campaign, "strict_validate_bundles") as pooled:
            result = run_campaign._whole_window_member_evaluations(
                [run_campaign.WholeWindowMemberSource(path=Path("/r/one"))], {}, runs_dir=Path("/r"))
        self.assertEqual(result, ["one"])
        self.assertEqual(calls, [None])
        self.assertFalse(pooled.called)

    def test_worker_count(self) -> None:
        with patch.dict("os.environ", {whole_window.WHOLE_WINDOW_WORKERS_ENV: "3"}):
            self.assertEqual(whole_window.whole_window_strict_workers(107), 3)
            self.assertEqual(whole_window.whole_window_strict_workers(2), 2)
        with patch.dict("os.environ", {whole_window.WHOLE_WINDOW_WORKERS_ENV: "zero"}), \
                patch("os.cpu_count", return_value=16):
            self.assertEqual(whole_window.whole_window_strict_workers(107), 8)
        with patch("os.cpu_count", return_value=2), \
                patch.dict("os.environ", {}, clear=True):
            self.assertEqual(whole_window.whole_window_strict_workers(107), 1)

    def test_hazard_root_uses_the_parallel_path_and_other_roots_the_serial_loop(self) -> None:
        sources = [run_campaign.WholeWindowMemberSource(path=Path(f"/r/b{i}")) for i in range(3)] \
            if "path" in run_campaign.WholeWindowMemberSource.__dataclass_fields__ else None
        self.assertIsNotNone(sources)
        calls = []

        def member(source, waivers, *, strict_problems=None):
            calls.append((source.path.name, strict_problems))
            return source.path.name

        for hazard, expected in ((True, [("b0", ["p0"]), ("b1", ["p1"]), ("b2", ["p2"])]),
                                 (False, [("b0", None), ("b1", None), ("b2", None)])):
            with self.subTest(hazard=hazard):
                calls.clear()
                with patch.object(run_campaign, "_whole_window_member", side_effect=member), \
                        patch.object(run_campaign._window_lineage, "is_hazard_runs_root",
                                     return_value=hazard), \
                        patch.object(run_campaign, "strict_validate_bundles",
                                     return_value=[["p0"], ["p1"], ["p2"]]) as pooled:
                    result = run_campaign._whole_window_member_evaluations(
                        sources, {}, runs_dir=Path("/r"))
                self.assertEqual(result, ["b0", "b1", "b2"])
                self.assertEqual(calls, expected)
                self.assertEqual(pooled.called, hazard)


if __name__ == "__main__":
    unittest.main()
