"""A173 fixture-only arm observations and unchanged plan-span counterfactuals."""

from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import arm_census, night_gate
from joulewise.night_plan_writer import night_plan_mapping
from joulewise.quiet_guard_process import (
    DarwinProcessRecord, KernelProcessRecord, KernelProcessTable, ProcessObservationError,
)
from tests.test_night_gate import FakeProbeSource, make_plan, result


def row(pid, ppid, executable, *args):
    return DarwinProcessRecord(pid, ppid, f"start-{pid}", executable, (executable, *args))


def observation(*rows, hits=(20,)):
    rows = (row(1, 0, "/sbin/launchd"), *rows)
    return arm_census.Observation(
        KernelProcessTable(tuple(KernelProcessRecord(r.pid, r.ppid, r.start_time) for r in rows)),
        rows, hits,
    )


def plan(receipt_class="REHEARSAL_STUB"):
    value = make_plan(receipt_class, plan_id="rehearsal-is-only-a-name")
    if receipt_class == "TRANSACTION_PACK":
        value = replace(value, pack_night={
            "pack_id": "pack", "pack_root": "/fixture/pack", "pack_sha256": "a" * 64,
            "attempt_ordinal": 1,
            "authorization_record": {"path": "/custody/auth.json", "sha256": "b" * 64},
            "confirmation_record": {"path": "/custody/confirm.json", "sha256": "c" * 64},
        })
    return night_gate.NightPlan.from_mapping(night_plan_mapping(value))


class FakeReader:
    def __init__(self, fixture, unreadable=()):
        self.fixture = fixture
        self.unreadable = unreadable
        self.reads = []
        self.inventory_calls = 0

    def inventory(self):
        self.inventory_calls += 1
        return self.fixture.inventory

    def read_exact(self, expected):
        self.reads.append(expected.pid)
        if expected.pid in self.unreadable:
            raise ProcessObservationError("fixture unreadable")
        return next(r for r in self.fixture.records if r.pid == expected.pid)


