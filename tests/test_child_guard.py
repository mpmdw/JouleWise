"""tests/child_guard.py: stopping a test's child processes, and failing a test that leaves one.

Every check here runs a small throwaway test class inside the test, with real
child processes (``/bin/sleep``, ``/bin/sh``, a Python one-liner), and then
asks the system whether those processes are still there. The pairs matter: for
each kind of leftover there is one throwaway test that leaves it (the guard
must report it, and must stop it) and one that cleans up (the guard must stay
silent).
"""

from __future__ import annotations

import io
import os
import signal
import subprocess
import sys
import textwrap
import threading
import time
import unittest
import warnings
from pathlib import Path

from tests import child_guard

REPO_ROOT = Path(__file__).resolve().parents[1]
LONG_S = "45"   # how long a deliberately left child would live if nothing stopped it


def setUpModule() -> None:   # noqa: N802 (unittest hook)
    # Every check below asks the system which processes exist. Some sandboxes deny ``ps``;
    # there the guard itself falls back to the children it recorded, and these tests cannot look.
    try:
        child_guard.table()
    except child_guard.ProcessTableUnavailable as problem:
        raise unittest.SkipTest(f"no process list in this environment: {problem}")


def running(pid: int) -> bool:
    """Whether the system lists ``pid`` as a process that has not exited."""

    return any(row.pid == pid and not row.zombie for row in child_guard.table())


def wait_not_running(pid: int, timeout_s: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while running(pid):
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)
    return True


def group_members(pgid: int) -> list[int]:
    return [row.pid for row in child_guard.table() if row.pgid == pgid and not row.zombie]


def run_class(case: type) -> unittest.TestResult:
    """Run one throwaway test class the way the suite runs a class (fixtures and cleanups included)."""

    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(case).run(result)
    return result


def problems(result: unittest.TestResult) -> list[str]:
    return [f"{test}: {text}" for test, text in result.failures + result.errors]


def leader_with_member() -> subprocess.Popen:
    """A shell that leads a new process group, starts one sleeper in it, prints the sleeper's pid, and waits."""

    return subprocess.Popen(["/bin/sh", "-c", f"/bin/sleep {LONG_S} & echo $!; wait"],
                            stdout=subprocess.PIPE, text=True, start_new_session=True)


