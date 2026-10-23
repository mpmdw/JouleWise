"""Exercise the real opt-in boundaries without executing any live reader."""
from contextlib import ExitStack
import importlib
import inspect
import os
import unittest
from unittest import mock

from tests.live_hw import live_hw_only


class LiveHardwareOptInTests(unittest.TestCase):
    # This census of class-wide live probes includes SupervisorTests, guarded
    # on macOS only; the class guard test patches sys.platform to darwin for it.
    # The mixed classes and function-style G10 probe are exercised separately below.
    LIVE_CLASSES = (
        ("tests.hazards.test_smc", "LiveSmcTests"),
        ("tests.hazards.test_battery", "LiveReadOnlyTests"),
        ("tests.hazards.test_thermal", "LiveReadOnlyTests"),
        ("tests.hazards.test_clock", "LiveReadOnlyTests"),
        ("tests.hazards.test_monitor", "SupervisorTests"),
    )

    def environments(self):
        for opt_in in (None, "", "0", "true", "yes", "01", "1"):
            for synthetic in (None, "0", "1"):
                env = {}
                if opt_in is not None:
                    env["JW_LIVE_HW"] = opt_in
                if synthetic is not None:
                    env["JW_B5_SYNTHETIC_ONLY"] = synthetic
                yield env, opt_in == "1" and synthetic != "1"

    def test_class_guards_precede_setup_and_every_live_body(self):
        for module_name, class_name in self.LIVE_CLASSES:
            cls = getattr(importlib.import_module(module_name), class_name)
            names = unittest.defaultTestLoader.getTestCaseNames(cls)
            for env, enabled in self.environments():
                with self.subTest(cls=f"{module_name}.{class_name}", env=env), ExitStack() as stack:
                    stack.enter_context(mock.patch.dict(os.environ, env, clear=True))
                    stack.enter_context(mock.patch("sys.platform", "darwin"))
                    # Bypass only the existing OS prerequisite: the actual
                    # class setup must enforce opt-in even in Linux CI.
                    stack.enter_context(mock.patch.object(cls, "__unittest_skip__", False, create=True))
                    setup = stack.enter_context(mock.patch.object(cls, "setUp", return_value=None))
                    bodies = [stack.enter_context(mock.patch.object(cls, name, return_value=None))
                              for name in names]
                    result = unittest.TestResult()
                    unittest.defaultTestLoader.loadTestsFromTestCase(cls).run(result)
                    self.assertEqual(result.errors, [])
                    self.assertEqual(result.failures, [])
                    if enabled:
                        self.assertEqual(result.skipped, [])
                        self.assertEqual(setup.call_count, len(names))
                        for body in bodies:
                            body.assert_called_once_with()
                    else:
                        self.assertEqual(len(result.skipped), 1)  # class setup
                        self.assertIn("JW_B5_SYNTHETIC_ONLY=1" if env.get("JW_B5_SYNTHETIC_ONLY") == "1"
                                      else "JW_LIVE_HW=1", result.skipped[0][1])
                        setup.assert_not_called()
                        for body in bodies:
                            body.assert_not_called()

    def test_supervisor_tests_are_not_guarded_off_macos(self):
        from tests.hazards.test_monitor import SupervisorTests

        for env, enabled in self.environments():
            with self.subTest(env=env), mock.patch.dict(os.environ, env, clear=True):
                with mock.patch("sys.platform", "linux"):
                    try:
                        SupervisorTests.setUpClass()
                    except unittest.SkipTest as exc:
                        self.fail(f"SupervisorTests must not skip off macOS: {exc}")
                if not enabled:
                    with mock.patch("sys.platform", "darwin"), self.assertRaises(unittest.SkipTest):
                        SupervisorTests.setUpClass()

    def test_individual_guards_precede_the_first_live_operation(self):
        from tests.hazards import test_contention as c
        from tests import test_g10_clock_step_control as g10
        from tests import test_sample_quiet_predicate_evidence as sample

        g10_method = g10.G10ControlTests.test_real_readers_are_read_only_probes
        # The G10 unittest adapter closes over its original function.
        g10_function = inspect.getclosurevars(g10_method).nonlocals["function"]
        cases = (
            (c.HostAggregateTests.test_live_host_ticks_read_without_privileges,
             c.contention, "read_host_cpu"),
            (c.PsFormatTests.test_parse_equals_parse_ps_on_live_ps_output,
             c.base, "run_probe"),
            (c.PsFormatTests.test_live_snapshot_parses_and_this_process_is_in_the_tree,
             c.contention, "take_snapshot"),
            (g10_function, g10.g10, "real_read_frequency"),
            (sample.CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers,
             sample.subprocess, "run"),
        )

        class BodyReached(Exception):
            pass

        for function, owner, operation in cases:
            # On non-macOS, skipUnless adds an outer unconditional skip
            # wrapper. Remove only that wrapper, retaining our runtime guard.
            if getattr(function, "__unittest_skip__", False):
                function = function.__wrapped__
            for env, enabled in self.environments():
                with self.subTest(test=function.__qualname__, env=env), \
                        mock.patch.dict(os.environ, env, clear=True), \
                        mock.patch.object(owner, operation, side_effect=BodyReached) as boundary:
                    case = unittest.TestCase()
                    case.network_time_record = "unused-fixture"
                    args = () if function is g10_function else (case,)
                    with self.assertRaises(BodyReached if enabled else unittest.SkipTest):
                        function(*args)
                    self.assertEqual(boundary.call_count, int(enabled))

    def test_individual_guard_preserves_arguments_and_return_value(self):
        body = mock.Mock(return_value="fixture result")
        guarded = live_hw_only(body)
        with mock.patch.dict(os.environ, {"JW_LIVE_HW": "1"}, clear=True):
            self.assertEqual(guarded("fixture", flag=True), "fixture result")
        body.assert_called_once_with("fixture", flag=True)
