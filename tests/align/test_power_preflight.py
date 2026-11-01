"""Run preflight through real ctypes sampling and fake executables on PATH."""

from __future__ import annotations

import ctypes
import json
import math
import os
import random
import signal
import statistics
import subprocess
import time
import threading
import types
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.align.power import preflight
from joulewise.align.power.nvml import CtypesNvml, NvmlSampler
from joulewise.align.records import PowerTrace
from tests.align.test_power_nvml import FakeNvmlLibrary


class FakeExecutables:
    def __init__(self, directory: Path, *, lock_fails: bool = False,
                 virtualization: str = "None") -> None:
        self.directory = directory
        self.log = directory / "commands.jsonl"
        self.state = directory / "load-active"
        self.load = directory / "synthetic-load"
        smi = directory / "nvidia-smi"
        xml = (
            "<nvidia_smi_log><driver_version>550.54.15</driver_version><gpu>"
            "<product_name>NVIDIA A100-SXM4-40GB</product_name><uuid>GPU-synthetic</uuid>"
            "<mig_mode><current_mig>Disabled</current_mig></mig_mode>"
            "<gpu_virtualization_mode><virtualization_mode>" + virtualization +
            "</virtualization_mode></gpu_virtualization_mode></gpu></nvidia_smi_log>")
        smi.write_text(
            "#!" + sys.executable + "\n"
            "import json,sys\n"
            "from pathlib import Path\n"
            f"log=Path({str(self.log)!r})\n"
            "with log.open('a') as stream: stream.write(json.dumps(sys.argv[1:])+'\\n')\n"
            f"lock_fails={lock_fails!r}\n"
            f"xml={xml!r}\n"
            "if '-q' in sys.argv: print(xml)\n"
            "elif any(x.startswith('--query-gpu=') for x in sys.argv):\n"
            " print('2026/10/22 00:00:00.000, 50.0, 35')\n"
            "elif any(x.startswith('--query-supported-clocks=') for x in sys.argv):\n"
            " print('900\\n1200')\n"
            "elif '-lgc' in sys.argv and lock_fails:\n"
            " print('Insufficient Permissions',file=sys.stderr);sys.exit(4)\n",
            encoding="utf-8")
        self.load.write_text(
            "#!" + sys.executable + "\n"
            "import signal,sys,time\n"
            "from pathlib import Path\n"
            "state=Path(sys.argv[1])\n"
            "def stop(signum, frame): raise SystemExit(0)\n"
            "signal.signal(signal.SIGTERM,stop)\n"
            "state.write_text('loaded')\n"
            "try:\n"
            " while True: time.sleep(0.01)\n"
            "finally: state.unlink(missing_ok=True)\n", encoding="utf-8")
        smi.chmod(0o755)
        self.load.chmod(0o755)

    def commands(self) -> list[list[str]]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]


