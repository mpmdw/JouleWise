"""The ALIGN v4 R1 arm route (Opus build): a ruled, chain-bound DIAGNOSTIC_NO_PACK night.

Unit checks pin the registration, the payload kind, the sizing (RUN_STATE
items 215/216), the wrapper and the installer/probe refusals. The end-to-end
cases run the REAL run_night driver and the REAL night gate on a generated
plan; the gate's host probes are tests.test_run_night's ProbeSource and the
derivation admission is its existing stub. The chain is real: run_night
launches the generated wrapper under its census and deadline, the wrapper runs
the unchanged R1 zsh chain, which runs the unchanged R1 driver, which runs the
WP15 runtime as subprocesses on the synthetic backend (no MLX, no hardware).
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import night_gate
from joulewise.night_kinds import NIGHT_KINDS, kind_row
from scripts import write_align_r1_night as r1night
from tests import test_run_night as rn
from tests.align import r1_synthetic as rs

REPO = Path(__file__).resolve().parents[2]
TMP = os.environ.get("TMPDIR")
REGISTRATION = REPO / "configs/align/v4/r1_night_registration.json"
CHAIN = REPO / "scripts/night_chains/align_r1_rehearsal.zsh"
# Before the custody cutoff, so the synthetic measurement root need not sit
# under /Users/edr/night-custody/measurement (a production-only rule).
T0 = datetime(2026, 9, 2, 1, 0).timestamp()


class RegistrationAndKindTests(unittest.TestCase):
    def test_registration_is_ruled_and_binds_the_unchanged_r1_chain(self):
        raw = REGISTRATION.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(digest, night_gate.ALIGN_V4_R1_REGISTRATION_SHA256)
        entry = night_gate.armable_registration(digest)
        self.assertIsNotNone(entry)
        self.assertTrue(entry["binds_chain"])
        value = json.loads(raw)
        self.assertEqual(value["chain_source_sha256"], hashlib.sha256(CHAIN.read_bytes()).hexdigest())
        self.assertEqual(value["chain_source_path"], kind_row("align_v4_r1").chain_source_path)
        self.assertEqual(value["ac_powermode"], 0)
        self.assertEqual(value["sizing"]["r1_floor_s"], 96427)        # item 216
        self.assertEqual(value["sizing"]["batch_encounter_s"], 11164)  # items 214-216

    def test_kind_row_authenticates_the_chain_and_needs_the_bound_registration(self):
        row = NIGHT_KINDS["align_v4_r1"]
        self.assertTrue(row.payload_kind)
        self.assertTrue(row.authenticate_chain_source)
        self.assertTrue(row.requires_chain_bound_registration)
        self.assertEqual(row.receipt_class, "DIAGNOSTIC_NO_PACK")
        self.assertEqual(row.protocol_path, "configs/align/v4/r1_night_registration.json")
        self.assertEqual(row.generator_script, "scripts/write_align_r1_night.py")


class SizingTests(unittest.TestCase):
    def sizing(self):
        return json.loads(REGISTRATION.read_text())["sizing"]

    def local(self, hour, minute=0):
        return datetime(2026, 11, 8, hour, minute, tzinfo=r1night.BATCH_ZONE).timestamp()

    def test_the_batch_clock_is_the_r1_drivers(self):
        from scripts import align_r1_rehearsal as r1
        self.assertEqual(r1night.BATCH_ZONE, r1.LOCAL_ZONE)
        self.assertEqual(r1night.BATCH_WINDOW_START, r1.OS_BATCH_WINDOW_LOCAL[0])

    def test_one_crossing_is_the_redo_floor_plus_route_allowances(self):
        sized = r1night.size_window(self.local(14), self.sizing())
        # 96,427 + 3,000 + 300 + 30 + 600 + 1,800 + 120 = 102,277 -> whole minute.
        self.assertEqual(sized["window_max_s"], 102300)
        self.assertEqual(sized["batch_window_crossings"], 1)
        self.assertEqual(sized["extra_batch_encounters"], 0)
        self.assertEqual(sized["programmed_span_s"], 102300 - 3000)
        self.assertGreaterEqual(sized["window_max_s"], 96427)

    def test_a_second_local_1145_adds_one_encounter(self):
        sized = r1night.size_window(self.local(9), self.sizing())
        self.assertEqual(sized["batch_window_crossings"], 2)
        self.assertEqual(sized["extra_batch_encounters"], 1)
        self.assertEqual(sized["window_max_s"], 60 * -(-(102277 + 11164) // 60))

    def test_the_sizing_never_falls_below_the_floor_at_any_start_minute(self):
        for hour in range(24):
            sized = r1night.size_window(self.local(hour, 30), self.sizing())
            self.assertGreaterEqual(sized["window_max_s"] - 3000 - 300 - 30 - 600 - 1800 - 120,
                                    96427 + 11164 * sized["extra_batch_encounters"], hour)


class WrapperAndInstallTests(unittest.TestCase):
    def render(self):
        return r1night.render_wrapper(plan_id="align-v4-r1-x", chain_source_sha256="a" * 64,
                                      programmed_span_s=99300, display_dwell_s=300).decode()

    def test_wrapper_literals_are_what_the_gate_reads(self):
        text = self.render()
        self.assertEqual(night_gate.probe_payload_kind(text), "align_v4_r1")
        self.assertEqual(night_gate.chain_literal(text, "EVIDENCE_CHAIN_SOURCE_SHA256"), "a" * 64)
        self.assertEqual(night_gate.chain_literal(text, "NIGHT_PROGRAMMED_SPAN_S"), "99300")
        self.assertIn('/bin/zsh "$SOURCE"', text)
        self.assertIn("scripts/km003c_monitor.py", text)
        self.assertIn("displaysleepnow", text)

    def test_wrapper_refuses_both_installer_inspection_modes_without_running_anything(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            chain = Path(td) / "chain.zsh"
            chain.write_text(self.render())
            for name in ("NIGHT_VERIFY_ONLY", "NIGHT_RESERVATION_ARGV_ONLY"):
                env = dict(os.environ, **{name: "1"}, NIGHT_DIR=td, MEASUREMENT_ROOT=td, PY="/usr/bin/false")
                proc = subprocess.run(["/bin/zsh", str(chain)], env=env, capture_output=True, text=True)
                self.assertEqual(proc.returncode, r1night.EXIT_INSPECTION_REFUSED)
                self.assertFalse((Path(td) / "r1_wrapper.jsonl").exists())

    def test_probe_worker_never_executes_an_r1_chain(self):
        driver = rn._load_driver()
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            chain = root / "chain.zsh"
            chain.write_text(self.render())
            plan = mock.Mock(chain_path=str(chain), plan_id="p", measurement_head="f" * 40)
            with mock.patch.object(driver, "_load_plan", return_value=plan), \
                    mock.patch.object(driver.subprocess, "Popen") as popen:
                code = driver._probe_worker(root / "plan.json", root / "receipt.json", root / "progress.json",
                                            1e18)
            popen.assert_not_called()
            self.assertEqual(code, 2)
            self.assertEqual(json.loads((root / "receipt.json").read_text())["refusal_code"],
                             "align_v4_r1_chain_never_probed")

    def test_installer_never_requires_or_runs_a_probe_for_an_r1_chain(self):
        from joulewise import night_agent_install as install
        self.assertTrue(install.never_probed_payload(self.render()))
        self.assertFalse(install.never_probed_payload("export NIGHT_PROGRAMMED_SPAN_S=1\n"))


class _Synthetic(unittest.TestCase):
    """A synthetic measurement checkout around the real R1 chain, driver and runtime."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.measurement = self.root / "measurement"
        chains = self.measurement / "scripts/night_chains"
        chains.mkdir(parents=True)
        shutil.copyfile(CHAIN, chains / CHAIN.name)
        for name in ("align_r1_rehearsal.py", "km003c_monitor.py"):
            (self.measurement / "scripts" / name).symlink_to(REPO / "scripts" / name)
        (self.measurement / "configs/align/v4").mkdir(parents=True)
        shutil.copyfile(REGISTRATION, self.measurement / r1night.REGISTRATION_PATH)
        venv = self.measurement / ".venv/bin"
        venv.mkdir(parents=True)
        (venv / "python").write_text(f"#!/bin/sh\nexec {sys.executable} -B "
                                     f"{REPO / 'tests/align/r1_arm_bootstrap.py'} \"$@\"\n")
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        # The R1 chain's own sudo calls (sudo -n -l and its Automatic restore).
        (bin_dir / "sudo").write_text("#!/bin/sh\nif [ \"$2\" = -l ]; then\n"
                                      "echo '(root) NOPASSWD: /usr/bin/pmset -c powermode 0'\n"
                                      "echo '(root) NOPASSWD: /usr/bin/pmset -c powermode 2'\nfi\nexit 0\n")
        self.pmset_log = self.root / "pmset.log"
        (bin_dir / "pmset").write_text(f"#!/bin/sh\necho \"$@\" >> {self.pmset_log}\n")
        for path in (venv / "python", bin_dir / "sudo", bin_dir / "pmset"):
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        mode_file = self.root / "ac_powermode"
        mode_file.write_text("0")
        config = rs.synthetic_config(self.root / "cfg", powermode_file=str(mode_file))
        inputs = self.root / "inputs.json"
        inputs.write_text(json.dumps({"WP15": {"runtime_entrypoint": [
            "scripts/align_r1_runtime.py", "--config", str(config)]}}))
        self.world_file = self.root / "world.json"
        env = mock.patch.dict(os.environ, {
            "PATH": f"{bin_dir}:{os.environ['PATH']}", "ALIGN_R1_INPUTS": str(inputs),
            "R1_ARM_TEST_MODE_FILE": str(mode_file), "R1_ARM_TEST_WORLD": str(self.world_file),
            "JOULEWISE_HOST_STATE_DIR": str(self.root / "host-power")})
        env.start()
        self.addCleanup(env.stop)
        self.custody = self.root / "custody"
        record = r1night.write(self.measurement, self.custody, T0, repo_head=rn.HEAD,
                               measurement_head=rn.HEAD, now=lambda: T0 - 600,
                               pmset_bin=str(bin_dir / "pmset"), display_dwell_s=1)
        self.plan_path = Path(record["plan"]["path"])
        self.record = record
        self.driver = rn._load_driver()
        self.source = rn.ProbeSource(T0 + 1, str(self.measurement))
        self.source.plan_path = self.plan_path
        show = ("/usr/bin/git", "-C", str(self.measurement), "show", f"{rn.HEAD}:{r1night.CHAIN_SOURCE_PATH}")
        self.source.results[show] = rn._probe(show, stdout=CHAIN.read_text())
        courier = self.root / "claude"
        courier.write_text("#!/bin/zsh\nexit 0\n")
        courier.chmod(0o755)
        for target, value in (("make_probes", self.source.probes()),
                              ("_resolve_courier_bin", (courier, None, None))):
            patcher = mock.patch.object(self.driver, target, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.driver._durable_record = mock.Mock(return_value=None)
        self.driver.run_courier = mock.Mock(return_value={"attempted": 1, "sent": True,
                                                          "heartbeat_seen": True, "last_error": None})
        identity = mock.patch.object(self.driver, "observe_identity",
                                     return_value=rn.Identity("LIVE", "Tue Sep 8 01:02:03 2026"))
        identity.start()
        self.addCleanup(identity.stop)

    def night(self, name):
        return json.loads((self.custody / "night" / name).read_text())


class EndToEndTests(_Synthetic):
    def test_synthetic_r1_night_runs_through_the_real_gate_driver_and_chain(self):
        code = self.driver.run_night(self.plan_path)
        result = self.night("result.json")
        receipt = self.night("receipt.json")
        self.assertEqual(receipt["verdict"], "GO", receipt.get("refusal"))
        conditions = {row["condition_id"]: row for row in receipt["conditions"]}
        self.assertEqual(conditions["C1"]["measured"]["registration_sha256"],
                         night_gate.ALIGN_V4_R1_REGISTRATION_SHA256)
        self.assertEqual(conditions["C5"]["measured"]["payload_kind"], "align_v4_r1")
        self.assertEqual(conditions["C5"]["measured"]["chain_source_sha256"],
                         hashlib.sha256(CHAIN.read_bytes()).hexdigest())
        r1_result = self.night("align-r1/r1_result.json")
        self.assertEqual(r1_result["status"], "complete", r1_result.get("error"))
        self.assertEqual((code, result["verdict"], result["chain_exit_code"]), (0, "GO", 0))
        slots = self.night("align-r1/r1_slots.json")
        self.assertEqual(slots["source"], "R1 synthetic rehearsal")
        # The R1 driver ran its own ruling 20 census and ended in Automatic.
        self.assertTrue(r1_result["external_volumes"])
        self.assertEqual(json.loads(self.world_file.read_text())["mode"], 0)
        # The wrapper: display asleep, the meter streamed and was stopped cleanly.
        events = [json.loads(line) for line in (self.custody / "night/r1_wrapper.jsonl").read_text().splitlines()]
        names = [e["event"] for e in events]
        self.assertEqual(names[0], "start")
        self.assertLess(names.index("displaysleepnow"), names.index("r1_chain_exit"))
        self.assertEqual([e for e in events if e["event"] == "displaysleepnow"][0]["rc"], 0)
        self.assertIn("displaysleepnow", self.pmset_log.read_text())
        self.assertEqual([e for e in events if e["event"] == "meter_stop"][0]["forced"], False)
        streams = sorted((self.custody / "hazards/meter").glob("stream-*.jsonl"))
        self.assertEqual(len(streams), 1)
        lines = [json.loads(line) for line in streams[0].read_text().splitlines()]
        self.assertEqual((lines[0]["k"], lines[-1]["k"], lines[-1]["stop"]), ("h", "t", "stop_file"))
        self.assertGreater(len(lines), 2)
        # The chain ran exactly once, under the driver's census and deadline.
        started = json.loads((self.custody / "night/chain.started").read_text())
        self.assertIsInstance(started["pgid"], int)
        self.assertGreaterEqual(result["census_count"], 1)

    def test_a_changed_registration_refuses_before_the_chain_is_claimed(self):
        target = self.measurement / r1night.REGISTRATION_PATH
        target.write_text(target.read_text().replace('"display_dwell_s": 300', '"display_dwell_s": 299'))
        code = self.driver.run_night(self.plan_path)
        receipt = self.night("receipt.json")
        self.assertEqual(receipt["refusal"]["reason"], "night_refused_registration")
        self.assertEqual(code, self.driver.EXIT_REFUSED)
        self.assertFalse((self.custody / "night/chain.started").exists())

    def test_a_changed_r1_chain_refuses_at_c5(self):
        source = self.measurement / r1night.CHAIN_SOURCE_PATH
        source.write_text(source.read_text() + "\n# drift\n")
        code = self.driver.run_night(self.plan_path)
        receipt = self.night("receipt.json")
        self.assertEqual(receipt["refusal"]["reason"], "night_chain_digest_mismatch")
        self.assertEqual(code, self.driver.EXIT_REFUSED)
        self.assertFalse((self.custody / "night/chain.started").exists())

    def test_desk_check_passes_the_static_gates_without_launching(self):
        verdict = r1night.check(self.plan_path, probes=self.source.probes())
        self.assertEqual(verdict["verdict"], "STATIC_PASS", verdict)
        self.assertEqual(verdict["conditions"], {"C1": "PASS", "C5": "PASS"})
        self.assertFalse((self.custody / "night").exists())

    def test_generator_refuses_reused_custody_and_a_past_t0(self):
        with self.assertRaisesRegex(r1night.R1NightError, "absent or empty"):
            r1night.write(self.measurement, self.custody, T0, repo_head=rn.HEAD, measurement_head=rn.HEAD,
                          now=lambda: T0 - 600)
        with self.assertRaisesRegex(r1night.R1NightError, "future"):
            r1night.write(self.measurement, self.root / "c2", T0, repo_head=rn.HEAD, measurement_head=rn.HEAD,
                          now=lambda: T0 + 1)


if __name__ == "__main__":
    unittest.main()
