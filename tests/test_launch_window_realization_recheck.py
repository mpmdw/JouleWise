from __future__ import annotations

import argparse
import copy
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import types
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness, identity_pins
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig
from scripts import launch_window
from tests import test_identity_pins as projection_fixtures
from tests import test_run_night as night_fixtures


class LaunchRealizationRecheckTests(unittest.TestCase):
    """Real projection/file hashing; synthetic ARM replay and runtime metadata."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        projection_fixtures.init_git(self.root)
        self.pack, self.weight = projection_fixtures.make_pack(
            self.root, prompt_expectation=True
        )
        self.tokenizer = self.pack / "model/tokenizer.json"
        self.tokenizer.write_bytes(b'{"vocab":{"hello":1}}\n')
        head = projection_fixtures.commit_pack(self.root, self.pack, "projection inputs")
        probe = mock.patch.object(
            identity_pins, "_runtime_probe_metadata",
            side_effect=self._probe_metadata,
        )
        probe.start()
        self.addCleanup(probe.stop)
        with mock.patch.object(identity_pins, "_mint_git_anchor", return_value=(self.root, head)):
            identity_pins.freeze_projection(self.pack)
        # The ARM receipt stands for an already successful freeze/arm boundary.
        # The launch plumbing is isolated; all projection helpers remain real.
        self.arm = self.root / "arm.json"
        self.arm.write_bytes(b'{"status":"PASS"}\n')
        self.consumption = self.root / "consumed.json"
        self.night = self.root / "night"
        self.night.mkdir()
        self.runs = self.root / "runs"
        self.config = BenchmarkConfig.from_mapping(
            json.loads((self.pack / "configs/member-1.json").read_bytes())
        )
        self.argv = ["/bin/zsh", str(self.root / "window-chain.zsh")]
        self.args = argparse.Namespace(
            pack_root=self.pack, arm_receipt=self.arm,
            arm_readiness_custody_root=self.root,
            launch_manifest=self.root / "manifest.json",
            step6_confirmation_table=None, expected_confirmation_digest=None,
        )
        self.events: list[str] = []

    def _probe_metadata(self, config, realization_configs=()):
        metadata = projection_fixtures.probe_metadata(config, realization_configs)
        # Model inventory deliberately excludes tokenizer JSON. Simulate the
        # encoder's changed token sequence, as the real runtime probe observes.
        if json.loads(self.tokenizer.read_bytes())["vocab"]["hello"] != 1:
            for row in metadata.get("prompt_realizations", []):
                row["token_ids_sha256"] = "e" * 64
        return metadata

    def _consume(self, **_kwargs):
        self.events.append("consume")
        self.consumption.write_bytes(b'{"status":"CONSUMED"}\n')
        return {"consumption_path": self.consumption}

    def _verify(self, *_args, **_kwargs):
        self.events.append("verify")
        return {"exec_argv": self.argv}

    def _collect(self, _program, _argv, _environment):
        self.events.append("exec")
        (self.night / "chain.started").write_bytes(b"started\n")
        RunBundleWriter.create(self.runs, self.config, FakeClock())
        raise SystemExit(0)

    def _launch(self, *, verify=None):
        output = io.BytesIO()
        stream = io.TextIOWrapper(output, encoding="utf-8", write_through=True)
        cli = ["--pack-root", str(self.pack), "--arm-receipt", str(self.arm),
               "--arm-readiness-custody-root", str(self.root),
               "--launch-manifest", str(self.args.launch_manifest)]
        with mock.patch.object(launch_window, "_assemble_launch_inputs", return_value={
                "pack_root": self.pack, "exec_argv": self.argv}), \
             mock.patch.object(launch_window, "_install_handoff"), \
             mock.patch.object(launch_window, "_consume_launch_capability", side_effect=self._consume), \
             mock.patch.object(launch_window, "verify_consumed_launch", side_effect=verify or self._verify), \
             mock.patch.object(launch_window.os, "execve", side_effect=self._collect) as execute, \
             mock.patch.object(RunBundleWriter, "create", wraps=RunBundleWriter.create) as create, \
             mock.patch.object(launch_window.sys, "stdout", stream):
            try:
                code = launch_window.main(cli)
            except SystemExit as exc:
                code = exc.code
            raw = output.getvalue()
        return code, json.loads(raw) if raw else None, execute, create

    def _assert_dirty_refusal(self, result) -> None:
        code, refusal, execute, create = result
        self.assertEqual(code, 2)
        self.assertEqual(refusal["status"], "REFUSE")
        self.assertEqual(refusal["reason_codes"], ["readiness_identity_environment_dirty"])
        self.assertEqual(self.events, ["consume", "verify"])
        execute.assert_not_called()
        create.assert_not_called()
        self.assertTrue(self.consumption.is_file())
        self.assertFalse(self.runs.exists())
        self.assertFalse((self.night / "chain.started").exists())

    def test_post_arm_tokenizer_mutation_refuses_before_bundle_create(self) -> None:
        self.tokenizer.write_bytes(b'{"vocab":{"hello":2}}\n')
        self._assert_dirty_refusal(self._launch())

    def test_tokenizer_mutation_after_consumed_replay_leaves_chain_unstarted(self) -> None:
        def verify_then_mutate(*args, **kwargs):
            result = self._verify(*args, **kwargs)
            self.tokenizer.write_bytes(b'{"vocab":{"hello":3}}\n')
            return result
        self._assert_dirty_refusal(self._launch(verify=verify_then_mutate))

    def test_post_arm_model_file_mutation_refuses_before_bundle_create(self) -> None:
        self.weight.write_bytes(b"changed-model-weights")
        self._assert_dirty_refusal(self._launch())

    def test_clean_projection_reaches_unchanged_exec_and_bundle_create(self) -> None:
        before = projection_fixtures.pack_bytes(self.pack)
        code, refusal, execute, create = self._launch()
        self.assertEqual(code, 0)
        self.assertIsNone(refusal)
        self.assertEqual(self.events, ["consume", "verify", "exec"])
        execute.assert_called_once_with(self.argv[0], self.argv, dict(os.environ))
        create.assert_called_once()
        self.assertTrue((self.night / "chain.started").is_file())
        self.assertTrue(self.runs.is_dir())
        self.assertEqual(projection_fixtures.pack_bytes(self.pack), before)

    def test_projection_digest_mismatch_refuses_even_when_units_match(self) -> None:
        derive = identity_pins._derive_projection_units
        def changed_digest(*args):
            units, digest, checks = derive(*args)
            return units, ("0" if digest[0] != "0" else "1") + digest[1:], checks
        with mock.patch.object(identity_pins, "_derive_projection_units", side_effect=changed_digest):
            self._assert_dirty_refusal(self._launch())

    def test_unit_mismatch_refuses_even_when_projection_digest_matches(self) -> None:
        derive = identity_pins._derive_projection_units
        def changed_unit(*args):
            units, digest, checks = derive(*args)
            units = copy.deepcopy(units)
            units[0]["model_runtime_config"]["runtime_identity_sha256"] = "0" * 64
            return units, digest, checks
        with mock.patch.object(identity_pins, "_derive_projection_units", side_effect=changed_unit):
            self._assert_dirty_refusal(self._launch())

    def test_underivable_live_inputs_emit_identity_dirty_refusal(self) -> None:
        with mock.patch.object(identity_pins, "_derive_projection_units", side_effect=
                identity_pins.IdentityPinProjectionError(
                    "readiness_identity_artifact_unreadable", "missing tokenizer")):
            self._assert_dirty_refusal(self._launch())

    def test_failed_consumed_replay_does_not_rederive_or_exec(self) -> None:
        def refuse(*args, **kwargs):
            self._verify(*args, **kwargs)
            raise arm_readiness.LaunchLineageError("launch_binding_mismatch", "changed replay")
        with mock.patch.object(identity_pins, "_derive_projection_units") as derive:
            code, refusal, execute, create = self._launch(verify=refuse)
        self.assertEqual(code, 2)
        self.assertEqual(refusal["reason_codes"], ["launch_binding_mismatch"])
        derive.assert_not_called()
        execute.assert_not_called()
        create.assert_not_called()

    def _driver_launch(self, mutation, *, fixture_group_census=True, start_fd198=False):
        """Real launcher child/barrier, projection hashing, exec and bundle writer."""
        collect = self.root / "collect.py"
        collect.write_text(f'''
import json, os
from pathlib import Path
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig
night = Path({str(self.night)!r})
record = json.loads((night / "chain.started").read_bytes())
assert record["pid"] == record["pgid"] == os.getpid()
assert set(record) == {{"pid", "pgid", "epoch_s", "start_time"}}
assert "{launch_window.CHAIN_START_FD_ENV}" not in os.environ
config = BenchmarkConfig.from_mapping(json.loads(Path({str(self.pack / 'configs/member-1.json')!r}).read_bytes()))
RunBundleWriter.create(Path({str(self.runs)!r}), config, FakeClock())
''')
        launcher = self.root / "launcher.py"
        launcher.write_text(f'''
import json
from pathlib import Path
from unittest import mock
from scripts import launch_window
from joulewise import identity_pins
from tests.test_identity_pins import probe_metadata
pack = Path({str(self.pack)!r})
tokenizer = Path({str(self.tokenizer)!r})
argv = [{sys.executable!r}, "-B", {str(collect)!r}]
def metadata(config, realization_configs=()):
    result = probe_metadata(config, realization_configs)
    if json.loads(tokenizer.read_bytes())["vocab"]["hello"] != 1:
        for row in result.get("prompt_realizations", []):
            row["token_ids_sha256"] = "e" * 64
    return result
def consume(**kwargs):
    Path({str(self.consumption)!r}).write_bytes(b'{{"status":"CONSUMED"}}\\n')
    return {{"consumption_path": Path({str(self.consumption)!r})}}
def verify(*args, **kwargs):
    if {mutation!r} == "tokenizer":
        tokenizer.write_bytes(b'{{"vocab":{{"hello":2}}}}\\n')
    elif {mutation!r} == "model":
        Path({str(self.weight)!r}).write_bytes(b"changed-model-weights")
    return {{"exec_argv": argv}}
with mock.patch.object(launch_window, "_assemble_launch_inputs", return_value={{"pack_root": pack, "exec_argv": argv}}), \\
     mock.patch.object(launch_window, "_consume_launch_capability", side_effect=consume), \\
     mock.patch.object(launch_window, "verify_consumed_launch", side_effect=verify), \\
     mock.patch.object(identity_pins, "_runtime_probe_metadata", side_effect=metadata):
    raise SystemExit(launch_window.main(["--pack-root", str(pack), "--arm-receipt", {str(self.arm)!r},
        "--arm-readiness-custody-root", {str(self.root)!r}, "--launch-manifest", {str(self.args.launch_manifest)!r}]))
''')
        driver = night_fixtures._load_driver()
        now = time.time()
        plan = types.SimpleNamespace(plan_id="driver-recheck", t0_epoch_s=now, window_max_s=60,
                                     measurement_root=str(launch_window.REPOSITORY_ROOT))
        probes = night_fixtures.ProbeSource(now, str(self.root)).probes()
        environment = dict(os.environ, PYTHONPATH=str(launch_window.REPOSITORY_ROOT))
        # The rejection fixture has only this blocked launcher child, which
        # the real termination helper reaps. Its group census is fixture data
        # so sandbox process-inspection permissions do not change the test.
        census = (mock.patch.object(driver, "_group_census", return_value=(True, []))
                  if fixture_group_census else nullcontext())
        socketpair = driver.socket.socketpair
        def reserved_slot_pair():
            parent, child = socketpair()
            if child.fileno() == launch_window.HANDOFF_FD:
                return parent, child
            try:
                saved = os.dup(launch_window.HANDOFF_FD)
            except OSError:
                saved = None
            if saved is not None:
                def restore():
                    os.dup2(saved, launch_window.HANDOFF_FD)
                    os.close(saved)
                self.addCleanup(restore)
            os.dup2(child.fileno(), launch_window.HANDOFF_FD)
            child.close()
            return parent, driver.socket.socket(fileno=launch_window.HANDOFF_FD)
        barrier = (mock.patch.object(driver.socket, "socketpair", side_effect=reserved_slot_pair)
                   if start_fd198 else nullcontext())
        with census, barrier, mock.patch.object(driver, "_chain_environment", return_value=environment), \
             mock.patch.object(driver, "_claim_chain_start", wraps=driver._claim_chain_start) as claim:
            result = driver._run_chain_once(collect, plan, probes, self.night, None,
                command=[sys.executable, "-B", str(launcher)])
        return driver, result, claim

    def test_driver_tokenizer_mutation_after_consumed_replay_never_claims_start(self):
        driver, result, claim = self._driver_launch("tokenizer")
        self.assertIsNone(result[0])
        self.assertEqual(result[1]["reason"], "night_chain_launch_failed")
        self.assertEqual(result[1]["evidence"]["launcher_refusal"]["reason_codes"],
                         ["readiness_identity_environment_dirty"])
        self.assertTrue(result[4])
        claim.assert_not_called()
        self.assertFalse((self.night / "chain.started").exists())
        self.assertFalse((self.night / "chain.exited").exists())
        self.assertTrue((self.night / "launch.resolved").exists())
        self.assertFalse(self.runs.exists())
        self.assertTrue(self.consumption.exists())
        pending = json.loads((self.night / "launch.pending").read_bytes())
        self.assertEqual(pending["plan_id"], "driver-recheck")
        self.assertEqual(pending["pid"], pending["pgid"])
        self.assertIn("start_time", pending)
        self.assertEqual(len(pending["attempt_id"]), 32)
        self.assertEqual((self.night / "launch.pending").stat().st_mode & 0o777, 0o600)

    def test_driver_model_mutation_after_consumed_replay_never_claims_start(self):
        _driver, result, claim = self._driver_launch("model")
        self.assertEqual(result[1]["evidence"]["launcher_refusal"]["reason_codes"],
                         ["readiness_identity_environment_dirty"])
        claim.assert_not_called()
        self.assertFalse((self.night / "chain.started").exists())
        self.assertFalse(self.runs.exists())

    def test_driver_clean_recheck_claims_once_before_real_exec_and_bundle(self):
        driver, result, claim = self._driver_launch(None)
        self.assertEqual(result[0:2], (0, None))
        self.assertTrue(result[4])
        claim.assert_called_once_with(self.night)
        self.assertTrue(self.runs.exists())
        record = json.loads((self.night / "chain.started").read_bytes())
        before = (self.night / "chain.started").read_bytes()
        self.assertIsNone(driver._claim_chain_start(self.night))
        self.assertEqual((self.night / "chain.started").read_bytes(), before)
        self.assertEqual(record["pid"], record["pgid"])
        self.assertIsInstance(record["epoch_s"], float)
        self.assertEqual((self.night / "chain.started").stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads((self.night / "chain.exited").read_bytes())["exit_code"], 0)

    def test_driver_existing_exclusive_claim_prevents_real_collection_exec(self):
        original = b'{"pid":123,"pgid":123,"epoch_s":1.0,"start_time":"prior"}\n'
        (self.night / "chain.started").write_bytes(original)
        _driver, result, claim = self._driver_launch(None, fixture_group_census=True)
        claim.assert_called_once_with(self.night)
        self.assertEqual(result[1]["reason"], "night_chain_already_started")
        self.assertTrue(result[4])
        self.assertEqual((self.night / "chain.started").read_bytes(), original)
        self.assertFalse(self.runs.exists())

    def test_driver_barrier_does_not_collide_with_reserved_capability_fd198(self):
        _driver, result, claim = self._driver_launch(None, start_fd198=True)
        self.assertEqual(result[0:2], (0, None))
        claim.assert_called_once_with(self.night)
        self.assertTrue(self.runs.exists())


class PendingLauncherCustodyTests(unittest.TestCase):
    def test_skewed_measurement_launcher_refuses_before_popen_or_collection(self):
        """Fable F2: an old launcher ignores the barrier and collects directly."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            night = root / "night"
            night.mkdir()
            launcher = root / "measurement/scripts/launch_window.py"
            launcher.parent.mkdir(parents=True)
            marker = root / "collection-ran"
            launcher.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
            driver = night_fixtures._load_driver()
            now = time.time()
            plan = types.SimpleNamespace(plan_id="skew", t0_epoch_s=now, window_max_s=60,
                                         measurement_root=str(launcher.parents[1]))
            probes = night_fixtures.ProbeSource(now, str(root)).probes()
            with mock.patch.object(driver.subprocess, "Popen") as spawn:
                result = driver._run_chain_once(Path("/dev/null"), plan, probes, night, None,
                    command=[sys.executable, "-B", str(launcher)])
            spawn.assert_not_called()
            self.assertEqual(result[1]["reason"], "night_chain_launch_failed")
            self.assertIn("barrier refused before launch", result[1]["detail"])
            self.assertTrue(result[4])
            self.assertFalse(marker.exists())
            self.assertEqual(list(night.iterdir()), [])

    def test_measurement_barrier_capability_is_literal_and_versioned(self):
        driver = night_fixtures._load_driver()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            launcher = root / "scripts/launch_window.py"
            launcher.parent.mkdir()
            plan = types.SimpleNamespace(measurement_root=str(root))
            for version in ("0", "2", "True", "int('1')"):
                launcher.write_text(f'CHAIN_START_BARRIER_VERSION = {version}\n'
                                    'CHAIN_START_FD_ENV = "JOULEWISE_CHAIN_START_FD"\nHANDOFF_FD = 198\n')
                with self.subTest(version=version), self.assertRaises(ValueError):
                    driver._launcher_barrier(plan)
            launcher.write_text('CHAIN_START_BARRIER_VERSION = 1\n'
                                'CHAIN_START_FD_ENV = "JOULEWISE_CHAIN_START_FD"\nHANDOFF_FD = 198\n'
                                'raise RuntimeError("must never import measurement launcher")\n')
            self.assertEqual(driver._launcher_barrier(plan), ("JOULEWISE_CHAIN_START_FD", 198))

    def test_non_speaking_launcher_timeout_claims_possible_collection_for_recover(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            night = root / "night"
            night.mkdir()
            marker = root / "collection-ran"
            driver = night_fixtures._load_driver()
            now = time.time()
            plan = types.SimpleNamespace(plan_id="silent", t0_epoch_s=now, window_max_s=60,
                                         measurement_root=str(launch_window.REPOSITORY_ROOT))
            probes = night_fixtures.ProbeSource(now, str(root)).probes()
            # An unexpected launcher implementation violates its advertised
            # protocol. Use Fable's direct-collection stand-in after admission.
            command = ["/bin/sh", "-c", 'printf bundle > "$1"; sleep 30', "--", str(marker)]
            with mock.patch.object(driver, "_chain_environment", return_value=dict(os.environ)), \
                 mock.patch.object(driver, "LAUNCHER_FIRST_BYTE_TIMEOUT_S", .5), \
                 mock.patch.object(driver, "_group_census", return_value=(True, [])), \
                 mock.patch.object(driver, "_claim_chain_start", wraps=driver._claim_chain_start) as claim:
                result = driver._run_chain_once(Path("/dev/null"), plan, probes, night, None,
                                               command=command)
            self.assertTrue(marker.exists())
            self.assertTrue(result[4])
            self.assertEqual(result[1]["reason"], "night_chain_launch_failed")
            self.assertIn("first-byte timeout", result[1]["detail"])
            claim.assert_called_once_with(night)
            self.assertTrue((night / "chain.started").exists())  # RECOVER, never NULL.
            self.assertTrue((night / "chain.exited").exists())
            self.assertTrue((night / "launch.resolved").exists())

    def test_driver_death_before_custody_ack_refuses_before_consumption_or_recheck(self):
        import socket
        parent, child = socket.socketpair()
        parent.close()
        descriptor = child.detach()  # launch() owns and closes the descriptor.
        with mock.patch.dict(os.environ, {launch_window.CHAIN_START_FD_ENV: str(descriptor)}), \
             mock.patch.object(launch_window, "_launch") as proceed:
            with self.assertRaises((launch_window.LaunchLineageError, OSError)):
                launch_window.launch(argparse.Namespace())
        proceed.assert_not_called()

    def test_driver_death_during_stalled_recheck_retains_deadman_custody(self):
        """Review V5: kill the driver after the real launch enters recheck."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            night = root / "night"
            night.mkdir()
            ready = root / "ready"
            launcher = root / "launcher.py"
            launcher.write_text(f'''
import argparse, json, os, time
from pathlib import Path
from unittest import mock
from scripts import launch_window
night = Path({str(night)!r})
def stalled(pack):
    record = json.loads((night / "launch.pending").read_bytes())
    assert record["pid"] == record["pgid"] == os.getpid()
    assert record["plan_id"] == "driver-death"
    assert not (night / "chain.started").exists()
    Path({str(ready)!r}).write_text(str(os.getpid()))
    time.sleep(30)
args = argparse.Namespace(pack_root=Path('pack'), launch_manifest=Path('manifest'),
    step6_confirmation_table=None, expected_confirmation_digest=None)
with mock.patch.object(launch_window, "_assemble_launch_inputs", return_value={{"pack_root": Path('pack'), "exec_argv": ['/usr/bin/true']}}), \\
     mock.patch.object(launch_window, "_consume_launch_capability", return_value={{"consumption_path": Path('consumed')}}), \\
     mock.patch.object(launch_window, "verify_consumed_launch", return_value={{"exec_argv": ['/usr/bin/true']}}), \\
     mock.patch.object(launch_window, "_recheck_identity_projection", side_effect=stalled):
    launch_window.launch(args)
''')
            worker = root / "driver.py"
            worker.write_text(f'''
import os, sys, time, types
from pathlib import Path
from unittest import mock
from tests.test_run_night import _load_driver, ProbeSource
driver = _load_driver()
plan = types.SimpleNamespace(plan_id="driver-death", t0_epoch_s=time.time(), window_max_s=60,
    measurement_root={str(launch_window.REPOSITORY_ROOT)!r})
with mock.patch.object(driver, "_chain_environment", return_value=dict(os.environ)):
    driver._run_chain_once(Path({str(launcher)!r}), plan, ProbeSource(time.time()).probes(),
        Path({str(night)!r}), None, command=[sys.executable, '-B', {str(launcher)!r}])
''')
            environment = dict(os.environ, PYTHONPATH=str(launch_window.REPOSITORY_ROOT))
            with (root / "driver.log").open("wb") as log:
                process = subprocess.Popen([sys.executable, "-B", str(worker)],
                    env=environment, stdout=log, stderr=log, start_new_session=True)
                child_pid = None
                try:
                    deadline = time.monotonic() + 10
                    while not ready.exists():
                        if process.poll() is not None or time.monotonic() >= deadline:
                            self.fail((root / "driver.log").read_text())
                        time.sleep(.02)
                    child_pid = int(ready.read_text())
                    process.kill()
                    process.wait(timeout=3)
                    os.kill(child_pid, 0)
                    self.assertFalse((night / "chain.started").exists())
                    self.assertFalse((night / "chain.exited").exists())
                    original = (night / "launch.pending").read_bytes()
                    case = night_fixtures.NightDriverTests()
                    case.setUp()
                    try:
                        from dataclasses import replace
                        plan = replace(case.driver._load_plan(case.plan_path), custody_root=str(root))
                        with mock.patch.object(case.driver, "_load_plan", return_value=plan):
                            code = case.driver.dead_man(root / "plan.json")
                        self.assertEqual(code, case.driver.EXIT_REFUSED)
                        case.driver.run_courier.assert_not_called()
                        refusal = json.loads((night / "refusal.json").read_bytes())
                        self.assertEqual(refusal["refusal"]["reason"], "night_chain_alive")
                        self.assertEqual(refusal["refusal"]["evidence"]["pgid"], child_pid)
                        self.assertEqual((night / "launch.pending").read_bytes(), original)
                        self.assertFalse((night / "chain.exited").exists())
                    finally:
                        case.tearDown()
                        case.doCleanups()
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=3)
                    if child_pid is None and (night / "launch.pending").exists():
                        child_pid = json.loads((night / "launch.pending").read_bytes())["pgid"]
                    if child_pid is not None:
                        try:
                            os.killpg(child_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        # Wait for all group members, not just the dead driver.
                        deadline = time.monotonic() + 5
                        while time.monotonic() < deadline:
                            try:
                                os.killpg(child_pid, 0)
                            except ProcessLookupError:
                                break
                            time.sleep(.02)
                        else:
                            self.fail("pending launcher group survived test cleanup")


class NonPackLaunchRouteTests(unittest.TestCase):
    def _run_non_pack(self, receipt_class):
        case = night_fixtures.NightDriverTests()
        case.setUp()
        self.addCleanup(case.tearDown)
        case._write_plan(receipt_class=receipt_class)
        with mock.patch.object(identity_pins, "_derive_projection_units",
                side_effect=AssertionError("non-pack route must not derive a projection")) as derive, \
             mock.patch.object(launch_window, "launch",
                side_effect=AssertionError("non-pack route must not enter pack launcher")) as launch:
            code, commands = case._run_night()
        derive.assert_not_called()
        launch.assert_not_called()
        receipt = json.loads((case.custody / "night/receipt.json").read_bytes())
        return case, code, commands, receipt

    def test_diagnostic_no_pack_keeps_direct_chain_route(self):
        case, code, commands, receipt = self._run_non_pack("DIAGNOSTIC_NO_PACK")
        self.assertEqual(code, case.driver.EXIT_GO)
        self.assertEqual(commands, [["/bin/zsh", str(case.chain)]])
        self.assertEqual(receipt["verdict"], "GO")

    def test_rehearsal_stub_keeps_stub_route_and_rehearsal_verdict(self):
        case, code, commands, receipt = self._run_non_pack("REHEARSAL_STUB")
        self.assertEqual(code, case.driver.EXIT_REFUSED)
        self.assertEqual(commands, [["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]])
        self.assertEqual(receipt["verdict"], "REHEARSAL_ONLY")


if __name__ == "__main__":
    unittest.main()