@child_guard.fails_on_leftover_children
class StopTests(unittest.TestCase):
    def test_stop_terminates_a_running_child_and_collects_it(self):
        child = subprocess.Popen(["/bin/sleep", LONG_S])
        child_guard.stop(child)
        self.assertEqual(-signal.SIGTERM, child.returncode)
        self.assertFalse(running(child.pid))
        child_guard.stop(child)   # a second call finds nothing to do

    def test_stop_kills_a_child_that_ignores_sigterm(self):
        child = subprocess.Popen(
            [sys.executable, "-c",
             "import signal, sys, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
             f"print('ready', flush=True); time.sleep({LONG_S})"],
            stdout=subprocess.PIPE, text=True)
        self.addCleanup(child.stdout.close)
        self.addCleanup(child_guard.stop, child, grace_s=0.0)
        self.assertEqual("ready\n", child.stdout.readline())
        started = time.monotonic()
        child_guard.stop(child, grace_s=0.3)
        self.assertEqual(-signal.SIGKILL, child.returncode)
        self.assertGreaterEqual(time.monotonic() - started, 0.3)

    def test_stop_signals_the_whole_group_a_child_leads(self):
        leader = leader_with_member()
        self.addCleanup(leader.stdout.close)
        self.addCleanup(child_guard.stop, leader)
        member = int(leader.stdout.readline())
        self.assertTrue(running(member))
        child_guard.stop(leader)
        self.assertIsNotNone(leader.returncode)
        self.assertTrue(wait_not_running(member), "the sleeper in the stopped child's group is still running")

    def test_stop_clears_the_group_of_an_owned_child_that_already_exited(self):
        # The leader exits at once and is collected; its sleeper stays, with parent 1.
        leader = subprocess.Popen(["/bin/sh", "-c", f"/bin/sleep {LONG_S} & echo $!"],
                                  stdout=subprocess.PIPE, text=True, start_new_session=True)
        self.addCleanup(leader.stdout.close)
        child_guard.own(self, leader)
        member = int(leader.stdout.readline())
        self.assertEqual(0, leader.wait(timeout=10))
        self.assertTrue(running(member))
        child_guard.stop(leader)
        self.assertTrue(wait_not_running(member), "the orphaned sleeper is still running")

    def test_stop_with_tree_stops_the_processes_a_child_started_outside_any_group_of_its_own(self):
        parent = subprocess.Popen(
            ["/bin/sh", "-c", f"/bin/sleep {LONG_S} & echo $!; exec /bin/sleep {LONG_S}"],
            stdout=subprocess.PIPE, text=True)
        self.addCleanup(parent.stdout.close)
        child_guard.own(self, parent, tree=True)
        grandchild = int(parent.stdout.readline())
        self.addCleanup(lambda: running(grandchild) and os.kill(grandchild, signal.SIGKILL))
        self.assertTrue(running(grandchild))
        child_guard.stop(parent)
        self.assertTrue(wait_not_running(grandchild), "the child's own child is still running")

    def test_stop_leaves_other_processes_alone(self):
        bystander = subprocess.Popen(["/bin/sleep", LONG_S])
        self.addCleanup(child_guard.stop, bystander)
        child = subprocess.Popen(["/bin/sleep", LONG_S])
        child_guard.stop(child)
        self.assertIsNone(bystander.poll())

    def test_owned_block_stops_the_child_when_the_block_raises(self):
        with self.assertRaises(KeyboardInterrupt):
            with child_guard.owned(subprocess.Popen(["/bin/sleep", LONG_S])) as child:
                raise KeyboardInterrupt
        self.assertIsNotNone(child.returncode)
        self.assertFalse(running(child.pid))