class ArmCensusTests(unittest.TestCase):
    def classify(self, fixture, receipt_class="REHEARSAL_STUB", caller_pid=90):
        return arm_census.classify_arm_census(plan(receipt_class), fixture, caller_pid=caller_pid)

    def test_idle_interactive_root_with_shell_and_unknown_helpers(self):
        fixture = observation(
            row(20, 1, "/usr/local/bin/claude"),
            row(30, 20, "/bin/zsh", "-c", "source /fake/snapshot; wait"),
            row(40, 30, "/bin/ugrep", "claude", "notes.txt"),
            row(50, 20, "/fake/codex-code-mode-host"),
            row(60, 20, "/usr/bin/python3", "-m", "unknown_future_runner"),
            hits=(20, 40, 50),
        )
        verdict = self.classify(fixture)
        self.assertFalse(verdict.publication_blocked)
        self.assertEqual((), verdict.foreign_pids)
        self.assertEqual((), verdict.workloads)
        self.assertEqual((30, 40, 50, 60), verdict.sessions[0].descendant_pids)
        self.assertTrue(verdict.sessions[0].exempt)

    def test_identical_idle_tree_is_exempt_only_for_stub(self):
        fixture = observation(row(20, 1, "/bin/claude"))
        for receipt_class, exempt, foreign in (
            ("REHEARSAL_STUB", True, ()),
            ("DIAGNOSTIC_NO_PACK", False, (20,)),
            ("TRANSACTION_PACK", False, (20,)),
        ):
            with self.subTest(receipt_class=receipt_class):
                verdict = self.classify(fixture, receipt_class)
                self.assertEqual(exempt, verdict.sessions[0].exempt)
                self.assertEqual(foreign, verdict.foreign_pids)
                self.assertFalse(verdict.publication_blocked)

    def test_only_ruled_root_shapes_receive_idle_exemption(self):
        for executable, args, permitted in (
            ("/bin/claude", (), True),
            ("/bin/claude", ("--resume", "session"), True),
            ("/bin/node", ("--require", "loader", "/opt/t3-code/dist/cli.js"), True),
            ("/bin/node", ("/opt/t3-code/dist/helper.js",), False),
            ("/bin/node", ("/x/t3-code-fork/y.js",), False),
            ("/bin/node", ("other.js", "/opt/t3-code/dist/cli.js"), False),
            ("/Applications/T3 Code.app/Contents/MacOS/T3 Code", (), False),
            ("/fake/claude/versions/2.1.3", (), False),
            ("/bin/notclaude", (), False),
            ("/bin/echo", ("claude",), False),
            ("/bin/claude", ("-p", "task"), False),
            ("/bin/claude", ("--print=json",), False),
            ("/bin/claude", ("daemon", "run"), False),
            ("/bin/claude", ("bg-spare",), False),
            ("/bin/claude", ("--bg-pty-host",), False),
            ("/bin/codex", ("mcp-server",), False),
        ):
            with self.subTest(executable=executable, args=args):
                verdict = self.classify(observation(row(20, 1, executable, *args)))
                self.assertEqual(not permitted, verdict.publication_blocked)
                self.assertEqual(() if permitted else (20,), verdict.foreign_pids)

    def test_each_workload_family_in_grandchild_blocks_whole_tree(self):
        # Literal cases independent of the production table: omission must bite.
        cases = (
            ("/bin/python3", ("-B", "-X", "dev", "-m", "unittest", "tests.test_x"), "unittest"),
            ("/bin/python3", ("-m", "unittest.main"), "unittest"),
            ("/bin/unittest", (), "unittest"),
            ("/bin/python3", ("-m", "pytest"), "pytest"),
            ("/bin/pytest", (), "pytest"),
            ("/bin/py.test", (), "pytest"),
            ("/bin/pytest-3.12", (), "pytest"),
            ("/bin/python3", ("-B", "scripts/shard_tests.py", "--worker"), "shard"),
            ("/usr/bin/powermetrics", ("--samplers", "cpu_power"), "telemetry"),
            ("/bin/nvidia-smi", (), "telemetry"),
            ("/bin/python3", ("scripts/run_night.py", "preflight"), "capture"),
            ("/bin/python3", ("/checkout/scripts/run_campaign.py",), "capture"),
            ("/bin/python3", ("scripts/capture_t0_step.py",), "capture"),
            ("/bin/zsh", ("/tmp/fixture/chain.zsh",), "capture"),
            ("/bin/python3", ("-m", "joulewise"), "joulewise"),
            ("/bin/python3", ("-m", "joulewise.adapters.node_worker"), "joulewise"),
            ("/tmp/mock/bin/vllm", ("serve", "/fake/model"), "model"),
            ("/bin/python3", ("/tmp/mock/bin/vllm", "serve", "/fake/model"), "model"),
            ("/bin/mlx", ("serve", "/fake/model"), "model"),
            ("/bin/python3", ("-m", "vllm.entrypoints.openai.api_server"), "model"),
            ("/bin/python3", ("-m", "mlx_lm.server"), "model"),
            ("/bin/codex", ("-m", "model", "exec", "task"), "codex_exec"),
            ("/bin/node", ("/opt/bin/codex", "exec", "-m", "model", "task"), "codex_exec"),
            ("/bin/claude", ("--model", "model", "-p", "task"), "claude_print"),
            ("/bin/claude", ("--print=json", "task"), "claude_print"),
        )
        for executable, args, category in cases:
            for root in (row(20, 1, "/bin/claude"), row(20, 1, "/bin/node", "/opt/t3-code/dist/cli.js")):
                with self.subTest(executable=executable, args=args, root=root.executable):
                    fixture = observation(root, row(30, 20, "/bin/zsh", "-c", "tool"),
                        row(40, 30, executable, *args), row(50, 20, "/bin/codex", "mcp-server"), hits=(20, 50))
                    verdict = self.classify(fixture)
                    self.assertTrue(verdict.publication_blocked)
                    self.assertEqual(((40, category),), verdict.workloads)
                    self.assertEqual((20, 50), verdict.foreign_pids)
                    self.assertFalse(verdict.sessions[0].exempt)

    def test_arguments_that_only_name_work_are_idle(self):
        for executable, args in (
            ("/bin/cat", ("scripts/run_night.py",)),
            ("/bin/python3", ("-c", "print('pytest')")),
            ("/bin/python3", ("-cprint('idle')", "/checkout/scripts/run_night.py")),
            ("/bin/zsh", ("-c", "sleep 1; pytest")),
            ("/bin/zsh", ("-lc", "cat /checkout/scripts/run_night.py")),
            ("/bin/codex", ("-m", "exec", "mcp-server")),
            ("/bin/node", ("helper.js", "codex", "exec")),
        ):
            with self.subTest(args=args):
                self.assertFalse(self.classify(observation(row(20, 1, "/bin/claude"),
                    row(30, 20, executable, *args))).publication_blocked)

    def test_magistrate_own_chain_exempt_but_not_foreign_or_side_work(self):
        rows = (row(20, 1, "/bin/claude", "-p", "magistrate"),
                row(30, 20, "/bin/zsh", "-c", "census"),
                row(90, 30, "/bin/python3", "-m", "joulewise.arm_census"))
        for receipt_class in ("REHEARSAL_STUB", "DIAGNOSTIC_NO_PACK", "TRANSACTION_PACK"):
            with self.subTest(receipt_class=receipt_class):
                verdict = self.classify(observation(*rows), receipt_class)
                self.assertEqual((20, 30, 90), verdict.own_pids)
                self.assertEqual((), verdict.foreign_pids)
                self.assertEqual((), verdict.workloads)
                self.assertFalse(verdict.publication_blocked)
        self.assertTrue(self.classify(observation(*rows), caller_pid=99).publication_blocked)
        side = self.classify(observation(*rows, row(40, 20, "/bin/python3", "-m", "unittest")))
        self.assertTrue(side.publication_blocked)
        self.assertEqual(((40, "unittest"),), side.workloads)

    def test_own_root_selection_without_ancestor_discovery_hits(self):
        for case, root, extra, hits, foreign, workloads in (
            ("helper_only", row(20, 1, "/bin/claude", "-p", "magistrate"),
             (), (50, 60), (), ()),
            ("workload", row(20, 1, "/bin/claude", "-p", "magistrate"),
             (row(71, 20, "/bin/python3", "-m", "unittest"),),
             (50, 60), (50, 60), ((71, "unittest"),)),
            ("sibling", row(20, 1, "/bin/claude", "-p", "magistrate"),
             (row(52207, 1, "/bin/codex", "exec", "task"),),
             (50, 60, 52207), (52207,), ()),
            ("bare_shell", row(20, 1, "/bin/zsh"),
             (), (50, 60), (50, 60), ()),
        ):
            with self.subTest(case=case):
                fixture = observation(
                    root,
                    row(30, 20, "/bin/zsh", "-c", "census"),
                    row(90, 30, "/bin/python3", "-m", "joulewise.arm_census"),
                    row(50, 20, "/bin/node", "/opt/bin/codex", "mcp-server"),
                    row(60, 50, "/fake/codex-code-mode-host"),
                    *extra, hits=hits,
                )
                reader = FakeReader(fixture)
                # Darwin pgrep excludes ancestors: PID 20 is never a hit.
                with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
                    arm_census.ARM_DISCOVERY_ARGV, 0, "".join(f"{pid}\n" for pid in hits), "")):
                    observed = arm_census.observe_arm_census(caller_pid=90, reader=reader)
                verdict = self.classify(observed)
                self.assertEqual(case != "helper_only", verdict.publication_blocked)
                self.assertEqual(foreign, verdict.foreign_pids)
                self.assertEqual((20, 30, 90), verdict.own_pids)
                self.assertEqual(workloads, verdict.workloads)
                self.assertEqual(hits, observed.hit_pids)
                self.assertEqual(sorted(r.pid for r in fixture.records if r.pid != 1),
                                 sorted(reader.reads))
                if case == "bare_shell":
                    self.assertEqual((), verdict.sessions)
                else:
                    self.assertEqual((20,), tuple(s.root_pid for s in verdict.sessions))
                    self.assertEqual(case != "workload", verdict.sessions[0].exempt)
                if case == "helper_only":
                    for receipt_class in ("DIAGNOSTIC_NO_PACK", "TRANSACTION_PACK"):
                        with self.subTest(receipt_class=receipt_class), tempfile.TemporaryDirectory() as tmp:
                            self.assertFalse(self.classify(observed, receipt_class).publication_blocked)
                            path = Path(tmp) / "plan.json"
                            path.write_text(json.dumps(night_plan_mapping(plan(receipt_class))))
                            with mock.patch.object(arm_census, "observe_arm_census", return_value=observed), \
                                 mock.patch.object(arm_census.os, "getpid", return_value=90), \
                                 redirect_stdout(io.StringIO()):
                                self.assertEqual(0, arm_census.main(["--plan", str(path)]))

    def test_outermost_exact_own_agent_root_is_selected(self):
        for root in (
            row(20, 1, "/bin/claude"),
            row(20, 1, "/bin/claude", "--print=json", "magistrate"),
            row(20, 1, "/bin/node", "/opt/t3-code/dist/cli.js"),
        ):
            with self.subTest(root=root):
                fixture = observation(
                    root,
                    row(25, 20, "/bin/claude", "-p", "nested"),
                    row(30, 25, "/bin/zsh", "-c", "census"),
                    row(90, 30, "/bin/python3", "-m", "joulewise.arm_census"),
                    row(50, 20, "/bin/node", "/opt/bin/codex", "mcp-server"),
                    row(60, 50, "/fake/codex-code-mode-host"),
                    row(71, 20, "/bin/unknown-helper"), hits=(50, 60),
                )
                reader = FakeReader(fixture)
                with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
                    arm_census.ARM_DISCOVERY_ARGV, 0, "50\n60\n", "")):
                    observed = arm_census.observe_arm_census(caller_pid=90, reader=reader)
                verdict = self.classify(observed)
                self.assertFalse(verdict.publication_blocked)
                self.assertEqual((), verdict.foreign_pids)
                self.assertEqual((), verdict.workloads)
                self.assertEqual((20,), tuple(s.root_pid for s in verdict.sessions))
                self.assertEqual((25, 30, 50, 60, 71, 90), verdict.sessions[0].descendant_pids)
                self.assertEqual([20, 25, 30, 50, 60, 71, 90], sorted(reader.reads))

    def test_unreadable_hit_outside_exempt_tree_is_idle(self):
        fixture = observation(row(20, 1, "/bin/codex", "exec", "task"))
        with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
            arm_census.ARM_DISCOVERY_ARGV, 0, "20\n", "")):
            observed = arm_census.observe_arm_census(caller_pid=90, reader=FakeReader(fixture, (20,)))
        verdict = self.classify(observed)
        self.assertEqual((20,), observed.hit_pids)
        self.assertEqual((), verdict.sessions)
        self.assertEqual((), verdict.foreign_pids)
        self.assertFalse(verdict.publication_blocked)
        self.assertIn("fixture unreadable", verdict.diagnostics[0])

    def test_discovery_timeout_is_bounded_and_diagnostic(self):
        def timeout_probe(argv, **kwargs):
            self.assertEqual(30, kwargs.get("timeout"))
            raise subprocess.TimeoutExpired(argv, 30, output="20\n")

        fixture = observation(row(20, 1, "/bin/codex", "exec", "task"))
        with mock.patch.object(arm_census.subprocess, "run", side_effect=timeout_probe):
            observed = arm_census.observe_arm_census(caller_pid=90, reader=FakeReader(fixture))
        self.assertEqual((), observed.hit_pids)
        self.assertFalse(self.classify(observed).publication_blocked)
        self.assertEqual(1, len(observed.diagnostics))
        self.assertIn("timed out after 30 seconds", observed.diagnostics[0])

    def test_discovery_exit_two_stdout_is_diagnostic_never_hits(self):
        fixture = observation(row(20, 1, "/bin/codex", "exec", "task"))
        with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
            arm_census.ARM_DISCOVERY_ARGV, 2, "20\n", "fixture error")):
            observed = arm_census.observe_arm_census(caller_pid=90, reader=FakeReader(fixture))
        self.assertEqual((), observed.hit_pids)
        self.assertFalse(self.classify(observed).publication_blocked)
        self.assertEqual(("discovery unknown: exit=2 stderr='fixture error'",), observed.diagnostics)

    def test_multiline_argv_cannot_inject_hit_and_unknown_rows_are_counted(self):
        fixture = observation(row(20, 1, "/bin/claude", "-p", "prompt"),
                              row(52207, 1, "/bin/unrelated"))
        multiline = "20 claude -p prompt\ncontinuation\n52207 injected text\nmore prompt\n"

        def discovery_probe(argv, **kwargs):
            # Model pgrep's two formats: only -l exposes multiline argv text.
            output = multiline if "-lf" in argv else "20\n"
            return subprocess.CompletedProcess(argv, 0, output, "")

        with mock.patch.object(arm_census.subprocess, "run", side_effect=discovery_probe):
            observed = arm_census.observe_arm_census(caller_pid=20, reader=FakeReader(fixture))
        self.assertEqual((20,), observed.hit_pids)
        self.assertEqual((), observed.diagnostics)
        self.assertFalse(self.classify(observed, caller_pid=20).publication_blocked)
        # Even malformed numeric-probe output cannot turn text into a hit.
        with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
            arm_census.ARM_DISCOVERY_ARGV, 0, "20\n" + multiline, "")):
            observed = arm_census.observe_arm_census(caller_pid=20, reader=FakeReader(fixture))
        self.assertEqual((20,), observed.hit_pids)
        self.assertEqual(("discovery unknown row: count=4",), observed.diagnostics)
        self.assertFalse(self.classify(observed, caller_pid=20).publication_blocked)

    def test_observation_uses_fake_inventory_and_exact_descendants_once(self):
        fixture = observation(row(20, 1, "/bin/claude"), row(30, 20, "/bin/zsh", "-c", "tool"),
            row(40, 30, "/bin/python3", "-m", "unittest"), row(60, 1, "/bin/unrelated"))
        reader = FakeReader(fixture)
        with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
            arm_census.ARM_DISCOVERY_ARGV, 0, "20\n", "")) as run:
            observed = arm_census.observe_arm_census(caller_pid=90, reader=reader)
        run.assert_called_once_with(("/usr/bin/pgrep", "-f", "[c]odex|[c]laude|[t]3"),
                                    capture_output=True, text=True, check=False, timeout=30)
        self.assertEqual(1, reader.inventory_calls)
        self.assertEqual([20, 30, 40], reader.reads)
        self.assertEqual(((40, "unittest"),), self.classify(observed).workloads)

    def test_unknown_observation_is_idle_with_diagnostics(self):
        fixture = observation(row(20, 1, "/bin/claude"), row(30, 20, "/bin/powermetrics"))
        reader = FakeReader(fixture, unreadable=(30,))
        with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
            arm_census.ARM_DISCOVERY_ARGV, 0, "20\n", "")):
            observed = arm_census.observe_arm_census(caller_pid=90, reader=reader)
        self.assertFalse(self.classify(observed).publication_blocked)
        self.assertIn("fixture unreadable", observed.diagnostics[0])
        with mock.patch.object(arm_census.subprocess, "run", side_effect=OSError("fixture discovery")), \
             mock.patch.object(reader, "inventory", side_effect=ProcessObservationError("fixture inventory")):
            observed = arm_census.observe_arm_census(caller_pid=90, reader=reader)
        self.assertFalse(self.classify(observed).publication_blocked)
        self.assertEqual(2, len(observed.diagnostics))

    def test_main_parses_plan_class_and_blocks_only_busy_stub(self):
        for receipt_class in ("REHEARSAL_STUB", "DIAGNOSTIC_NO_PACK", "TRANSACTION_PACK"):
            for busy in (False, True):
                with self.subTest(receipt_class=receipt_class, busy=busy), tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "rehearsal-stub.json"
                    raw = json.dumps(night_plan_mapping(plan(receipt_class))).encode()
                    path.write_bytes(raw)
                    fixture = observation(row(20, 1, "/bin/claude"),
                        row(30, 20, "/bin/powermetrics" if busy else "/bin/unknown"))
                    output = io.StringIO()
                    with mock.patch.object(arm_census, "observe_arm_census", return_value=fixture), \
                         mock.patch.object(arm_census.os, "getpid", return_value=90), \
                         mock.patch.object(Path, "mkdir", side_effect=AssertionError("arm wrote directory")), \
                         redirect_stdout(output):
                        code = arm_census.main(["--plan", str(path)])
                    self.assertEqual(3 if busy and receipt_class == "REHEARSAL_STUB" else 0, code)
                    record = json.loads(output.getvalue().splitlines()[0])
                    self.assertEqual(receipt_class, record["receipt_class"])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), record["plan_sha256"])
                    if receipt_class != "REHEARSAL_STUB":
                        self.assertIn("diagnostic only", output.getvalue())

    def test_unreadable_own_root_retains_known_side_work(self):
        for busy in (False, True):
            with self.subTest(busy=busy):
                fixture = observation(row(20, 1, "/bin/claude", "-p", "magistrate"),
                    row(90, 20, "/bin/python3", "-m", "joulewise.arm_census"),
                    row(30, 20, "/bin/powermetrics" if busy else "/bin/unknown"))
                with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
                    arm_census.ARM_DISCOVERY_ARGV, 0, "", "")):
                    # pgrep never lists the caller's own ancestors: no hits at all.
                    observed = arm_census.observe_arm_census(caller_pid=90, reader=FakeReader(fixture, (20,)))
                verdict = self.classify(observed)
                self.assertEqual(busy, verdict.publication_blocked)
                self.assertEqual((), verdict.foreign_pids)
                self.assertEqual(((30, "telemetry"),) if busy else (), verdict.workloads)
                self.assertIn("fixture unreadable", verdict.diagnostics[0])

    def test_unreadable_outer_own_hit_scans_work_and_exempts_idle_helpers(self):
        for busy in (False, True):
            with self.subTest(busy=busy):
                fixture = observation(
                    row(20, 1, "/bin/claude", "-p", "outer"),
                    row(25, 20, "/bin/claude", "-p", "inner"),
                    row(90, 25, "/bin/python3", "-m", "joulewise.arm_census"),
                    row(50, 20, "/bin/node", "/opt/bin/codex", "mcp-server"),
                    row(60, 50, "/fake/codex-code-mode-host"),
                    row(71, 20, "/bin/python3", "-m", "unittest") if busy else
                    row(71, 20, "/bin/unknown-helper"), hits=(50, 60),
                )
                reader = FakeReader(fixture, (20,))
                with mock.patch.object(arm_census.subprocess, "run", return_value=subprocess.CompletedProcess(
                    arm_census.ARM_DISCOVERY_ARGV, 0, "50\n60\n", "")):
                    observed = arm_census.observe_arm_census(caller_pid=90, reader=reader)
                verdict = self.classify(observed)
                self.assertEqual(busy, verdict.publication_blocked)
                self.assertEqual((50, 60) if busy else (), verdict.foreign_pids)
                self.assertEqual(((71, "unittest"),) if busy else (), verdict.workloads)
                self.assertEqual((20,), tuple(s.root_pid for s in verdict.sessions))
                self.assertEqual(not busy, verdict.sessions[0].exempt)
                self.assertEqual((25, 50, 60, 71, 90), verdict.sessions[0].descendant_pids)
                self.assertEqual([20, 25, 50, 60, 71, 90], sorted(reader.reads))
                self.assertIn("fixture unreadable", verdict.diagnostics[0])

    def test_invalid_plan_and_class_override_never_observe(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.json"
            invalid = night_plan_mapping(plan())
            invalid["receipt_class"] = "UNKNOWN"
            path.write_text(json.dumps(invalid))
            with mock.patch.object(arm_census, "observe_arm_census") as observe, redirect_stderr(io.StringIO()):
                self.assertEqual(2, arm_census.main(["--plan", str(path)]))
                with self.assertRaises(SystemExit) as caught:
                    arm_census.main(["--plan", str(path), "--class", "REHEARSAL_STUB"])
                self.assertEqual(2, caught.exception.code)
                observe.assert_not_called()

    def test_night_gate_and_driver_never_import_arm_census(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("joulewise/night_gate.py", "scripts/run_night.py"):
            with self.subTest(path=name):
                tree = ast.parse((root / name).read_text())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        imports = [alias.name for alias in node.names]
                        if isinstance(node, ast.ImportFrom):
                            imports.append(node.module or "")
                        self.assertFalse(any("arm_census" in item.split(".") for item in imports))
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        self.assertNotIn("arm_census", node.value)  # dynamic import too

    def test_stub_gate_records_agent_refusal_without_arm_filtering(self):
        stub = plan()
        self.assertFalse(self.classify(observation(row(20, 1, "/bin/claude"))).publication_blocked)
        source = FakeProbeSource(now_epoch_s=stub.t0_epoch_s)
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, stdout="20 claude\n")
        receipt = night_gate.evaluate_night(stub, source.probes())
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("night_refused_agent_present", receipt.refusal.reason)
        self.assertEqual("FAIL", next(c.status for c in receipt.conditions if c.condition_id == "C3"))
        self.assertEqual("20 claude\n", receipt.refusal.evidence[0].stdout)
        self.assertEqual(("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3"), receipt.refusal.evidence[0].argv)
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(night_gate.AGENT_CENSUS_ARGV, exit_code=1)
        with mock.patch.object(night_gate, "D166_REGISTRATION_SHA256",
                               hashlib.sha256(source.text[stub.registration_path].encode()).hexdigest()):
            self.assertEqual("REHEARSAL_ONLY", night_gate.evaluate_night(stub, source.probes()).verdict)


if __name__ == "__main__":
    unittest.main()
