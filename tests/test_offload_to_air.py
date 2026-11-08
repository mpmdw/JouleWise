"""Synthetic records only. No ssh, network, hardware, model or study-data access."""
from __future__ import annotations

import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import offload_to_air as air


class OffloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="jw-air-synthetic-", dir="/private/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.record = self.base / "closed-window"
        self.record.mkdir()
        (self.record / "data.bin").write_bytes(b"synthetic bytes\n" * 100)
        night = self.record / "night"
        night.mkdir()
        air.save(night / "result.json", {"plan_id": "synthetic-window", "verdict": "COLLECTED",
                                        "ended_epoch_s": time.time() - 60})
        for marker in ("chain.started", "chain.exited", "courier.sent"):
            (night / marker).write_text("synthetic\n")
        self.manifest = {"schema": air.MANIFEST_SCHEMA, "closed": True, "files": self.rows()}
        self.pin_manifest()
        self.primary, self.backup = self.base / "air-ssd", self.base / "second-disk"
        self.primary.mkdir()
        self.backup.mkdir()
        self.gate_path, self.watch_path = self.base / "gate.json", self.base / "watchdog.json"
        self.gate = {"schema": air.GATE_SCHEMA, "generation": "turnaround-1", "phase": "cooldown",
                     "armed": False, "measuring": False, "record_manifest_sha256": self.record_id,
                     "record_committed": True, "record_pushed": True,
                     "quiet_dwell_epoch_s": time.time() + 600, "expires_epoch_s": time.time() + 600}
        air.save(self.gate_path, self.gate)
        air.save(self.watch_path, {"fenced_checkouts": []})
        self.identity, self.known = self.base / "key", self.base / "known_hosts"
        self.identity.touch()
        self.known.touch()
        self.config = air.Client(self.record, "manifest.json", self.record_id,
                                 self.gate_path, self.watch_path, "night/result.json",
                                 self.base / "loop.lock", self.base / "client-state",
                                 "jw-offload@air.invalid", self.identity, self.known, 300, 50,
                                 overhead_s=0)
        self.calls = []
        self.copy_fault = None
        self.receipt_fault = None
        self.before_command = None

    def rows(self):
        return {name: {"sha256": air.file_sha(self.record / name), "size": size}
                for name, size in air.files(self.record).items() if name != "manifest.json"}

    def pin_manifest(self):
        air.save(self.record / "manifest.json", self.manifest)
        self.record_id = air.sha((self.record / "manifest.json").read_bytes())

    def devices(self, path):
        # Deliberately synthetic filesystem identity, not a hardware proof.
        return "second" if self.backup == path or self.backup in path.parents else "primary"

    def runner(self, command, *, timeout, check=lambda: None):
        self.calls.append(command)
        self.assertGreater(timeout, 0)
        if self.before_command:
            self.before_command(command)
        check()
        if command[0] == "ssh":
            self.assertIn("StrictHostKeyChecking=yes", command)
            self.assertIn("BatchMode=yes", command)
            _, value = air.serve(self.primary, self.backup, self.base / "rrsync", command[-1])
            if self.receipt_fault and "receipt" in value:
                value = self.receipt_fault(copy.deepcopy(value))
            return subprocess.CompletedProcess(command, 0, air.encode(value), b"")
        self.assertEqual(command[0], "rsync")
        source = Path(command[-2].rstrip("/"))
        if ":" in command[-1]:
            target = self.primary / "incoming" / command[-1].split(":", 1)[1].rstrip("/")
        else:
            target = Path(command[-1].rstrip("/"))
        target.mkdir(parents=True, exist_ok=True)
        if self.copy_fault == "interrupt":
            (target / "data.bin").write_bytes(b"partial")
            return subprocess.CompletedProcess(command, 23, b"", b"interrupted")
        shutil.copytree(source, target, dirs_exist_ok=True)
        if self.copy_fault == "corrupt":
            (target / "data.bin").write_bytes(b"corrupt")
        if self.copy_fault == "missing":
            (target / "data.bin").unlink()
        if self.copy_fault == "extra":
            (target / "unmanifested").write_text("unexpected")
        check()
        return subprocess.CompletedProcess(command, 0, b"", b"")

    def push(self, **changes):
        with patch.object(air, "device_id", side_effect=self.devices):
            return air.offload(replace(self.config, **changes), runner=self.runner)

    def make_backup(self):
        with patch.object(air, "device_id", side_effect=self.devices):
            return air.backup_once(self.primary, self.backup, runner=self.runner)

    def test_one_air_copy_retains_local_and_queues_then_two_allow_delete(self):
        first = self.push()
        self.assertEqual((first["status"], first["copies"]), ("retained", 1))
        self.assertTrue(self.record.exists())
        self.assertEqual(air.read_json(self.primary / "jobs" / (self.record_id + ".json"))["status"], "queued")
        self.assertEqual(self.make_backup(), [self.record_id])
        confirmed = self.push()
        self.assertEqual((confirmed["status"], confirmed["copies"]), ("deleted", 2))
        self.assertFalse(self.record.exists())
        self.assertEqual(self.push()["status"], "already-deleted")

    def test_native_terminal_go_and_aborted_are_supported(self):
        for verdict in ("GO", "ABORTED"):
            with self.subTest(verdict=verdict):
                air.save(self.record / "night/result.json", {"plan_id": "synthetic-window",
                    "verdict": verdict, "ended_epoch_s": time.time() - 60})
                air.terminal_check(self.record, "night/result.json")

    def test_process_alarm_also_bounds_a_stalled_injected_runner(self):
        def stalled(*args, **kwargs):
            time.sleep(5)
        started = time.monotonic()
        with self.assertRaisesRegex(air.Refusal, "process budget"):
            air.offload(replace(self.config, budget_s=0.1), runner=stalled)
        self.assertLess(time.monotonic() - started, 1)
        self.assertTrue(self.record.exists())

    def test_duplicate_run_does_not_transfer_again_or_duplicate_job(self):
        self.push()
        transferred = sum(c[0] == "rsync" for c in self.calls)
        again = self.push()
        self.assertEqual(again["status"], "retained")
        self.assertEqual(sum(c[0] == "rsync" for c in self.calls), transferred)
        self.assertEqual(len(list((self.primary / "jobs").iterdir())), 1)

    def test_interruption_is_resumable_and_never_deletes(self):
        self.copy_fault = "interrupt"
        with self.assertRaisesRegex(air.Refusal, "interrupted"):
            self.push()
        self.assertTrue(self.record.exists())
        self.assertFalse((self.primary / "records" / self.record_id).exists())
        self.copy_fault = None
        self.assertEqual(self.push()["status"], "retained")
        self.assertIn("--partial", next(c for c in self.calls if c[0] == "rsync"))
        self.assertIn("--checksum", next(c for c in self.calls if c[0] == "rsync"))

    def test_corrupt_partial_or_extra_remote_copy_never_receipted(self):
        for fault in ("corrupt", "missing", "extra"):
            with self.subTest(fault=fault):
                self.copy_fault = fault
                with self.assertRaises(air.Refusal):
                    self.push()
                self.assertTrue(self.record.exists())
                self.assertFalse((self.primary / "receipts" / (self.record_id + ".json")).exists())
                shutil.rmtree(self.primary / "incoming" / self.record_id)

    def test_local_corruption_refuses_before_transport(self):
        (self.record / "data.bin").write_bytes(b"corrupt")
        with self.assertRaisesRegex(air.Refusal, "digest mismatch"):
            self.push()
        self.assertEqual(self.calls, [])

    def test_partial_hash_wrong_binding_stale_challenge_and_copy_status_refuse(self):
        self.push()

        def mutations():
            yield lambda v: {"receipt": v["receipt"]}
            yield lambda v: {**v, "sha256": "0" * 64}
            for field, replacement in (("record_id", "0" * 64), ("challenge", "0" * 32),
                                       ("summary", {"bytes": 0}), ("backup_status", "confirmed")):
                def mutate(v, field=field, replacement=replacement):
                    v["receipt"][field] = replacement
                    return air.envelope(v["receipt"])
                yield mutate
            def same_device(v):
                v["receipt"]["copies"] *= 2
                v["receipt"]["backup_status"] = "confirmed"
                return air.envelope(v["receipt"])
            yield same_device
        for mutate in mutations():
            with self.subTest(mutation=mutate):
                self.receipt_fault = mutate
                with self.assertRaises(air.Refusal):
                    self.push()
                self.assertTrue(self.record.exists())

    def test_armed_measuring_dwell_unknown_or_wrong_record_refuse(self):
        for changes in ({"armed": True}, {"measuring": True}, {"phase": "dwell"},
                        {"record_manifest_sha256": "0" * 64}, {"schema": "unknown"},
                        {"quiet_dwell_epoch_s": time.time() - 1}, {"record_pushed": False}):
            with self.subTest(changes=changes):
                air.save(self.gate_path, {**self.gate, **changes})
                with self.assertRaises(air.Refusal):
                    self.push()
        self.assertEqual(self.calls, [])

    def test_native_watchdog_armed_and_missing_state_refuse(self):
        for watch in ({"fenced_checkouts": [["armed-plan"]]}, {}, {"fenced_checkouts": None}):
            air.save(self.watch_path, watch)
            with self.assertRaisesRegex(air.Refusal, "watchdog"):
                self.push()
        self.watch_path.unlink()
        with self.assertRaises(OSError):
            self.push()
        self.assertEqual(self.calls, [])

    def test_loop_lock_excludes_arm_transition_and_concurrent_offload(self):
        with air.lock(self.config.loop_lock):
            with self.assertRaisesRegex(air.Refusal, "lock busy"):
                self.push()
        self.assertEqual(self.calls, [])

    def test_open_or_unknown_terminal_refuses(self):
        (self.record / "night/chain.exited").unlink()
        with self.assertRaisesRegex(air.Refusal, "chain is open"):
            self.push()
        self.assertEqual(self.calls, [])

    def test_deadline_estimate_and_bandwidth_cap_refuse_before_network(self):
        for config in ({"budget_s": 0.000001}, {"bwlimit_kib": 1, "budget_s": 1}):
            with self.subTest(config=config), self.assertRaisesRegex(air.Refusal, "estimate|deadline"):
                self.push(**config)
        self.assertEqual(self.calls, [])
        self.push(bwlimit_kib=512)
        self.assertIn("--bwlimit=512", next(c for c in self.calls if c[0] == "rsync"))

    def test_state_change_during_transport_aborts_and_retains(self):
        def change(command):
            if command[0] == "rsync":
                air.save(self.gate_path, {**self.gate, "measuring": True})
        self.before_command = change
        with self.assertRaisesRegex(air.Refusal, "measuring"):
            self.push()
        self.assertTrue(self.record.exists())
        self.assertFalse((self.primary / "records" / self.record_id).exists())

    def test_generation_change_during_transport_refuses(self):
        self.before_command = lambda _: air.save(self.gate_path, {**self.gate, "generation": "next"})
        with self.assertRaisesRegex(air.Refusal, "lease changed"):
            self.push()

    def test_deadline_uses_monotonic_clock_even_if_wall_clock_moves_backward(self):
        monotonic = [10.0]
        gate = air.Gate(self.config, wall=lambda: time.time() - 100, monotonic=lambda: monotonic[0])
        monotonic[0] += self.config.budget_s + 1
        with self.assertRaisesRegex(air.Refusal, "deadline"):
            gate.check()

    def test_symlinks_hardlinks_and_escape_manifest_refuse_before_network(self):
        outside = self.base / "outside"
        outside.write_text("never copy this")
        (self.record / "link").symlink_to(outside)
        with self.assertRaisesRegex(air.Refusal, "symlink"):
            self.push()
        (self.record / "link").unlink()
        os.link(outside, self.record / "linked")
        with self.assertRaisesRegex(air.Refusal, "hard-linked"):
            self.push()
        (self.record / "linked").unlink()
        self.manifest["files"]["../outside"] = {"sha256": "0" * 64, "size": 1}
        self.pin_manifest()
        self.gate["record_manifest_sha256"] = self.record_id
        air.save(self.gate_path, self.gate)
        with self.assertRaisesRegex(air.Refusal, "relative path"):
            self.push(manifest_sha256=self.record_id)
        self.assertEqual(self.calls, [])

    def test_symlink_parent_never_traversed(self):
        link = self.base / "alias"
        link.symlink_to(self.record, target_is_directory=True)
        with self.assertRaisesRegex(air.Refusal, "symlink path"):
            self.push(record=link)
        self.assertEqual(self.calls, [])

    def test_missing_or_unmanifested_files_refuse(self):
        (self.record / "extra").touch()
        with self.assertRaisesRegex(air.Refusal, "inventory mismatch"):
            self.push()
        (self.record / "extra").unlink()
        (self.record / "data.bin").unlink()
        with self.assertRaisesRegex(air.Refusal, "inventory mismatch"):
            self.push()

    def test_disk_pressure_never_weakens_two_copy_requirement(self):
        first = self.push(delete_policy="pressure", min_free_bytes=10**30)
        self.assertEqual(first["status"], "retained")
        self.assertTrue(first["hold_next_window"])
        self.make_backup()
        self.assertEqual(self.push(delete_policy="pressure", min_free_bytes=0)["status"], "retained")
        self.assertEqual(self.push(delete_policy="pressure", min_free_bytes=10**30)["status"], "deleted")

    def test_never_policy_retains_even_after_two_verified_copies(self):
        self.push()
        self.make_backup()
        self.assertEqual(self.push(delete_policy="never")["status"], "retained")
        self.assertTrue(self.record.exists())

    def test_same_filesystem_cannot_count_as_second_copy(self):
        self.push()
        with self.assertRaisesRegex(air.Refusal, "independent"):
            air.backup_once(self.primary, self.backup, runner=self.runner)

    def test_background_interruption_or_corruption_never_confirms(self):
        self.push()
        for fault in ("interrupt", "corrupt"):
            self.copy_fault = fault
            with self.assertRaises(air.Refusal):
                self.make_backup()
            self.assertEqual(air.read_json(self.primary / "jobs" / (self.record_id + ".json"))["status"], "queued")
            self.assertTrue(self.record.exists())
        self.copy_fault = None
        self.make_backup()
        self.assertEqual(self.push()["status"], "deleted")

    def test_previously_confirmed_backup_must_still_verify(self):
        self.push()
        self.make_backup()
        (self.backup / "records" / self.record_id / "data.bin").write_bytes(b"lost")
        with self.assertRaisesRegex(air.Refusal, "digest mismatch"):
            self.push()
        self.assertTrue(self.record.exists())

    def test_lost_receipt_after_air_commit_recovers_without_retransfer(self):
        self.receipt_fault = lambda _: {"receipt": {}}
        with self.assertRaises(air.Refusal):
            self.push()
        self.assertTrue((self.primary / "records" / self.record_id).exists())
        transfers = sum(c[0] == "rsync" for c in self.calls)
        self.receipt_fault = None
        self.push()
        self.assertEqual(sum(c[0] == "rsync" for c in self.calls), transfers)

    def test_interrupted_deletion_recovers_from_journal_and_fresh_two_copies(self):
        self.push()
        self.make_backup()
        unlink = os.unlink
        removed = []

        def interrupt(path, *args, **kwargs):
            if kwargs.get("dir_fd") is not None:
                if len(removed) >= 2:
                    raise OSError("synthetic deletion interruption")
                removed.append(path)
            return unlink(path, *args, **kwargs)
        with patch.object(os, "unlink", interrupt), self.assertRaisesRegex(OSError, "interruption"):
            self.push()
        self.assertTrue(self.record.exists())
        self.assertFalse((self.record / "manifest.json").exists())
        self.assertEqual(self.push()["status"], "deleted")

    def test_receiver_dispatcher_only_allows_rrsync_or_exact_receipt_verbs(self):
        for command in ("", "sh", "jw-air verify ../escape manifest.json abc", "jw-air status; sh",
                        "rsync --sender", "jw-air verify a b c extra"):
            with self.subTest(command=command), self.assertRaises(air.Refusal):
                air.serve(self.primary, self.backup, self.base / "rrsync", command)
        executed = []
        air.serve(self.primary, self.backup, self.base / "rrsync", "rsync --server -tr . hash/",
                  exec_fn=lambda executable, argv: executed.append(argv))
        self.assertEqual(executed[0][1:3], ["-wo", "-no-del"])
        self.assertEqual(executed[0][-1], str(self.primary / "incoming"))

    def test_native_harvest_inventory_adapter_ignores_absolute_path_references(self):
        rows = self.rows()
        harvest = {"schema": "joulewise.harvest_window.v1", "custody_root": "/DO-NOT-OPEN",
                   "inventory": {"custody-root": {".": {"mode": 0o40755}}}}
        old = self.record
        target = self.base / "synthetic-harvest"
        target.mkdir()
        shutil.copytree(old, target / "custody-root")
        (target / "custody-root/manifest.json").unlink()
        for name, row in rows.items():
            harvest["inventory"]["custody-root"][name] = {**row, "mode": 0o100644}
        air.save(target / "harvest.json", harvest)
        pin = air.sha((target / "harvest.json").read_bytes())
        result = air.inspect_record(target, "harvest.json", pin)
        self.assertEqual(result["files"], len(rows) + 1)

    def test_ssd_p1_native_closed_manifest_works_without_reauthoring(self):
        rows = self.rows()
        (self.record / "manifest.json").unlink()
        manifest = {"schema": "joulewise.ssd_closed_record.v1", "state": "closed",
                    "window_id": "synthetic-window", "files": {key: row["sha256"] for key, row in rows.items()}}
        air.save(self.record / "ssd-closed.json", manifest)
        pin = air.sha((self.record / "ssd-closed.json").read_bytes())
        self.gate["record_manifest_sha256"] = pin
        air.save(self.gate_path, self.gate)
        result = self.push(manifest="ssd-closed.json", manifest_sha256=pin)
        self.assertEqual(result["status"], "retained")
        self.assertEqual(result["receipt"]["summary"]["files"], len(rows) + 1)

    def test_real_receiver_entrypoint_with_only_synthetic_local_inputs(self):
        self.push()
        challenge = "a" * 32
        result = subprocess.run([sys.executable, "-B", str(Path(air.__file__)), "serve",
            "--root", str(self.primary), "--rrsync", str(self.base / "not-executed-rrsync")],
            env={**os.environ, "SSH_ORIGINAL_COMMAND":
                 f"jw-air status {self.record_id} manifest.json {challenge}"},
            capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = air.decode(result.stdout)
        receipt = air.validate_receipt(value, self.config, challenge)
        self.assertEqual(len(receipt["copies"]), 1)

    def test_duplicate_manifest_keys_refuse(self):
        with self.assertRaisesRegex(air.Refusal, "duplicate"):
            air.decode(b'{"files":{},"files":{}}')

    def test_cli_refusal_reports_elapsed_without_contacting_network(self):
        air.save(self.gate_path, {**self.gate, "armed": True})
        c = self.config
        result = subprocess.run([sys.executable, "-B", str(Path(air.__file__)), "push",
            "--record", str(c.record), "--manifest-sha256", c.manifest_sha256,
            "--armed-state", str(c.armed_state), "--watchdog-state", str(c.watchdog_state),
            "--terminal", c.terminal, "--loop-lock", str(c.loop_lock), "--state-dir", str(c.state_dir),
            "--host", c.host, "--identity", str(c.identity), "--known-hosts", str(c.known_hosts),
            "--budget-s", "300", "--transfer-mbps", "50"], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertGreaterEqual(json.loads(result.stderr)["elapsed_s"], 0)


class CommandTests(unittest.TestCase):
    def test_cancellable_runner_kills_its_local_process_group(self):
        # Local synthetic process only. The second check happens after spawn.
        checks = []
        def check():
            checks.append(True)
            if len(checks) > 1:
                raise air.Refusal("synthetic state transition")
        started = time.monotonic()
        with self.assertRaisesRegex(air.Refusal, "state transition"):
            air.run_command([sys.executable, "-c", "import time; time.sleep(30)"], timeout=2, check=check)
        self.assertLess(time.monotonic() - started, 2)

    def test_runner_enforces_command_timeout(self):
        with self.assertRaisesRegex(air.Refusal, "deadline"):
            air.run_command([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.02)

    def test_timeout_kills_grandchild_even_after_direct_child_has_exited(self):
        script = ("import subprocess,sys; subprocess.Popen([sys.executable, '-c', "
                  "'import time; time.sleep(3)'])")
        started = time.monotonic()
        with self.assertRaisesRegex(air.Refusal, "deadline"):
            air.run_command([sys.executable, "-c", script], timeout=0.1)
        self.assertLess(time.monotonic() - started, 1)


if __name__ == "__main__":
    unittest.main()