@child_guard.fails_on_leftover_children
class OwnTests(unittest.TestCase):
    """own(): the child is stopped when the test passes, fails, or a wait times out."""

    def outcome(self, body):
        pids = []

        class Throwaway(unittest.TestCase):
            def test_it(inner):
                child = child_guard.own(inner, subprocess.Popen(["/bin/sleep", LONG_S]))
                pids.append(child.pid)
                body(inner, child)

        result = run_class(Throwaway)
        self.assertEqual(1, len(pids))
        self.assertFalse(running(pids[0]), "the owned child outlived its test")
        return result

    def test_child_is_stopped_after_a_passing_test(self):
        self.assertEqual([], problems(self.outcome(lambda inner, child: None)))

    def test_child_is_stopped_after_a_failing_test(self):
        result = self.outcome(lambda inner, child: inner.fail("deliberate"))
        self.assertEqual(1, len(result.failures))

    def test_child_is_stopped_after_a_wait_that_times_out(self):
        result = self.outcome(lambda inner, child: child.wait(timeout=0.1))
        self.assertEqual(1, len(result.errors))
        self.assertIn("TimeoutExpired", result.errors[0][1])

    def test_class_scope_child_is_stopped_with_the_class(self):
        pids = []

        class Throwaway(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                cls.server = child_guard.own(cls, subprocess.Popen(["/bin/sleep", LONG_S]))
                pids.append(cls.server.pid)

            def test_it(inner):
                inner.assertIsNone(inner.server.poll())

        self.assertEqual([], problems(run_class(child_guard.fails_on_leftover_children(Throwaway))))
        self.assertFalse(running(pids[0]))


@child_guard.fails_on_leftover_children
class GuardTests(unittest.TestCase):
    """The decorator: each kind of leftover is reported and stopped; each clean variant passes."""

    def guarded(self, body, **fixtures):
        namespace = {"test_it": body, **fixtures}
        return run_class(child_guard.fails_on_leftover_children(settle_s=0.5)(
            type("Throwaway", (unittest.TestCase,), namespace)))

    def test_a_child_left_running_fails_the_test_that_started_it(self):
        kept = []

        def body(inner):
            kept.append(subprocess.Popen(["/bin/sleep", LONG_S]))

        result = self.guarded(body)
        self.assertEqual(1, len(result.failures), problems(result))
        test, text = result.failures[0]
        self.assertIn("test_it", test.id())
        self.assertIn(f"pid {kept[0].pid} is still running", text)
        self.assertIn("/bin/sleep", text)
        self.assertFalse(running(kept[0].pid), "the guard reported the child but did not stop it")

    def test_a_child_left_running_is_found_after_the_test_dropped_its_popen_object(self):
        pids = []

        def body(inner):
            pids.append(subprocess.Popen(["/bin/sleep", LONG_S]).pid)   # the object is dropped here

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)   # Python's own "still running" note
            result = self.guarded(body)
        self.assertEqual(1, len(result.failures), problems(result))
        self.assertIn(f"pid {pids[0]} is still running", result.failures[0][1])
        self.assertFalse(running(pids[0]), "the guard reported the child but did not stop it")

    def test_the_same_child_stopped_in_a_cleanup_passes(self):
        def body(inner):
            child_guard.own(inner, subprocess.Popen(["/bin/sleep", LONG_S]))

        self.assertEqual([], problems(self.guarded(body)))

    def test_a_child_that_exited_without_being_collected_passes(self):
        def body(inner):
            child = subprocess.Popen(["/bin/sh", "-c", "exit 0"])
            inner.addCleanup(child.wait)
            deadline = time.monotonic() + 10
            while running(child.pid) and time.monotonic() < deadline:
                time.sleep(0.02)

        self.assertEqual([], problems(self.guarded(body)))

    def test_a_group_left_by_an_exited_leader_fails_the_test(self):
        members = []

        def body(inner):
            leader = subprocess.Popen(["/bin/sh", "-c", f"/bin/sleep {LONG_S} & echo $!"],
                                      stdout=subprocess.PIPE, text=True, start_new_session=True)
            inner.addCleanup(leader.stdout.close)
            members.append(int(leader.stdout.readline()))
            leader.wait(timeout=10)

        result = self.guarded(body)
        self.assertEqual(1, len(result.failures), problems(result))
        self.assertIn("the process group it led still has members", result.failures[0][1])
        self.assertTrue(wait_not_running(members[0]), "the guard reported the group but did not stop it")

    def test_a_child_left_running_is_stopped_with_the_processes_it_started(self):
        # The child is in this process's own group and has started a sleeper. Stopping only the
        # child would leave the sleeper running with parent 1, where nothing could find it.
        seen = {}

        def body(inner):
            parent = subprocess.Popen(
                ["/bin/sh", "-c", f"/bin/sleep {LONG_S} & echo $!; exec /bin/sleep {LONG_S}"],
                stdout=subprocess.PIPE, text=True)
            inner.addCleanup(parent.stdout.close)
            seen["grandchild"] = int(parent.stdout.readline())
            seen["parent"] = parent.pid
            seen["object"] = parent

        result = self.guarded(body)
        self.assertEqual(1, len(result.failures), problems(result))
        self.assertEqual([], result.errors, problems(result))
        self.assertIn(f"pid {seen['parent']} is still running", result.failures[0][1])
        self.assertTrue(wait_not_running(seen["parent"]), "the reported child is still running")
        self.assertTrue(wait_not_running(seen["grandchild"]), "the reported child's own child is still running")

    def test_a_forked_child_left_running_fails_the_class(self):
        pids = []

        def body(inner):
            pid = os.fork()
            if pid == 0:   # the child: nothing but a sleep, then a hard exit
                try:
                    time.sleep(float(LONG_S))
                finally:
                    os._exit(0)
            pids.append(pid)

        result = self.guarded(body)
        self.assertEqual(1, len(result.errors), problems(result))
        self.assertIn(f"pid {pids[0]} ", result.errors[0][1])
        self.assertFalse(running(pids[0]))

    def test_a_class_fixture_left_running_fails_the_class(self):
        pids = []

        def set_up_class(cls):
            pids.append(subprocess.Popen(["/bin/sleep", LONG_S]))

        result = self.guarded(lambda inner: None, setUpClass=classmethod(set_up_class))
        self.assertEqual(1, len(result.errors), problems(result))
        self.assertIn("The class fixtures of", result.errors[0][1])
        self.assertIn(f"pid {pids[0].pid} is still running", result.errors[0][1])
        self.assertFalse(running(pids[0].pid))

    def test_a_class_fixture_stopped_in_teardown_passes(self):
        def set_up_class(cls):
            cls.server = subprocess.Popen(["/bin/sleep", LONG_S])

        def tear_down_class(cls):
            child_guard.stop(cls.server)

        result = self.guarded(lambda inner: inner.assertIsNone(inner.server.poll()),
                              setUpClass=classmethod(set_up_class), tearDownClass=classmethod(tear_down_class))
        self.assertEqual([], problems(result))

    def test_a_child_that_existed_before_the_class_is_not_blamed_on_it(self):
        earlier = child_guard.own(self, subprocess.Popen(["/bin/sleep", LONG_S]))
        self.assertEqual([], problems(self.guarded(lambda inner: None)))
        self.assertIsNone(earlier.poll())

    def test_the_multiprocessing_resource_tracker_is_not_a_leftover(self):
        def body(inner):
            from multiprocessing import resource_tracker
            resource_tracker.ensure_running()
            inner.assertIn(resource_tracker._resource_tracker._pid, child_guard._standing_helpers())

        self.assertEqual([], problems(self.guarded(body)))

    def test_decorating_a_class_and_its_base_checks_each_test_once(self):
        kept = []
        open_recorders = len(child_guard._RECORDERS)

        class Base(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                super().setUpClass()

        class Throwaway(child_guard.fails_on_leftover_children(settle_s=0.2)(Base)):
            @classmethod
            def setUpClass(cls):
                super().setUpClass()
                cls.fixture = subprocess.Popen(["/bin/sleep", LONG_S])
                kept.append(cls.fixture)

            def test_it(inner):
                kept.append(subprocess.Popen(["/bin/sleep", LONG_S]))

        result = run_class(child_guard.fails_on_leftover_children(settle_s=0.2)(Throwaway))
        self.assertEqual(1, len(result.failures), problems(result))   # the test's child, reported once
        self.assertEqual(1, len(result.errors), problems(result))     # the class fixture, reported once
        self.assertEqual(1, result.failures[0][1].count("is still running"))
        self.assertEqual(1, result.errors[0][1].count("is still running"))
        self.assertEqual(open_recorders, len(child_guard._RECORDERS))
        self.assertFalse(any(running(child.pid) for child in kept))

    def test_guard_test_classes_decorates_the_classes_a_module_defines_and_no_others(self):
        kept = []

        class Local(unittest.TestCase):
            def test_it(inner):
                kept.append(subprocess.Popen(["/bin/sleep", LONG_S]))

        class Imported(unittest.TestCase):
            def test_it(inner):
                kept.append(child_guard.own(inner, subprocess.Popen(["/bin/sleep", LONG_S])))

        Imported.__module__ = "tests.some_other_module"
        namespace = {"__name__": Local.__module__, "Local": Local, "Imported": Imported, "helper": object()}
        self.assertEqual([Local], child_guard.guard_test_classes(namespace, settle_s=0.2))
        self.assertEqual(1, len(run_class(Local).failures))
        self.assertEqual([], problems(run_class(Imported)))
        self.assertFalse(any(running(child.pid) for child in kept))

    def test_short_probes_started_by_a_helper_thread_are_not_leftovers(self):
        # A thread that outlives the test and starts a 0.2 s process again and again: at every
        # look some process is running, but never the same one, so nothing was left behind.
        stop = threading.Event()

        def probe():
            while not stop.is_set():
                subprocess.Popen(["/bin/sleep", "0.2"]).wait()

        thread = threading.Thread(target=probe, daemon=True)
        try:
            result = self.guarded(lambda inner: thread.start())
        finally:
            stop.set()
            thread.join(timeout=10)
        self.assertEqual([], problems(result))

    def test_a_skipped_test_leaves_no_recorder_open(self):
        before = len(child_guard._RECORDERS)

        class Throwaway(unittest.TestCase):
            @unittest.skip("deliberate")
            def test_it(inner):
                raise AssertionError("not reached")

        result = run_class(child_guard.fails_on_leftover_children(Throwaway))
        self.assertEqual(1, len(result.skipped))
        self.assertEqual(before, len(child_guard._RECORDERS))


@child_guard.fails_on_leftover_children
class ExitSweepTests(unittest.TestCase):
    """An interrupted run (Ctrl-C) skips unittest's cleanups; the exit sweep stops the children anyway."""

    SCRIPT = textwrap.dedent("""
        import subprocess, sys, unittest
        {imports}

        class Interrupted(unittest.TestCase):
            def test_it(self):
                # The sleepers get /dev/null, so they do not hold this script's output pipes open.
                child = subprocess.Popen(["/bin/sleep", "{long_s}"], stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                self.addCleanup(child.kill)
                leader = subprocess.Popen(["/bin/sh", "-c", "/bin/sleep {long_s} >/dev/null 2>&1 & echo $!"],
                                          stdout=subprocess.PIPE, text=True, start_new_session=True)
                {own}
                member = int(leader.stdout.readline())
                leader.wait()
                print(child.pid, member, flush=True)
                raise KeyboardInterrupt

        unittest.main(argv=["interrupted"])
        """)

    def interrupted_run(self, *, with_guard: bool) -> tuple[int, int, int]:
        script = self.SCRIPT.format(
            imports="from tests import child_guard" if with_guard else "",
            own="child_guard.own(self, leader)" if with_guard else "pass", long_s=LONG_S)
        started = time.monotonic()
        run = subprocess.run([sys.executable, "-B", "-c", script], cwd=REPO_ROOT, capture_output=True,
                             text=True, timeout=120)
        self.assertLess(time.monotonic() - started, float(LONG_S) - 5, "the run waited for its sleepers")
        self.assertIn("KeyboardInterrupt", run.stderr)
        child, member = (int(field) for field in run.stdout.split())
        for pid in (child, member):
            self.addCleanup(lambda pid=pid: running(pid) and os.kill(pid, signal.SIGKILL))
        return run.returncode, child, member

    def test_without_the_module_an_interrupted_run_leaves_its_children(self):
        # The control: unittest ran no cleanup, so both sleepers outlive the interrupted run.
        _code, child, member = self.interrupted_run(with_guard=False)
        self.assertTrue(running(child))
        self.assertTrue(running(member))

    def test_with_the_module_an_interrupted_run_leaves_none(self):
        _code, child, member = self.interrupted_run(with_guard=True)
        self.assertTrue(wait_not_running(child), "the child of the interrupted run is still running")
        self.assertTrue(wait_not_running(member), "the owned child's orphaned group member is still running")

    def test_a_helper_process_that_only_imports_the_module_sweeps_nothing(self):
        # Tests start helper processes that import test modules, and with them this module. Such a
        # helper may leave a child on purpose for the test to deal with; its exit must not sweep.
        script = textwrap.dedent("""
            import subprocess, sys
            from tests import child_guard
            from tests import test_child_guard   # a guarded test module, imported but not run
            child = subprocess.Popen(["/bin/sleep", "{long_s}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(child.pid, flush=True)
            """).format(long_s=LONG_S)
        run = subprocess.run([sys.executable, "-B", "-c", script], cwd=REPO_ROOT, capture_output=True,
                             text=True, timeout=120)
        self.assertEqual(0, run.returncode, run.stderr)
        child = int(run.stdout)
        self.addCleanup(lambda: running(child) and os.kill(child, signal.SIGKILL))
        time.sleep(0.5)
        self.assertTrue(running(child), "the helper's exit stopped a child it had left running")

    TERMINATED = textwrap.dedent("""
        import subprocess, sys, time, unittest
        from tests import child_guard

        class Terminated(unittest.TestCase):
            def test_it(self):
                child = subprocess.Popen(["/bin/sleep", "{long_s}"], stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                self.addCleanup(child.kill)
                leader = subprocess.Popen(["/bin/sh", "-c", "/bin/sleep {long_s} >/dev/null 2>&1 & echo $!; wait"],
                                          stdout=subprocess.PIPE, text=True, start_new_session=True)
                member = int(leader.stdout.readline())
                print(child.pid, leader.pid, member, flush=True)
                time.sleep({long_s})

        {decorate}
        unittest.main(argv=["terminated"])
        """)

    def terminated_run(self, *, guarded: bool) -> tuple[int, list[int]]:
        script = self.TERMINATED.format(
            decorate="child_guard.guard_test_classes(globals())" if guarded else "", long_s=LONG_S)
        run = subprocess.Popen([sys.executable, "-B", "-c", script], cwd=REPO_ROOT, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True)
        child_guard.own(self, run)
        self.addCleanup(run.stdout.close)
        pids = [int(field) for field in run.stdout.readline().split()]
        self.assertEqual(3, len(pids), "the run did not report its children")
        for pid in pids:
            self.addCleanup(lambda pid=pid: running(pid) and os.kill(pid, signal.SIGKILL))
        run.send_signal(signal.SIGTERM)
        return run.wait(timeout=60), pids

    def test_without_the_guard_a_terminated_run_leaves_its_children(self):
        # The control: SIGTERM kills the run at once; the child, the group leader and its member stay.
        code, pids = self.terminated_run(guarded=False)
        self.assertEqual(-signal.SIGTERM, code)
        self.assertEqual([True, True, True], [running(pid) for pid in pids])

    def test_with_the_guard_a_terminated_run_stops_its_children_and_still_dies_of_the_signal(self):
        code, pids = self.terminated_run(guarded=True)
        self.assertEqual(-signal.SIGTERM, code)
        for pid, what in zip(pids, ("the child", "the group leader", "the group member")):
            self.assertTrue(wait_not_running(pid), f"{what} of the terminated run is still running")

    def test_a_forked_copy_of_a_guarded_run_keeps_the_default_action(self):
        script = textwrap.dedent("""
            import os, signal, sys, unittest
            from tests import child_guard

            class Forking(unittest.TestCase):
                def test_it(self):
                    self.assertIs(signal.getsignal(signal.SIGTERM), child_guard._sweep_then_die)
                    pid = os.fork()
                    if pid == 0:
                        os._exit(0 if signal.getsignal(signal.SIGTERM) is signal.SIG_DFL else 9)
                    self.assertEqual(0, os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1]))

            child_guard.guard_test_classes(globals())
            unittest.main(argv=["forking"])
            """)
        run = subprocess.run([sys.executable, "-B", "-c", script], cwd=REPO_ROOT, capture_output=True,
                             text=True, timeout=120)
        self.assertEqual(0, run.returncode, run.stderr)


if __name__ == "__main__":
    unittest.main()