class PreflightTests(unittest.TestCase):
    def test_load_and_no_load_control_use_real_sampler_and_executables(self) -> None:
        for moves in (True, False):
            with self.subTest(moves=moves), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                executables = FakeExecutables(directory)
                class ClockedLibrary(FakeNvmlLibrary):
                    def __init__(self) -> None:
                        super().__init__(state_file=executables.state, moves=moves)
                        self.now = 10**15
                        self.wall_origin = 1_800_000_000_000_000_000
                        self.progress = threading.Condition()
                        self.active_reads = 0

                    def mono(self) -> int:
                        with self.progress:
                            self.now += 100  # Synthetic call cost, not a test tolerance.
                            return self.now

                    def wall(self) -> int:
                        with self.progress:
                            return self.wall_origin+self.now

                    def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                        status = super().nvmlDeviceGetPowerUsage(handle, output)
                        with self.progress:
                            self.now += 100_000_000  # One actual sensor update per poll.
                            self.active_reads += int(executables.state.exists())
                            self.progress.notify_all()
                        return status

                    def nvmlDeviceGetFieldValues(self, handle: object, count: int, values: object) -> int:
                        status = super().nvmlDeviceGetFieldValues(handle, count, values)
                        for index in range(count):
                            values[index].timestamp = (self.wall_origin+self.now)//1000
                        return status

                    def wait_readings(self, target: int, *, loaded: bool = False) -> None:
                        # Deadline only detects deadlock. Phase completion is
                        # driven by integer driver observations, never elapsed
                        # wall time or scheduler-dependent short sleeps.
                        with self.progress:
                            ready = self.progress.wait_for(
                                lambda: (self.active_reads if loaded else self.power_calls) >= target,
                                timeout=120)
                        if not ready:
                            raise AssertionError("fake driver did not finish the phase")

                library = ClockedLibrary()
                original_popen = subprocess.Popen

                def make_sampler(*args: object, **kwargs: object) -> NvmlSampler:
                    return NvmlSampler(*args, **kwargs, clock_ns=library.mono,
                                       wall_clock_ns=library.wall)

                def phase_sleep(seconds: float) -> None:
                    # Runbook: 10 s / 100 ms = 100 idle updates. Recovery is
                    # 2 s / 100 ms = 20 updates. Record clocks use this grid.
                    library.wait_readings(library.power_calls+round(seconds/.1))

                def popen(*args: object, **kwargs: object) -> subprocess.Popen:
                    process = original_popen(*args, **kwargs)
                    if args[0][0] == str(executables.load):
                        original_wait = process.wait
                        measured = False

                        def wait(timeout: float | None = None) -> int:
                            nonlocal measured
                            if not measured and timeout == 10.0:
                                measured = True
                                # One hundred active updates are the same
                                # ten-second load span as the runbook defaults.
                                library.wait_readings(100, loaded=True)
                                raise subprocess.TimeoutExpired(process.args, timeout)
                            return original_wait(timeout=timeout)
                        process.wait = wait
                    return process

                with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}), \
                        mock.patch.object(preflight, "NvmlSampler", side_effect=make_sampler), \
                        mock.patch.object(preflight.subprocess, "Popen", side_effect=popen), \
                        mock.patch.object(preflight, "time", types.SimpleNamespace(
                            monotonic=time.monotonic, monotonic_ns=library.mono, sleep=phase_sleep)):
                    report = preflight.run_preflight(
                        library=library, idle_seconds=10, load_seconds=10,
                        recovery_seconds=2, interval_ns=1_000_000,
                        load_cmd=[str(executables.load), str(executables.state)])
                self.assertFalse(report["refused"])
                self.assertEqual(report["movement"]["power_moved"], moves)
                self.assertEqual(report["measurement_ready"], moves)
                self.assertEqual(report["cuda_driver_version"], 12040)
                self.assertTrue(report["capabilities"])
                self.assertTrue(any(row["source"] == "nvml_energy" and row["supported"]
                                    for row in report["capabilities"]))
                self.assertTrue(all("-lgc" not in row and "-rgc" not in row
                                    for row in executables.commands()))
                self.assertFalse(executables.state.exists())
                device = report["devices"][0]
                self.assertEqual(device["nvidia_smi"]["snapshot_power_w"], [50.0])
                self.assertIn("parser_local_legacy_fallback",
                              device["nvidia_smi"]["snapshot_parse"]["timestamp_timezone_source"])
                # The fake-clock phases contain 100 updates each; the 200 W
                # effect is 1000x the 0.2 W ripple and survives clock uncertainty.
                channels = report["movement"]["channels"]
                measured = [row for row in channels if row["power_moved"] is not None]
                self.assertTrue(measured)
                for row in measured:
                    self.assertGreater(row["idle_samples"], 1)
                    if moves:
                        # Derive the detection bar from the reported idle
                        # criterion itself, not a second arbitrary watt cut.
                        self.assertGreater(row["load_peak_w"], row["threshold_w"])
                    else:
                        self.assertLessEqual(row["load_peak_w"], row["threshold_w"])
                json.dumps(report, allow_nan=False)
                print("NVML PREFLIGHT WORLD", json.dumps({
                    "moves": moves, "measurement_ready": report["measurement_ready"],
                    "channels": measured}))

    def test_vgpu_and_mig_slice_are_refused_before_load_or_clocks(self) -> None:
        for mode in ("vgpu", "mig"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                executables = FakeExecutables(directory)
                library = FakeNvmlLibrary()
                library.virtualization = 2 if mode == "vgpu" else 0
                library.mig_slice = int(mode == "mig")
                with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}):
                    report = preflight.run_preflight(
                        library=library, try_lock_clocks=True,
                        load_cmd=[str(executables.load), str(executables.state)])
                self.assertTrue(report["refused"])
                self.assertTrue(report["hazards"])
                self.assertEqual(library.power_calls, 0)
                self.assertTrue(all("-lgc" not in row for row in executables.commands()))

    def test_parent_mig_and_passthrough_are_recorded_not_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executables = FakeExecutables(directory, virtualization="Pass Through")
            library = FakeNvmlLibrary()
            library.mig_mode = (1, 1)
            library.virtualization = 1
            with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}), \
                    mock.patch.object(preflight.importlib.util, "find_spec", return_value=None):
                report = preflight.run_preflight(
                    library=library, idle_seconds=0, load_seconds=0, recovery_seconds=0)
            self.assertFalse(report["refused"])
            self.assertIn("mig_enabled_on_parent_verify_exclusive_ownership",
                          report["devices"][0]["flags"])
            self.assertIn("no_load_available", report["flags"])

    def test_clock_attempt_records_refusal_and_always_restores(self) -> None:
        for fails in (False, True):
            with self.subTest(fails=fails), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                executables = FakeExecutables(directory, lock_fails=fails)
                with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}), \
                        mock.patch.object(preflight.importlib.util, "find_spec", return_value=None):
                    report = preflight.run_preflight(
                        library=FakeNvmlLibrary(), try_lock_clocks=True,
                        idle_seconds=0, load_seconds=0, recovery_seconds=0)
                commands = executables.commands()
                self.assertIn(["-i", "0", "-lgc", "1200,1200"], commands)
                self.assertEqual(commands[-1], ["-i", "0", "-rgc"])
                self.assertFalse(report["refused"])
                self.assertEqual("gpu0_clock_lock_failed" in report["flags"], fails)
                if fails:
                    self.assertTrue(any("Insufficient Permissions" in row["stderr"]
                                        for row in report["clock_commands"]))

    def test_failing_load_command_still_restores_clocks_and_sampler(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executables = FakeExecutables(directory)
            library = FakeNvmlLibrary()
            with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}):
                report = preflight.run_preflight(
                    library=library, try_lock_clocks=True, graphics_clock_mhz=900,
                    idle_seconds=0, recovery_seconds=0,
                    load_cmd=[str(directory / "missing-load")])
            self.assertFalse(report["refused"])
            self.assertTrue(any("preflight_incomplete" in flag for flag in report["flags"]))
            self.assertEqual(executables.commands()[-1], ["-i", "0", "-rgc"])
            self.assertEqual(library.shutdown_calls, 2)  # Preflight and sampler own one init each.

    def test_sigterm_unwinds_clock_lock_from_the_real_cli_main(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executables = FakeExecutables(directory)
            backend = CtypesNvml(FakeNvmlLibrary())
            previous_handler = signal.getsignal(signal.SIGTERM)
            with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}), \
                    mock.patch.object(preflight, "open_nvml", return_value=backend), \
                    mock.patch.object(preflight, "time", types.SimpleNamespace(
                        monotonic=time.monotonic, monotonic_ns=time.monotonic_ns,
                        sleep=lambda _: signal.raise_signal(signal.SIGTERM))):
                with self.assertRaises(SystemExit):
                    preflight.main(["--out", str(directory / "interrupted.json"),
                                    "--try-lock-clocks"])
            self.assertEqual(executables.commands()[-1], ["-i", "0", "-rgc"])
            self.assertIs(signal.getsignal(signal.SIGTERM), previous_handler)

    def test_cli_writes_json_and_missing_capabilities_are_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executables = FakeExecutables(directory)
            library = FakeNvmlLibrary()
            library.energy_supported = False
            library.unsupported_fields = {185}
            target = directory / "report.json"
            with mock.patch.dict(os.environ, {"PATH": str(directory) + os.pathsep + os.defpath}), \
                    mock.patch.object(preflight, "open_nvml", return_value=CtypesNvml(library)), \
                    mock.patch.object(preflight.importlib.util, "find_spec", return_value=None):
                code = preflight.main([
                    "--out", str(target), "--idle-seconds", "0",
                    "--load-seconds", "0", "--recovery-seconds", "0"])
            self.assertEqual(code, 0)
            report = json.loads(target.read_text())
            self.assertFalse(report["refused"])
            self.assertFalse(report["measurement_ready"])
            self.assertIn("no_load_available", report["flags"])
            self.assertTrue(any(not row["supported"] for row in report["capabilities"]))

    def test_missing_library_is_a_recorded_outcome(self) -> None:
        with mock.patch.object(preflight, "open_nvml", side_effect=OSError("driver absent")):
            report = preflight.run_preflight()
        self.assertFalse(report["refused"])
        self.assertFalse(report["measurement_ready"])
        self.assertTrue(any("driver absent" in flag for flag in report["flags"]))

    def test_unknown_virtualization_text_is_a_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executables = FakeExecutables(directory, virtualization="Unknown future mode")
            with mock.patch.dict(os.environ, {"PATH": str(directory)+os.pathsep+os.defpath}), \
                    mock.patch.object(preflight.importlib.util, "find_spec", return_value=None):
                report = preflight.run_preflight(
                    library=FakeNvmlLibrary(), idle_seconds=0, load_seconds=0, recovery_seconds=0)
            self.assertFalse(report["refused"])
            self.assertIn("virtualization_evidence_unknown", report["devices"][0]["flags"])

    def test_default_torch_load_runs_in_a_killable_owned_process(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            executables = FakeExecutables(directory)
            # This tiny CUDA-shaped module exercises the actual child load
            # command without importing torch or touching hardware.
            (directory/"torch.py").write_text(
                "from contextlib import nullcontext\n"
                "from pathlib import Path\n"
                "import time\n"
                "class CUDA:\n"
                " def is_available(self): return True\n"
                " def device(self,index): return nullcontext()\n"
                " def synchronize(self): pass\n"
                "cuda=CUDA()\n"
                "def randn(*args,**kwargs): return object()\n"
                "def no_grad(): return nullcontext()\n"
                f"def mm(a,b): Path({str(executables.state)!r}).touch(); time.sleep(0.005)\n",
                encoding="utf-8")
            env = {"PATH": str(directory)+os.pathsep+os.defpath, "PYTHONPATH": str(directory)}
            with mock.patch.dict(os.environ, env), \
                    mock.patch.object(preflight.importlib.util, "find_spec", return_value=object()):
                report = preflight.run_preflight(
                    library=FakeNvmlLibrary(state_file=executables.state),
                    idle_seconds=0.45, load_seconds=0.25, recovery_seconds=0,
                    interval_ns=5_000_000)
            self.assertTrue(report["load"]["available"], report["load"])
            self.assertEqual(report["load"]["kind"], "torch_cuda_matmul")
            self.assertTrue(report["measurement_ready"], report.get("movement"))
            self.assertIn("cleanup", report["load"])

    @unittest.skipUnless(os.name == "posix" and Path("/proc").is_dir(),
                         "owned-process-group orphan regression uses Linux subreaper support")
    def test_owned_group_cleanup_reaps_a_term_resistant_child_after_leader_exit(self) -> None:
        # Linux prctl.h: PR_SET_CHILD_SUBREAPER=36, PR_GET_CHILD_SUBREAPER=37.
        # Temporarily adopt this test's orphan so the regression itself leaves
        # neither active work nor a zombie waiting on a container's PID 1.
        libc = ctypes.CDLL(None)
        old = ctypes.c_int()
        self.assertEqual(libc.prctl(37, ctypes.byref(old), 0, 0, 0), 0)
        self.assertEqual(libc.prctl(36, 1, 0, 0, 0), 0)
        process = None
        child_pid = None
        try:
            with tempfile.TemporaryDirectory() as temp:
                ready = Path(temp)/"child-ready"
                child = (
                    "import os,signal,time;from pathlib import Path;"
                    "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                    f"p=Path({str(ready)!r});pending=p.with_suffix('.pending');"
                    "pending.write_text(str(os.getpid()));os.replace(pending,p);"
                    "time.sleep(60)")
                leader = (
                    "import subprocess,sys,time;from pathlib import Path;"
                    f"subprocess.Popen([sys.executable,'-c',{child!r}]);"
                    f"ready=Path({str(ready)!r});"
                    "exec('while not ready.exists(): time.sleep(0.001)')")
                process = subprocess.Popen([sys.executable, "-c", leader], start_new_session=True)
                process.wait(timeout=2)
                child_pid = int(ready.read_text())
                receipt = preflight._terminate_load(process, timeout_s=0.05)
                self.assertTrue(receipt["kill_escalated"])
                waited, status = os.waitpid(child_pid, 0)
                self.assertEqual(waited, child_pid)
                self.assertTrue(os.WIFSIGNALED(status))
                self.assertEqual(os.WTERMSIG(status), signal.SIGKILL)
                child_pid = None
        finally:
            if process is not None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=2)
                # Reap every adopted member of this owned group even if the
                # PID receipt was never parsed; unrelated children are excluded.
                while True:
                    try:
                        os.waitpid(-process.pid, 0)
                    except ChildProcessError:
                        break
            libc.prctl(36, old.value, 0, 0, 0)

    @unittest.skipUnless(os.name == "posix", "process-group probe requires POSIX")
    def test_permission_denied_presence_probe_keeps_cleanup_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            FakeExecutables(directory)
            original_killpg = os.killpg
            denied = False

            def killpg(group: int, sig: int) -> None:
                nonlocal denied
                if sig == 0 and not denied:
                    denied = True
                    # run_preflight has already waited/reaped the short-lived
                    # leader; emulate Darwin's zombie-only EPERM once.
                    raise PermissionError("synthetic zombie-group EPERM")
                original_killpg(group, sig)

            with mock.patch.dict(os.environ, {"PATH": str(directory)+os.pathsep+os.defpath}), \
                    mock.patch.object(preflight.os, "killpg", side_effect=killpg):
                report = preflight.run_preflight(
                    library=FakeNvmlLibrary(), idle_seconds=0, load_seconds=1,
                    recovery_seconds=0, load_cmd=[sys.executable, "-c", "pass"])
            self.assertTrue(denied)
            self.assertIn("cleanup", report["load"])
            self.assertTrue(report["load"]["cleanup"]["presence_permission_denied"])
            self.assertEqual(report["load"]["returncode"], 0)
            self.assertFalse(any(flag.startswith(("preflight_incomplete", "load_cleanup_failed"))
                                 for flag in report["flags"]), report["flags"])

    def test_failed_sampler_cleanup_owner_never_shuts_down_under_native_call(self) -> None:
        for fail_outer in (False, True):
            with self.subTest(fail_outer=fail_outer), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                FakeExecutables(directory)

                class BlockingLibrary(FakeNvmlLibrary):
                    def __init__(self) -> None:
                        super().__init__()
                        self.entered, self.release = threading.Event(), threading.Event()

                    def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                        if self.power_calls:
                            self.entered.set()
                            self.release.wait()
                        return super().nvmlDeviceGetPowerUsage(handle, output)

                library = BlockingLibrary()
                binding = CtypesNvml(library)
                samplers = []
                owners = []
                original_start = threading.Thread.start

                def make_sampler(*args: object, **kwargs: object) -> NvmlSampler:
                    sampler = NvmlSampler(*args, **kwargs, stop_timeout_s=0)
                    samplers.append(sampler)
                    return sampler

                def start(thread: threading.Thread) -> None:
                    if thread.name == "joulewise-nvml-cleanup" or (
                            fail_outer and thread.name == "joulewise-preflight-nvml-cleanup"):
                        raise RuntimeError("synthetic cleanup owner creation failure")
                    if thread.name == "joulewise-preflight-nvml-cleanup":
                        owners.append(thread)
                    original_start(thread)

                def idle_sleep(_: float) -> None:
                    self.assertTrue(library.entered.wait(timeout=2))

                try:
                    with mock.patch.dict(os.environ, {
                            "PATH": str(directory)+os.pathsep+os.defpath}), \
                            mock.patch.object(preflight.importlib.util, "find_spec", return_value=None), \
                            mock.patch.object(preflight, "NvmlSampler", side_effect=make_sampler), \
                            mock.patch.object(threading.Thread, "start", new=start), \
                            mock.patch.object(preflight, "time", types.SimpleNamespace(
                                monotonic=time.monotonic, monotonic_ns=time.monotonic_ns,
                                sleep=idle_sleep)):
                        report = preflight.run_preflight(
                            nvml=binding, idle_seconds=0, load_seconds=0,
                            recovery_seconds=0, interval_ns=1_000_000)
                    self.assertEqual(library.init_calls, 2)
                    self.assertEqual(library.shutdown_calls, 0)
                    self.assertIn("preflight_shutdown_deferred_worker_active", report["flags"])
                    self.assertEqual(any(flag.startswith("native_references_retained:")
                                         for flag in report["flags"]), fail_outer)
                finally:
                    library.release.set()
                    for sampler in samplers:
                        for device in sampler._devices:
                            device.thread.join(timeout=2)
                    for owner in owners:
                        owner.join(timeout=2)
                    if fail_outer:
                        # Both owners failed to start. Explicit fixture teardown
                        # occurs only after the blocked native call has returned.
                        binding.nvmlShutdown()
                        binding.nvmlShutdown()
                self.assertEqual(library.shutdown_calls, 2)

    def test_predictive_criterion_has_its_stated_nominal_false_alarm_rate(self) -> None:
        seed_count, alpha = 1000, 0.05
        exceeded = 0
        for seed in range(seed_count):
            rng = random.Random(seed)
            # 64 idle and one held-out load reading make the exact Gaussian
            # predictive Student distribution applicable. The 0.001 W quantum
            # is 1/500 of the synthetic 0.5 W idle standard deviation.
            values = tuple(50 + rng.gauss(0, 0.5) for _ in range(65))
            trace = PowerTrace(
                "nvml_power", "gpu0:synthetic", "synthetic:monotonic",
                tuple(index*100_000_000+25_000_000 for index in range(65)), values, "W",
                100_000_000, 25_000_000, 0.25, 0.001,
                json.dumps({"sensor_facts": {"period_ns": 100_000_000}}))
            result = preflight.assess_power_movement(
                [trace], (0, 64*100_000_000), (64*100_000_000, 65*100_000_000),
                false_alarm_rate=alpha)
            exceeded += result["power_moved"]
        fraction = exceeded / seed_count
        # N1: four binomial SE. With alpha=.05 and S=1000 (>304), neither
        # m=0 (never fires) nor m=S (always fires) can pass this bar.
        bar = 4*math.sqrt(alpha*(1-alpha)/seed_count)
        print("NVML PREFLIGHT CALIBRATION", json.dumps({
            "seeds": seed_count, "outside": exceeded, "fraction": fraction,
            "alpha": alpha, "binomial_se": bar/4, "four_se_bar": bar}))
        self.assertLessEqual(abs(fraction-alpha), bar,
                             (exceeded, seed_count, fraction, alpha, bar))


if __name__ == "__main__":
    unittest.main()
