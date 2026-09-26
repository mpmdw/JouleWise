"""Focused driver tests against the real night-gate module."""

from __future__ import annotations

import hashlib
import inspect
import io
import importlib.util
import json
import math
import os
import plistlib
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from datetime import date, datetime
from contextlib import ExitStack, redirect_stdout
import dataclasses
from dataclasses import replace
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

from joulewise.measurement_liveness import Identity
from joulewise import calibration_ledger, night_gate
from joulewise.night_plan_writer import write_night_plan
from tests.git_fixture import init_git_fixture


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_night.py"
HEAD = "f" * 40
BOOT_UUID = "12345678-1234-5678-9234-567812345678"


def _probe(
    argv: tuple[str, ...],
    *,
    exit_code: int = 0,
    stdout: str = "",
    stderr: str = "",
    monotonic_ns: int = 10,
) -> night_gate.ProbeResult:
    return night_gate.ProbeResult(argv, exit_code, stdout, stderr, monotonic_ns)


def _green_results() -> dict[tuple[str, ...], night_gate.ProbeResult]:
    return {
        night_gate.IOREG_BATTERY_ARGV: _probe(
            night_gate.IOREG_BATTERY_ARGV,
            stdout=(REPO_ROOT / "tests/fixtures/battery_float/float.ioreg").read_text(),
        ),
        night_gate.HID_IDLE_ARGV: _probe(night_gate.HID_IDLE_ARGV, stdout="0\n"),
        night_gate.PMSET_BATT_ARGV: _probe(
            night_gate.PMSET_BATT_ARGV, stdout="Now drawing from 'AC Power'\n"
        ),
        night_gate.PMSET_GENERAL_ARGV: _probe(
            night_gate.PMSET_GENERAL_ARGV,
            stdout="System-wide power settings:\n displaysleep 0\n sleep 0\n",
        ),
        night_gate.LOAD_AVG_ARGV: _probe(
            night_gate.LOAD_AVG_ARGV, stdout="{ 0.75 0.63 0.58 }\n"
        ),
        night_gate.THERMAL_ARGV: _probe(
            night_gate.THERMAL_ARGV,
            stdout="Note: No thermal warning level has been recorded\n",
        ),
        night_gate.BOOT_SESSION_ARGV: _probe(
            night_gate.BOOT_SESSION_ARGV, stdout=BOOT_UUID + "\n"
        ),
    }


def _init_git_repo(root: Path) -> str:
    root.mkdir(parents=True)
    init_git_fixture(root, "-q")
    marker = root / "measurement.txt"
    marker.write_text("initial\n", encoding="utf-8")
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", marker.name], check=True)
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=JouleWise Test",
            "-c",
            "user.email=joulewise-test@example.invalid",
            "commit",
            "-qm",
            "initial",
        ],
        check=True,
    )
    return subprocess.check_output(
        ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def make_probe_fixture(root: Path, plan_path: Path, *, mode="ok") -> None:
    """Fake seat A at its CLI boundary; never import its implementation."""
    import shlex
    plan = json.loads(plan_path.read_text())
    measurement = Path(plan["measurement_root"])
    scripts = measurement / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    chain = scripts / "night_chains/calibration_derivation_only.zsh"
    chain.parent.mkdir(exist_ok=True)
    shutil.copyfile(REPO_ROOT / "scripts/night_chains/calibration_derivation_only.zsh", chain)
    python = measurement / ".venv/bin/python"
    python.parent.mkdir(parents=True, exist_ok=True)
    if not python.exists():
        python.symlink_to(sys.executable)
    module = measurement / "joulewise"
    module.mkdir(exist_ok=True)
    for name in ("calibration_ledger.py", "calibration_custody_worker.py"):
        (module / name).write_text("# fake seat A code identity\n")
    for name in ("recover_calibration_ledger.py", "validate_powermetrics_fiducial.py"):
        (scripts / name).write_text("from pathlib import Path\nPath(__file__).with_suffix('.CALLED').touch()\nraise SystemExit(91)\n")
    # The installer binds the driver and the writer as well as the reservation;
    # the real measurement checkout always carries this file.
    (scripts / "run_night.py").write_text("# fake measurement-checkout driver\n")
    stub = scripts / "reserve_calibration_window_bracket.py"
    stub.write_text('''import argparse, hashlib, json, os, sys, time, subprocess
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--verify-only', action='store_true')
p.add_argument('--pre-reserve-strict', action='store_true')
p.add_argument('--custody-budget-s', type=float, required=True)
p.add_argument('--custody-deadline-epoch-s', type=float, required=True)
a, rest = p.parse_known_args()
root = Path(__file__).parents[1]
(root / 'reservation-argv.json').write_text(json.dumps(sys.argv[1:]))
mode = (root / 'stub-mode').read_text()
if mode == 'hang':
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    (root / 'stub-pids.json').write_text(json.dumps([os.getpid(), child.pid]))
    time.sleep(60)
if mode in ('refused', 'mismatch', 'malformed'):
    document = {'schema':'joulewise.calibration_refusal.v1',
        'code':'calibration_ledger_custody_timeout', 'exit_code':2,
        'phase':'reservation', 'plan_id':os.environ['JOULEWISE_NIGHT_PLAN_ID'],
        'session_id':'stub-session', 'existing_session':False,
        'ledger':{'path':str(root / 'ledger.jsonl'), 'head_sha256':'a'*64},
        'budget_s':a.custody_budget_s, 'elapsed_s':0.1, 'last_observation':None,
        'written_epoch_s':time.time(), 'pid':os.getpid(), 'detail':'governed read expired'}
    if mode == 'mismatch': document['plan_id'] = 'wrong-plan'
    path = Path(os.environ['JOULEWISE_CALIBRATION_REFUSAL_PATH'])
    path.write_text('{' if mode == 'malformed' else json.dumps(document))
    raise SystemExit(2)
if mode == 'no-document': raise SystemExit(2)
assert a.verify_only, 'capture would be attempted'
if a.pre_reserve_strict:
    print(json.dumps({'pre_reserve_readiness':'ready','frozen_plan':{},'custody_elapsed_s':0.1}))
code = ['scripts/reserve_calibration_window_bracket.py',
        'joulewise/calibration_ledger.py', 'joulewise/calibration_custody_worker.py']
print(json.dumps({'verify_only':'ok', 'ledger_head_sha256':'a'*64,
    'observations':38, 'custody_elapsed_s':0.1, 'custody_budget_s':a.custody_budget_s,
    'python':sys.executable, 'python_version':'.'.join(map(str,sys.version_info[:3])),
    'code_digests':{name:'sha256:'+hashlib.sha256((root/name).read_bytes()).hexdigest() for name in code}}))
''')
    (measurement / "stub-mode").write_text(mode)
    ledger = measurement / "ledger.jsonl"
    ledger.write_text(json.dumps({"receipt_digest": "a" * 64}) + "\n")
    pin = measurement / "head.json"
    pin.write_text(json.dumps({"head_digest": "a" * 64}))
    for name in ("frozen-plan.json", "identity.json", "t1.json"):
        (measurement / name).write_text("{}\n")
    exports = {"SESSION_ID": "stub-session", "WINDOW_ID": "window", "PLAN_ID": "frozen-plan",
               "PLAN_SHA256": "b" * 64, "PLAN": str(measurement / "frozen-plan.json"),
               "EVIDENCE_ROOT_ID": "stub-evidence", "RUNS_ROOT": str(measurement / "runs"),
               "WINDOW_CUSTODY_ROOT": str(root / "window"), "CALIBRATION_LEDGER": str(ledger),
               "LEDGER_HEAD_PIN": str(pin), "IDENTITY_EPOCH_JSON": str(measurement / "identity.json"),
               "T1_BINDINGS_JSON": str(measurement / "t1.json"),
               "WINDOW_END_EPOCH_S": str(int(plan["t0_epoch_s"] + plan["window_max_s"]))}
    wrapper = plan_path.parent / "probe-chain.zsh"
    wrapper.write_text("set -euo pipefail\n" + "\n".join(
        "export " + name + "=" + shlex.quote(value) for name, value in exports.items()) +
        "\nexec /bin/zsh " + shlex.quote(str(chain)) + " --slot-attempt-id stub\n")
    sidecar = wrapper.with_suffix(".sha256")
    sidecar.write_text(hashlib.sha256(wrapper.read_bytes()).hexdigest() + "\n")
    plan.update(chain_path=str(wrapper), chain_sha256_path=str(sidecar))
    plan_path.write_text(json.dumps(plan) + "\n")


def write_matching_probe_receipt(plan_path, python=sys.executable, *, now=None):
    # Fixture-owned oracle: do not depend on the new installer API. In
    # particular, the missing-receipt regression must reach the old installer's
    # real admission path when these tests are copied to the base revision.
    plan = json.loads(plan_path.read_text())
    root = Path(plan["measurement_root"])
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    def identity(executable):
        code = ("import json,sys; print(json.dumps([sys.executable,"
                "'.'.join(map(str,sys.version_info[:3]))]))")
        path, version = json.loads(subprocess.check_output([str(executable), "-B", "-c", code], text=True))
        return {"path": path, "version": version, "sha256": digest(path)}
    code_paths = ("scripts/reserve_calibration_window_bracket.py",
                  "scripts/validate_powermetrics_fiducial.py", "scripts/run_night.py",
                  "joulewise/calibration_ledger.py", "joulewise/calibration_custody_worker.py")
    stamp = time.time() if now is None else now
    from joulewise import night_agent_install
    from scripts import run_night
    parsed_plan = night_gate.NightPlan.from_mapping(plan)
    fixture_root = (plan_path.parent.parent if plan_path.parent.name.startswith("custody")
                    else plan_path.parent)
    courier = fixture_root / "bin/claude"
    try:
        fixture_schedule = run_night.schedule(parsed_plan)
    except night_gate.PlanError:
        # Malformed-calendar tests only need a receipt to reach the installer's
        # own timing refusal; these rendering fields are never consumed there.
        calendar = {"Month": 9, "Day": 25, "Hour": 22, "Minute": 0}
        fixture_schedule = {"night_calendar": calendar, "deadman_calendar": calendar}
    prepared = night_agent_install.Prepared(
        parsed_plan, plan_path.resolve(), REPO_ROOT, str(python),
        (REPO_ROOT / "configs/launchd/com.joulewise.night.plist.template").read_text(),
        str(courier.resolve()), str(courier.parent) + ":/usr/bin:/bin:/usr/sbin:/sbin",
        fixture_schedule, lambda _: [], 600)
    record = {"schema": "joulewise.night_probe_receipt.v2", "outcome": "ok", "refusal_code": None,
              "ProcessType": "Interactive",
              "launch_context": prepared.launch_context(),
              "cadence": {"median_ms": 132, "p95_ms": 132, "max_ms": 132, "count": 300,
                          "elapsed_s": 39.6, "bound_s": 55, "passed": True},
              "plan_id": plan["plan_id"], "plan_sha256": digest(plan_path),
              "measurement_head": plan["measurement_head"], "ledger_head_sha256": "a" * 64,
              "code_digests": {name: "sha256:" + digest(root / name) for name in code_paths},
              "input_digests": {str(p.absolute()): "sha256:" + digest(p) for p in
                  (plan_path.resolve(), root / "ledger.jsonl", root / "head.json", root / "frozen-plan.json",
                   root / "identity.json", root / "t1.json")},
              "driver_python": identity(python), "chain_python": identity(root / ".venv/bin/python"),
              "chain_sha256": digest(plan["chain_path"]),
              "chain_source_sha256": digest(root / "scripts/night_chains/calibration_derivation_only.zsh"),
              "ledger_sha256": digest(root / "ledger.jsonl"), "ledger_pin_sha256": digest(root / "head.json"),
              "custody_budget_s": 120.0, "custody_elapsed_s": 0.1, "observations": 38,
              "started_epoch_s": stamp - 1, "finished_epoch_s": stamp,
              "launchd_label": "com.joulewise.night-probe." + plan["plan_id"]}
    path = plan_path.parent / "night_probe_receipt.json"
    path.write_text(json.dumps(record))
    os.utime(path, (stamp, stamp))
    return path


class ProbeSource:
    def __init__(self, now_epoch_s: float, measurement_root: str = str(REPO_ROOT)) -> None:
        self.now_epoch_s = now_epoch_s
        self.measurement_root = measurement_root
        self.plan_path: Path | None = None
        self.results = _green_results()
        self.census_responses: list[night_gate.ProbeResult] = []
        self.monotonic_calls = 0

    def run(self, argv: tuple[str, ...]) -> night_gate.ProbeResult:
        if argv == night_gate.AGENT_CENSUS_ARGV:
            if self.census_responses:
                return self.census_responses.pop(0)
            return _probe(argv, exit_code=1)
        if argv[:4] == ("/usr/bin/git", "-c", "core.fsmonitor=false", "-C"):
            measurement_root = (json.loads(self.plan_path.read_text())["measurement_root"]
                                if self.plan_path is not None else self.measurement_root)
            if argv == ("/usr/bin/git", "-c", "core.fsmonitor=false", "-C",
                        measurement_root, "--no-optional-locks", "status",
                        "--porcelain=v1", "--untracked-files=all"):
                return _probe(argv)
        return self.results[argv]

    def monotonic_ns(self) -> int:
        self.monotonic_calls += 1
        return 99_000 + self.monotonic_calls

    def probes(self) -> night_gate.Probes:
        return night_gate.Probes(
            run=self.run,
            now_epoch_s=lambda: self.now_epoch_s,
            monotonic_ns=self.monotonic_ns,
            read_text=lambda path: Path(path).read_text(encoding="utf-8"),
            checkout_head=lambda: HEAD,
            measurement_head=lambda _root: HEAD,
        )


def _load_driver(script_path: Path = SCRIPT_PATH, module_name: str = "run_night_test_module"):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeProcess:
    def __init__(self, argv, return_code: int = 0, running_once: bool = False) -> None:
        self.argv = argv
        self.return_code = return_code
        self.running_once = running_once
        self.pid = 4242
        self.poll_count = 0

    def poll(self):
        self.poll_count += 1
        if self.running_once and self.poll_count == 1:
            return None
        return self.return_code

    def wait(self, timeout=None):
        return self.return_code


class UnkillableProcess(FakeProcess):
    def __init__(self, argv) -> None:
        super().__init__(argv)
        self.pid = 4343

    def poll(self):
        return None

    def wait(self, timeout=None):
        raise subprocess.TimeoutExpired(self.argv, timeout)


class NightDriverTests(unittest.TestCase):
    def test_production_battery_probe_uses_ten_second_timeout_only_for_ioreg(self):
        driver = _load_driver()
        from joulewise import battery_float
        observed = []

        def fake_run(argv, **kwargs):
            observed.append((tuple(argv), kwargs["timeout"]))
            return subprocess.CompletedProcess(argv, 0, "", "")

        with mock.patch.object(driver.subprocess, "run", side_effect=fake_run):
            driver._probe_runner(battery_float.IOREG_BATTERY_ARGV)
            driver._probe_runner(("/usr/bin/true",))
        self.assertEqual(observed, [
            (battery_float.IOREG_BATTERY_ARGV, battery_float.PROBE_TIMEOUT_S),
            (("/usr/bin/true",), driver.PROBE_TIMEOUT_S),
        ])

    def setUp(self) -> None:
        self.driver = _load_driver()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        identity_patch = mock.patch.object(
            self.driver, "observe_identity", return_value=Identity("LIVE", "Tue Sep 8 01:02:03 2026")
        )
        self.identity_mock = identity_patch.start()
        self.addCleanup(identity_patch.stop)
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.chain = self.root / "chain.zsh"
        self.chain.write_text("echo chain\n", encoding="utf-8")
        self.sidecar = self.root / "chain.zsh.sha256"
        # GNU shasum form, exactly what `gen_g2_phase_d.py --emit-chain` writes;
        # both the gate and the driver must read it.
        self.sidecar.write_text(
            hashlib.sha256(self.chain.read_bytes()).hexdigest() + "  chain.zsh\n",
            encoding="utf-8",
        )
        self.registration = self.root / "registration.json"
        self.registration.write_text((REPO_ROOT / night_gate.D166_REGISTRATION_PATH).read_text(), encoding="utf-8")
        self.t0_epoch_s = datetime(2026, 9, 2, 1, 0).timestamp()
        self.source = ProbeSource(self.t0_epoch_s + 1, str(self.root))
        self.plan_path = self.root / "plan.json"
        self._write_plan()
        self.source.plan_path = self.plan_path
        self.courier = self.root / "claude"
        self.courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        self.courier.chmod(0o755)
        self.registration_hash_patch = mock.patch.object(
            night_gate,
            "D166_REGISTRATION_SHA256",
            hashlib.sha256(self.registration.read_bytes()).hexdigest(),
        )
        self.registration_hash_patch.start()
        self.real_make_probes = self.driver.make_probes
        self.probes_patch = mock.patch.object(
            self.driver, "make_probes", return_value=self.source.probes()
        )
        self.probes_mock = self.probes_patch.start()
        self.real_resolve_courier_bin = self.driver._resolve_courier_bin
        self.resolve_patch = mock.patch.object(
            self.driver,
            "_resolve_courier_bin",
            return_value=(self.courier, None, None),
        )
        self.resolve_mock = self.resolve_patch.start()
        self.real_durable_record = self.driver._durable_record
        self.driver._durable_record = mock.Mock(return_value=None)
        self.real_run_courier = self.driver.run_courier
        self.sent_outcome = {
            "attempted": 1,
            "sent": True,
            "heartbeat_seen": True,
            "last_error": None,
        }
        # Mocking the entire courier also omits its lock-owned prelaunch publish.
        # Real courier publication and delivery are covered by the boundary tests.
        self.driver.run_courier = mock.Mock(return_value=self.sent_outcome)
        self.popen_kwargs = []

    def tearDown(self) -> None:
        self.probes_patch.stop()
        self.resolve_patch.stop()
        self.registration_hash_patch.stop()
        self.temporary.cleanup()

    def test_status_fake_only_cleans_planned_measurement_root(self) -> None:
        suffix = ("--no-optional-locks", "status", "--porcelain=v1",
                  "--untracked-files=all")
        prefix = ("/usr/bin/git", "-c", "core.fsmonitor=false", "-C")
        own = prefix + (str(self.root),) + suffix
        other = prefix + (str(self.root / "other"),) + suffix
        self.source.results[other] = _probe(other, stdout="?? unexpected.py\n")
        self.assertEqual("", self.source.run(own).stdout)
        self.assertEqual("?? unexpected.py\n", self.source.run(other).stdout)

    def _write_plan(
        self,
        *,
        t0_epoch_s: float | None = None,
        window_max_s: int = 60,
        receipt_class: str = "DIAGNOSTIC_NO_PACK",
    ) -> None:
        t0 = self.t0_epoch_s if t0_epoch_s is None else t0_epoch_s
        write_night_plan(
            self.plan_path,
            night_gate.NightPlan(
                plan_id="night-plan",
                receipt_class=receipt_class,
                t0_epoch_s=t0,
                window_max_s=window_max_s,
                authored_epoch_s=t0 - 1,
                repo_head=HEAD,
                measurement_root=str(self.root),
                measurement_head=HEAD,
                chain_path=str(self.chain),
                chain_sha256_path=str(self.sidecar),
                custody_root=str(self.custody),
                registration_path=str(self.registration),
            ),
        )

    def _run_calibration_stub(self, mode):
        import shlex
        make_probe_fixture(self.root, self.plan_path, mode=mode)
        plan = self.driver._load_plan(self.plan_path)
        # Exactly the same chain stimulus on the base: exit 2 plus a complete
        # seat-A document. Environment plumbing is tested independently below.
        chain = Path(plan.chain_path)
        chain.write_text("export JOULEWISE_NIGHT_PLAN_ID=" + shlex.quote(plan.plan_id) +
            "\nexport JOULEWISE_CALIBRATION_REFUSAL_PATH=" +
            shlex.quote(str(self.custody / "night/calibration-refusal.json")) +
            "\nexec " + shlex.quote(sys.executable) + " " +
            shlex.quote(str(self.root / "scripts/reserve_calibration_window_bracket.py")) +
            " --custody-budget-s 120 --custody-deadline-epoch-s 9999999999\n")
        Path(plan.chain_sha256_path).write_text(hashlib.sha256(chain.read_bytes()).hexdigest() + "\n")
        return self.driver.run_night(self.plan_path)

    def test_calibration_refusal_transports_to_result_and_courier(self):
        rc = self._run_calibration_stub("refused")
        result = json.loads((self.custody / "night/result.json").read_text())
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("night_calibration_refused", result["aborted_reason"])
        self.assertEqual(2, result["chain_exit_code"])
        self.assertEqual("calibration_ledger_custody_timeout", result["calibration_code"])
        payload = json.loads((self.custody / "night/calibration-refusal.json").read_text())
        self.assertEqual(payload, result["calibration_refusal"]["evidence"])
        self.assertIn("night/calibration-refusal.json", [a["path"] for a in result["artifacts"]])
        self.assertEqual(self.driver.EXIT_REFUSED, rc)
        self.driver.run_courier.assert_called_once()
        self.assertEqual(1, self.driver._durable_record.call_count)
        self.assertEqual(self.custody / "night", self.driver._durable_record.call_args.args[1])

    def test_driver_census_abort_keeps_precedence_over_calibration_document(self):
        payload = {"schema": "joulewise.calibration_refusal.v1", "plan_id": "night-plan",
                   "code": "calibration_ledger_custody_timeout", "exit_code": 2}
        def abort(*args, **kwargs):
            night = args[3]
            (night / "calibration-refusal.json").write_text(json.dumps(payload))
            return -15, {"reason": "night_aborted_agent_present", "detail": "census hit",
                         "evidence": {"pid": 123}}, 1, [], True
        with mock.patch.object(self.driver, "_run_chain_once", side_effect=abort):
            rc = self.driver.run_night(self.plan_path)
        result = json.loads((self.custody / "night/result.json").read_text())
        self.assertEqual(4, rc)
        self.assertEqual("ABORTED", result["verdict"])
        self.assertEqual("night_aborted_agent_present", result["aborted_reason"])
        self.assertEqual(-15, result["chain_exit_code"])
        self.assertEqual(payload, result["evidence"]["calibration_refusal"]["evidence"])
        self.assertIn("night/calibration-refusal.json", result["refusal_documents"])
        self.assertEqual("night_aborted_agent_present",
            json.loads((self.custody / "night/refusal.json").read_text())["refusal"]["reason"])
        self.driver.run_courier.assert_called_once()

    def test_calibration_document_exit_code_must_match_self_exit(self):
        def chain(*args, **kwargs):
            (args[3] / "calibration-refusal.json").write_text(json.dumps({
                "schema": "joulewise.calibration_refusal.v1", "plan_id": "night-plan",
                "code": "calibration_ledger_custody_timeout", "exit_code": 2}))
            return 7, None, 0, [], True
        with mock.patch.object(self.driver, "_run_chain_once", side_effect=chain):
            self.driver.run_night(self.plan_path)
        result = json.loads((self.custody / "night/result.json").read_text())
        self.assertEqual("document_invalid", result["calibration_refusal"]["detail"])
        self.assertEqual(7, result["chain_exit_code"])

    def test_calibration_refusal_plan_mismatch_is_document_invalid(self):
        self._run_calibration_stub("mismatch")
        result = json.loads((self.custody / "night/result.json").read_text())
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("document_invalid", result["calibration_refusal"]["detail"])
        self.assertEqual(2, result["chain_exit_code"])
        self.driver.run_courier.assert_called_once()

    def test_calibration_refusal_malformed_is_document_invalid(self):
        self._run_calibration_stub("malformed")
        result = json.loads((self.custody / "night/result.json").read_text())
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("document_invalid", result["calibration_refusal"]["detail"])

    def test_calibration_exit_two_without_document_keeps_chain_failure(self):
        rc = self._run_calibration_stub("no-document")
        result = json.loads((self.custody / "night/result.json").read_text())
        self.assertEqual("GO", result["verdict"])
        self.assertEqual(2, result["chain_exit_code"])
        self.assertEqual(self.driver.EXIT_CHAIN_FAILED, rc)

    def test_real_abort_command_refusal_reaches_the_driver_as_refused(self):
        """The night's own abort step, refusing, must not be read as a GO night.

        `abort_window_exhausted` in the chain runs the real
        `scripts/recover_calibration_ledger.py … abort-session`, and that CLI
        used to report its typed refusals on one stream only. The chain then
        exited 2 with no document, which this driver records as verdict GO with
        `chain_exit_code` 2 (the case above, still pinned for a chain that
        writes nothing). Here the real command refuses for a real reason, so a
        document must exist and the night must read REFUSED.
        """
        import shlex
        ledger_root = self.root / "abort-ledger"
        ledger_root.mkdir()
        plan = self.driver._load_plan(self.plan_path)
        chain = Path(plan.chain_path)
        chain.write_text(
            "export JOULEWISE_NIGHT_PLAN_ID=" + shlex.quote(plan.plan_id)
            + '\nexport JOULEWISE_CALIBRATION_REFUSAL_PATH="$NIGHT_DIR/calibration-refusal.json"'
            + "\nexport JOULEWISE_NIGHT_CUSTODY_BUDGET_S=3"
            + "\nexec " + shlex.quote(sys.executable) + " -B "
            + shlex.quote(str(REPO_ROOT / "scripts/recover_calibration_ledger.py"))
            + " --ledger " + shlex.quote(str(ledger_root / "ledger.jsonl"))
            + " --head-pin " + shlex.quote(str(ledger_root / "head.json"))
            + " abort-session --session-id night-session --plan "
            + shlex.quote(str(self.plan_path)) + " --reason window_exhausted\n")
        Path(plan.chain_sha256_path).write_text(
            hashlib.sha256(chain.read_bytes()).hexdigest() + "\n")
        rc = self.driver.run_night(self.plan_path)
        result = json.loads((self.custody / "night/result.json").read_text())
        document = json.loads((self.custody / "night/calibration-refusal.json").read_text())
        self.assertEqual("abort", document["phase"])
        self.assertEqual(2, document["exit_code"])
        self.assertEqual("night-plan", document["plan_id"])
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("night_calibration_refused", result["aborted_reason"])
        self.assertEqual(2, result["chain_exit_code"])
        self.assertEqual(document["code"], result["calibration_code"])
        self.assertEqual(document, result["calibration_refusal"]["evidence"])
        self.assertEqual(self.driver.EXIT_REFUSED, rc)
        self.driver.run_courier.assert_called_once()

    def test_deadman_then_calibration_refusal_preserves_both_paths(self):
        original = self.driver._run_chain_once
        def chain(*args, **kwargs):
            plan, night = args[1], args[3]
            self.driver._write_driver_refusal(night / "refusal.json", plan,
                "night_chain_alive", "dead-man observed live chain", {"pgid": 123})
            return original(*args, **kwargs)
        with mock.patch.object(self.driver, "_run_chain_once", side_effect=chain):
            self._run_calibration_stub("refused")
        night = self.custody / "night"
        first = json.loads((night / "refusal.json").read_text())
        second = json.loads((night / "refusal-01.json").read_text())
        self.assertEqual("night_chain_alive", first["refusal"]["reason"])
        self.assertEqual("night_calibration_refused", second["refusal"]["reason"])
        result = json.loads((night / "result.json").read_text())
        for path in ("night/refusal.json", "night/refusal-01.json"):
            self.assertIn(path, result["refusal_documents"])
            self.assertIn(path, [item["path"] for item in result["artifacts"]])
        self.driver.run_courier.assert_called_once()

    def test_gate_and_driver_refusal_writers_retry_existing_sequence(self):
        night = self.custody / "night"
        night.mkdir()
        (night / "refusal.json").write_text("first")
        (night / "refusal-01.json").write_text("second")
        receipt = types.SimpleNamespace(to_json_bytes=lambda: b'gate refusal')
        self.driver._write_gate_refusal(night / "refusal.json", receipt)
        self.driver._write_driver_refusal(night / "refusal.json", self.driver._load_plan(self.plan_path),
                                          "night_chain_alive", "still alive")
        self.assertEqual("first", (night / "refusal.json").read_text())
        self.assertEqual("second", (night / "refusal-01.json").read_text())
        self.assertEqual(b"gate refusal", (night / "refusal-02.json").read_bytes())
        self.assertEqual("night_chain_alive", json.loads((night / "refusal-03.json").read_text())["refusal"]["reason"])

    def test_preflight_emits_json_without_running_or_creating_custody(self) -> None:
        self.custody.rmdir()
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT_PATH), "preflight", "--plan", str(self.plan_path)],
            capture_output=True, text=True, check=False,
            env={"HOME": str(self.root), "PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stderr)
        self.assertEqual(1, len(completed.stdout.splitlines()))
        record = json.loads(completed.stdout)
        self.assertEqual("ok", record["preflight"])
        self.assertEqual(sys.executable, record["python"])
        self.assertEqual(".".join(map(str, sys.version_info[:3])), record["version"])
        self.assertEqual({
            "scripts.run_night",
            "joulewise.arm_readiness", "joulewise.arm_readiness_evidence_t0",
            "joulewise.t0_rehearsal", "joulewise.night_gate",
            "joulewise.measurement_liveness",
        }, set(record["modules"]))
        self.assertFalse(self.custody.exists())
        with redirect_stdout(io.StringIO()), \
             mock.patch.object(self.driver.subprocess, "Popen", side_effect=AssertionError("process in preflight")), \
             mock.patch.object(Path, "mkdir", side_effect=AssertionError("mkdir in preflight")):
            self.assertEqual(0, self.driver.main(["preflight", "--plan", str(self.plan_path)]))
        self.probes_mock.assert_not_called()

    def test_preflight_refuses_every_formerly_lazy_project_import(self) -> None:
        # Import hook runs in a fresh interpreter, so cached modules cannot
        # hide a missing dependency or leak this injection into other tests.
        harness = """
import builtins, runpy, sys
blocked, script, plan = sys.argv[1:]
original = builtins.__import__
def refusing_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == 'joulewise' and blocked in fromlist:
        raise ImportError('missing preflight dependency: ' + blocked)
    return original(name, globals, locals, fromlist, level)
builtins.__import__ = refusing_import
sys.argv = [script, 'preflight', '--plan', plan]
runpy.run_path(script, run_name='__main__')
"""
        for name in ("arm_readiness", "arm_readiness_evidence_t0", "t0_rehearsal"):
            with self.subTest(module=name):
                completed = subprocess.run(
                    [sys.executable, "-B", "-c", harness, name,
                     str(SCRIPT_PATH), str(self.plan_path)],
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(f"ImportError: missing preflight dependency: {name}", completed.stderr)
                self.assertIn("Traceback", completed.stderr)
                self.assertNotIn('"preflight": "ok"', completed.stdout)

    def test_minimum_python_matches_project_requires_python(self) -> None:
        import tomllib
        metadata = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
        floor = metadata["project"]["requires-python"].removeprefix(">=")
        self.assertEqual(tuple(map(int, floor.split("."))), self.driver.MIN_PYTHON)

    def _popen_recorder(self, return_code: int = 0, running_once: bool = False):
        calls = []

        def spawn(argv, *args, **kwargs):
            calls.append(argv)
            self.popen_kwargs.append(kwargs)
            return FakeProcess(argv, return_code, running_once)

        return calls, spawn

    def _run_night(self, *, return_code: int = 0, rehearsal: bool = False):
        calls, spawn = self._popen_recorder(return_code=return_code)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            exit_code = self.driver.run_night(self.plan_path, rehearsal=rehearsal)
        return exit_code, calls

    def test_refusal_writes_receipt_and_refusal_without_spawning_chain(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n")
        ]
        exit_code, calls = self._run_night()
        night = self.custody / "night"
        self.assertEqual(exit_code, 3)
        self.assertTrue((night / "receipt.json").is_file())
        self.assertTrue((night / "refusal.json").is_file())
        self.assertEqual(calls, [])

    def test_real_idle_agent_hit_refuses_without_chain_or_pack_authoring(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="20 claude\n")
        ]
        events = []
        original_run = self.source.run
        def probe(argv):
            events.append(tuple(argv))
            return original_run(argv)
        original_read = Path.read_bytes
        def read(path):
            if path == self.plan_path.resolve():
                events.append("plan")
            return original_read(path)
        self.probes_mock.return_value = replace(self.source.probes(), run=probe)
        with mock.patch.object(Path, "read_bytes", read), \
             mock.patch.object(self.driver, "_prepare_pack_night") as prepare, \
             mock.patch.object(self.driver, "_author_pack_arm") as author:
            code, calls = self._run_night()
        self.assertEqual(3, code)
        self.assertEqual([], calls)
        prepare.assert_not_called()
        author.assert_not_called()
        self.assertEqual(("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3"), events[0])
        night = self.custody / "night"
        for name in ("receipt.json", "refusal.json"):
            record = json.loads((night / name).read_text())
            self.assertEqual("night_refused_agent_present", record["refusal"]["reason"])
            self.assertEqual("20 claude\n", record["refusal"]["evidence"][0]["stdout"])
        result = json.loads((night / "result.json").read_text())
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("night_refused_agent_present", result["aborted_reason"])
        self.assertFalse((night / "go_receipt.json").exists())

    def test_go_spawns_chain_once_even_if_the_chain_fails(self) -> None:
        exit_code, calls = self._run_night(return_code=17)
        self.assertEqual(exit_code, 5)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        night = self.custody / "night"
        result = json.loads((night / "result.json").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(result["chain_exit_code"], 17)
        self.assertEqual(exited["exit_code"], 17)
        self.assertIn("epoch_s", exited)
        self.assertIn("monotonic_ns", exited)
        self.assertTrue(self.popen_kwargs[0]["start_new_session"])

    def test_gate_refusal_log_includes_reason_and_bounded_single_line_detail(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\nsecond\r\n" + "x" * 250)
        ]
        exit_code, calls = self._run_night()
        self.assertEqual(3, exit_code)
        self.assertEqual([], calls)
        receipt = json.loads((self.custody / "night" / "receipt.json").read_text())
        refusal = receipt["refusal"]
        expected_detail = " ".join(refusal["detail"].splitlines())[:200]
        self.assertEqual(200, len(expected_detail))
        messages = [
            line.split(" ", 1)[1]
            for line in (self.custody / "night.log").read_text().splitlines()
        ]
        self.assertEqual(
            [f"night gate verdict=REFUSED reason={refusal['reason']} detail={expected_detail}"],
            [message for message in messages if message.startswith("night gate verdict=")],
        )

    def test_non_refused_gate_log_keeps_exact_verdict_form(self) -> None:
        self._run_night()
        messages = [
            line.split(" ", 1)[1]
            for line in (self.custody / "night.log").read_text().splitlines()
        ]
        self.assertEqual(["night gate verdict=GO"],
                         [message for message in messages if message.startswith("night gate verdict=")])

    def test_stub_without_chain_files_logs_rehearsal_only(self) -> None:
        self._write_plan(receipt_class="REHEARSAL_STUB")
        self.chain.unlink()
        self.sidecar.unlink()
        exit_code, calls = self._run_night()
        self.assertEqual(self.driver.EXIT_REFUSED, exit_code)
        self.assertEqual([["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]], calls)
        receipt = json.loads((self.custody / "night" / "receipt.json").read_text())
        self.assertEqual("REHEARSAL_ONLY", receipt["verdict"])
        messages = [
            line.split(" ", 1)[1]
            for line in (self.custody / "night.log").read_text().splitlines()
        ]
        self.assertEqual(["night gate verdict=REHEARSAL_ONLY"],
                         [message for message in messages if message.startswith("night gate verdict=")])

    def test_counterfactual_inherited_coordinates_override_parsed_night_plan(self) -> None:
        parsed = night_gate.NightPlan.from_mapping(json.loads(self.plan_path.read_text()))
        parsed = replace(
            parsed,
            measurement_root=str(self.root / "measurement with spaces"),
            measurement_head="a" * 40,
        )
        write_night_plan(self.plan_path, parsed)
        self.probes_mock.return_value = replace(
            self.source.probes(), measurement_head=lambda _root: parsed.measurement_head
        )
        inherited = {
            "NIGHT_PLAN_ID": "stale-plan",
            "MEASUREMENT_ROOT": "/stale/measurement",
            "MEASUREMENT_HEAD": "b" * 40,
            "PY": "/stale/development/python",
        }
        with mock.patch.dict(os.environ, inherited):
            exit_code, calls = self._run_night()
            # The handoff changes only the child's environment.
            self.assertEqual({key: os.environ[key] for key in inherited}, inherited)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        environment = self.popen_kwargs[0]["env"]
        self.assertEqual(
            {key: environment.get(key) for key in inherited},
            {
                "NIGHT_PLAN_ID": parsed.plan_id,
                "MEASUREMENT_ROOT": parsed.measurement_root,
                "MEASUREMENT_HEAD": parsed.measurement_head,
                "PY": parsed.measurement_root + "/.venv/bin/python",
            },
        )

    def test_plan_supplies_coordinates_when_parent_exports_are_absent(self) -> None:
        keys = ("MEASUREMENT_ROOT", "MEASUREMENT_HEAD", "PY", "NIGHT_DIR",
                "JOULEWISE_NIGHT_PLAN_ID", "CUSTODY_BUDGET_S")
        parent = {key: value for key, value in os.environ.items() if key not in keys}
        with mock.patch.dict(os.environ, parent, clear=True):
            exit_code, calls = self._run_night()
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        environment = self.popen_kwargs[0]["env"]
        self.assertEqual(
            [environment.get(key) for key in keys],
            [str(self.root), HEAD, str(self.root) + "/.venv/bin/python",
             str(self.custody / "night"), "night-plan", "120"],
        )

    def test_chain_spawn_failure_records_refusal_and_finishes_reporting(self) -> None:
        self.driver._durable_record = self.real_durable_record
        run_argv = []

        def run_command(argv, **kwargs):
            run_argv.append(list(argv))
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        try:
            with mock.patch.object(
                self.driver.subprocess,
                "Popen",
                side_effect=FileNotFoundError("chain executable missing"),
            ), mock.patch.object(
                self.driver.subprocess, "run", side_effect=run_command
            ):
                exit_code = self.driver.run_night(self.plan_path)
        except FileNotFoundError as error:
            self.fail(f"chain launch failure escaped instead of becoming a refusal: {error}")

        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        started = json.loads((night / "chain.started").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        pushes = [argv for argv in run_argv if "push" in argv]
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["chain_launch_failed"]
        )
        self.assertEqual(self.driver.validate_refusal(refusal), [])
        self.assertIsNone(started["pid"])
        self.assertIsNone(started["pgid"])
        self.assertEqual(
            started["launch_error"],
            "FileNotFoundError: chain executable missing",
        )
        self.assertIsNone(exited["exit_code"])
        self.assertIs(exited["launch_failed"], True)
        self.driver.run_courier.assert_called_once()
        self.assertEqual(len(pushes), 1)

    def test_chain_identity_probe_follows_complete_closed_marker(self) -> None:
        from joulewise.measurement_liveness import census
        night = self.root / "claim-test" / "night"
        night.mkdir(parents=True)
        descriptor = self.driver._claim_chain_start(night)
        process = types.SimpleNamespace(pid=4242)
        class DriverKilled(BaseException):
            pass
        def killed_during_probe(pid):
            record = json.loads((night / "chain.started").read_text())
            self.assertEqual(set(record), {"pid", "pgid", "epoch_s"})
            self.assertEqual(record["pid"], pid)
            self.assertEqual(self.driver._read_started_pgid(night / "chain.started"), pid)
            with self.assertRaises(OSError):
                os.fstat(descriptor)
            raise DriverKilled()
        with mock.patch.object(self.driver, "observe_identity", side_effect=killed_during_probe):
            with self.assertRaises(DriverKilled):
                self.driver._complete_chain_start(descriptor, process, night)
        result = census(parents=[night.parent.parent], observer=lambda pid: Identity("DEAD"))
        self.assertFalse(result.clear)
        self.assertIn("indeterminate", result.refusals[0])
        self.assertFalse((night / "chain.exited").exists())
        self.assertEqual(self.driver._read_started_pgid(night / "chain.started"), 4242)

    def test_chain_identity_is_added_by_atomic_replace(self) -> None:
        night = self.root / "atomic-test"
        night.mkdir()
        descriptor = self.driver._claim_chain_start(night)
        process = types.SimpleNamespace(pid=4242)
        replace = os.replace
        def inspect_replace(source, target):
            self.assertEqual(source, night / "chain.started.tmp")
            self.assertEqual(target, night / "chain.started")
            before = json.loads(target.read_text())
            after = json.loads(source.read_text())
            self.assertEqual(set(before), {"pid", "pgid", "epoch_s"})
            self.assertEqual({k: after[k] for k in before}, before)
            self.assertEqual(after["start_time"], "Tue Sep 8 01:02:03 2026")
            replace(source, target)
        with mock.patch.object(self.driver.os, "replace", side_effect=inspect_replace) as swap:
            self.assertEqual(self.driver._complete_chain_start(descriptor, process, night), 4242)
        swap.assert_called_once()
        self.assertFalse((night / "chain.started.tmp").exists())
        self.assertEqual(json.loads((night / "chain.started").read_text())["start_time"],
                         "Tue Sep 8 01:02:03 2026")

    def test_chain_claim_prevents_a_second_spawn_after_a_failed_chain(self) -> None:
        calls, spawn = self._popen_recorder(return_code=17)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 5)
            self.assertEqual(self.driver.run_night(self.plan_path), 3)
        night = self.custody / "night"
        claim = json.loads((night / "chain.started").read_text())
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        self.assertEqual(set(claim), {"pid", "pgid", "epoch_s", "start_time"})
        self.assertEqual(claim["start_time"], "Tue Sep 8 01:02:03 2026")
        self.identity_mock.assert_called_once_with(claim["pid"])
        self.assertNotEqual(claim["pid"], os.getpid())
        # The first night already published result.json, so the second fire
        # records nothing at all: no authoritative refusal, no rerun sibling.
        self.assertEqual([], list(night.glob("refusal*.json")))
        self.assertEqual([], list(night.glob("rerun.refusal*.json")))

    def test_group_census_distinguishes_absence_from_failed_probes(self) -> None:
        argv = ["/usr/bin/pgrep", "-lf", "-g", "4242", "."]
        cases = (
            ("malformed", subprocess.CompletedProcess(
                argv, 2, stdout="", stderr="usage: pgrep ...\n"),
             (False, ["census_exit_2: usage: pgrep ..."])),
            ("timeout", subprocess.TimeoutExpired(argv, 0.25),
             (False, [f"census_failed: TimeoutExpired: Command '{argv}' "
                      "timed out after 0.25 seconds"])),
            ("permission", PermissionError("census denied"),
             (False, ["census_failed: PermissionError: census denied"])),
            ("live member", subprocess.CompletedProcess(
                argv, 0, stdout="6622 /bin/sleep 5\n", stderr=""),
             (False, ["6622 /bin/sleep 5"])),
            ("empty", subprocess.CompletedProcess(
                argv, 1, stdout="", stderr=""), (True, [])),
        )
        for label, outcome, expected in cases:
            with self.subTest(case=label), mock.patch.object(
                self.driver.subprocess, "run"
            ) as run:
                if isinstance(outcome, Exception):
                    run.side_effect = outcome
                else:
                    run.return_value = outcome
                self.assertEqual(expected, self.driver._group_census(4242, 0.25))
                run.assert_called_once_with(
                    argv, capture_output=True, text=True, timeout=0.25, check=False)

    def test_census_refusal_terminates_group_and_records_abort(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n"),
        ]
        calls, spawn = self._popen_recorder(running_once=True)
        # The group census runs a real /usr/bin/pgrep; with Popen mocked for
        # the chain it cannot also spawn that, so absence is stated here. The
        # census itself is proven against real process groups in
        # test_deadline_terminates_a_group_with_a_grandchild and its siblings.
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.os, "killpg"
        ) as kill_group, mock.patch.object(self.driver.time, "sleep"), mock.patch.object(
            self.driver, "_group_census", return_value=(True, [])
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 4)
        kill_group.assert_any_call(4242, self.driver.signal.SIGTERM)
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["aborted_agent_present"]
        )
        self.assertEqual(exited["exit_code"], 0)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def _run_with_peer_census(self, *, foreign_after_go=False):
        peer = "79146 " + " ".join(night_gate.AGENT_CENSUS_ARGV)
        census_calls = []

        def run(argv):
            if argv != night_gate.AGENT_CENSUS_ARGV:
                return self.source.run(argv)
            processes = [peer]
            if foreign_after_go and census_calls:
                processes.append("42 /usr/bin/claude -p inspect /usr/bin/pgrep")
            hits = [line for line in processes if re.search(argv[-1], line)]
            census_calls.append(argv)
            return _probe(argv, exit_code=0 if hits else 1,
                          stdout="".join(line + "\n" for line in hits))

        self.probes_mock.return_value = replace(self.source.probes(), run=run)
        _, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), \
             mock.patch.object(self.driver.os, "killpg") as kill_group, \
             mock.patch.object(self.driver.time, "sleep"), \
             mock.patch.object(self.driver, "_group_census", return_value=(True, [])), \
             mock.patch.object(self.driver, "_run_chain_once", wraps=self.driver._run_chain_once) as chain:
            code = self.driver.run_night(self.plan_path)
        result = json.loads((self.custody / "night/result.json").read_text())
        return code, result, chain, kill_group, census_calls

    def test_peer_census_reaches_and_completes_chain(self) -> None:
        """Old literal + peer-only argv refuses before run_night._run_chain_once."""
        code, result, chain, kill_group, censuses = self._run_with_peer_census()
        self.assertEqual(0, code, result)
        chain.assert_called_once()
        self.assertGreaterEqual(len(censuses), 2)  # admission AND running census
        kill_group.assert_not_called()
        self.assertIsNone(result["aborted_reason"])
        self.assertEqual([], result["census_hits"])

    def test_foreign_agent_alongside_peer_still_aborts_chain(self) -> None:
        """Foreign claude after GO must abort inside run_night._run_chain_once."""
        code, result, chain, kill_group, _ = self._run_with_peer_census(foreign_after_go=True)
        self.assertEqual(4, code, result)
        chain.assert_called_once()
        kill_group.assert_any_call(4242, self.driver.signal.SIGTERM)
        self.assertEqual("night_aborted_agent_present", result["aborted_reason"])
        self.assertEqual("42 /usr/bin/claude -p inspect /usr/bin/pgrep\n", result["census_hits"][0]["stdout"])

    def test_idle_agent_appearing_after_go_still_aborts_real_chain(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="20 claude\n"),
        ]
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), \
             mock.patch.object(self.driver.os, "killpg") as kill_group, \
             mock.patch.object(self.driver.time, "sleep"), \
             mock.patch.object(self.driver, "_group_census", return_value=(True, [])):
            self.assertEqual(4, self.driver.run_night(self.plan_path))
        kill_group.assert_any_call(4242, self.driver.signal.SIGTERM)
        self.assertEqual([["/bin/zsh", str(self.chain)]], calls)
        night = self.custody / "night"
        receipt = json.loads((night / "receipt.json").read_text())
        result = json.loads((night / "result.json").read_text())
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual("GO", receipt["verdict"])
        self.assertEqual("night_aborted_agent_present", result["aborted_reason"])
        self.assertEqual("night_aborted_agent_present", refusal["refusal"]["reason"])
        self.assertEqual("20 claude\n", result["census_hits"][0]["stdout"])
        self.assertEqual(["/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3"], result["census_hits"][0]["argv"])

    def test_courier_uses_one_launch_three_retries_and_every_backoff(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        calls, spawn = self._popen_recorder(running_once=True)
        sleeps = []
        old_deadline = self.driver.COURIER_DEADLINE_S
        self.driver.COURIER_DEADLINE_S = 0
        try:
            self.driver.run_courier = self.real_run_courier
            with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
                self.driver.os, "killpg"
            ), mock.patch.object(self.driver.time, "sleep", side_effect=sleeps.append):
                outcome = self.driver.run_courier(self.custody, plan, self.courier)
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline
        self.assertFalse(outcome["sent"])
        self.assertEqual(outcome["attempted"], 4)
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [60, 180, 600])
        self.assertEqual(self.driver.COURIER_BACKOFF_S, (60, 180, 600))
        self.assertTrue(all(item["cwd"] == REPO_ROOT for item in self.popen_kwargs))
        self.assertTrue(all(item["start_new_session"] for item in self.popen_kwargs))

    def test_dead_man_skips_when_courier_sent_exists(self) -> None:
        sent = self.custody / "night" / "courier.sent"
        sent.parent.mkdir()
        sent.write_text("sent\n", encoding="utf-8")
        self.assertEqual(self.driver.dead_man(self.plan_path), 0)
        self.driver.run_courier.assert_not_called()

    def test_dead_man_stands_down_immediately_after_t0_on_empty_night(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        entries_before = set(night.iterdir())
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=self.t0_epoch_s + 1
        ), mock.patch.object(self.driver.subprocess, "Popen") as spawn, mock.patch.object(
            self.driver.subprocess, "run"
        ) as run_command, mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(set(night.iterdir()), entries_before)
        self.assertEqual(set(self.custody.iterdir()), {night, self.custody / "night.log"})
        lines = (self.custody / "night.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn(f"completion epoch {int(completion_epoch_s)}; standing down", lines[0])
        spawn.assert_not_called()
        run_command.assert_not_called()
        kill_group.assert_not_called()
        self.resolve_mock.assert_not_called()
        self.driver.run_courier.assert_not_called()
        self.driver._durable_record.assert_not_called()

    def test_dead_man_stands_down_one_second_before_completion_epoch(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        entries_before = set(night.iterdir())
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s - 1
        ), mock.patch.object(self.driver.subprocess, "Popen") as spawn, mock.patch.object(
            self.driver.subprocess, "run"
        ) as run_command, mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(set(night.iterdir()), entries_before)
        self.assertEqual(set(self.custody.iterdir()), {night, self.custody / "night.log"})
        spawn.assert_not_called()
        run_command.assert_not_called()
        kill_group.assert_not_called()
        self.resolve_mock.assert_not_called()
        self.driver.run_courier.assert_not_called()
        self.driver._durable_record.assert_not_called()

    def test_dead_man_absent_marker_at_completion_epoch_couriers(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        plan = self.driver._load_plan(self.plan_path)
        with mock.patch.object(
            self.driver.time,
            "time",
            return_value=plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S,
        ):
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertTrue((night / "censuses.jsonl").is_file())
        self.driver.run_courier.assert_called_once()

    def test_dead_man_empty_start_marker_waits_until_completion_epoch(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text("", encoding="utf-8")
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(self.driver.subprocess, "Popen") as spawn, mock.patch.object(
            self.driver.subprocess, "run"
        ) as run_command, mock.patch.object(self.driver.os, "killpg") as kill_group, mock.patch.object(
            self.driver.time, "time", return_value=self.t0_epoch_s + 2
        ):
            early_exit = self.driver.dead_man(self.plan_path)
        self.assertEqual(early_exit, self.driver.EXIT_GO)
        self.assertFalse((night / "chain.exited").exists())
        self.driver.run_courier.assert_not_called()
        spawn.assert_not_called()
        run_command.assert_not_called()
        kill_group.assert_not_called()

        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as completion_kill_group:
            completion_exit = self.driver.dead_man(self.plan_path)
        self.assertEqual(completion_exit, self.driver.EXIT_GO)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertIs(exited["launch_failed"], True)
        self.driver.run_courier.assert_called_once()
        completion_kill_group.assert_not_called()

    def test_dead_man_couriers_after_an_empty_start_marker_without_killpg(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text("", encoding="utf-8")
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertIs(exited["launch_failed"], True)
        self.assertEqual(exited["reaped_by"], "dead-man")
        kill_group.assert_not_called()
        self.driver.run_courier.assert_called_once()

    def test_dead_man_couriers_after_a_null_pgid_marker_without_killpg(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text(
            json.dumps(
                {
                    "pid": None,
                    "pgid": None,
                    "epoch_s": time.time(),
                    "launch_error": "FileNotFoundError: missing",
                }
            ),
            encoding="utf-8",
        )
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertIs(exited["launch_failed"], True)
        self.assertEqual(exited["reaped_by"], "dead-man")
        kill_group.assert_not_called()
        self.driver.run_courier.assert_called_once()

    def test_overrun_refuses_before_the_gate_or_chain(self) -> None:
        t0_epoch_s = datetime(2026, 9, 2, 6, 50).timestamp()
        self._write_plan(t0_epoch_s=t0_epoch_s, window_max_s=3600)
        self.source.now_epoch_s = t0_epoch_s + 1
        gate_calls = []
        real_evaluate = self.driver.evaluate_night

        def record_evaluate(*args, **kwargs):
            gate_calls.append(args)
            return real_evaluate(*args, **kwargs)

        calls, spawn = self._popen_recorder()
        with mock.patch.object(
            self.driver, "deadman_epoch", return_value=t0_epoch_s + 3900
        ), mock.patch.object(
            self.driver, "evaluate_night", side_effect=record_evaluate
        ), mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 3)
        refusal = json.loads((self.custody / "night" / "refusal.json").read_text())
        detail = refusal["refusal"]["detail"]
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["plan_overruns_deadman"]
        )
        self.assertIn(f"t0_epoch_s={t0_epoch_s}", detail)
        self.assertIn("window_max_s=3600", detail)
        self.assertIn("deadman_epoch_s=", detail)
        self.assertNotIn("courier_backoff", detail)
        self.assertEqual(gate_calls, [])
        self.assertEqual(calls, [])

    def test_deadman_boundary_refuses_equality_and_allows_one_second_before(self) -> None:
        deadman_epoch_s = self.driver.deadman_epoch(self.driver._load_plan(self.plan_path))
        fixed_deadman = mock.patch.object(self.driver, "deadman_epoch", return_value=deadman_epoch_s)
        fixed_deadman.start()
        self.addCleanup(fixed_deadman.stop)
        equal_window_s = int(
            deadman_epoch_s - self.t0_epoch_s - self.driver.COURIER_DEADLINE_S
        )
        self.assertEqual(
            self.t0_epoch_s + equal_window_s + self.driver.COURIER_DEADLINE_S,
            deadman_epoch_s,
        )
        self._write_plan(window_max_s=equal_window_s)
        self.source.now_epoch_s = self.t0_epoch_s + 1
        calls, spawn = self._popen_recorder()
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            equal_exit = self.driver.run_night(self.plan_path)
        self.assertEqual(equal_exit, self.driver.EXIT_REFUSED)
        equal_refusal = json.loads(
            (self.custody / "night" / "refusal.json").read_text()
        )
        self.assertEqual(
            equal_refusal["refusal"]["reason"],
            self.driver._CODES["plan_overruns_deadman"],
        )
        self.assertEqual(calls, [])

        earlier_custody = self.root / "earlier-custody"
        earlier_plan = json.loads(self.plan_path.read_text())
        earlier_plan["window_max_s"] = equal_window_s - 1
        earlier_plan["custody_root"] = str(earlier_custody)
        self.plan_path.write_text(json.dumps(earlier_plan), encoding="utf-8")
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            earlier_exit = self.driver.run_night(self.plan_path)
        self.assertEqual(earlier_exit, self.driver.EXIT_GO)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def test_courier_backoffs_do_not_enter_the_overrun_predicate(self) -> None:
        t0_epoch_s = datetime(2026, 9, 2, 6, 45).timestamp()
        self._write_plan(t0_epoch_s=t0_epoch_s, window_max_s=60)
        self.source.now_epoch_s = t0_epoch_s + 1
        exit_code, calls = self._run_night()
        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def test_rehearsal_refuses_a_non_rehearsal_plan(self) -> None:
        exit_code, calls = self._run_night(rehearsal=True)
        self.assertEqual(exit_code, 3)
        self.assertEqual(calls, [])

    def test_clone_failure_does_not_change_a_go_exit_code(self) -> None:
        self.driver._durable_record = self.real_durable_record
        calls, spawn = self._popen_recorder()
        run_argv = []

        def fail_clone(argv, **kwargs):
            run_argv.append(list(argv))
            if argv[:3] == ["git", "clone", "--depth"]:
                raise OSError("clone unavailable")
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.subprocess, "run", side_effect=fail_clone
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        self.assertEqual(len(calls), 1)
        clones = [
            argv for argv in run_argv if argv[:3] == ["git", "clone", "--depth"]
        ]
        self.assertEqual(len(clones), 1)
        self.assertEqual(clones[0][:4], ["git", "clone", "--depth", "1"])
        self.assertEqual(clones[0][-1], str(self.custody / "results-clone"))

    def test_courier_argv_has_the_reviewed_shape(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        argv = self.driver._courier_argv(self.custody, plan, self.courier)
        self.assertEqual(argv[:2], (str(self.courier), "-p"))
        self.assertEqual(
            argv[-4:],
            ("--output-format", "text", "--allowedTools", self.driver.COURIER_ALLOWED_TOOLS),
        )
        self.assertIn(str(self.custody), argv[2])
        self.assertIn(plan.plan_id, argv[2])
        self.assertIn(str(REPO_ROOT / "docs" / "process" / "NIGHT_HANDBACK.md"), argv[2])
        self.assertIn("may not exist yet", argv[2])

    def test_courier_body_reads_watchdog_age_and_last_decision_directly(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        state_path = self.custody.parent / "magistrate" / "state.json"
        state_path.parent.mkdir()
        state_path.write_text(
            json.dumps({"state": "HOLD_UNSAFE", "reason": "plan malformed"})
            + "\n",
            encoding="utf-8",
        )
        os.utime(state_path, (1_000.0, 1_000.0))

        with mock.patch.object(self.driver.time, "time", return_value=1_901.25):
            argv = self.driver._courier_argv(self.custody, plan, self.courier)

        self.assertIn(f"Watchdog state path: {state_path}", argv[2])
        self.assertIn("Watchdog state age seconds: 901.250", argv[2])
        self.assertIn("Watchdog last decision: HOLD_UNSAFE", argv[2])
        self.assertIn("include these watchdog fields in the email body", argv[2])
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("from scripts import magistrate_watchdog", source)

    def test_launch_agent_template_disables_restart_and_installer_rejects_keepalive(self) -> None:
        template = (
            REPO_ROOT / "configs" / "launchd" / "com.joulewise.night.plist.template"
        ).read_text()
        installer = (REPO_ROOT / "scripts" / "install_night_agent.sh").read_text()
        self.assertIn("com.joulewise.night", template)
        self.assertIn("@@HOUR@@", template)
        self.assertIn("@@MINUTE@@", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.err", template)
        self.assertIn("<key>WorkingDirectory</key>\n  <string>@@REPO@@</string>", template)
        self.assertIn("<key>PATH</key>\n    <string>@@PATH@@</string>", template)
        self.assertIn("@@COURIER_BIN@@", template)
        self.assertNotIn("<key>KeepAlive</key>", template)
        self.assertIn("<key>RunAtLoad</key>\n  <false/>", template)
        root = self.root / "keepalive-install"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        driver = root / "driver"
        driver_head = _init_git_repo(driver)
        shutil.copytree(REPO_ROOT / "joulewise", driver / "joulewise",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(REPO_ROOT / "scripts", driver / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(REPO_ROOT / "tests/fixtures", driver / "tests/fixtures")
        bad_template = driver / "configs/launchd/com.joulewise.night.plist.template"
        bad_template.parent.mkdir(parents=True)
        bad_template.write_text(
            template.replace("<key>RunAtLoad</key>",
                             "<key>KeepAlive</key><true/>\n  <key>RunAtLoad</key>"),
            encoding="utf-8",
        )
        mapping = json.loads(plan.read_text())
        mapping["repo_head"] = driver_head
        plan.write_text(json.dumps(mapping), encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            '#!/bin/zsh\nprint -r -- "$*" >> "$LAUNCH_LOG"\nexit 0\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            ["/bin/zsh", str(driver / "scripts/install_night_agent.sh"),
             "--plan", str(plan), "--launchctl-bin", str(launcher)],
            env=environment, capture_output=True, text=True, check=False,
        )
        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertIn("template must not contain KeepAlive", completed.stderr)
        self.assertFalse((root / "home/Library/LaunchAgents").exists())
        self.assertFalse((root / "custody/night").exists())
        self.assertFalse(launch_log.exists())
        # The old assertion here checked that the SHELL ran `schedule --plan`, i.e.
        # that the installer derives its timing from the plan instead of hardcoding
        # it. That derivation moved into the engine in the transactional redesign.
        # A substring check on the engine source was tried and REMOVED: a delta
        # auditor showed it survives replacing the derivation with `schedule = {}`,
        # so it looked like coverage without being any. The property is covered
        # behaviourally, by execution, in:
        #   tests.test_run_night.test_schedule_subcommand_prints_calendar_fields_from_the_plan
        #   tests.test_install_night_agent.test_installer_derives_calendar_fields_from_plan_without_hour_flags
        # both of which fail if the derivation is removed.
        self.assertIn("@@MONTH@@", template)
        self.assertIn("@@DAY@@", template)
        self.assertNotIn("<integer>7</integer>", template)
        self.assertNotIn("<integer>7</integer>", installer)
        self.assertEqual(installer.count("sudo"), 0)

    def test_sidecar_digest_accepts_shasum_form_and_refuses_malformed_forms(self) -> None:
        # The seam with the gate: `gen_g2_phase_d.py --emit-chain` writes GNU
        # shasum form; the driver (and the gate) must read it, not bare hex
        # only.  Wrong basename / extra tokens / uppercase / empty refuse.
        digest = "ab" * 32
        self.assertEqual(self.driver._sidecar_digest(f"{digest}  chain.zsh\n", "chain.zsh"), digest)
        self.assertEqual(self.driver._sidecar_digest(f"{digest}\n", "chain.zsh"), digest)
        self.assertIsNone(self.driver._sidecar_digest(f"{digest}  other.zsh\n", "chain.zsh"))
        self.assertIsNone(self.driver._sidecar_digest(f"{digest}  a  b\n", "chain.zsh"))
        self.assertIsNone(self.driver._sidecar_digest(f"{digest.upper()}\n", "chain.zsh"))
        self.assertIsNone(self.driver._sidecar_digest("", "chain.zsh"))

    def test_driver_reason_codes_are_registered_and_are_not_literal_call_sites(self) -> None:
        registered = night_gate.NIGHT_GATE_REASON_CODES | night_gate.NIGHT_DRIVER_REASON_CODES
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        literal_lines = [
            line
            for line in source.splitlines()
            if '"night_' in line
            and "_CODES" not in line
            and 'startswith("night_")' not in line
            and '"night_calendar":' not in line  # schedule field, not a refusal code
        ]
        self.assertTrue(set(self.driver._CODES.values()) <= registered)
        self.assertEqual(literal_lines, [])

    def test_absolute_script_help_works_from_root_with_launchd_path(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            cwd="/",
            env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("unattended", completed.stdout)

    def test_missing_courier_is_a_durable_driver_refusal(self) -> None:
        self.resolve_mock.return_value = (None, "not executable", None)
        exit_code, calls = self._run_night()
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        outcome = json.loads((night / "courier.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        self.assertEqual(calls, [])
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["courier_unavailable"])
        self.assertEqual(outcome["attempted"], 0)
        self.assertFalse(outcome["sent"])
        self.assertEqual(self.driver._durable_record.call_count, 2)
        self.resolve_mock.assert_called_once()

    def test_courier_spawn_failure_records_outcome_and_second_publish(self) -> None:
        self.driver.run_courier = self.real_run_courier
        self.driver._durable_record = self.real_durable_record
        popen_argv = []
        run_argv = []

        def spawn(argv, *args, **kwargs):
            popen_argv.append(list(argv))
            if argv[0] == "/bin/zsh":
                return FakeProcess(argv)
            raise FileNotFoundError("courier vanished")

        def run_command(argv, **kwargs):
            run_argv.append(list(argv))
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        old_deadline = self.driver.COURIER_DEADLINE_S
        self.driver.COURIER_DEADLINE_S = 0
        try:
            # Pin the clock inside the night: the fixture's absolute t0 is a fixed
            # 2026-09-02 date, so its 07:00 local dead-man is in the past for any
            # real clock after that morning.
            with mock.patch.object(
                self.driver.subprocess, "Popen", side_effect=spawn
            ), mock.patch.object(
                self.driver.subprocess, "run", side_effect=run_command
            ), mock.patch.object(self.driver.time, "sleep"), mock.patch.object(
                self.driver.time, "time", return_value=self.t0_epoch_s + 1
            ):
                exit_code = self.driver.run_night(self.plan_path)
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline
        outcome = json.loads((self.custody / "night" / "courier.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        self.assertEqual(outcome["attempted"], 4)
        self.assertFalse(outcome["sent"])
        self.assertIn("courier vanished", outcome["last_error"])
        self.assertEqual(sum(argv[0] == str(self.courier) for argv in popen_argv), 4)
        pushes = [argv for argv in run_argv if "push" in argv]
        self.assertEqual(len(pushes), 2)
        self.assertTrue(all(argv[-1].startswith("HEAD:night-results/") for argv in pushes))

    def test_deleted_pinned_courier_falls_back_and_records_substitution(self) -> None:
        pinned = self.root / "versions" / "2.1.252"
        pinned.parent.mkdir()
        pinned.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        pinned.chmod(0o755)
        fallback = self.root / "bin" / "claude"
        fallback.parent.mkdir()
        fallback.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        fallback.chmod(0o755)
        pinned.unlink()

        calls, spawn = self._popen_recorder()
        self.resolve_mock.side_effect = self.real_resolve_courier_bin
        self.driver.run_courier = self.real_run_courier
        old_deadline = self.driver.COURIER_DEADLINE_S
        self.driver.COURIER_DEADLINE_S = 0
        try:
            with mock.patch.object(
                self.driver.shutil, "which", return_value=str(fallback)
            ), mock.patch.object(
                self.driver.subprocess, "Popen", side_effect=spawn
            ), mock.patch.object(self.driver.time, "sleep"), mock.patch.object(
                self.driver.time, "time", return_value=self.t0_epoch_s + 1
            ):
                exit_code = self.driver.run_night(self.plan_path, courier_bin=pinned)
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline

        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        courier_calls = [argv for argv in calls if argv[0] == str(fallback)]
        self.assertEqual(len(courier_calls), 4)
        self.assertFalse((self.custody / "night" / "refusal.json").exists())
        attempts = [
            json.loads(line)
            for line in (
                self.custody / "night" / "courier.attempts.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]
        expected_substitution = {"requested": str(pinned), "used": str(fallback)}
        self.assertTrue(attempts)
        self.assertTrue(
            all(
                attempt["courier_bin_substitution"] == expected_substitution
                for attempt in attempts
            )
        )
        night_log = (self.custody / "night.log").read_text(encoding="utf-8")
        self.assertIn(
            f"courier binary substituted requested={pinned} used={fallback}",
            night_log,
        )

    def test_legacy_write_once_tuple_matches_base(self):
        import ast
        base = ast.parse(subprocess.check_output(
            ['git', 'show', 'a90ab4e8:scripts/run_night.py'], cwd=REPO_ROOT, text=True))
        assignment = next(node for node in base.body if isinstance(node, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == '_WRITE_ONCE_RECORDS' for t in node.targets))
        self.assertEqual(self.driver._WRITE_ONCE_RECORDS, ast.literal_eval(assignment.value))

    def test_v2_existing_quiet_journal_reaches_legacy_evaluator(self):
        night = self.custody / 'night'
        night.mkdir()
        journal = night / 'quiet_samples.jsonl'
        journal.write_text('pre-existing unrelated journal\n')
        with mock.patch.object(self.driver, 'evaluate_night', side_effect=RuntimeError('legacy evaluated')) as evaluate:
            with self.assertRaisesRegex(RuntimeError, 'legacy evaluated'):
                self.driver.run_night(self.plan_path)
        evaluate.assert_called_once()
        self.assertIsNone(evaluate.call_args.args[0].quiet_admission)
        self.assertEqual(journal.read_text(), 'pre-existing unrelated journal\n')
        self.assertFalse((night / 'rerun.refusal.json').exists())

    def test_v4_existing_quiet_journal_blocks_rerun(self):
        from dataclasses import replace
        from tests.test_quiet_admission import POLICY
        plan = replace(self.driver._load_plan(self.plan_path), window_max_s=9600,
                       quiet_admission=dict(POLICY))
        self.plan_path.unlink()
        write_night_plan(self.plan_path, plan)
        night = self.custody / 'night'
        night.mkdir()
        (night / 'quiet_samples.jsonl').write_text('retained\n')
        with mock.patch.object(self.driver, 'bind_until_quiet') as bind:
            self.assertEqual(self.driver.run_night(self.plan_path), self.driver.EXIT_REFUSED)
        bind.assert_not_called()
        self.assertEqual((night / 'quiet_samples.jsonl').read_text(), 'retained\n')

    def test_write_once_rerun_preserves_the_first_nights_records(self) -> None:
        first_exit, first_calls = self._run_night()
        night = self.custody / "night"
        result_before = (night / "result.json").read_bytes()
        receipt_before = (night / "receipt.json").read_bytes()
        courier_calls = self.driver.run_courier.call_count
        probe_calls = self.probes_mock.call_count
        second_exit = self.driver.run_night(self.plan_path)
        self.assertEqual(first_exit, 0)
        self.assertEqual(second_exit, self.driver.EXIT_REFUSED)
        self.assertEqual(first_calls, [["/bin/zsh", str(self.chain)]])
        self.assertEqual((night / "result.json").read_bytes(), result_before)
        self.assertEqual((night / "receipt.json").read_bytes(), receipt_before)
        self.assertEqual(self.driver.run_courier.call_count, courier_calls)
        self.assertEqual(self.probes_mock.call_count, probe_calls + 1)  # first-act census precedes plan reads
        self.assertEqual([], list(night.glob("refusal*.json")))

    def test_second_fire_beside_a_go_night_writes_no_refusal_document(self) -> None:
        """A spurious rerun must never report a finished night as refused."""
        first_exit, _ = self._run_night()
        night = self.custody / "night"
        result_before = (night / "result.json").read_bytes()
        published = json.loads(result_before)
        self.assertEqual(first_exit, 0)
        self.assertEqual("GO", published["verdict"])
        self.assertEqual([], published["refusal_documents"])
        self.assertEqual(self.driver.EXIT_REFUSED, self.driver.run_night(self.plan_path))
        # No authoritative refusal.json (the courier's `refusal*.json`
        # discovery and result.json's refusal_documents both key on that
        # name), and no rerun sibling either once a verdict exists.
        self.assertEqual([], list(night.glob("refusal*.json")))
        self.assertEqual([], list(night.glob("rerun.refusal*.json")))
        self.assertEqual(result_before, (night / "result.json").read_bytes())
        self.assertEqual([], self.driver._refusal_paths(night))
        self.assertEqual([], [entry for entry in published["artifacts"]
                              if "refusal" in entry["path"]])
        self.assertEqual([], [entry for entry in self.driver._artifact_list(self.custody, night)
                              if "refusal" in entry["path"]])

    def test_second_fire_during_a_running_night_uses_the_rerun_stem(self) -> None:
        """While the first night runs there is no verdict yet; keep the record."""
        night = self.custody / "night"
        night.mkdir(parents=True)
        (night / "chain.started").write_text(json.dumps({"pid": 4242, "pgid": 4242}))
        self.assertEqual(self.driver.EXIT_REFUSED, self.driver.run_night(self.plan_path))
        self.assertFalse((night / "refusal.json").exists())
        document = json.loads((night / "rerun.refusal.json").read_text())
        self.assertEqual(document["refusal"]["reason"], self.driver._CODES["record_exists"])
        self.assertEqual(document["refusal"]["evidence"], {"existing": "chain.started"})
        self.assertEqual([], self.driver._refusal_paths(night))
        # A concurrent second fire numbers through the same allocator.
        self.assertEqual(self.driver.EXIT_REFUSED, self.driver.run_night(self.plan_path))
        self.assertTrue((night / "rerun.refusal-01.json").is_file())
        self.assertFalse((night / "refusal.json").exists())
        self.assertIn("night/rerun.refusal.json",
                      [entry["path"] for entry in self.driver._artifact_list(self.custody, night)])

    def test_driver_refusal_schema_is_exact_and_not_a_gate_receipt(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        reasons = sorted(
            self.driver.NIGHT_DRIVER_REASON_CODES | self.driver.NIGHT_GATE_REASON_CODES
        )
        for index, reason in enumerate(reasons):
            with self.subTest(reason=reason):
                path = self.root / f"driver-refusal-{index}.json"
                self.driver._write_driver_refusal(path, plan, reason, "defect detail")
                document = json.loads(path.read_text())
                self.assertEqual(self.driver.validate_refusal(document), [])
                self.assertNotEqual(night_gate.validate_receipt(document), [])
                self.assertEqual(
                    set(document),
                    {"schema", "receipt_class", "plan_id", "verdict", "refusal"},
                )

    def test_unproven_chain_termination_records_unkilled_and_spawns_no_courier(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n"),
        ]
        process = UnkillableProcess(["/bin/zsh", str(self.chain)])
        census = ["4343 /bin/zsh chain.zsh"]
        with mock.patch.object(self.driver.subprocess, "Popen", return_value=process), \
             mock.patch.object(self.driver, "GROUP_CENSUS_WINDOW_S", 0.05), \
             mock.patch.object(self.driver, "_group_census", return_value=(False, census)), \
             mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.run_night(self.plan_path)
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        unkilled = json.loads((night / "chain.unkilled").read_text())
        # The census that refused to empty is preserved as the evidence a desk
        # reader needs: which processes were still in the group.
        self.assertEqual(census, unkilled["group_census"])
        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["chain_alive"])
        self.assertEqual(unkilled["pgid"], process.pid)
        self.assertEqual(kill_group.call_args_list[0].args, (process.pid, self.driver.signal.SIGTERM))
        self.driver.run_courier.assert_not_called()

    def test_dead_man_reaps_a_gone_group_then_censuses_and_couriers(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text(
            json.dumps({"pid": 7171, "pgid": 7171, "epoch_s": time.time()}),
            encoding="utf-8",
        )
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg", side_effect=ProcessLookupError):
            exit_code = self.driver.dead_man(self.plan_path)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(exit_code, 0)
        self.assertEqual(exited["reaped_by"], "dead-man")
        self.assertTrue((night / "censuses.jsonl").is_file())
        self.driver.run_courier.assert_called_once()
        self.assertGreaterEqual(self.driver._durable_record.call_count, 2)

    def test_dead_man_refuses_a_proven_live_process_group(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text(
            json.dumps({"pid": 7272, "pgid": 7272, "epoch_s": time.time()}),
            encoding="utf-8",
        )
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        kill_group.assert_called_once_with(7272, 0)
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["chain_alive"])
        self.driver.run_courier.assert_not_called()
        self.driver._durable_record.assert_called_once()

    def test_dead_man_refuses_a_fresh_live_courier_lock(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        (night / "courier.lock").write_text(
            json.dumps({"pid": os.getpid(), "epoch_s": completion_epoch_s}),
            encoding="utf-8",
        )
        (night / "courier.heartbeat").write_text("alive\n", encoding="utf-8")
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ):
            exit_code = self.driver.dead_man(self.plan_path)
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["courier_running"])
        self.driver.run_courier.assert_not_called()

    def test_empty_non_json_and_missing_plans_refuse_and_attempt_courier(self) -> None:
        cases = (("empty", "{}"), ("text", "not json"), ("missing", None))
        for name, contents in cases:
            with self.subTest(name=name):
                case_root = self.root / name
                case_root.mkdir()
                plan_path = case_root / "plan.json"
                if contents is not None:
                    plan_path.write_text(contents, encoding="utf-8")
                self.driver.run_courier.reset_mock()
                self.driver._durable_record.reset_mock()
                exit_code = self.driver.run_night(plan_path)
                night = case_root / "night-custody" / "night"
                refusal = json.loads((night / "refusal.json").read_text())
                self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
                self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["plan_malformed"])
                self.assertTrue((night / "result.json").is_file())
                self.driver.run_courier.assert_called_once()
                self.assertEqual(self.driver._durable_record.call_count, 1)

    def test_rehearsal_census_hits_are_observed_without_killing_the_stub(self) -> None:
        self._write_plan(receipt_class="REHEARSAL_STUB")
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="12345 claude\n"),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="12345 claude\n"),
        ]
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.os, "killpg"
        ) as kill_group, mock.patch.object(self.driver.time, "sleep"):
            exit_code = self.driver.run_night(self.plan_path)
        night = self.custody / "night"
        result = json.loads((night / "result.json").read_text())
        receipt = json.loads((night / "receipt.json").read_text())
        self.assertEqual("REFUSED", receipt["verdict"])
        self.assertEqual("night_refused_agent_present", receipt["refusal"]["reason"])
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        self.assertEqual(result["verdict"], "REHEARSAL_ONLY")
        self.assertGreater(result["census_count"], 0)
        self.assertTrue(result["census_hits"])
        self.assertEqual(result["census_hits"][0]["stdout"], "12345 claude\n")
        self.assertFalse((night / "refusal.json").exists())
        self.assertEqual(calls, [["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]])
        kill_group.assert_not_called()
        self.driver.run_courier.assert_called_once()

    def test_chain_exit_is_recorded_before_the_first_durable_publish(self) -> None:
        events = []
        real_record_exit = self.driver._record_chain_exit

        def record_exit(*args, **kwargs):
            real_record_exit(*args, **kwargs)
            events.append("exited")

        self.driver._durable_record.side_effect = lambda *args: events.append("publish")
        with mock.patch.object(self.driver, "_record_chain_exit", side_effect=record_exit):
            exit_code, _calls = self._run_night()
        self.assertEqual(exit_code, 0)
        self.assertLess(events.index("exited"), events.index("publish"))

    def test_living_chain_records_a_thirty_second_census(self) -> None:
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.time, "sleep"
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        result = json.loads((self.custody / "night" / "result.json").read_text())
        self.assertGreater(result["census_count"], 0)
        self.assertEqual(self.driver.CENSUS_INTERVAL_S, 30)
        self.assertTrue(self.popen_kwargs[0]["start_new_session"])

    def test_durable_publish_uses_shallow_clone_and_named_results_branch_twice(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        night = self.custody / "night"
        night.mkdir()
        (self.custody / "night.log").write_text("record\n", encoding="utf-8")
        argvs = []

        def fake_run(argv, **kwargs):
            argvs.append(list(argv))
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        with mock.patch.object(self.driver.subprocess, "run", side_effect=fake_run):
            self.real_durable_record(self.custody, night, plan)
            (night / "courier.heartbeat").write_text("seen\n", encoding="utf-8")
            self.real_durable_record(self.custody, night, plan)
        clone = next(argv for argv in argvs if argv[:4] == ["git", "clone", "--depth", "1"])
        pushes = [argv for argv in argvs if "push" in argv]
        branch = f"night-results/{plan.plan_id}"
        self.assertEqual(clone, ["git", "clone", "--depth", "1", "example-origin", str(self.custody / "results-clone")])
        self.assertEqual(len(pushes), 2)
        self.assertTrue(all(argv[-1] == f"HEAD:{branch}" for argv in pushes))
        destination = self.custody / "results-clone/docs/process_traces/night-results" / plan.plan_id
        self.assertTrue((destination / "night.log").is_file())
        commits = [argv for argv in argvs if "commit" in argv]
        self.assertTrue(all(argv[-1] == f"record night {plan.plan_id}" for argv in commits))

    def test_courier_deadline_is_derived_from_the_measured_artifact(self) -> None:
        artifact = json.loads(
            (REPO_ROOT / "docs" / "process_traces" / "2026-09-01-unattended" / "cold_start.json").read_text()
        )
        measured = artifact["median_ms"] / 1000
        expected = min(600, max(3 * measured, 300))
        self.assertEqual(self.driver.COURIER_DEADLINE_S, expected)

    def test_artifact_inventory_includes_every_courier_record(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        for name in (
            "courier.json",
            "courier.attempts.jsonl",
            "courier.heartbeat",
            "courier.sent",
        ):
            (night / name).write_text(name + "\n", encoding="utf-8")
        paths = {item["path"] for item in self.driver._artifact_list(self.custody, night)}
        self.assertTrue(
            {
                "night/courier.json",
                "night/courier.attempts.jsonl",
                "night/courier.heartbeat",
                "night/courier.sent",
            }
            <= paths
        )

    def test_code_map_rejects_a_non_night_registry_member(self) -> None:
        with self.assertRaises(RuntimeError):
            self.driver._build_code_map({"bad_prefix"})

    def test_run_path_courier_hands_off_at_the_dead_man_epoch(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        calls, spawn = self._popen_recorder()
        self.driver.run_courier = self.real_run_courier
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            outcome = self.driver.run_courier(
                self.custody,
                plan,
                self.courier,
                deadman_epoch_s=time.time() - 1,
            )
        self.assertEqual(outcome["attempted"], 0)
        self.assertFalse(outcome["sent"])
        self.assertEqual(calls, [])
        self.assertFalse((self.custody / "night" / "courier.lock").exists())

    def test_courier_wait_caps_sleep_at_the_dead_man_epoch(self) -> None:
        heartbeat = self.root / "absent-heartbeat"
        sent = self.root / "absent-sent"
        stop_epoch_s = 10_000.0
        wall_clock = [stop_epoch_s - 0.3]
        monotonic_clock = [50.0]
        sleeps = []

        def advance(delay: float) -> None:
            sleeps.append(delay)
            wall_clock[0] += delay
            monotonic_clock[0] += delay

        with mock.patch.object(
            self.driver.time, "time", side_effect=lambda: wall_clock[0]
        ), mock.patch.object(
            self.driver.time, "monotonic", side_effect=lambda: monotonic_clock[0]
        ), mock.patch.object(self.driver.time, "sleep", side_effect=advance):
            heartbeat_seen, was_sent = self.driver._wait_for_courier(
                heartbeat,
                sent,
                stop_epoch_s=stop_epoch_s,
            )
        self.assertFalse(heartbeat_seen)
        self.assertFalse(was_sent)
        self.assertTrue(sleeps)
        self.assertLessEqual(max(sleeps), 0.3)

    def test_results_branch_and_trace_dir_are_keyed_by_plan_id(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        night = self.custody / "night"
        night.mkdir()
        (self.custody / "night.log").write_text("record\n")
        calls = []

        def fake_run(argv, **kwargs):
            calls.append(argv)
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="fixture-origin\n", returncode=0)

        with mock.patch.object(self.driver.subprocess, "run", side_effect=fake_run):
            for plan_id in ("same-day-a", "same-day-b"):
                self.real_durable_record(self.custody, night, replace(plan, plan_id=plan_id))
                destination = self.custody / "results-clone/docs/process_traces/night-results" / plan_id
                self.assertTrue((destination / "night.log").is_file())
        self.assertEqual({"HEAD:night-results/same-day-a", "HEAD:night-results/same-day-b"},
                         {argv[-1] for argv in calls if "push" in argv})
        self.assertEqual({"record night same-day-a", "record night same-day-b"},
                         {argv[-1] for argv in calls if "commit" in argv})

    def test_deadman_epoch_is_completion_plus_grace_at_a_midday_t0(self) -> None:
        for second in (0, 17):
            with self.subTest(second=second):
                plan = replace(self.driver._load_plan(self.plan_path),
                               t0_epoch_s=datetime(2026, 9, 15, 13, 20, second).timestamp(),
                               window_max_s=9000)
                completion = self.driver._completion_epoch_s(plan)
                rounded = (-completion) % 60
                self.assertEqual(self.driver.deadman_epoch(plan) - completion,
                                 self.driver.DEADMAN_GRACE_S + rounded)

    def test_deadman_grace_covers_every_courier_attempt_and_backoff(self) -> None:
        self.assertGreaterEqual(self.driver.DEADMAN_GRACE_S,
            self.driver.COURIER_DEADLINE_S * (len(self.driver.COURIER_BACKOFF_S) + 1)
            + sum(self.driver.COURIER_BACKOFF_S))

    def test_driver_accepts_a_t0_in_the_former_dead_man_hour(self) -> None:
        t0 = datetime(2026, 9, 2, 7, 20).timestamp()
        self._write_plan(t0_epoch_s=t0, window_max_s=9000)
        self.source.now_epoch_s = t0 + 1
        result, calls = self._run_night()
        self.assertEqual(self.driver.EXIT_GO, result)
        self.assertEqual([["/bin/zsh", str(self.chain)]], calls)
        self.assertEqual(self.driver.deadman_epoch(self.driver._load_plan(self.plan_path)),
                         self.driver.run_courier.call_args.kwargs["deadman_epoch_s"])

    def test_install_close_precedes_the_plan_span_by_the_margin(self) -> None:
        from scripts.magistrate_watchdog import PLAN_LEAD_S, REQUEST_LEAD_S
        plan = self.driver._load_plan(self.plan_path)
        self.assertEqual(self.driver.INSTALL_CLOSE_MARGIN_S, 120)
        self.assertEqual(plan.t0_epoch_s - PLAN_LEAD_S - self.driver.install_close_epoch(plan),
                         self.driver.INSTALL_CLOSE_MARGIN_S)
        self.assertLess(self.driver.install_close_epoch(plan),
                        plan.t0_epoch_s - REQUEST_LEAD_S)

    def test_fixed_epoch_install_close_is_1799999400(self) -> None:
        plan = replace(self.driver._load_plan(self.plan_path), t0_epoch_s=1800000000,
                       window_max_s=9000)
        self.assertEqual(1799999400, self.driver.install_close_epoch(plan))

    def test_fixed_epoch_deadman_is_1800012900(self) -> None:
        plan = replace(self.driver._load_plan(self.plan_path), t0_epoch_s=1800000000,
                       window_max_s=9000)
        self.assertEqual(1800012900, self.driver.deadman_epoch(plan))
        self.assertEqual(1800012960, self.driver.deadman_epoch(replace(plan, t0_epoch_s=1800000001)))

    def test_reversed_0500_0400_spans_are_rejected_at_fresh_import(self) -> None:
        # Change only the configuration literal; execute the actual module's
        # import-time validation in a fresh interpreter.
        code = (
            "from pathlib import Path\n"
            f"path = Path({str(SCRIPT_PATH)!r})\n"
            "source = path.read_text().replace('((\"00:00\", \"24:00\"),)', '((\"05:00\", \"04:00\"),)', 1)\n"
            "exec(compile(source, str(path), 'exec'), {'__file__': str(path), '__name__': 'span_import_probe'})\n"
        )
        completed = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("install spans must be ordered, disjoint, and close > open", completed.stderr)

    def test_schedule_missing_malformed_fields_and_unrepresentable_windows_refuse(self) -> None:
        original = json.loads(self.plan_path.read_text())
        cases = [(field, value) for field in ("t0_epoch_s", "window_max_s", "authored_epoch_s")
                 for value in (None, "malformed")]
        cases += [("window_max_s", 10**15), ("window_max_s", 10**400)]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                mapping = original.copy()
                if value is None:
                    del mapping[field]
                else:
                    mapping[field] = value
                self.plan_path.write_text(json.dumps(mapping))
                completed = subprocess.run([sys.executable, "-B", str(SCRIPT_PATH), "schedule",
                    "--plan", str(self.plan_path)], capture_output=True, text=True)
                self.assertEqual(2, completed.returncode, completed.stderr)
                self.assertIn("plan_schedule_unrepresentable" if isinstance(value, int)
                              else "night_plan_malformed", completed.stderr)
                self.assertEqual(1, len(completed.stderr.splitlines()))
                self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    @unittest.skipUnless(hasattr(time, "tzset"), "requires POSIX local timezone")
    def test_schedule_rejects_dst_inverted_and_overlapping_resolved_spans(self) -> None:
        cases = ((date(2026, 3, 8), (("02:45", "03:15"),)),
                 (date(2026, 11, 1), (("01:15", "01:45"), ("01:45", "02:00"))))
        try:
            with mock.patch.dict(os.environ, {"TZ": "America/Los_Angeles"}):
                time.tzset()
                plan = self.driver._load_plan(self.plan_path)
                for day, spans in cases:
                    with self.subTest(day=day), mock.patch.object(self.driver, "INSTALL_SPANS", spans), mock.patch.object(
                        self.driver.time, "time", return_value=datetime.combine(day, datetime.min.time()).timestamp()
                    ):
                        with self.assertRaises(night_gate.PlanError) as refusal:
                            self.driver.schedule(plan)
                        self.assertEqual("install_spans_unresolvable_on_day", refusal.exception.reason)
                        self.assertIn(str(day), refusal.exception.detail)
                        code = (
                            "import sys, time\nfrom pathlib import Path\n"
                            f"path = Path({str(SCRIPT_PATH)!r})\n"
                            f"time.time = lambda: {datetime.combine(day, datetime.min.time()).timestamp()!r}\n"
                            "source = path.read_text().replace('((\"00:00\", \"24:00\"),)', "
                            f"{repr(spans)!r}, 1)\n"
                            f"sys.argv = [str(path), 'schedule', '--plan', {str(self.plan_path)!r}]\n"
                            "exec(compile(source, str(path), 'exec'), {'__file__': str(path), '__name__': '__main__'})\n"
                        )
                        completed = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True)
                        self.assertEqual(2, completed.returncode, completed.stderr)
                        self.assertIn("install_spans_unresolvable_on_day", completed.stderr)
                        self.assertIn(str(day), completed.stderr)
                        self.assertNotIn("Traceback", completed.stderr)
                for day, seconds in ((date(2026, 3, 8), 82800), (date(2026, 11, 1), 90000)):
                    with self.subTest(default_day=day), mock.patch.object(self.driver.time, "time",
                        return_value=datetime.combine(day, datetime.min.time()).timestamp()
                    ):
                        spans = self.driver.schedule(plan)["install_spans_today"]
                        self.assertEqual(1, len(spans))
                        self.assertEqual(seconds, spans[0][1] - spans[0][0])
        finally:
            time.tzset()

    def test_install_spans_default_is_the_whole_day_and_validates_shape(self) -> None:
        self.assertEqual((("00:00", "24:00"),), self.driver.INSTALL_SPANS)
        self.driver._validate_install_spans((("01:00", "02:00"), ("02:00", "04:00")))
        for spans in ([('00:00', '24:00')], (("24:00", "24:00"),),
                      (("1:00", "02:00"),), (("02:00", "02:00"),),
                      (("23:00", "01:00"),), (("01:00", "02:00"), ("01:59", "03:00")),
                      (("12:00", "13:00"), ("10:00", "11:00")), (("00:00",),)):
            with self.subTest(spans=spans), self.assertRaises(ValueError):
                self.driver._validate_install_spans(spans)
        with mock.patch.object(self.driver, "INSTALL_SPANS", (("09:00", "10:00"),)):
            self.assertIsNone(self.driver.install_span_containing(datetime(2026, 9, 15, 10).timestamp()))

    @unittest.skipUnless(hasattr(time, "tzset"), "requires POSIX local timezone")
    def test_install_span_containing_resolves_local_time_across_dst(self) -> None:
        try:
            with mock.patch.dict(os.environ, {"TZ": "America/Los_Angeles"}):
                time.tzset()
                for day, hours in ((date(2026, 3, 8), 23), (date(2026, 11, 1), 25)):
                    with self.subTest(day=day):
                        opening, closing = self.driver.install_spans_for_day(day)[0]
                        self.assertEqual(hours * 3600, closing - opening)
                        self.assertEqual((opening, closing), self.driver.install_span_containing(opening))
                        self.assertEqual((opening, closing), self.driver.install_span_containing(closing - 1))
                        self.assertNotEqual((opening, closing), self.driver.install_span_containing(closing))
                with mock.patch.object(self.driver, "INSTALL_SPANS", (("01:15", "01:45"),)):
                    span = self.driver.install_spans_for_day(date(2026, 11, 1))[0]
                    for fold in (0, 1):
                        now = datetime(2026, 11, 1, 1, 30, fold=fold).timestamp()
                        self.assertEqual(span, self.driver.install_span_containing(now))
        finally:
            time.tzset()

    def _schedule_local_t0(self, local: datetime) -> subprocess.CompletedProcess[str]:
        t0 = local.replace(tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()
        self._write_plan(t0_epoch_s=t0)
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT_PATH), "schedule", "--plan", str(self.plan_path)],
            env={**os.environ, "TZ": "America/Los_Angeles"}, capture_output=True, text=True,
        )

    def _assert_t0_schedule_refused(self, local: datetime, reason: str) -> None:
        completed = self._schedule_local_t0(local)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertIn(reason, completed.stderr)
        self.assertEqual("", completed.stdout)
        self.assertEqual(1, len(completed.stderr.splitlines()))
        self.assertFalse((self.custody / "night").exists())

    def test_schedule_refuses_132017_t0_instead_of_rendering_1320(self) -> None:
        self._assert_t0_schedule_refused(datetime(2026, 9, 16, 13, 20, 17),
                                         "plan_t0_not_minute_aligned")

    def test_schedule_refuses_first_20261101_0130_occurrence(self) -> None:
        self._assert_t0_schedule_refused(datetime(2026, 11, 1, 1, 30, fold=0),
                                         "plan_t0_ambiguous_local_time")

    def test_schedule_refuses_second_20261101_0130_occurrence(self) -> None:
        self._assert_t0_schedule_refused(datetime(2026, 11, 1, 1, 30, fold=1),
                                         "plan_t0_ambiguous_local_time")

    def test_schedule_accepts_ordinary_20260916_0256_whole_minute(self) -> None:
        completed = self._schedule_local_t0(datetime(2026, 9, 16, 2, 56))
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual({"Month": 9, "Day": 16, "Hour": 2, "Minute": 56},
                         json.loads(completed.stdout)["night_calendar"])

    def test_schedule_accepts_spring_20260308_0430_after_gap(self) -> None:
        completed = self._schedule_local_t0(datetime(2026, 3, 8, 4, 30))
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual({"Month": 3, "Day": 8, "Hour": 4, "Minute": 30},
                         json.loads(completed.stdout)["night_calendar"])

    def test_schedule_subcommand_prints_calendar_fields_from_the_plan(self) -> None:
        completed = subprocess.run([sys.executable, "-B", str(SCRIPT_PATH), "schedule",
                                    "--plan", str(self.plan_path)], capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stderr)
        schedule = json.loads(completed.stdout)
        self.assertEqual({"Month": 9, "Day": 2, "Hour": 1, "Minute": 0}, schedule["night_calendar"])
        self.assertEqual({"Hour": 2, "Minute": 6}, schedule["deadman_calendar"])
        plan = self.driver._load_plan(self.plan_path)
        self.assertEqual(self.driver.install_close_epoch(plan), schedule["install_close_epoch_s"])
        self.assertEqual(self.driver.deadman_epoch(plan), schedule["deadman_epoch_s"])
        self.assertEqual(plan.t0_epoch_s, schedule["t0_epoch_s"])
        self.assertEqual([list(span) for span in self.driver.install_spans_for_day(date.today())],
                         schedule["install_spans_today"])

    def test_exclusive_record_writers_and_markers_are_fsynced(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        record = night / "result.json"
        with mock.patch.object(self.driver.os, "open", wraps=os.open) as open_file, mock.patch.object(
            self.driver.os, "fsync", wraps=os.fsync
        ) as fsync:
            self.driver._write_json(record, {"value": 1})
            flags = open_file.call_args_list[0].args[1]
            self.assertEqual(
                flags & (os.O_CREAT | os.O_EXCL | os.O_WRONLY),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
            with self.assertRaises(FileExistsError):
                self.driver._write_json(record, {"value": 2})
            descriptor = self.driver._claim_chain_start(night)
            self.assertIsNotNone(descriptor)
            assert descriptor is not None
            self.driver._complete_chain_start(descriptor, FakeProcess(["chain"]), night)
            self.driver._record_chain_exit(night, 0)
            sent = night / "courier.sent"
            sent.write_text("sent\n", encoding="utf-8")
            heartbeat_seen, was_sent = self.driver._wait_for_courier(
                night / "courier.heartbeat", sent
            )
        self.assertFalse(heartbeat_seen)
        self.assertTrue(was_sent)
        self.assertGreaterEqual(fsync.call_count, 4)

    def test_moved_real_measurement_checkout_refuses_as_stale(self) -> None:
        measurement = self.root / "measurement-probe"
        pinned_head = _init_git_repo(measurement)
        plan_mapping = json.loads(self.plan_path.read_text(encoding="utf-8"))
        plan_mapping["measurement_root"] = str(measurement)
        plan_mapping["measurement_head"] = pinned_head
        self.plan_path.write_text(json.dumps(plan_mapping), encoding="utf-8")

        marker = measurement / "measurement.txt"
        marker.write_text("moved\n", encoding="utf-8")
        subprocess.run(
            ["/usr/bin/git", "-C", str(measurement), "add", marker.name], check=True
        )
        subprocess.run(
            [
                "/usr/bin/git",
                "-C",
                str(measurement),
                "-c",
                "user.name=JouleWise Test",
                "-c",
                "user.email=joulewise-test@example.invalid",
                "commit",
                "-qm",
                "moved",
            ],
            check=True,
        )
        moved_head = subprocess.check_output(
            ["/usr/bin/git", "-C", str(measurement), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        self.assertNotEqual(pinned_head, moved_head)

        production_measurement_probe = self.real_make_probes().measurement_head
        fake = self.source.probes()
        probes = night_gate.Probes(
            run=fake.run,
            now_epoch_s=fake.now_epoch_s,
            monotonic_ns=fake.monotonic_ns,
            read_text=fake.read_text,
            checkout_head=fake.checkout_head,
            measurement_head=production_measurement_probe,
        )
        plan = self.driver._load_plan(self.plan_path)
        receipt = night_gate.evaluate_night(plan, probes)
        self.assertEqual("night_plan_stale", receipt.refusal.reason)
        self.assertIn("measurement_head", receipt.refusal.detail)

    def test_matching_real_measurement_checkout_uses_requested_root_and_strips_head(self) -> None:
        measurement = self.root / "matching-measurement-probe"
        pinned_head = _init_git_repo(measurement)
        driver_head = subprocess.check_output(
            ["/usr/bin/git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        self.assertNotEqual(driver_head, pinned_head)

        plan_mapping = json.loads(self.plan_path.read_text(encoding="utf-8"))
        plan_mapping["measurement_root"] = str(measurement)
        plan_mapping["measurement_head"] = pinned_head
        self.plan_path.write_text(json.dumps(plan_mapping), encoding="utf-8")

        production_measurement_probe = self.real_make_probes().measurement_head
        observed_head = production_measurement_probe(str(measurement))
        self.assertEqual(pinned_head, observed_head)
        self.assertFalse(observed_head.endswith("\n"))

        fake = self.source.probes()
        probes = night_gate.Probes(
            run=fake.run,
            now_epoch_s=fake.now_epoch_s,
            monotonic_ns=fake.monotonic_ns,
            read_text=fake.read_text,
            checkout_head=lambda: driver_head,
            measurement_head=production_measurement_probe,
        )
        plan = self.driver._load_plan(self.plan_path)
        receipt = night_gate.evaluate_night(plan, probes)
        self.assertNotIn(
            None if receipt.refusal is None else receipt.refusal.reason,
            {"night_plan_stale", "night_plan_malformed"},
        )
        self.assertEqual("GO", receipt.verdict)
        c5 = next(row for row in receipt.conditions if row.condition_id == "C5")
        self.assertEqual(pinned_head, c5.measured["measurement_checkout_head"])

    def _installer_plan(self, root: Path) -> Path:
        plan = json.loads(self.plan_path.read_text())
        plan["repo_head"] = subprocess.check_output(
            ["/usr/bin/git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        measurement_root = root / "measurement"
        plan["measurement_root"] = str(measurement_root)
        plan["measurement_head"] = _init_git_repo(measurement_root)
        python = measurement_root / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        plan["custody_root"] = str(root / "custody")
        plan["authored_epoch_s"] = time.time()  # bench fix: fixture authored "now" so the installer age check passes
        plan["t0_epoch_s"] = (int(time.time()) // 60 + 24 * 60) * 60
        path = root / "custody/night_plan.json"
        path.parent.mkdir()
        path.write_text(json.dumps(plan), encoding="utf-8")
        make_probe_fixture(root, path)
        write_matching_probe_receipt(path, sys.executable)
        return path

    def _installer_environment(self, root: Path) -> tuple[dict[str, str], Path]:
        binary_dir = root / "bin"
        binary_dir.mkdir()
        courier = binary_dir / "claude"
        courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        courier.chmod(0o755)
        environment = os.environ.copy()
        environment["HOME"] = str(root / "home")
        environment["PATH"] = f"{binary_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        return environment, courier

    def _installer_symlink_environment(
        self, root: Path
    ) -> tuple[dict[str, str], Path, Path]:
        binary_dir = root / "bin"
        versions_dir = root / "share" / "claude" / "versions"
        binary_dir.mkdir()
        versions_dir.mkdir(parents=True)
        version = versions_dir / "2.1.252"
        version.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        version.chmod(0o755)
        courier = binary_dir / "claude"
        courier.symlink_to(version)
        environment = os.environ.copy()
        environment["HOME"] = str(root / "home")
        environment["PATH"] = f"{binary_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        return environment, courier, version.resolve()

    def test_installer_symlinked_courier_renders_resolved_binary_and_lookup_path(
        self,
    ) -> None:
        root = self.root / "symlink-render"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, courier, resolved_courier = self._installer_symlink_environment(
            root
        )
        rendered = root / "rendered"
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--render-only",
                str(rendered),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        night = plistlib.loads((rendered / "com.joulewise.night.plist").read_bytes())
        rendered_path = night["EnvironmentVariables"]["PATH"]
        self.assertEqual(
            night["ProgramArguments"][-2:],
            ["--courier-bin", str(resolved_courier)],
        )
        self.assertEqual(
            rendered_path,
            f"{courier.parent}:/usr/bin:/bin:/usr/sbin:/sbin",
        )
        with mock.patch.dict(os.environ, {"PATH": rendered_path}, clear=True):
            found, error, substitution = self.real_resolve_courier_bin(None)
        self.assertEqual(found, courier)
        self.assertIsNone(error)
        self.assertIsNone(substitution)

    def test_installer_renders_working_directory_path_binary_and_distinct_logs(self) -> None:
        root = self.root / "render"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, courier = self._installer_environment(root)
        rendered = root / "rendered"
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--render-only",
                str(rendered),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        night = plistlib.loads((rendered / "com.joulewise.night.plist").read_bytes())
        deadman = plistlib.loads((rendered / "com.joulewise.night.deadman.plist").read_bytes())
        expected_path = f"{courier.parent}:/usr/bin:/bin:/usr/sbin:/sbin"
        self.assertEqual(night["WorkingDirectory"], str(REPO_ROOT))
        self.assertEqual(night["EnvironmentVariables"]["PATH"], expected_path)
        self.assertEqual(
            night["ProgramArguments"][-2:],
            ["--courier-bin", str(courier.resolve())],
        )
        self.assertNotEqual(night["StandardOutPath"], deadman["StandardOutPath"])
        self.assertNotEqual(night["StandardErrorPath"], deadman["StandardErrorPath"])

    def test_installer_refuses_when_command_lookup_has_no_courier(self) -> None:
        root = self.root / "no-courier"
        root.mkdir()
        plan = self._installer_plan(root)
        empty_path = root / "empty-bin"
        empty_path.mkdir()
        # The default-interpreter derivation (fix round 3) needs a python3 on
        # PATH for its stdlib-only JSON read; this test is about the ABSENT
        # courier, so provide python3 and nothing else.
        (empty_path / "python3").symlink_to(sys.executable)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--render-only",
                str(root / "rendered"),
            ],
            env={"HOME": str(root / "home"), "PATH": str(empty_path)},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("courier unavailable", completed.stderr)

    def test_installer_refuses_a_stale_courier_sent_before_bootstrap(self) -> None:
        root = self.root / "stale-courier"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "courier.sent").write_text("sent\n", encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            '#!/bin/zsh\n'
            'print -r -- "$*" >> "$LAUNCH_LOG"\n'
            'label="${${3:-$2}:t:r}"\n'
            '[[ "$1" == print ]] && { [[ -f "$LAUNCH_LOG.${2:t}" ]]; exit $?; }\n'
            '[[ "$1" == bootstrap ]] && /usr/bin/touch "$LAUNCH_LOG.$label"\n'
            '[[ "$1" == bootout ]] && /bin/rm -f "$LAUNCH_LOG.${2:t}"\n'
            'exit 0\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("courier.sent", completed.stderr)
        self.assertFalse(launch_log.exists())

    def test_installer_refuses_a_dangling_symlink_night_record(self) -> None:
        # Sol 135 F1: zsh `[[ -e ]]` is false for a dangling symlink, so the
        # stale-night guard must also test `-L`.
        root = self.root / "stale-symlink"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "result.json").symlink_to(root / "missing-target.json")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            '#!/bin/zsh\n'
            'print -r -- "$*" >> "$LAUNCH_LOG"\n'
            'label="${${3:-$2}:t:r}"\n'
            '[[ "$1" == print ]] && { [[ -f "$LAUNCH_LOG.${2:t}" ]]; exit $?; }\n'
            '[[ "$1" == bootstrap ]] && /usr/bin/touch "$LAUNCH_LOG.$label"\n'
            '[[ "$1" == bootout ]] && /bin/rm -f "$LAUNCH_LOG.${2:t}"\n'
            'exit 0\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("result.json", completed.stderr)
        self.assertFalse(launch_log.exists())

    def test_installer_uninstalls_with_stale_courier_sent(self) -> None:
        root = self.root / "stale-uninstall"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "courier.sent").write_text("sent\n", encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            '#!/bin/zsh\n'
            'print -r -- "$*" >> "$LAUNCH_LOG"\n'
            'label="${${3:-$2}:t:r}"\n'
            'if [[ "$1" == print ]]; then\n'
            '  if [[ -f "$LAUNCH_LOG.${2:t}" ]]; then\n'
            '    print -r -- "$2 = {"; print -r -- "}"; exit 0\n'
            '  fi\n'
            '  print -r -- "Bad request." >&2\n'
            '  print -r -- "Could not find service \\"${2:t}\\" in domain for user gui: ${${2:h}:t}" >&2\n'
            '  exit 113\n'
            'fi\n'
            '[[ "$1" == bootstrap ]] && /usr/bin/touch "$LAUNCH_LOG.$label"\n'
            '[[ "$1" == bootout ]] && /bin/rm -f "$LAUNCH_LOG.${2:t}"\n'
            'exit 0\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--uninstall",
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        calls = launch_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            [line.split()[0] for line in calls if "night-probe." not in line][-4:],
            ["bootout", "bootout", "print", "print"],
        )
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))

    def test_installer_uninstalls_without_courier_on_minimal_path(self) -> None:
        root = self.root / "minimal-path-uninstall"
        root.mkdir()
        plan = self._installer_plan(root)
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            '#!/bin/zsh\n'
            'print -r -- "$*" >> "$LAUNCH_LOG"\n'
            'label="${${3:-$2}:t:r}"\n'
            'if [[ "$1" == print ]]; then\n'
            '  if [[ -f "$LAUNCH_LOG.${2:t}" ]]; then\n'
            '    print -r -- "$2 = {"; print -r -- "}"; exit 0\n'
            '  fi\n'
            '  print -r -- "Bad request." >&2\n'
            '  print -r -- "Could not find service \\"${2:t}\\" in domain for user gui: ${${2:h}:t}" >&2\n'
            '  exit 113\n'
            'fi\n'
            '[[ "$1" == bootstrap ]] && /usr/bin/touch "$LAUNCH_LOG.$label"\n'
            '[[ "$1" == bootout ]] && /bin/rm -f "$LAUNCH_LOG.${2:t}"\n'
            'exit 0\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--uninstall",
                "--launchctl-bin",
                str(launcher),
            ],
            env={
                "HOME": str(root / "home"),
                "PATH": "/usr/bin:/bin",
                "LAUNCH_LOG": str(launch_log),
            },
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        calls = launch_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            [line.split()[0] for line in calls if "night-probe." not in line][-4:],
            ["bootout", "bootout", "print", "print"],
        )
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))

    def test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap(self) -> None:
        root = self.root / "install"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "chain.started").write_text("active\n", encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            '#!/bin/zsh\n'
            'print -r -- "$*" >> "$LAUNCH_LOG"\n'
            'label="${${3:-$2}:t:r}"\n'
            'if [[ "$1" == print ]]; then\n'
            '  if [[ -f "$LAUNCH_LOG.${2:t}" ]]; then\n'
            '    print -r -- "$2 = {"; print -r -- "}"; exit 0\n'
            '  fi\n'
            '  print -r -- "Bad request." >&2\n'
            '  print -r -- "Could not find service \\"${2:t}\\" in domain for user gui: ${${2:h}:t}" >&2\n'
            '  exit 113\n'
            'fi\n'
            'if [[ "$1" == bootstrap && "$*" == *deadman* ]]; then exit 1; fi\n'
            '[[ "$1" == bootstrap ]] && /usr/bin/touch "$LAUNCH_LOG.$label"\n'
            '[[ "$1" == bootout ]] && /bin/rm -f "$LAUNCH_LOG.${2:t}"\n'
            'exit 0\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        base_argv = [
            "/bin/zsh",
            str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
            "--plan",
            str(plan),
            "--python",
            sys.executable,
            "--launchctl-bin",
            str(launcher),
        ]
        environment["LAUNCH_LOG"] = str(launch_log)
        active = subprocess.run(
            base_argv,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(active.returncode, 3)
        self.assertIn("chain.started", active.stderr)
        self.assertFalse(launch_log.exists())
        (custody_night / "chain.started").unlink()
        failed = subprocess.run(
            base_argv,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(failed.returncode, 3, failed.stderr)
        calls = launch_log.read_text().splitlines()
        self.assertTrue(any(line.startswith("bootstrap ") and "com.joulewise.night.plist" in line for line in calls))
        self.assertTrue(any(line.startswith("bootstrap ") and "deadman.plist" in line for line in calls))
        self.assertTrue(any(line.startswith("bootout ") and line.endswith("com.joulewise.night") for line in calls))
        self.assertEqual(
            [line.split()[0] for line in calls if "night-probe." not in line][-4:],
            ["bootout", "bootout", "print", "print"],
        )




def probe_census_available():
    try:
        result = subprocess.run(["/usr/bin/pgrep", "-lf", "-g", "999999", "."],
                                capture_output=True, timeout=5)
        return result.returncode == 1
    except (OSError, subprocess.SubprocessError):
        return False


class NightProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Every subprocess probe in this fixture resolves sudo to a fake.
        # The fake dispatches to a 300-frame plist emitter and never invokes
        # the machine's sudo or powermetrics binaries.
        from tests.test_run_night_probe_cadence import FAKE
        import shlex
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        fake_power = fake_bin / "fake-powermetrics"
        fake_power.write_text(FAKE.format(interval=132, spike=0, timeout=False))
        fake_power.chmod(0o755)
        fake_sudo = fake_bin / "sudo"
        fake_sudo.write_text("#!/bin/sh\n"
            "[ \"$1\" = \"-n\" ] || exit 8\nshift\n"
            "[ \"$1\" = \"/usr/bin/powermetrics\" ] || exit 9\nshift\n"
            "exec {} \"$@\"\n".format(shlex.quote(str(fake_power))))
        fake_sudo.chmod(0o755)
        path_patch = mock.patch.dict(os.environ, {"PATH": str(fake_bin) + ":" + os.environ.get("PATH", "")})
        path_patch.start()
        self.addCleanup(path_patch.stop)
        self.plan_path = self.root / "night_plan.json"
        plan = night_gate.NightPlan(plan_id="probe-fixture", receipt_class="DIAGNOSTIC_NO_PACK",
            t0_epoch_s=(int(time.time()) // 60 + 60) * 60, window_max_s=9000,
            authored_epoch_s=time.time(), repo_head=HEAD, measurement_root=str(self.root / "measurement"),
            measurement_head=HEAD, chain_path=str(self.root / "chain"),
            chain_sha256_path=str(self.root / "chain.sha256"), custody_root=str(self.root / "custody"),
            registration_path="fixture-registration")
        write_night_plan(self.plan_path, plan)
        make_probe_fixture(self.root, self.plan_path)
        self.plan = night_gate.NightPlan.from_mapping(json.loads(self.plan_path.read_text()))
        self.receipt = self.root / "night_probe_receipt.json"

    def run_probe(self, mode="ok", timeout=5):
        (Path(self.plan.measurement_root) / "stub-mode").write_text(mode)
        return subprocess.run([sys.executable, "-B", str(SCRIPT_PATH), "probe", "--plan",
            str(self.plan_path), "--receipt", str(self.receipt), "--timeout-s", str(timeout)],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, "JOULEWISE_LAUNCHD_LABEL": "com.joulewise.night-probe.probe-fixture"})

    def test_verify_only_chain_runs_only_reservation(self):
        night = self.root / "probe-output"
        night.mkdir()
        result = subprocess.run(["/bin/zsh", self.plan.chain_path], env={**os.environ,
            "NIGHT_VERIFY_ONLY": "1", "NIGHT_DIR": str(night),
            "JOULEWISE_NIGHT_PLAN_ID": self.plan.plan_id,
            "PY": self.plan.measurement_root + "/.venv/bin/python", "CUSTODY_BUDGET_S": "0.75"},
            text=True, capture_output=True, timeout=5)
        self.assertEqual(0, result.returncode, result.stderr)
        receipt = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual("ok", receipt["verify_only"])
        argv = json.loads((Path(self.plan.measurement_root) / "reservation-argv.json").read_text())
        self.assertIn("--verify-only", argv)
        self.assertNotIn("--execute", argv)
        self.assertEqual("0.75", argv[argv.index("--custody-budget-s") + 1])
        self.assertEqual(str(int(self.plan.t0_epoch_s + self.plan.window_max_s) - 10),
                         argv[argv.index("--custody-deadline-epoch-s") + 1])
        self.assertFalse(list(self.root.rglob("*.CALLED")))
        self.assertFalse(list(self.root.rglob("chain.started")))
        self.assertFalse((self.root / "window").exists())

    def test_execute_chain_carries_pre_reserve_strict_flag(self):
        night = self.root / "execute-output"
        night.mkdir()
        (Path(self.plan.measurement_root) / "stub-mode").write_text("refused")
        result = subprocess.run(["/bin/zsh", self.plan.chain_path], env={**os.environ,
            "NIGHT_DIR": str(night), "JOULEWISE_NIGHT_PLAN_ID": self.plan.plan_id,
            "PY": self.plan.measurement_root + "/.venv/bin/python"},
            text=True, capture_output=True, timeout=5)
        self.assertEqual(2, result.returncode, result.stderr)
        argv = json.loads((Path(self.plan.measurement_root) / "reservation-argv.json").read_text())
        self.assertIn("--execute", argv)
        self.assertIn("--pre-reserve-strict", argv)
        self.assertFalse(list(self.root.rglob("*.CALLED")))

    def test_receipt_checks_mtime_and_finished_clock_bounds(self):
        from joulewise import night_agent_install as engine
        prepared = types.SimpleNamespace(plan=self.plan, plan_path=self.plan_path, python=sys.executable)
        for field, age, finished_offset in (("mtime", 21601, 0),
                ("finished_epoch_s", 0, -21601), ("finished_epoch_s", 0, 61)):
            with self.subTest(field=field, offset=finished_offset):
                path = write_matching_probe_receipt(self.plan_path)
                record = json.loads(path.read_text())
                record["finished_epoch_s"] = time.time() + finished_offset
                path.write_text(json.dumps(record))
                os.utime(path, (time.time() - age, time.time() - age))
                with self.assertRaisesRegex(engine.Refused, field) as raised:
                    engine.validate_probe_receipt(prepared)
                self.assertEqual(2, raised.exception.code)
        path = write_matching_probe_receipt(self.plan_path, now=time.time() + 30)
        self.assertEqual("ok", engine.validate_probe_receipt(prepared)["outcome"])

    def test_receipt_requires_cadence_and_process_type(self):
        from joulewise import night_agent_install as engine
        prepared = types.SimpleNamespace(plan=self.plan, plan_path=self.plan_path,
                                         python=sys.executable)
        path = write_matching_probe_receipt(self.plan_path)
        original = json.loads(path.read_text())
        for key in ("median_ms", "p95_ms", "max_ms", "count"):
            with self.subTest(missing=key):
                changed = json.loads(json.dumps(original))
                changed["cadence"].pop(key)
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(engine.Refused, "cadence"):
                    engine.validate_probe_receipt(prepared)
        for value in (None, "Background", "Standard", "Adaptive"):
            with self.subTest(ProcessType=value):
                changed = json.loads(json.dumps(original))
                changed["ProcessType"] = value
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(engine.Refused, "ProcessType"):
                    engine.validate_probe_receipt(prepared)
        path.write_text(json.dumps(original))
        self.assertEqual("ok", engine.validate_probe_receipt(prepared)["outcome"])

    def test_supervised_probe_success_and_refusal_with_fixture_census(self):
        driver = _load_driver()
        # Real subprocess topology and receipt IO; only the unavailable census
        # seam is faked. The separate FIFO regression proves its worker is gone.
        for mode, outcome, code in (("ok", "ok", None),
                ("refused", "refused", "calibration_ledger_custody_timeout")):
            with self.subTest(mode=mode):
                (Path(self.plan.measurement_root) / "stub-mode").write_text(mode)
                with mock.patch.object(driver, "_probe_group_absent", return_value=True):
                    rc = driver.probe_night(self.plan_path, self.receipt, 5)
                self.assertEqual(0 if outcome == "ok" else 2, rc)
                record = json.loads(self.receipt.read_text())
                self.assertEqual(outcome, record["outcome"])
                self.assertEqual(code, record["refusal_code"])
                self.assertEqual(6, len(record["input_digests"]))

    def test_worker_receipt_is_admitted_by_the_real_install_validator(self):
        """End to end: real `_probe_worker` -> its receipt -> real admission.

        Neither side of this handoff was covered.  `_probe_worker` publishes
        the INSTALLER-side code_digests -- five paths, because the installer
        also pins the driver and the capture writer -- while the reservation
        echoes only the three programs it knows about.  Publishing the
        reservation's three-entry echo instead survived both modules in
        isolation, yet `validate_probe_receipt` compares `probe_bindings`
        field by field, so every real install would have refused with
        "probe receipt code_digests mismatch".  The mutation is only visible
        when one test runs the worker and then feeds its receipt to the
        validator, which is what this does.
        """
        from joulewise import night_agent_install as engine
        driver = _load_driver()
        label = "com.joulewise.night-probe." + self.plan.plan_id
        (Path(self.plan.measurement_root) / "stub-mode").write_text("ok")
        with (mock.patch.object(driver, "_probe_group_absent", return_value=True),
              mock.patch.dict(os.environ, {"JOULEWISE_LAUNCHD_LABEL": label})):
            rc = driver.probe_night(self.plan_path, self.receipt, 15)
        self.assertEqual(0, rc)
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual("ok", receipt["outcome"])
        receipt["ProcessType"] = "Interactive"
        receipt["launch_context"] = {label: {"ProcessType": "Interactive", "rendered_plist_sha256": "0" * 64}
            for label in ("com.joulewise.night", "com.joulewise.night.deadman", label)}
        self.receipt.write_text(json.dumps(receipt))
        # The receipt carries the installer's whole binding, not the
        # reservation's partial echo: the driver and the writer are pinned too.
        self.assertEqual(set(receipt["code_digests"]), set(engine.PROBE_CODE_PATHS))
        self.assertEqual(5, len(engine.PROBE_CODE_PATHS))
        prepared = types.SimpleNamespace(plan=self.plan, plan_path=self.plan_path,
                                         python=sys.executable)
        admitted = engine.validate_probe_receipt(prepared, receipt_path=self.receipt)
        self.assertEqual("ok", admitted["outcome"])
        self.assertEqual(receipt["code_digests"], admitted["code_digests"])

    def test_reservation_echo_below_its_own_floor_is_refused(self):
        """A silently shrunk echo attests to less code than the reservation ran.

        The installer binds a superset of the echo, so the reconciliation can
        only check the entries that are THERE.  Without a floor, an echo that
        dropped to two entries -- or to one -- reconciles exactly as happily
        as the full three, and the receipt would then be published as if the
        missing program had been hashed.  REQUIRED_RESERVATION_ECHO is that
        floor, and the refusal names the path that went missing.
        """
        driver = _load_driver()
        # Spelled literally, not read from the constant, so this test reaches
        # the reconciliation on the base revision instead of stopping at a
        # missing name.
        dropped = "joulewise/calibration_custody_worker.py"
        stub = Path(self.plan.measurement_root) / "scripts/reserve_calibration_window_bracket.py"
        source = stub.read_text()
        # Shrink the fixture reservation's echo to two entries, leaving the
        # two it still names byte-identical to the installer's binding.
        shrunk = source.replace(", '" + dropped + "']", "]")
        self.assertNotEqual(source, shrunk)
        stub.write_text(shrunk)
        (Path(self.plan.measurement_root) / "stub-mode").write_text("ok")
        with mock.patch.object(driver, "_probe_group_absent", return_value=True):
            rc = driver.probe_night(self.plan_path, self.receipt, 15)
        self.assertEqual(2, rc)
        record = json.loads(self.receipt.read_text())
        self.assertEqual("refused", record["outcome"])
        self.assertEqual("probe_receipt_invalid", record["refusal_code"])
        self.assertIn(dropped, record["detail"])
        self.assertIn("missing required reservation entries", record["detail"])
        # The floor is the reservation's own three programs, defined once.
        self.assertIn(dropped, driver.REQUIRED_RESERVATION_ECHO)
        self.assertEqual(3, len(driver.REQUIRED_RESERVATION_ECHO))

    def test_probe_deadline_covers_blocked_binding_read(self):
        import signal
        ledger = Path(self.plan.measurement_root) / "ledger.jsonl"
        ledger.unlink()
        os.mkfifo(ledger)
        # CLI imports precede probe_night's clock and can take several seconds
        # under load. Record its entry separately; worker imports and binding
        # reads remain inside the production deadline (15 s for this test).
        budget = 15.0
        entry_path = self.root / "probe-entry.monotonic"
        bootstrap = """import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from scripts import run_night
entry = Path(sys.argv[2])
probe = run_night.probe_night
def timed_probe(*args, **kwargs):
    temporary = entry.with_suffix('.tmp')
    temporary.write_text(str(time.monotonic()))
    temporary.replace(entry)
    return probe(*args, **kwargs)
run_night.probe_night = timed_probe
raise SystemExit(run_night.main(sys.argv[3:]))
"""
        startup_deadline = time.monotonic() + 30
        process = subprocess.Popen([sys.executable, "-B", "-c", bootstrap,
            str(REPO_ROOT), str(entry_path), "probe", "--plan", str(self.plan_path),
            "--receipt", str(self.receipt), "--timeout-s", str(budget)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            while not entry_path.exists():
                self.assertIsNone(process.poll(), "probe CLI exited before entry")
                self.assertLess(time.monotonic(), startup_deadline, "probe CLI startup stalled")
                time.sleep(0.01)
            started = float(entry_path.read_text())
            bindings_entered = False
            while time.monotonic() < started + budget and process.poll() is None:
                for progress in self.receipt.parent.glob("night-probe-supervisor-*/progress.json"):
                    try:
                        bindings_entered = json.loads(progress.read_text())["phase"] == "bindings"
                    except FileNotFoundError:  # Supervisor cleanup may remove the record.
                        continue
                    if bindings_entered:
                        break
                if bindings_entered:
                    break
                time.sleep(0.01)
            self.assertTrue(bindings_entered, "probe never entered the blocked binding read")
            self.assertLess(time.monotonic() - started, budget)
            # No writer opens the FIFO: after observing bindings, only the
            # production deadline can release this blocked worker.
            try:
                # Supervisor allows a two-second TERM relay grace before KILL,
                # then reaps and censuses the worker group.
                _, stderr = process.communicate(timeout=max(0, started + budget + 5 - time.monotonic()))
            except subprocess.TimeoutExpired:
                self.fail("probe exceeded whole deadline during binding read")
            self.assertLess(time.monotonic() - started, budget + 5)
            self.assertEqual(2, process.returncode, stderr)
            record = json.loads(self.receipt.read_text())
            self.assertEqual("timeout", record["outcome"])
            self.assertEqual("bindings", record["phase"])
            with self.assertRaises(ProcessLookupError):
                os.kill(record["chain_pgid"], 0)
            self.assertFalse((Path(self.plan.measurement_root) / "reservation-argv.json").exists())
        finally:
            if process.poll() is None:
                identity = self.receipt.with_name(self.receipt.name + ".process.json")
                if identity.exists():
                    try:
                        os.killpg(json.loads(identity.read_text())["chain_pgid"], signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    process.kill()
            process.communicate(timeout=2)

    @unittest.skipUnless(probe_census_available(), "process census unavailable in sandbox")
    def test_probe_success_receipt_binds_every_field_without_capture(self):
        completed = self.run_probe()
        self.assertEqual(0, completed.returncode, completed.stderr)
        receipt = json.loads(self.receipt.read_text())
        fields = {"schema", "plan_id", "plan_sha256", "measurement_head", "ledger_head_sha256",
                  "code_digests", "input_digests", "driver_python", "chain_python", "custody_budget_s", "custody_elapsed_s",
                  "observations", "outcome", "refusal_code", "started_epoch_s", "finished_epoch_s", "launchd_label"}
        self.assertTrue(fields <= receipt.keys())
        self.assertEqual("joulewise.night_probe_receipt.v2", receipt["schema"])
        self.assertEqual("ok", receipt["outcome"])
        self.assertEqual(38, receipt["observations"])
        self.assertEqual(120, receipt["custody_budget_s"])
        self.assertEqual(hashlib.sha256(self.plan_path.read_bytes()).hexdigest(), receipt["plan_sha256"])
        for field in ("driver_python", "chain_python"):
            identity = receipt[field]
            self.assertEqual({"path", "version", "sha256"}, identity.keys())
            self.assertEqual(hashlib.sha256(Path(identity["path"]).read_bytes()).hexdigest(), identity["sha256"])
        self.assertFalse(list(self.root.rglob("chain.started")))
        self.assertFalse(list(self.root.rglob("*.CALLED")))
        self.assertFalse(Path(self.plan.custody_root).exists())

    @unittest.skipUnless(probe_census_available(), "process census unavailable in sandbox")
    def test_probe_refused_stub_preserves_calibration_code(self):
        result = self.run_probe("refused")
        self.assertEqual(2, result.returncode, result.stderr)
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual("refused", receipt["outcome"])
        self.assertEqual("calibration_ledger_custody_timeout", receipt["refusal_code"])
        self.assertFalse(list(self.root.rglob("chain.started")))

    @unittest.skipUnless(probe_census_available(), "process census unavailable in sandbox")
    def test_probe_timeout_kills_reservation_and_descendant(self):
        # The stub records its own and its child's process identifiers only
        # after zsh, the chain and a Python interpreter have all started; on
        # this Mac that takes ~0.7 s, and the original 0.3 s deadline killed
        # the chain group before the file existed (hosted CI run 35234610245,
        # and once on the Mac at record 49). The supervisor's timeout has to
        # outlast that startup on a loaded runner, while the whole call stays
        # far inside the 8 s wall assertion below: 3 s is ~4x the observed
        # startup and ~3.4 s of wall, and the poll afterwards turns a slower
        # runner into a named failure instead of a FileNotFoundError.
        started = time.monotonic()
        result = self.run_probe("hang", timeout=3.0)
        self.assertLess(time.monotonic() - started, 8)
        self.assertEqual(2, result.returncode, result.stderr)
        timeout_receipt = json.loads(self.receipt.read_text())
        self.assertEqual("timeout", timeout_receipt["outcome"])
        self.assertIn("custody_elapsed_s=", timeout_receipt["detail"])
        self.assertIn("timeout_s=3", timeout_receipt["detail"])
        stub_pids = Path(self.plan.measurement_root) / "stub-pids.json"
        deadline = time.monotonic() + 2
        while not stub_pids.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(stub_pids.exists(),
            "the stalled reservation never reached its own startup inside the"
            " probe deadline, so this run proved nothing about the kill")
        pids = json.loads(stub_pids.read_text())
        for pid in pids:
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)
        self.assertFalse(list(self.root.rglob("chain.started")))

    def test_chain_exports_the_custody_budget_to_reservation_writer_and_abort(self):
        # The bound travels by INHERITANCE: one export in the chain reaches
        # every process it starts, including the session abort that runs when
        # the window is already spent. The recorder stands in for the
        # interpreter, so each call is captured with the environment it got.
        night = self.root / "marker-output"
        night.mkdir()
        record = self.root / "chain-calls.jsonl"
        recorder = Path(self.plan.measurement_root) / "recorder.zsh"
        recorder.write_text("#!/bin/zsh\nprintf '{\"script\": \"%s\", \"budget\": \"%s\"}\\n'"
            " \"${1:t}\" \"${JOULEWISE_NIGHT_CUSTODY_BUDGET_S-unset}\" >> \"$JW_CHAIN_RECORD\"\nexit 0\n")
        recorder.chmod(0o755)
        environment = {**os.environ, "NIGHT_DIR": str(night),
            "JOULEWISE_NIGHT_PLAN_ID": self.plan.plan_id, "PY": str(recorder),
            "JW_CHAIN_RECORD": str(record), "CUSTODY_BUDGET_S": "45",
            "SETTLE_S": "1", "SLOT_COUNT": "1", "SLOT_CADENCE_S": "1"}
        environment.pop("JOULEWISE_NIGHT_CUSTODY_BUDGET_S", None)
        for capture_budget in ("1", "99999999"):
            # The second run cannot finish a slot inside the window, which is
            # the branch that calls recover_calibration_ledger.py abort-session.
            result = subprocess.run(["/bin/zsh", self.plan.chain_path],
                env={**environment, "SLOT_CAPTURE_BUDGET_S": capture_budget},
                text=True, capture_output=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stderr)
        calls = [json.loads(line) for line in record.read_text().splitlines()]
        self.assertEqual([call["script"] for call in calls],
            ["reserve_calibration_window_bracket.py", "validate_powermetrics_fiducial.py",
             "reserve_calibration_window_bracket.py", "recover_calibration_ledger.py"])
        self.assertEqual({call["budget"] for call in calls}, {"45"})

    def test_driver_environment_drops_an_inherited_custody_budget(self):
        driver = _load_driver()
        with mock.patch.dict(os.environ, {"JOULEWISE_NIGHT_CUSTODY_BUDGET_S": "9999",
                                          "NIGHT_VERIFY_ONLY": "1"}):
            environment = driver._chain_environment(self.plan, self.root / "night")
        self.assertNotIn("JOULEWISE_NIGHT_CUSTODY_BUDGET_S", environment)
        self.assertNotIn("NIGHT_VERIFY_ONLY", environment)
        self.assertEqual(str(getattr(self.plan, "custody_budget_s", 120)),
                         environment["CUSTODY_BUDGET_S"])

    def test_R4_an_inherited_replay_recorder_variable_refuses_the_night(self):
        """R4: the ARM-side fail-closed point of the bench replay (brief D6).

        Counterfactual, executed below: pop the variable instead of raising,
        and the night launches -- silently repaired, with nothing in the
        record to say the shell it was armed from was carrying the switch that
        turns a measurement into a replay of archived frames.
        """

        from scripts import sample_quiet_predicate_evidence as sampler
        driver = _load_driver()
        # The spelling in the driver is a literal (the sampler imports the
        # driver, so importing back would close a cycle); this is what keeps
        # the two from drifting apart and disarming the refusal.
        self.assertEqual(driver.REPLAY_RECORDER_ENV, sampler.REPLAY_ENV)
        self.assertEqual(driver.REPLAY_RECORDER_ENV, "EVIDENCE_POWER_RECORDER_REPLAY")
        with mock.patch.dict(os.environ, {driver.REPLAY_RECORDER_ENV: "/Users/edr/night-archive/x"}):
            with self.assertRaises(ValueError) as caught:
                driver._chain_environment(self.plan, self.root / "night")
        message = str(caught.exception)
        self.assertIn(driver.REPLAY_RECORDER_ENV, message)
        self.assertIn("never runs a replay recorder", message)
        # The counterfactual: a POP leaves a usable environment and no signal.
        with mock.patch.dict(os.environ, {driver.REPLAY_RECORDER_ENV: "/Users/edr/night-archive/x"}):
            popped = dict(os.environ)
            popped.pop(driver.REPLAY_RECORDER_ENV)
            with mock.patch.dict(os.environ, popped, clear=True):
                environment = driver._chain_environment(self.plan, self.root / "night")
        self.assertNotIn(driver.REPLAY_RECORDER_ENV, environment)
        self.assertEqual(environment["NIGHT_PLAN_ID"], self.plan.plan_id)

    def test_R8_no_launchd_template_can_carry_the_replay_variable(self):
        """R8 (half): the agent's environment is the tracked template, and the
        template has no free-form environment to carry the switch in."""
        driver = _load_driver()
        repo = Path(__file__).resolve().parents[1]
        expected_environment = {
            "com.joulewise.night.plist.template": {"PATH"},
            "com.joulewise.night-probe.plist.template": {"PATH", "JOULEWISE_LAUNCHD_LABEL"},
            "com.joulewise.magistrate.plist.template": {
                "PATH", "MAGISTRATE_SESSION_BIN", "MAGISTRATE_WATCHDOG_CUSTODY_ROOT"}}
        templates = sorted((repo / "configs/launchd").glob("*.plist.template"))
        self.assertEqual({t.name for t in templates}, set(expected_environment))
        for template in templates:
            with self.subTest(template=template.name):
                text = template.read_text()
                self.assertNotIn(driver.REPLAY_RECORDER_ENV, text)
                self.assertNotIn("POWER_RECORDER", text)
                # Every substitution the renderer performs is an @@TOKEN@@
                # and no token is an environment KEY, so the rendered plist's
                # environment is exactly the template's.  Pin that set by
                # enumeration: a future template that grows a free-form
                # environment entry fails here rather than quietly acquiring
                # the ability to carry the switch into an armed night.
                body = text.split("<key>EnvironmentVariables</key>")[1].split("</dict>")[0] \
                    if "EnvironmentVariables" in text else ""
                self.assertEqual(set(re.findall(r"<key>(\w+)</key>", body)),
                                 expected_environment[template.name])

    def test_writer_custody_passes_constant_matches_the_memoized_writer(self):
        from joulewise import night_agent_install as engine
        # The worst-case number of whole-corpus custody passes the capture
        # writer can pay for inside one budget, after lane
        # CUSTODY-PASS-MEMO-01. A healthy slot reads twice (the pre-lease
        # preflight pass, and ONE pass under the writer lease that the
        # verified-set memo serves to the enforcing readiness gate and the
        # slot validation), but the count must cover THREE: a repair that
        # moves the head digest costs an honest re-read, and a corrupt corpus
        # costs preflight + the refused under-lease pass + the refusing
        # re-read. The headroom factor is growth margin, not a spare pass.
        self.assertEqual(3, engine.WRITER_CUSTODY_PASSES)
        self.assertEqual(1.5, engine.CUSTODY_HEADROOM_FACTOR)
        self.assertIn("CUSTODY-PASS-MEMO-01", Path(engine.__file__).read_text())

    def test_probe_receipt_gates_writer_passes_and_zero_observations(self):
        from joulewise import night_agent_install as engine
        prepared = types.SimpleNamespace(plan=self.plan, plan_path=self.plan_path,
                                         python=sys.executable)
        ledger = Path(self.plan.measurement_root) / "ledger.jsonl"
        ledger.write_text(json.dumps({"receipt_digest": "a" * 64, "event": "finalization",
                                      "attempt_id": "session-d01"}) + "\n")
        path = write_matching_probe_receipt(self.plan_path)
        record = json.loads(path.read_text())
        self.assertEqual("ok", engine.validate_probe_receipt(prepared)["outcome"])
        # Three writer passes -- the worst case, repaired ledger or corrupt
        # corpus -- times half a pass of growth margin. The arithmetic is
        # spelled out rather than read from the constants, so this same test
        # run against the base implementation (which makes four passes and
        # admits only 20 s) reaches the actual admission and fails.
        self.assertEqual(120.0, record["custody_budget_s"])
        limit = record["custody_budget_s"] / (3 * 1.5)
        # 120 s / 4.5 = 26.67 s: the largest single measured pass that leaves
        # the writer room for its worst case inside one allowance.
        self.assertAlmostEqual(26.667, limit, places=3)
        for elapsed, admitted in ((limit, True), (limit * 1.001, False)):
            with self.subTest(custody_elapsed_s=elapsed):
                record["custody_elapsed_s"] = elapsed
                path.write_text(json.dumps(record))
                if admitted:
                    self.assertEqual("ok", engine.validate_probe_receipt(prepared)["outcome"])
                    continue
                with self.assertRaisesRegex(engine.Refused, "custody_elapsed_s") as raised:
                    engine.validate_probe_receipt(prepared)
                self.assertEqual(2, raised.exception.code)
        record.update(custody_elapsed_s=0.1, observations=0)
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(engine.Refused, "observations") as raised:
            engine.validate_probe_receipt(prepared)
        self.assertEqual(2, raised.exception.code)
        # A ledger that holds no finalized observation yet admits a zero count.
        ledger.write_text(json.dumps({"receipt_digest": "a" * 64}) + "\n")
        path = write_matching_probe_receipt(self.plan_path)
        record = json.loads(path.read_text())
        record["observations"] = 0
        path.write_text(json.dumps(record))
        self.assertEqual("ok", engine.validate_probe_receipt(prepared)["outcome"])


class ProbeSupervisorDetailTests(unittest.TestCase):
    def test_timeout_detail_includes_elapsed_custody_and_bound(self):
        driver = _load_driver()
        process = mock.Mock(pid=4242, stdout=io.BytesIO(), stderr=io.BytesIO())
        process.communicate.side_effect = subprocess.TimeoutExpired("fixture probe", 0.25)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt_path = root / "night_probe_receipt.json"
            with mock.patch.object(driver.subprocess, "Popen", return_value=process), \
                 mock.patch.object(driver, "_stop_probe_group", return_value=True):
                code = driver.probe_night(root / "night_plan.json", receipt_path, timeout_s=0.25)
            self.assertEqual(2, code)
            receipt = json.loads(receipt_path.read_bytes())
            self.assertEqual("calibration_ledger_custody_timeout", receipt["refusal_code"])
            self.assertIn("supervisor timeout; custody_elapsed_s=", receipt["detail"])
            self.assertIn("timeout_s=0.25", receipt["detail"])
            self.assertGreaterEqual(receipt["custody_elapsed_s"], 0)


class PackNightProducerTests(unittest.TestCase):
    """Real driver/file custody with mocked ARM author and live probes only."""
    def setUp(self):
        from joulewise import arm_readiness as readiness, arm_readiness_evidence_t0 as author
        self.readiness, self.author = readiness, author
        self.driver = _load_driver()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.custody = (self.root / "home/night-custody/rehearsal-t0-unattended-producer-table"
                        if getattr(self, "_rehearsal_layout", False) else self.root / "custody")
        self.custody.mkdir(parents=True)
        self.pack = self.root / "pack-test"
        self.pack.mkdir()
        self.pack_custody = self.custody / self.pack.name
        self.inputs = self.pack_custody / "arm_readiness.t0.inputs"
        self.inputs.mkdir(parents=True)
        self.chain = self.root / "window-chain.zsh"
        self.chain.write_bytes(b"echo fixture\n")
        self.sidecar = self.root / "chain.sha256"
        self.sidecar.write_text(readiness.sha256_bytes(self.chain.read_bytes()) + "  window-chain.zsh\n")
        self.env = self.root / "window.env"
        self.env.write_bytes(b"fixture\n")
        self.table = self.custody / "table.json"
        self.table.write_bytes(b"{}\n")
        self.authorization = {"purpose": "G2B_SHAKEDOWN", "attempt_id": "pack-plan/1", "claim_eligible": False,
            "pack_sha256": "a" * 64, "permitted_chain_sha256": readiness.sha256_bytes(self.chain.read_bytes()),
            "permitted_blocks": 1, "authority": "D-171 §3"}
        self.confirmation = {"table_path": str(self.table), "table_sha256": readiness.sha256_bytes(self.table.read_bytes()),
            "transcript_sha256": "c" * 64, "confirmed_at": {"epoch_s": 0.0, "iso8601_utc": "1970-01-01T00:00:00.000000Z"}}
        auth_ref = self.write(self.custody / "authorization.json", self.authorization)
        confirmation_ref = self.write(self.custody / "confirmation.json", self.confirmation)
        self.manifest = self.inputs / "launch-manifest.json"
        self.write(self.manifest, {"schema_version": readiness.LAUNCH_MANIFEST_SCHEMA})
        self.write(self.inputs / "arm-context.json", {"custody_root": str(self.custody)})
        self.plan = night_gate.NightPlan(plan_id="pack-plan", receipt_class="TRANSACTION_PACK",
            t0_epoch_s=datetime(2026, 9, 2, 1, 0).timestamp(), window_max_s=60,
            authored_epoch_s=datetime(2026, 9, 2, 0, 59).timestamp(), repo_head=HEAD,
            measurement_root=str(REPO_ROOT), measurement_head=HEAD, chain_path=str(self.chain),
            chain_sha256_path=str(self.sidecar), custody_root=str(self.custody), registration_path=None,
            pack_night={"pack_id": self.pack.name, "pack_root": str(self.pack), "pack_sha256": "a" * 64,
                        "attempt_ordinal": 1, "authorization_record": auth_ref, "confirmation_record": confirmation_ref})
        self.plan_path = write_night_plan(self.custody / "night_plan.json", self.plan)
        self.raw = self.plan_path.read_bytes()
        self.events = []
        self.probe_source = ProbeSource(self.plan.t0_epoch_s + 1, self.plan.measurement_root)
        self.probe_source.plan_path = self.plan_path
        original_probes = self.probe_source.probes()
        def probe(argv):
            self.events.append("census" if argv == night_gate.AGENT_CENSUS_ARGV else "probe")
            return original_probes.run(argv)
        self.probes = replace(original_probes, run=probe)
        for target, name, replacement in (
            (readiness, "committed_pack_tree_sha256", mock.Mock(return_value="a" * 64)),
            (readiness, "_current_boot_session_id", mock.Mock(return_value=BOOT_UUID)),
            (readiness, "scan_receipt_namespace", mock.Mock(return_value=[])),
            (readiness, "_verify_arm_receipt", mock.Mock(side_effect=self.verify)),
            (readiness, "generate_arm_receipt", mock.Mock(side_effect=self.arm)),
            (readiness, "_attested_launch_artifact_references", mock.Mock(side_effect=lambda *a, **k: self.refs())),
            (author, "author_arm_readiness_evidence_t0", mock.Mock(side_effect=self.t0)),
            (self.driver, "make_probes", mock.Mock(return_value=self.probes)),
            (self.driver, "_resolve_courier_bin", mock.Mock(return_value=(Path('/fixture/courier'), None, None))),
            (self.driver, "_finish_reporting", lambda custody, night, plan, code, *a, **k: code),
            (self.driver, "observe_identity", mock.Mock(return_value=Identity("LIVE", "fixture-start"))),
        ):
            patch = mock.patch.object(target, name, replacement)
            patch.start()
            self.addCleanup(patch.stop)
        self.arm_path = self.pack_custody / "arm_readiness.receipts/arm-0001.json"

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.readiness.render_json(value))
        return {"path": str(path), "sha256": self.readiness.sha256_bytes(path.read_bytes())}

    def refs(self):
        return {key: {"path": str(path), "sha256": self.readiness.sha256_bytes(path.read_bytes())}
                for key, path in (("launch_manifest", self.manifest), ("window_environment", self.env), ("window_chain", self.chain))}

    def t0(self, pack, custody):
        self.events.append("T0")
        inputs = [self.write(self.inputs / filename, {"capture": step}) for step, filename in self.author._CAPTURE_FILES.items()]
        source = self.write(self.pack_custody / "arm_readiness.t0.sources/source.json", {"input_artifacts": inputs})
        self.evidence = []
        paths = []
        for row in self.author._EXPECTED_ROWS:
            path = self.pack_custody / self.author._EVIDENCE_DIRECTORY / self.author._receipt_name(row)
            ref = self.write(path, {"facts": [{"source_kind": "PROBE", "source_path": str(Path(source["path"]).relative_to(self.pack_custody)), "source_sha256": source["sha256"]}]})
            self.evidence.append({"namespace": "WINDOW_CUSTODY", "path": str(path.relative_to(self.pack_custody)), "sha256": ref["sha256"]})
            paths.append(str(path))
        return {"status": "PASS", "receipt_paths": paths}

    def arm(self, pack, context, custody, **kwargs):
        self.events.append("ARM")
        self.arm_value = {"status": "PASS", "arm_disposition": "GO", "receipt_id": "arm-0001",
            "boot_session_id": BOOT_UUID, "valid_until_monotonic_ns": time.monotonic_ns() + 10**12,
            "pack": {"pack_root": str(self.pack), "pack_sha256": "a" * 64, "pack_id": self.pack.name,
                     "plan_id": self.plan.plan_id, "window_id": getattr(self, "_window_id", "production-window")},
            "reviewed_main": {"head_commit": HEAD},
            "arm_context": context, "evidence": self.evidence}
        ref = self.write(self.arm_path, self.arm_value)
        return {"status": "PASS", "arm_disposition": "GO", "receipt_path": ref["path"], "receipt_sha256": ref["sha256"]}

    def verify(self, pack, path, **kwargs):
        self.events.append("VERIFY")
        self.assertEqual(self.arm_path, path)
        self.assertIs(kwargs["require_unconsumed"], True)
        self.assertEqual(self.confirmation["table_sha256"], kwargs["expected_confirmation_digest"])
        return {"status": "PASS", "arm_disposition": "GO", "receipt_sha256": self.readiness.sha256_bytes(Path(path).read_bytes())}

    def run_driver(self):
        calls = []
        def spawn(command, **kwargs):
            self.events.append("LAUNCH")
            self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
            calls.append(command)
            return FakeProcess(command, return_code=0)
        read_bytes = Path.read_bytes
        def observed_read(path):
            if path == self.plan_path:
                self.events.append("PLAN_BYTES")
            return read_bytes(path)
        with mock.patch.object(self.driver.subprocess, "Popen", side_effect=spawn), mock.patch.object(Path, "read_bytes", observed_read):
            code = self.driver.run_night(self.plan_path)
        return code, calls

    def test_driver_self_authors_arm_before_go_and_pins_all_eight_flags(self):
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_GO, code)
        self.assertEqual("census", self.events[0])
        self.assertLess(self.events.index("PLAN_BYTES"), self.events.index("T0"))
        self.assertLess(self.events.index("T0"), self.events.index("ARM"))
        self.assertLess(self.events.index("ARM"), self.events.index("VERIFY"))
        self.assertLess(self.events.index("VERIFY"), self.events.index("LAUNCH"))
        go_path = self.custody / "night/go_receipt.json"
        go = json.loads(go_path.read_bytes())
        self.assertEqual({"schema_version", "receipt_id", "receipt_class", "purpose", "plan_id", "plan_sha256",
            "pack_id", "pack_sha256", "arm_receipt", "boot_session_id", "t0_evidence", "t0_evidence_set_sha256",
            "launch_manifest_sha256", "window_environment_sha256", "window_chain_sha256", "repo_head",
            "measurement_root", "measurement_head", "confirmation_record", "authorization", "census",
            "issued_epoch_s", "issued_monotonic_ns", "valid_until_monotonic_ns", "conditions", "verdict"}, set(go))
        self.assertEqual("joulewise.pack_night_go_receipt.v1", go["schema_version"])
        self.assertEqual("TRANSACTION_PACK", go["receipt_class"])
        self.assertEqual("G2B_SHAKEDOWN", go["purpose"])
        for key in ("plan_id", "repo_head", "measurement_root", "measurement_head"):
            self.assertEqual(getattr(self.plan, key), go[key])
        self.assertEqual(self.plan.pack_night["confirmation_record"], go["confirmation_record"])
        self.assertEqual({**self.plan.pack_night["authorization_record"], **{key: self.authorization[key] for key in ("purpose", "attempt_id", "claim_eligible")}}, go["authorization"])
        self.assertEqual({"receipt_id": "arm-0001", "sha256": self.readiness.sha256_bytes(self.arm_path.read_bytes()), "valid_until_monotonic_ns": self.arm_value["valid_until_monotonic_ns"]}, go["arm_receipt"])
        self.assertEqual(self.readiness.sha256_bytes(self.readiness.render_json(go["t0_evidence"])), go["t0_evidence_set_sha256"])
        for key, ref in self.refs().items():
            self.assertEqual(ref["sha256"], go[key + "_sha256"])
        if hasattr(self.readiness, "validate_pack_night_go_receipt"):
            self.readiness.validate_pack_night_go_receipt(go)
        self.assertIs(type(go["issued_epoch_s"]), float)
        self.assertIs(type(go["issued_monotonic_ns"]), int)
        self.assertIs(type(go["valid_until_monotonic_ns"]), int)
        self.assertEqual(["C1", "C2", "C3", "C4", "C5"], [row["condition_id"] for row in go["conditions"]])
        self.assertEqual(["PASS"] * 5, [row["status"] for row in go["conditions"]])
        self.assertEqual([None] * 5, [row["basis"] for row in go["conditions"]])
        self.assertEqual(21, len(go["t0_evidence"]))
        census_ref = next(row for row in go["conditions"] if row["condition_id"] == "C3")["evidence"][0]
        census_path = self.custody / census_ref["path"]
        census_raw = census_path.read_bytes()
        census = json.loads(census_raw)
        self.assertEqual(go["census"]["monotonic_ns"], census["monotonic_ns"])
        self.assertEqual("", census["stdout"])
        self.assertEqual(1, census["exit_code"])
        self.assertEqual(self.readiness.sha256_bytes(census_raw), census_ref["sha256"])
        with (self.custody / "night/censuses.jsonl").open("a") as journal:
            journal.write("{}\n")
        self.assertEqual(census_raw, census_path.read_bytes())
        self.assertEqual(0o600, go_path.stat().st_mode & 0o777)
        self.assertEqual(self.readiness.sha256_bytes(self.raw), go["plan_sha256"])
        self.assertEqual({"C1", "C2", "C3", "C4", "C5"}, {row["condition_id"] for row in go["conditions"] if row["status"] == "PASS"})
        self.assertEqual([], night_gate.validate_receipt(json.loads((self.custody / "night/receipt.json").read_bytes())))
        argv = calls[0]
        expected = {"--pack-root": str(self.pack), "--arm-receipt": str(self.arm_path),
            "--arm-readiness-custody-root": str(self.custody), "--launch-manifest": str(self.manifest),
            "--night-plan": str(self.plan_path), "--go-receipt": str(go_path),
            "--step6-confirmation-table": str(self.table), "--expected-confirmation-digest": self.confirmation["table_sha256"]}
        self.assertEqual(expected, dict(zip(argv[2::2], argv[3::2])))
        self.assertEqual(8, len(argv[2::2]))
        # Independent of seat 3's parser landing; missing ANY transport flag
        # breaks the exact argv assertion without requiring a staged parser.
        self.assertEqual(str(REPO_ROOT / "scripts/launch_window.py"), argv[1])
        with self.assertRaises(FileExistsError):
            self.driver._write_bytes_exclusive(go_path, b"replacement")
        self.assertEqual(go, json.loads(go_path.read_bytes()))

    def test_gate_reauthenticates_c1_and_c2_despite_forged_driver_pass_rows(self):
        prepared = self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        state = self.driver._author_pack_arm(self.plan, prepared)
        forged = {key: night_gate.ConditionRow(key, "PASS", None, (), {"forged": True})
                  for key in ("C1", "C2")}
        def evaluate():
            return night_gate.evaluate_night(self.plan, self.probes,
                pack_arm_receipt=state["path"], pack_conditions=forged)
        receipt = evaluate()
        self.assertEqual("GO", receipt.verdict)
        self.assertEqual(["PASS"] * 5, [row.status for row in receipt.conditions])
        self.assertNotIn("forged", receipt.conditions[0].measured)
        self.assertNotIn("forged", receipt.conditions[1].measured)
        for key, expected_row in (("authorization_record", 0), ("confirmation_record", 0)):
            path = Path(self.plan.pack_night[key]["path"])
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            receipt = evaluate()
            self.assertEqual("REFUSED", receipt.verdict)
            self.assertEqual("launch_go_receipt_invalid", receipt.refusal.reason)
            self.assertIn(key, receipt.refusal.detail)
            self.assertEqual("FAIL", receipt.conditions[expected_row].status)
            path.write_bytes(original)
        with mock.patch.object(self.readiness, "_verify_arm_receipt",
                side_effect=self.readiness.ArmReadinessError("readiness_dependency_refused", "forged ARM")):
            receipt = evaluate()
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("PASS", receipt.conditions[0].status)
        self.assertEqual("FAIL", receipt.conditions[1].status)
        self.assertIn("forged ARM", receipt.refusal.detail)
        missing = night_gate.evaluate_night(self.plan, self.probes, pack_conditions=forged)
        self.assertEqual("launch_go_receipt_missing", missing.refusal.reason)
        self.assertEqual("FAIL", missing.conditions[1].status)
        path = Path(state["authored"]["receipt_paths"][0])
        path.write_bytes(path.read_bytes() + b" ")
        receipt = evaluate()
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("FAIL", receipt.conditions[1].status)
        self.assertIn("t0_evidence", receipt.refusal.detail)

    def test_pack_standard_refusal_receipt_preserves_each_actual_cause(self):
        for reason, receipt_reason in (
            ("night_courier_unavailable", "night_probe_error"),
            ("night_plan_overruns_deadman", "night_probe_error"),
            ("night_chain_digest_mismatch", "night_chain_digest_mismatch"),
            ("night_chain_already_started", "night_probe_error"),
            ("launch_go_receipt_missing", "launch_go_receipt_missing"),
            ("launch_go_receipt_invalid", "launch_go_receipt_invalid"),
        ):
            with self.subTest(reason=reason):
                custody = self.root / reason
                night = custody / "night"
                night.mkdir(parents=True)
                plan = replace(self.plan, custody_root=str(custody))
                self.driver._write_standard_refusal_result(custody, night, plan, reason,
                    "cause-specific detail", self.plan.t0_epoch_s, 123)
                receipt = json.loads((night / "receipt.json").read_bytes())
                refusal = json.loads((night / "refusal.json").read_bytes())
                self.assertEqual(receipt_reason, receipt["refusal"]["reason"])
                self.assertEqual(reason, refusal["refusal"]["reason"])
                self.assertEqual("cause-specific detail", refusal["refusal"]["detail"])
                self.assertEqual(
                    f"{refusal['refusal']['reason']}: {refusal['refusal']['detail']}",
                    receipt["refusal"]["detail"],
                )
                result = json.loads((night / "result.json").read_bytes())
                self.assertEqual(reason, result["aborted_reason"])
                self.assertEqual("REFUSED", receipt["verdict"])
                self.assertEqual([], night_gate.validate_receipt(receipt))
                self.assertFalse((night / "go_receipt.json").exists())

    def test_gate_checks_authorization_fields_and_confirmation_bytes(self):
        for key, changes in (
            ("authorization_record", {"attempt_id": "another-plan/1"}),
            ("authorization_record", {"purpose": "unruled"}),
            ("authorization_record", {"claim_eligible": True}),
            ("authorization_record", {"permitted_blocks": 2}),
            ("authorization_record", {"authority": "unruled"}),
            ("confirmation_record", {"table_sha256": "0" * 64}),
            ("confirmation_record", {"confirmed_at": {"epoch_s": "0", "iso8601_utc": "1970-01-01T00:00:00.000000Z"}}),
        ):
            with self.subTest(key=key, changes=changes):
                path = Path(self.plan.pack_night[key]["path"])
                original = path.read_bytes()
                ref = self.write(path, {**json.loads(original), **changes})
                changed = replace(self.plan, pack_night={**self.plan.pack_night, key: ref})
                receipt = night_gate.evaluate_night(changed, self.probes)
                self.assertEqual("REFUSED", receipt.verdict)
                self.assertEqual("launch_go_receipt_invalid", receipt.refusal.reason)
                self.assertIn(key, receipt.refusal.detail)
                self.assertEqual("FAIL", receipt.conditions[0].status)
                path.write_bytes(original)
        for key in ("authorization_record", "confirmation_record"):
            path = Path(self.plan.pack_night[key]["path"])
            original = path.read_bytes()
            path.unlink()
            receipt = night_gate.evaluate_night(self.plan, self.probes)
            self.assertEqual("launch_go_receipt_missing", receipt.refusal.reason)
            self.assertIn(key, receipt.refusal.detail)
            path.write_bytes(original)

    def test_no_go_on_arm_refusal(self):
        self.readiness.generate_arm_receipt.side_effect = lambda *a, **k: {"status": "REFUSE", "arm_disposition": "NO_GO"}
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        receipt = json.loads((self.custody / "night/receipt.json").read_bytes())
        self.assertEqual([], night_gate.validate_receipt(receipt))
        self.assertIn("NO_GO", receipt["refusal"]["detail"])

    def test_first_census_refusal_prevents_preparation_and_arm(self):
        self.probe_source.census_responses = [_probe(night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="42 claude\n")]
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.author.author_arm_readiness_evidence_t0.assert_not_called()
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())

    def test_idle_agent_hit_preserves_initial_refusal_code(self):
        self.probe_source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="20 claude\n")
        ]
        with mock.patch.object(self.driver, "_prepare_pack_night") as prepare:
            code, calls = self.run_driver()
        self.assertEqual(3, code)
        self.assertEqual([], calls)
        self.assertEqual(["census", "PLAN_BYTES"], self.events[:2])
        prepare.assert_not_called()
        self.author.author_arm_readiness_evidence_t0.assert_not_called()
        self.readiness.generate_arm_receipt.assert_not_called()
        night = self.custody / "night"
        for name in ("receipt.json", "refusal.json"):
            record = json.loads((night / name).read_text())
            self.assertEqual("night_refused_agent_present", record["refusal"]["reason"])
        result = json.loads((night / "result.json").read_text())
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("night_refused_agent_present", result["aborted_reason"])
        census = json.loads((night / "censuses.jsonl").read_text().splitlines()[0])
        self.assertEqual(["/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3"], census["argv"])
        self.assertEqual("20 claude\n", census["stdout"])
        self.assertFalse((night / "go_receipt.json").exists())

    def test_pack_digest_mismatch_at_preparation_and_go_refuses_without_go(self):
        self.readiness.committed_pack_tree_sha256.return_value = "f" * 64
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "pack_root.pack_sha256"):
            self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        self.readiness.committed_pack_tree_sha256.return_value = "a" * 64
        original = self.arm
        def mutate_after_arm(*args, **kwargs):
            result = original(*args, **kwargs)
            self.readiness.committed_pack_tree_sha256.return_value = "f" * 64
            return result
        self.readiness.generate_arm_receipt.side_effect = mutate_after_arm
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        self.assertIn("pack_root.pack_sha256", (self.custody / "night/receipt.json").read_text())

    def test_each_plan_record_digest_and_pinned_plan_swap_refuse(self):
        for key in ("authorization_record", "confirmation_record"):
            path = Path(self.plan.pack_night[key]["path"])
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            with self.subTest(key=key), self.assertRaisesRegex(self.driver.PackNightRefusal, key):
                self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
            path.write_bytes(original)
        self.plan_path.write_bytes(self.raw + b" ")
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "plan_sha256"):
            self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)

    def test_selected_old_arm_and_higher_receipt_and_consumption_refuse(self):
        self.arm_path.parent.mkdir()
        self.arm_path.write_bytes(b"{}")
        prepared = self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "self-written"):
            self.driver._author_pack_arm(self.plan, prepared)
        self.readiness.scan_receipt_namespace.return_value = [{"number": 2, "receipt": {"boot_session_id": BOOT_UUID}}]
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "higher-numbered"):
            self.driver._pack_no_retry(self.plan, BOOT_UUID, self.arm_path)
        self.write(self.pack_custody / "arm_readiness.consumptions/other.consumed.json", {"boot_session_id": BOOT_UUID})
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "consumption this boot"):
            self.driver._pack_no_retry(self.plan, BOOT_UUID, self.arm_path)

    def test_second_manifest_missing_symlink_and_attested_digest_refuse(self):
        for field in ("duplicate", "missing", "symlink", "digest"):
            raw = self.manifest.read_bytes()
            extra = self.inputs / "second-manifest.json"
            if field == "duplicate":
                self.write(extra, {"schema_version": self.readiness.LAUNCH_MANIFEST_SCHEMA})
            elif field == "missing":
                self.manifest.unlink()
            elif field == "symlink":
                self.manifest.unlink()
                extra.write_bytes(raw)
                self.manifest.symlink_to(extra)
            else:
                refs = self.refs()
                refs["launch_manifest"]["sha256"] = "0" * 64
                self.readiness._attested_launch_artifact_references.side_effect = lambda *a, **k: refs
            with self.subTest(field=field), self.assertRaisesRegex(self.driver.PackNightRefusal, "launch_manifest") as caught:
                self.driver._pack_launch_references(self.plan, {})
            self.assertEqual("launch_go_receipt_missing" if field == "missing" else "launch_go_receipt_invalid", caught.exception.reason)
            self.manifest.unlink(missing_ok=True)
            extra.unlink(missing_ok=True)
            self.manifest.write_bytes(raw)

    def test_machine_refusal_and_refused_receipt_never_publish_go(self):
        self.probe_source.results[night_gate.HID_IDLE_ARGV] = _probe(night_gate.HID_IDLE_ARGV, stdout="1\n")
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        refused = self.driver._pack_refused_receipt(self.plan, self.driver.PackNightRefusal("fixture refusal"), self.probes)
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "refused night"):
            self.driver._produce_pack_go(self.plan, self.plan_path, self.raw, {}, {}, refused, self.probes)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())

    def test_pack_root_must_match_the_written_arm_root_and_digest(self):
        arm = {"pack": {"pack_root": str(self.pack), "pack_id": self.pack.name, "pack_sha256": "a" * 64}}
        self.assertEqual(self.pack, self.driver._pack_digest(self.plan, arm))
        for key, value in (("pack_root", str(self.root / "other")), ("pack_sha256", "0" * 64), ("pack_id", "other")):
            changed = {"pack": {**arm["pack"], key: value}}
            with self.subTest(key=key), self.assertRaisesRegex(self.driver.PackNightRefusal, "arm_receipt.pack"):
                self.driver._pack_digest(self.plan, changed)

    def test_t0_inventory_cannot_omit_add_or_substitute_author_or_capture_bytes(self):
        prepared = self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        state = self.driver._author_pack_arm(self.plan, prepared)
        self.assertEqual(21, len(self.driver._pack_evidence(self.plan, state)))
        paths = state["authored"]["receipt_paths"]
        for replacement in (paths[:-1], paths + [paths[0]], paths[:-1] + [str(self.inputs / "arm-context.json")]):
            changed = {**state, "authored": {**state["authored"], "receipt_paths": replacement}}
            with self.subTest(replacement=replacement), self.assertRaisesRegex(self.driver.PackNightRefusal, "t0_evidence"):
                self.driver._pack_evidence(self.plan, changed)
        evidence = state["arm"]["evidence"]
        receipt = next(item for item in evidence if str(self.custody / self.pack.name / item["path"]) == paths[0])
        for replacement in ([item for item in evidence if item is not receipt],
                            evidence + [receipt],
                            [{**item, "path": item["path"] + ".substituted"} if item is receipt else item for item in evidence]):
            changed = {"arm": {**state["arm"], "evidence": replacement}}
            with self.subTest(evidence=replacement), self.assertRaisesRegex(self.driver.PackNightRefusal, "t0_evidence"):
                self.driver._pack_evidence(self.plan, changed)
        for path in (Path(paths[0]), self.inputs / next(iter(self.author._CAPTURE_FILES.values()))):
            raw = path.read_bytes()
            path.write_bytes(raw + b" ")
            with self.subTest(path=path), self.assertRaisesRegex(self.driver.PackNightRefusal, "t0_evidence"):
                self.driver._pack_evidence(self.plan, state)
            path.write_bytes(raw)

    def test_go_producer_enforces_two_by_two_purpose_window_table(self):
        for rehearsal in (False, True):
            for prefixed in (False, True):
                with self.subTest(rehearsal=rehearsal, prefixed=prefixed):
                    case = PackNightProducerTests()
                    case._rehearsal_layout = True
                    case.setUp()
                    try:
                        measurement = case.root / "JouleWise-rehearsal-producer-table"
                        measurement.mkdir()
                        case._window_id = case.custody.name if prefixed else "production-window"
                        case.authorization.update(purpose="T0_REHEARSAL" if rehearsal else "CAMPAIGN_TRANSACTION",
                            authority="T0-UNATTENDED-01" if rehearsal else "V5-TRANSACTION-GO-01")
                        ref = case.write(case.custody / "authorization.json", case.authorization)
                        case.plan = replace(case.plan, measurement_root=str(measurement),
                            pack_night={**case.plan.pack_night, "authorization_record": ref})
                        write_night_plan(case.plan_path, case.plan)
                        inventory = [{"deployment_id": "production", "measurement_root": str(case.root / "production"),
                            "custody_root": None, "ledger_path": None, "notes": "synthetic"}]
                        with mock.patch.object(Path, "home", return_value=case.root / "home"), \
                             mock.patch.object(case.readiness, "__file__", str(measurement / "joulewise/arm_readiness.py")), \
                             mock.patch.object(case.readiness, "_production_inventory", return_value=inventory):
                            code, calls = case.run_driver()
                        path = case.custody / "night/go_receipt.json"
                        if rehearsal == prefixed:
                            self.assertEqual(code, case.driver.EXIT_GO)
                            go = json.loads(path.read_bytes())
                            case.readiness.validate_pack_night_go_receipt(go)
                            self.assertEqual(go["purpose"], case.authorization["purpose"])
                            self.assertIs(go["authorization"]["claim_eligible"], False)
                            self.assertEqual(len(go), 26)
                            self.assertEqual(len(calls), 1)
                        else:
                            self.assertEqual(code, case.driver.EXIT_REFUSED)
                            self.assertFalse(path.exists())
                            self.assertEqual(calls, [])
                            refusal = json.loads((case.custody / "night/refusal.json").read_bytes())
                            self.assertIn("rehearsal_purpose_on_production_id" if rehearsal else "purpose", str(refusal))
                    finally:
                        case.doCleanups()

    def test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule(self):
        home = self.root / "home"
        window_id = "rehearsal-t0-unattended-test"
        custody = home / "night-custody" / window_id
        custody.mkdir(parents=True)
        # Keep launcher identity real; this test isolates the root predicates.
        measurement = Path(self.readiness.__file__).resolve().parents[1]
        claim = self.root / "isolated-claim"
        claim.mkdir()
        plan = replace(self.plan, custody_root=str(custody), measurement_root=str(measurement))
        arm = {"pack": {"window_id": window_id}, "arm_context": {"custody_root": str(custody), "claim_runs_root": str(claim)}}
        inventory = [{"deployment_id": "production", "measurement_root": str(self.root / "production"), "custody_root": None, "ledger_path": None, "notes": "synthetic"}]
        with mock.patch.object(Path, "home", return_value=home), mock.patch.object(self.readiness, "_production_inventory", return_value=inventory), mock.patch.object(self.readiness, "REHEARSAL_CLONE_PREFIX", measurement.name):
            self.driver._pack_rehearsal_roots(plan, arm, "T0_REHEARSAL")
            # Every non-custody ARM path may live inside this rehearsal child.
            for key in ("claim_runs_root", "bound_runs_root", "quarantine_root",
                        "claim_backup_destination", "bound_backup_destination", "waiver_path"):
                own = custody / key
                own.mkdir()
                changed = {**arm, "arm_context": {**arm["arm_context"], key: str(own)}}
                self.driver._pack_rehearsal_roots(plan, changed, "T0_REHEARSAL")
                for production in (home / "night-custody/magistrate" / key,
                                   self.root / "production" / key):
                    production.mkdir(parents=True)
                    changed = {**arm, "arm_context": {**arm["arm_context"], key: str(production)}}
                    with self.subTest(key=key, production=production), self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                        self.driver._pack_rehearsal_roots(plan, changed, "T0_REHEARSAL")
            # Exercise equality and both containment directions without changing
            # the authenticated launcher or creating paths in the real checkout.
            for production in (measurement, measurement / "runs", measurement.parent):
                with self.subTest(production=production), self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                    with mock.patch.object(self.readiness, "_production_inventory", return_value=[{**inventory[0], "measurement_root": str(production)}]):
                        self.driver._pack_rehearsal_roots(plan, arm, "T0_REHEARSAL")
            for root in (custody.parent, custody / window_id, custody.parent / "another"):
                root.mkdir(parents=True, exist_ok=True)
                with self.subTest(root=root), self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                    self.driver._pack_rehearsal_roots(replace(plan, custody_root=str(root)), arm, "T0_REHEARSAL")
            for field in ("measurement_root", "custody_root"):
                alias = self.root / (field + "-alias")
                alias.symlink_to(Path(getattr(plan, field)), target_is_directory=True)
                with self.subTest(field=field), self.assertRaisesRegex(self.driver.PackNightRefusal, field):
                    self.driver._pack_rehearsal_roots(replace(plan, **{field: str(alias)}), arm, "T0_REHEARSAL")
            with self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                self.driver._pack_rehearsal_roots(replace(plan, custody_root=str(measurement)), arm, "T0_REHEARSAL")
            changed = {**arm, "arm_context": {**arm["arm_context"], "claim_runs_root": str(custody.parent)}}
            with self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                self.driver._pack_rehearsal_roots(plan, changed, "T0_REHEARSAL")
            for purpose, changed_arm, detail in (
                ("G2B_SHAKEDOWN", arm, "purpose"),
                ("T0_REHEARSAL", {**arm, "pack": {"window_id": "production"}}, "rehearsal_purpose_on_production_id"),
            ):
                with self.assertRaisesRegex(self.driver.PackNightRefusal, detail) as caught:
                    self.driver._pack_rehearsal_roots(plan, changed_arm, purpose)
                self.assertEqual("launch_go_receipt_invalid", caught.exception.reason)

    def test_post_cutoff_t0_inside_measurement_custody_refuses_disjointness_end_to_end(self):
        case = PackNightProducerTests()
        case._rehearsal_layout = True
        case.setUp()
        try:
            cutoff = night_gate.MEASUREMENT_ROOT_CUSTODY_CUTOFF_EPOCH_S
            custody_root = case.root / "measurement"
            measurement = custody_root / "JouleWise-rehearsal-inside-custody"
            measurement.mkdir(parents=True)
            case._window_id = case.custody.name
            case.authorization.update(purpose="T0_REHEARSAL", authority="T0-UNATTENDED-01")
            ref = case.write(case.custody / "authorization.json", case.authorization)
            case.plan = replace(case.plan, t0_epoch_s=cutoff + 60, authored_epoch_s=cutoff,
                                measurement_root=str(measurement),
                                pack_night={**case.plan.pack_night, "authorization_record": ref})
            case.plan_path = write_night_plan(case.plan_path, case.plan)
            case.raw = case.plan_path.read_bytes()
            case.probe_source.now_epoch_s = cutoff + 61
            inventory = [{"deployment_id": "production", "measurement_root": str(custody_root),
                          "custody_root": None, "ledger_path": None, "notes": "synthetic"}]
            with mock.patch.object(night_gate, "MEASUREMENT_ROOT_CUSTODY_ROOT", custody_root), \
                 mock.patch.object(Path, "home", return_value=case.root / "home"), \
                 mock.patch.object(case.readiness, "_authenticate_launcher_identity", return_value=measurement), \
                 mock.patch.object(case.readiness, "_production_inventory", return_value=inventory):
                code, calls = case.run_driver()
            self.assertEqual(case.driver.EXIT_REFUSED, code)
            self.assertEqual([], calls)
            self.assertFalse((case.custody / "night/go_receipt.json").exists())
            receipt = json.loads((case.custody / "night/receipt.json").read_bytes())
            self.assertEqual("launch_go_receipt_invalid", receipt["refusal"]["reason"])
            self.assertIn("rehearsal_roots_not_disjoint: measurement_root", receipt["refusal"]["detail"])
        finally:
            case.doCleanups()

    def test_pack_rehearsal_gate_refuses_another_measurement_checkout(self):
        other = self.root / (self.readiness.REHEARSAL_CLONE_PREFIX + "other")
        other.mkdir()
        plan = replace(self.plan, measurement_root=str(other))
        arm = {"pack": {"window_id": "rehearsal-t0-unattended-test"}, "arm_context": {}}
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "launcher is not the planned clone") as caught:
            self.driver._pack_rehearsal_roots(plan, arm, "T0_REHEARSAL")
        self.assertEqual("launch_go_receipt_invalid", caught.exception.reason)

    def test_pack_gate_requires_absolute_strict_custody_root(self):
        alias = self.root / "custody-alias"
        alias.symlink_to(self.custody, target_is_directory=True)
        for root in ("relative-custody", str(self.root / "missing-custody"), str(alias)):
            with self.subTest(root=root), self.assertRaisesRegex(night_gate.PackNightRefusal, "custody_root") as caught:
                night_gate._authenticate_pack_records(replace(self.plan, custody_root=root))
            self.assertEqual(caught.exception.reason, "launch_go_receipt_invalid")

    def test_window_expiring_during_final_authentication_emits_no_go(self):
        def expire(*args, **kwargs):
            self.probe_source.now_epoch_s = self.plan.t0_epoch_s + self.plan.window_max_s + 1
            return self.refs()
        self.readiness._attested_launch_artifact_references.side_effect = expire
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        self.assertIn("conditions.C5.window_expired", (self.custody / "night/receipt.json").read_text())

    def test_existing_go_alone_prevents_rearm_and_is_in_custody_inventory(self):
        path = self.custody / "night/go_receipt.json"
        raw = self.readiness.render_json({"fixture": "existing GO"})
        path.parent.mkdir()
        path.write_bytes(raw)
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.author.author_arm_readiness_evidence_t0.assert_not_called()
        self.assertEqual(raw, path.read_bytes())
        self.assertIn({"path": "night/go_receipt.json", "sha256": self.readiness.sha256_bytes(raw)}, self.driver._artifact_list(self.custody, path.parent))


class WindowDeadlineTests(unittest.TestCase):
    """The driver's wall-clock stop: NIGHT-STALL-WALLCLOCK-ABORT-01.

    The night's exclusive window ends at `t0 + window_max_s`. Before this
    lane, nothing in the driver ended a chain that ran past it: the census
    loop only ever aborted for an agent, and the dead-man merely refused, an
    hour later, to start anything new. The 2026-09-16 night held a quiet
    machine for 11 h 07 m for exactly that reason. The driver now terminates
    the chain WINDOW_SHUTDOWN_GRACE_S after the window end -- one shutdown
    allowance, sized for the chain's bounded end-of-window abort -- and
    reports `night_window_exceeded`.

    Every test here runs a REAL chain in a REAL process group and proves the
    outcome from the night's own records. The gate's clock is the fixture's
    (`ProbeSource.now_epoch_s`), which is also the clock the driver reads once
    to place the deadline, so the plan's window and the patched grace are the
    only knobs; wall-clock scaling is what keeps these tests in seconds.
    """

    def setUp(self) -> None:
        if not probe_census_available():
            self.skipTest("/usr/bin/pgrep group census is unavailable")
        self.driver = _load_driver()
        self.temporary = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.chain = self.root / "chain.zsh"
        self.sidecar = self.root / "chain.zsh.sha256"
        self.registration = self.root / "registration.json"
        self.registration.write_text((REPO_ROOT / night_gate.D166_REGISTRATION_PATH).read_text(), encoding="utf-8")
        self.plan_path = self.root / "plan.json"
        self.courier = self.root / "claude"
        self.courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        self.courier.chmod(0o755)
        self.t0_epoch_s = datetime(2026, 9, 2, 1, 0).timestamp()
        self.source = ProbeSource(self.t0_epoch_s + 1, str(self.root))
        self.source.plan_path = self.plan_path
        for patch in (
            mock.patch.object(self.driver, "observe_identity",
                              return_value=Identity("LIVE", "Tue Sep 8 01:02:03 2026")),
            mock.patch.object(night_gate, "D166_REGISTRATION_SHA256",
                              hashlib.sha256(self.registration.read_bytes()).hexdigest()),
            mock.patch.object(self.driver, "make_probes",
                              return_value=self.source.probes()),
            mock.patch.object(self.driver, "_resolve_courier_bin",
                              return_value=(self.courier, None, None)),
        ):
            patch.start()
            self.addCleanup(patch.stop)
        self.driver._durable_record = mock.Mock(return_value=None)
        self.driver.run_courier = mock.Mock(return_value={
            "attempted": 1, "sent": True, "heartbeat_seen": True, "last_error": None,
        })

    def _write_chain(self, body: str) -> None:
        self.chain.write_text(body, encoding="utf-8")
        self.sidecar.write_text(
            hashlib.sha256(self.chain.read_bytes()).hexdigest() + "  chain.zsh\n",
            encoding="utf-8")

    def _write_plan(self, *, window_max_s: int) -> None:
        write_night_plan(
            self.plan_path,
            night_gate.NightPlan(
                plan_id="night-plan", receipt_class="DIAGNOSTIC_NO_PACK",
                t0_epoch_s=self.t0_epoch_s, window_max_s=window_max_s,
                authored_epoch_s=self.t0_epoch_s - 1, repo_head=HEAD,
                measurement_root=str(self.root), measurement_head=HEAD,
                chain_path=str(self.chain), chain_sha256_path=str(self.sidecar),
                custody_root=str(self.custody), registration_path=str(self.registration),
            ),
        )

    def _arm(self, body: str, *, window_max_s: int = 2, grace_s: float = 1.0) -> None:
        """Scale the window and the shutdown allowance, never the plan schema."""
        self._write_chain(body)
        self._write_plan(window_max_s=window_max_s)
        # create=True on purpose: run against the base head, which has no
        # shutdown allowance at all, these tests must reach the real
        # behaviour -- a chain that runs to its own end past the window --
        # and not stop at an AttributeError for a name head introduced.
        patch = mock.patch.object(
            self.driver, "WINDOW_SHUTDOWN_GRACE_S", grace_s, create=True)
        patch.start()
        self.addCleanup(patch.stop)

    def _signal_spy(self):
        """Record every signal sent to a group, and really send it."""
        sent = []
        real = os.killpg

        def spy(pgid, number):
            sent.append((pgid, number))
            return real(pgid, number)

        return sent, mock.patch.object(self.driver.os, "killpg", spy)

    @staticmethod
    def _alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def _await(self, path: Path, timeout_s: float = 30.0) -> None:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if path.exists():
                return
            time.sleep(0.05)
        raise AssertionError(f"{path} never appeared within {timeout_s} s")

    def _records(self) -> tuple[dict, dict, dict]:
        night = self.custody / "night"
        return (
            json.loads((night / "result.json").read_text()),
            json.loads((night / "refusal.json").read_text()),
            json.loads((night / "chain.deadline").read_text()),
        )

    # ---- (1) the group, not just the direct child --------------------------

    def test_deadline_kills_the_chain_and_its_grandchild_then_couriers(self) -> None:
        """A grandchild in the chain's group is terminated with it.

        `start_new_session=False` is what keeps the chain's own children --
        including every custody worker -- inside the group `killpg` reaches;
        the assertion below is the invariant, not an assumption.
        """
        grandchild = self.root / "grandchild.pid"
        # Bounded sleeps: past the deadline, but self-terminating, so the
        # base-head counterfactual fails on the verdict in half a minute
        # instead of holding a process group for ten.
        self._arm(f"/bin/sleep 25 &\necho $! > {grandchild}\n/bin/sleep 20\n")
        exit_code = self.driver.run_night(self.plan_path)
        pid = int(grandchild.read_text().strip())
        # The verdict first: a driver with no wall-clock stop lets the chain
        # run to its own end and reports GO, which is the defect.
        self.assertEqual(self.driver.EXIT_ABORTED, exit_code)
        result, refusal, deadline = self._records()
        self.assertEqual("ABORTED", result["verdict"])
        self.assertEqual("night_window_exceeded", result["aborted_reason"])
        self.assertEqual("night_window_exceeded", refusal["refusal"]["reason"])
        # The scaled fixture's own allowance, substituted into the sentence
        # the courier reports; the production wording is pinned in
        # test_an_abort_that_spends_its_whole_budget_is_not_interrupted.
        self.assertEqual(
            "chain terminated at the wall-clock deadline (window end + 1 s); "
            "process-group termination proven",
            refusal["refusal"]["detail"])
        self.assertTrue(deadline["proven"])
        self.assertEqual(self.t0_epoch_s + 2 + 1, deadline["deadline_epoch_s"])
        self.assertFalse(self._alive(pid), "a group member outlived the deadline")
        self.driver.run_courier.assert_called_once()
        self.assertIn(
            {"path": "night/chain.deadline",
             "sha256": self.driver._sha256_path(self.custody / "night/chain.deadline")},
            self.driver._artifact_list(self.custody, self.custody / "night"))
        source = inspect.getsource(calibration_ledger._bounded_custody_request)
        self.assertIn("start_new_session=False", source)

    # ---- (2) escalation to SIGKILL -----------------------------------------

    def test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven(self) -> None:
        grandchild = self.root / "grandchild.pid"
        ready = self.root / "grandchild.ready"
        self._arm(
            f"/bin/zsh -c 'trap \"\" TERM; : > {ready}; exec /bin/sleep 300' &\n"
            f"echo $! > {grandchild}\n/bin/sleep 20\n")
        # The two-second scaled deadline can fire before the grandchild has
        # installed its TERM trap; the census then proves the group gone with
        # TERM alone and the escalation under test never runs (CI, 09-23,
        # every run after c741678b). Hold the chain start until the trap is
        # in place and the grandchild is a member of the chain's group.
        complete_start = self.driver._complete_chain_start

        def complete_after_ready(descriptor, process, night_dir):
            pgid = complete_start(descriptor, process, night_dir)

            def reap() -> None:
                # A failed readiness wait raises before any deadline exists.
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

            self.addCleanup(reap)
            self._await(ready, timeout_s=10)
            self._await(grandchild, timeout_s=10)
            self.assertEqual(pgid, os.getpgid(int(grandchild.read_text().strip())))
            return pgid

        # Diagnostic trail (CI-only failure, 09-23): every census answer with
        # its time, plus a ps snapshot of the group, lands in the assertion
        # message so a Linux failure shows what the census actually saw.
        trail: list[str] = []
        real_census = self.driver._group_census

        def recording_census(pgid, timeout_s=1):
            absent, lines = real_census(pgid, timeout_s)
            snapshot = subprocess.run(
                ["ps", "-eo", "pid,pgid,ppid,stat,etimes,args"],
                capture_output=True, text=True, check=False).stdout.splitlines()
            members = [row for row in snapshot[1:] if row.split()[1:2] == [str(pgid)]]
            trail.append(f"{time.monotonic():.2f} absent={absent} lines={lines} ps={members}")
            return absent, lines

        sent, patch = self._signal_spy()
        with mock.patch.object(self.driver, "_complete_chain_start",
                               side_effect=complete_after_ready), \
                mock.patch.object(self.driver, "_group_census",
                                  side_effect=recording_census), patch:
            exit_code = self.driver.run_night(self.plan_path)
        pid = int(grandchild.read_text().strip())
        self.assertEqual(self.driver.EXIT_ABORTED, exit_code)
        _result, refusal, deadline = self._records()
        self.assertEqual("night_window_exceeded", refusal["refusal"]["reason"])
        self.assertTrue(deadline["proven"])
        self.assertIn(signal.SIGKILL, [number for _pgid, number in sent],
                      "a TERM-ignoring member must force the escalation; grandchild "
                      f"pid {pid}; census trail:\n" + "\n".join(trail[:3] + ["..."] + trail[-4:]))
        self.assertFalse(self._alive(pid), "the TERM-ignoring member survived")

    # ---- (3) a census that never empties -----------------------------------

    def test_a_census_that_never_empties_suppresses_the_courier(self) -> None:
        self._arm("/bin/sleep 20\n")
        census = ["9999 /bin/sleep 20"]
        with (mock.patch.object(self.driver, "GROUP_CENSUS_WINDOW_S", 0.2,
                                create=True),
              mock.patch.object(self.driver, "_group_census",
                                return_value=(False, census), create=True)):
            exit_code = self.driver.run_night(self.plan_path)
        night = self.custody / "night"
        self.assertEqual(self.driver.EXIT_COURIER_FAILED, exit_code)
        result, refusal, deadline = self._records()
        unkilled = json.loads((night / "chain.unkilled").read_text())
        self.assertEqual("REFUSED", result["verdict"])
        self.assertEqual("night_chain_alive", result["aborted_reason"])
        self.assertEqual("night_chain_alive", refusal["refusal"]["reason"])
        self.assertEqual("night_window_exceeded",
                         refusal["refusal"]["evidence"]["trigger"])
        self.assertEqual(census, refusal["refusal"]["evidence"]["group_census"])
        self.assertEqual(self.t0_epoch_s + 2 + 1,
                         refusal["refusal"]["evidence"]["deadline_epoch_s"])
        self.assertEqual(census, unkilled["group_census"])
        self.assertFalse(deadline["proven"])
        self.driver.run_courier.assert_not_called()

    # ---- (4) a lawful abort is not interrupted -----------------------------

    def test_an_abort_that_spends_its_whole_budget_is_not_interrupted(self) -> None:
        """The shutdown allowance covers the chain's closing abort, with room.

        The chain's end-of-window `abort-session` runs after the window is
        spent and is bounded by ONE custody allowance (CUSTODY_BUDGET_S, the
        seconds the driver exports). The grace must cover that allowance plus
        the termination sequence, or the driver would kill the very operation
        that closes the ledger session and leave it open under a live writer
        lease. The scaled fixture runs in seconds; the inequality asserted
        after it is the production one.
        """
        # Window ends 2 s after t0 (1 s after the fixture's clock); the chain
        # keeps working for 3 s and closes cleanly, well inside the deadline.
        # The allowance is scaled to 8 s so the margin (about 6 s) absorbs a
        # loaded hosted runner: with 3.0 s the margin was 1 s and the test
        # failed on two consecutive main runs (TEST-WALLCLOCK-ABORT-FIXTURE-
        # MARGIN-01). The chain still exits on its own, so the test's duration
        # does not grow; the production inequality below is unchanged.
        self._arm("/bin/sleep 3\nexit 0\n", window_max_s=2, grace_s=8.0)
        exit_code = self.driver.run_night(self.plan_path)
        night = self.custody / "night"
        result = json.loads((night / "result.json").read_text())
        self.assertEqual(self.driver.EXIT_GO, exit_code)
        self.assertEqual("GO", result["verdict"])
        self.assertEqual(0, result["chain_exit_code"])
        self.assertIsNone(result["aborted_reason"])
        self.assertFalse((night / "chain.deadline").exists())
        self.assertEqual([], list(night.glob("refusal*.json")))
        self.driver.run_courier.assert_called_once()
        # The real arithmetic, with the real constants.
        plan = self.driver._load_plan(self.plan_path)
        budget_s = float(self.driver._chain_environment(plan, night)["CUSTODY_BUDGET_S"])
        fresh = _load_driver(module_name="run_night_wallclock_constants")
        self.assertEqual(120.0, budget_s)
        self.assertEqual(300, fresh.WINDOW_SHUTDOWN_GRACE_S)
        self.assertEqual(70, fresh.TERMINATION_BOUND_S)
        self.assertLessEqual(
            budget_s, fresh.WINDOW_SHUTDOWN_GRACE_S - fresh.TERMINATION_BOUND_S,
            "the shutdown allowance must cover one custody budget plus termination")
        self.assertEqual(
            "chain terminated at the wall-clock deadline (window end + 300 s); "
            "process-group termination proven",
            fresh._window_exceeded_detail(fresh.WINDOW_SHUTDOWN_GRACE_S))

    # ---- (B) the watchdog thread, with the loop blocked --------------------

    def test_the_watchdog_fires_while_the_main_loop_is_blocked_on_the_volume(self) -> None:
        """A census write that never returns must not swallow the deadline.

        `_append_census` writes under the custody root -- the volume whose
        blocked open held the 2026-09-16 night. A deadline checked only
        between loop iterations is unreachable in that state, so the watchdog
        thread terminates the group AND writes the refusal document itself:
        otherwise the night's only report would be the dead-man's generic
        `night_chain_alive`, 3900 s after the window end.
        """
        self._arm("/bin/sleep 20\n")
        night = self.custody / "night"
        fifo = self.root / "blocked-census.fifo"
        os.mkfifo(fifo)
        real_append = self.driver._append_census
        appends = []

        def blocking_append(path, probe, refusal):
            appends.append(path)
            if len(appends) == 1:            # the driver's pre-chain census
                return real_append(path, probe, refusal)
            with fifo.open("w"):             # no reader: blocks forever
                pass
            return real_append(path, probe, refusal)

        outcome = {}

        def run():
            try:
                outcome["exit_code"] = self.driver.run_night(self.plan_path)
            except BaseException as error:   # recorded, never raised in a thread
                outcome["error"] = error

        with mock.patch.object(self.driver, "_append_census", blocking_append):
            worker = threading.Thread(target=run, daemon=True)
            worker.start()
            try:
                self._await(night / "refusal.json")
                self._await(night / "chain.deadline")
                _refusal = json.loads((night / "refusal.json").read_text())
                deadline = json.loads((night / "chain.deadline").read_text())
                pgid = json.loads((night / "chain.started").read_text())["pgid"]
                self.assertEqual("night_window_exceeded",
                                 _refusal["refusal"]["reason"])
                self.assertTrue(deadline["proven"])
                self.assertEqual(pgid, deadline["pgid"])
                self.assertFalse(self._alive(pgid),
                                 "the watchdog must terminate the group itself")
            finally:
                # Unblock the loop so the night can finish and be inspected.
                reader = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
                os.close(reader)
                worker.join(timeout=60)
        self.assertFalse(worker.is_alive())
        self.assertIsNone(outcome.get("error"))
        result = json.loads((night / "result.json").read_text())
        self.assertEqual("ABORTED", result["verdict"])
        self.assertEqual("night_window_exceeded", result["aborted_reason"])
        # Exactly one document for one cause: the resuming loop must not
        # allocate a second copy of the refusal the watchdog already wrote.
        self.assertEqual(["refusal.json"],
                         [path.name for path in night.glob("refusal*.json")])
        self.driver.run_courier.assert_called_once()

    # ---- the schedule the deadline does and does not touch -----------------

    def test_the_deadline_changes_no_plan_field_and_no_dead_man_instant(self) -> None:
        fresh = _load_driver(module_name="run_night_wallclock_schedule")
        self._write_plan(window_max_s=9000)
        plan = fresh._load_plan(self.plan_path)
        self.assertEqual(
            plan.t0_epoch_s + plan.window_max_s + fresh.COURIER_DEADLINE_S,
            fresh._completion_epoch_s(plan))
        self.assertEqual(
            60 * math.ceil((fresh._completion_epoch_s(plan) + fresh.DEADMAN_GRACE_S) / 60),
            fresh.deadman_epoch(plan))
        # 300 s to the deadline, <= 70 s to prove termination, <= 300 s of
        # courier, against 3900 s of dead-man grace.
        self.assertLessEqual(
            plan.t0_epoch_s + plan.window_max_s + fresh.WINDOW_SHUTDOWN_GRACE_S
            + fresh.TERMINATION_BOUND_S + fresh.COURIER_DEADLINE_S,
            fresh.deadman_epoch(plan))
        fields = {field.name for field in dataclasses.fields(night_gate.NightPlan)}
        self.assertNotIn("custody_budget_s", fields)
        self.assertNotIn("window_shutdown_grace_s", fields)
        # The constant's own comment says why it is not the courier's number:
        # the value 300 s is right, the OWNERSHIP matters, and a future
        # courier retune must not silently move where the chain is killed.
        comment = " ".join(
            line.lstrip("# ") for line in
            inspect.getsource(fresh).split("WINDOW_SHUTDOWN_GRACE_S = 300")[0]
            .splitlines()[-4:])
        self.assertIn("Separate shutdown allowance", comment)
        self.assertIn("not derived from the courier deadline", comment)


class ProcessGroupRetryTests(unittest.TestCase):
    def test_nonempty_census_resignals_every_retry_in_both_phases(self) -> None:
        self.driver = _load_driver()
        clock = [0.0]

        def sleep(seconds):
            clock[0] += seconds

        # Reuse the real-process fixture's spy, with a mocked signal transport
        # underneath it: this regression needs neither pgrep nor a live group.
        with mock.patch.object(self.driver.os, "killpg"):
            sent, signal_patch = WindowDeadlineTests._signal_spy(self)
            with (signal_patch,
                  mock.patch.object(self.driver.time, "monotonic",
                                    side_effect=lambda: clock[0]),
                  mock.patch.object(self.driver.time, "sleep", side_effect=sleep),
                  mock.patch.object(self.driver, "GROUP_CENSUS_WINDOW_S", 0.2),
                  mock.patch.object(self.driver, "GROUP_CENSUS_INTERVAL_S", 0.1)):
                for phase in (signal.SIGTERM, signal.SIGKILL):
                    with self.subTest(phase=phase):
                        sent.clear()

                        def census(pgid, timeout_s):
                            # Each look must be preceded by a fresh signal,
                            # including retries for newly forked group members.
                            self.assertEqual(
                                [(4242, phase)] * probe.call_count, sent)
                            return False, ["4242 /bin/sleep 20"]

                        with mock.patch.object(
                            self.driver, "_group_census", side_effect=census
                        ) as probe:
                            self.assertEqual(
                                (False, ["4242 /bin/sleep 20"]),
                                self.driver._prove_group_absent(4242, phase))
                        self.assertGreater(len(sent), 1)


if __name__ == "__main__":
    unittest.main()


class BindClock:
    def __init__(self, late=0):
        self.elapsed = float(late)
        self.offset = 1000.0
        self.sleeps = []
        self.limit = None

    def monotonic(self):
        return self.elapsed

    def wall(self):
        return self.offset + self.elapsed

    def sleep(self, duration):
        if self.limit is not None and self.elapsed + duration > self.limit + 1e-9:
            raise AssertionError('bind exceeded the original monotonic deadline')
        self.sleeps.append(duration)
        self.elapsed = round(self.elapsed + duration, 9)


class BindFakeTask:
    def __init__(self, call, clock):
        self.call, self.clock = call, clock
        self.ends = clock.monotonic() + getattr(call, 'duration', 0)
        self.hang = getattr(call, 'hang', False)
        self.closed = False

    def ready(self):
        return not self.hang and self.clock.monotonic() >= self.ends

    def result(self):
        return self.call()

    def advance(self):
        pass

    def cancel(self):
        self.closed = True

    def poll_cleanup(self):
        return self.closed


class QuietBindingTests(unittest.TestCase):
    def setUp(self):
        from tests.test_night_gate import FakeProbeSource, make_plan, REGISTRATION_TEXT
        from tests.test_quiet_admission import POLICY
        from dataclasses import replace
        self.driver = _load_driver()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.night = Path(self.temporary.name)
        self.clock = BindClock()
        self.source = FakeProbeSource()
        self.plan = replace(make_plan(), window_max_s=9600, quiet_admission=dict(POLICY))
        self.probes = replace(self.source.probes(), now_epoch_s=self.clock.wall,
                             monotonic_ns=lambda: int(self.clock.monotonic() * 1e9))
        patch = mock.patch.object(night_gate, 'D166_REGISTRATION_SHA256',
                                 hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest())
        patch.start()
        self.addCleanup(patch.stop)
        self.tasks = []
        self.samples = 0

    def task(self, kind, job_id, call, request, launcher):
        task = BindFakeTask(call, self.clock)
        self.tasks.append(task)
        return task

    def sampler(self, values, *, load=1.2, duration=30):
        from tests.test_quiet_admission import metrics
        def sample():
            self.samples += 1
            busy = values[min(self.samples - 1, len(values) - 1)]
            return dict(wall_start=self.clock.wall() - duration, wall_end=self.clock.wall(),
                monotonic_start=self.clock.monotonic() - duration, monotonic_end=self.clock.monotonic(),
                interval_s=duration, boot_identity=BOOT_UUID,
                census=dict(exit_code=1, stdout='', stderr=''),
                raw_sha256=dict(ps_before='a'*64, ps_after='b'*64, top='c'*64),
                metrics=metrics(busy), load_avg_diagnostic={'raw': str(load)})
        sample.duration = duration
        return sample

    def bind(self, sampler, **kwargs):
        receipt = self.driver.bind_until_quiet(self.plan, self.probes, self.night,
            sampler=sampler, test_dispatch=self.task, monotonic=self.clock.monotonic,
            sleep=self.clock.sleep, wall_clock=self.clock.wall, **kwargs)
        self.assertTrue(all(task.closed for task in self.tasks))
        value = json.loads(receipt.to_json_bytes())
        self.assertEqual(night_gate.validate_receipt(value), [])
        return receipt, value

    def journal(self):
        return [json.loads(line) for line in (self.night/'quiet_samples.jsonl').read_text().splitlines()]

    def test_bind_go_on_second_consecutive_quiet_sample_at_k(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        receipt, value = self.bind(self.sampler([.9, .9, .02, .9, .02, .02]))
        self.assertEqual(receipt.verdict, 'GO')
        self.assertEqual(self.samples, 6)
        self.assertEqual(value['samples_total'], 6)
        self.assertEqual(value['samples_quiet_run_at_go'], 2)
        self.assertEqual(value['go_epoch_s'], 1180)
        self.assertEqual([s['decision'] for s in self.journal()], ['WAIT', 'WAIT', 'quiet', 'WAIT', 'quiet', 'quiet'])
        self.assertNotIn(night_gate.LOAD_AVG_ARGV, self.source.run_calls)
        self.assertGreaterEqual(self.source.run_calls.count(night_gate.HID_IDLE_ARGV), 13)

    def test_bind_expiry_refuses_with_every_sample_recorded(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        receipt, value = self.bind(self.sampler([.9]))
        self.assertEqual(receipt.refusal.reason, 'night_refused_bind_expired')
        self.assertEqual(self.clock.monotonic(), 600)
        self.assertEqual(len(self.journal()), 20)
        self.assertEqual(value['quiet_samples_lines'], 20)
        self.assertEqual(value['quiet_samples_sha256'], hashlib.sha256((self.night/'quiet_samples.jsonl').read_bytes()).hexdigest())
        self.assertFalse((self.night/'refusal.json').exists())
        self.assertIn('last_busy_cores', receipt.refusal.detail)
        self.assertEqual(value['top_consumers_at_decision'][0]['command'], 'fseventsd')

    def test_low_load_busy_daemon_never_admits(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        receipt, value = self.bind(self.sampler([.9], load=1.2))
        self.assertEqual(receipt.verdict, 'REFUSED')
        self.assertTrue(all(s['decision'] == 'WAIT' for s in self.journal()[:-1]))
        self.assertEqual(self.journal()[-1]['error_code'], 'night_refused_bind_expired')
        self.assertEqual(value['load_avg_diagnostic'], {'raw': '1.2'})

    def test_finished_burst_admits_despite_high_load(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        receipt, value = self.bind(self.sampler([.02], load=3.7))
        self.assertEqual(receipt.verdict, 'GO')
        self.assertEqual(self.samples, 2)
        self.assertEqual(value['load_avg_diagnostic'], {'raw': '3.7'})

    def test_census_hit_during_bind_is_terminal_agent_present(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        from dataclasses import replace
        self.plan = replace(self.plan, quiet_admission=dict(self.plan.quiet_admission, consecutive_quiet_samples=3))
        original = self.source.run
        def run(argv):
            if argv == night_gate.AGENT_CENSUS_ARGV and self.clock.monotonic() >= 90:
                return _probe(argv, exit_code=0, stdout='123 agent\n')
            return original(argv)
        self.probes = replace(self.probes, run=run)
        receipt, value = self.bind(self.sampler([.02]))
        self.assertEqual(receipt.refusal.reason, 'night_refused_agent_present')
        self.assertEqual(self.clock.monotonic(), 90)
        self.assertEqual(value['samples_total'], 3)
        self.assertIsNone(value['go_epoch_s'])

    def test_late_go_preserves_absolute_deadlines(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        original_end = self.plan.t0_epoch_s + self.plan.window_max_s
        original_completion = self.driver._completion_epoch_s(self.plan)
        original_deadman = self.driver.deadman_epoch(self.plan)
        receipt, value = self.bind(self.sampler([.9]*16 + [.02, .02]))
        self.assertEqual(value['go_epoch_s'], 1540)
        self.assertEqual(self.plan.t0_epoch_s + self.plan.window_max_s, original_end)
        self.assertEqual(self.driver._completion_epoch_s(self.plan), original_completion)
        self.assertEqual(self.driver.deadman_epoch(self.plan), original_deadman)
        self.assertEqual(value['bind_deadline_epoch_s'], 1600)
        # Test the actual driver consumer as well as the bind producer, so a
        # t0 rewrite after GO cannot pass this named regression.
        integration = QuietDriverIntegrationTests()
        self.addCleanup(integration.doCleanups)
        for go_offset in (0, 540):
            with self.subTest(go_offset=go_offset):
                integration.assert_driver_deadlines(go_offset)
        # Three completed samples cannot restart the remaining bind allowance.
        phase = QuietBindingTests()
        phase.setUp()
        self.addCleanup(phase.doCleanups)
        phase.clock.limit = 600
        sample = phase.sampler([.9])
        deadlines = []
        def observed():
            observation = sample()
            deadlines.append(phase.driver.quiet_admission.bind_deadline_epoch(phase.plan))
            if phase.samples == 3:
                observed.hang = True
            return observation
        observed.duration = 30
        refused, decision = phase.bind(observed)
        self.assertEqual(refused.refusal.reason, 'night_refused_bind_expired')
        self.assertEqual(deadlines, [1600, 1600, 1600])
        self.assertEqual(decision['bind_deadline_epoch_s'], 1600)
        self.assertEqual(phase.clock.monotonic(), 600)
        # The new local allowance interrupts each hung attempt before global expiry.
        errors = [entry for entry in phase.journal() if entry['decision'] == 'error']
        self.assertEqual([entry['error_code'] for entry in errors],
            ['night_probe_error', 'night_probe_error', 'night_refused_bind_expired'])
        self.assertEqual([entry['monotonic_end'] for entry in errors], [335, 580, 600])

    def test_late_driver_consumes_bind_allowance(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        self.clock.elapsed = 300
        self.clock.limit = 600
        receipt, value = self.bind(self.sampler([.9]))
        self.assertEqual(receipt.refusal.reason, 'night_refused_bind_expired')
        self.assertEqual(self.clock.monotonic(), 600)
        self.assertEqual(value['samples_total'], 10)
        self.assertEqual(receipt.refusal.reason, 'night_refused_bind_expired')

    def test_wall_rollback_never_extends_absolute_deadline(self):
        self.clock.limit = 600
        sample = self.sampler([.9])
        sample.hang = True
        original_sleep = self.clock.sleep
        rolled_back = False
        def sleep(duration):
            nonlocal rolled_back
            original_sleep(duration)
            if self.clock.elapsed >= 90 and not rolled_back:
                self.clock.offset -= 100
                rolled_back = True
        self.clock.sleep = sleep
        receipt, value = self.bind(sample)
        self.assertTrue(rolled_back)
        self.assertEqual(receipt.refusal.reason, 'night_refused_bind_expired')
        self.assertEqual(self.clock.monotonic(), 600)
        self.assertEqual(value['bind_deadline_epoch_s'], 1600)
        self.assertEqual([entry['error_code'] for entry in self.journal()],
            ['night_probe_error', 'night_probe_error', 'night_refused_bind_expired'])

    def test_observed_wall_rollback_is_terminal_boot_clock(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        original = self.sampler([.9])
        def rollback():
            observation = original()
            self.clock.offset -= 100
            return observation
        rollback.duration = 30
        receipt, value = self.bind(rollback)
        self.assertEqual(receipt.refusal.reason, 'night_refused_boot_clock')
        self.assertLessEqual(self.clock.monotonic(), 600)
        self.assertEqual(value['bind_deadline_epoch_s'], 1600)

    def test_sampler_hang_cannot_block_census_or_expiry(self):
        # Real transport/process tests below exercise the supervisor seam. This
        # pure test asserts the newly distinct local and absolute decisions.
        sample = self.sampler([.9])
        sample.hang = True
        receipt, value = self.bind(sample)
        self.assertEqual(receipt.refusal.reason, 'night_refused_bind_expired')
        entries = self.journal()
        self.assertEqual(entries[0]['error_code'], 'night_probe_error')
        self.assertEqual(entries[0]['monotonic_end'], 245)
        self.assertEqual(entries[-1]['error_code'], 'night_refused_bind_expired')
        self.assertGreaterEqual(len((self.night/'censuses.jsonl').read_text().splitlines()), 20)

    def test_changed_boot_identity_is_terminal_boot_clock(self):
        original = self.sampler([.02])
        def changed():
            observation = original()
            self.source.results[night_gate.BOOT_SESSION_ARGV] = _probe(
                night_gate.BOOT_SESSION_ARGV, stdout='11111111-1111-4111-8111-111111111111')
            return observation
        changed.duration = 30
        receipt, value = self.bind(changed)
        self.assertEqual(receipt.refusal.reason, 'night_refused_boot_clock')
        self.assertEqual(self.samples, 1)
        self.assertIsNone(value['go_epoch_s'])

    def test_malformed_sampler_is_probe_error_never_quiet(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        def malformed():
            return {'metrics': {'busy_cores': 0}}
        malformed.duration = 30
        receipt, value = self.bind(malformed)
        self.assertEqual(receipt.refusal.reason, 'night_probe_error')
        self.assertEqual(value['samples_total'], 1)
        self.assertEqual(self.journal()[0]['decision'], 'error')

    def test_boot_identity_unavailable_is_error_in_journal_and_receipt(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05
        sample = self.sampler([.02])
        def unavailable():
            return dict(sample(), boot_identity=None,
                        boot_identity_unavailable='OSError: fixture sysctl denied')
        unavailable.duration = 30
        receipt, value = self.bind(unavailable)
        self.assertEqual(receipt.refusal.reason, 'night_probe_error')
        self.assertEqual(value['samples_total'], 1)
        self.assertIsNone(value['go_epoch_s'])
        self.assertFalse(value['admission_is_capture_evidence'])
        self.assertEqual(self.journal()[0]['decision'], 'error')
        self.assertEqual(value['boot_identity_unavailable'], 'OSError: fixture sysctl denied')
        self.assertEqual(value['boot_identity_unavailable'], self.journal()[0]['boot_identity_unavailable'])
        self.assertTrue(value['top_consumers_at_decision'])

    def test_sampler_census_hit_is_terminal(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05
        sample = self.sampler([.02])
        def hit():
            return dict(sample(), census=dict(exit_code=0, stdout='42 agent\n', stderr=''))
        hit.duration = 30
        receipt, value = self.bind(hit)
        self.assertEqual(receipt.refusal.reason, 'night_refused_agent_present')
        self.assertIsNone(value['go_epoch_s'])

    def test_hard_probe_error_and_thermal_restriction_are_terminal(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        self.source.raise_for[night_gate.PMSET_BATT_ARGV] = OSError('fixture failure')
        receipt, value = self.bind(self.sampler([.02]))
        self.assertEqual(receipt.refusal.reason, 'night_probe_error')
        self.assertEqual(self.samples, 0)
        self.assertIn('attribution_unavailable', value)

    def test_journal_is_courier_artifact(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        self.bind(self.sampler([.02]))
        artifacts = self.driver._artifact_list(self.night.parent, self.night)
        self.assertIn(str((self.night/'quiet_samples.jsonl').relative_to(self.night.parent)),
                      [artifact['path'] for artifact in artifacts])

    def test_final_census_wins_after_required_quiet_run(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        from dataclasses import replace
        original = self.source.run
        calls_at_two = 0
        def run(argv):
            nonlocal calls_at_two
            if argv == night_gate.AGENT_CENSUS_ARGV and self.samples == 2:
                calls_at_two += 1
                if calls_at_two == 2:
                    return _probe(argv, exit_code=0, stdout='123 agent\n')
            return original(argv)
        self.probes = replace(self.probes, run=run)
        receipt, value = self.bind(self.sampler([.02]))
        self.assertEqual(receipt.refusal.reason, 'night_refused_agent_present')
        self.assertIsNone(value['go_epoch_s'])
        self.assertEqual(self.samples, 2)

    def test_power_screensaver_thermal_and_malformed_census_are_terminal(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        for argv, result, reason in [
            (night_gate.PMSET_BATT_ARGV, _probe(night_gate.PMSET_BATT_ARGV, stdout="Now drawing from 'Battery Power'"), 'night_refused_not_quiet'),
            (night_gate.HID_IDLE_ARGV, _probe(night_gate.HID_IDLE_ARGV, stdout='10'), 'night_refused_hid_idle'),
            (night_gate.THERMAL_ARGV, _probe(night_gate.THERMAL_ARGV, stdout='CPU_Speed_Limit = 80'), 'night_refused_not_quiet'),
            (night_gate.AGENT_CENSUS_ARGV, _probe(night_gate.AGENT_CENSUS_ARGV, exit_code=2), 'night_probe_error'),
        ]:
            with self.subTest(argv=argv):
                old = self.source.results[argv]
                self.source.results[argv] = result
                receipt, value = self.bind(self.sampler([.02]))
                self.assertEqual(receipt.refusal.reason, reason)
                self.assertEqual(self.samples, 0)
                self.source.results[argv] = old

    def test_v3_receipt_refuses_missing_attribution_and_inconsistent_count(self):
        self.plan.quiet_admission['busy_core_max'] = 0.05  # injected test threshold
        import copy
        _, receipt = self.bind(self.sampler([.02]))
        self.assertIs(receipt['admission_is_capture_evidence'], False)
        for invalid in (True, None, 0, 'false'):
            self.assertTrue(night_gate.validate_receipt(dict(receipt, admission_is_capture_evidence=invalid)))
        bad = copy.deepcopy(receipt)
        bad['quiet_admission']['busy_core_max'] = 0.0
        self.assertTrue(night_gate.validate_receipt(bad))
        for key in ('quiet_admission', 'quiet_samples_sha256', 'samples_total', 'admission_is_capture_evidence'):
            bad = copy.deepcopy(receipt)
            del bad[key]
            self.assertTrue(night_gate.validate_receipt(bad))
        bad = copy.deepcopy(receipt)
        bad['quiet_samples_lines'] += 1
        self.assertTrue(night_gate.validate_receipt(bad))
        bad = copy.deepcopy(receipt)
        bad['top_consumers_at_decision'] = []
        self.assertTrue(night_gate.validate_receipt(bad))
        bad['attribution_unavailable'] = 'host-only accounting'
        self.assertEqual(night_gate.validate_receipt(bad), [])


class QuietDriverIntegrationTests(unittest.TestCase):
    def fixture(self, **policy_overrides):
        from dataclasses import replace
        from tests.test_quiet_admission import POLICY
        fixture = NightDriverTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.addCleanup(fixture.tearDown)
        plan = replace(fixture.driver._load_plan(fixture.plan_path),
                       window_max_s=9600, quiet_admission=dict(POLICY, **policy_overrides))
        fixture.plan_path.unlink()  # fixture-only fresh publication
        write_night_plan(fixture.plan_path, plan)
        return fixture, plan

    def test_v4_driver_calls_bind_and_keeps_shutdown_anchored_to_entry(self):
        self.assert_driver_deadlines(540)

    def assert_driver_deadlines(self, go_offset):
        from dataclasses import replace
        # The synthetic 270 s observation now declares its actual interval;
        # a 30 s policy would correctly time it out at 30 + 215 s.
        fixture, plan = self.fixture(busy_core_max=0.05, sample_interval_s=270)
        driver = fixture.driver
        clock = BindClock()
        clock.offset = plan.t0_epoch_s
        probes = replace(fixture.source.probes(), now_epoch_s=clock.wall,
                         monotonic_ns=lambda: int(clock.monotonic()*1e9))
        driver.make_probes = lambda: probes
        real_bind = driver.bind_until_quiet
        def sample():
            from tests.test_quiet_admission import metrics
            return dict(wall_start=clock.wall()-270, wall_end=clock.wall(),
                monotonic_start=clock.monotonic()-270, monotonic_end=clock.monotonic(),
                interval_s=270, boot_identity=BOOT_UUID,
                census=dict(exit_code=1, stdout='', stderr=''),
                raw_sha256=dict(ps_before='a'*64, ps_after='b'*64, top='c'*64),
                metrics=metrics(.02), load_avg_diagnostic={'raw':'3.7'})
        sample.duration = 270
        def bind(*args, **kwargs):
            self.assertFalse((fixture.custody/'night/chain.started').exists())
            return real_bind(*args, **kwargs, sampler=sample,
                test_dispatch=lambda kind, job_id, call, request, launcher: BindFakeTask(call, clock),
                monotonic=clock.monotonic, sleep=clock.sleep, wall_clock=clock.wall)
        driver.bind_until_quiet = bind
        if go_offset == 0:
            # Boundary control for the downstream driver only. The +540 case
            # above uses the real interval loop; this is not admission evidence.
            from tests.test_quiet_admission import metrics
            receipt = driver.evaluate_night(replace(plan, quiet_admission=None), probes)
            admission = dict(quiet_admission=plan.quiet_admission, admission_is_capture_evidence=False,
                bind_deadline_epoch_s=plan.t0_epoch_s+600, go_epoch_s=plan.t0_epoch_s,
                samples_total=2, samples_quiet_run_at_go=2, quiet_samples_lines=2,
                quiet_samples_sha256='a'*64, top_consumers_at_decision=metrics(.02)['top_consumers'],
                load_avg_diagnostic={'raw': '3.7'})
            driver.bind_until_quiet = lambda *args, **kwargs: replace(
                receipt, schema=night_gate.QUIET_RECEIPT_SCHEMA, admission=admission)
        with mock.patch.object(driver.time, 'time', clock.wall), \
             mock.patch.object(driver.time, 'monotonic', clock.monotonic), \
             mock.patch.object(driver, '_run_chain_once', return_value=(0,None,0,[],True)) as chain, \
             mock.patch.object(driver, '_finish_reporting', wraps=driver._finish_reporting) as reporting:
            self.assertEqual(driver.run_night(fixture.plan_path), driver.EXIT_GO)
        self.assertEqual(clock.monotonic(), go_offset)
        self.assertEqual(chain.call_args.kwargs['shutdown_monotonic'], 9900)
        chain_plan = chain.call_args.args[1]
        t0 = fixture.t0_epoch_s
        self.assertEqual(chain_plan.t0_epoch_s, t0)
        # Exact instants from this fixture's scheduled t0, never from GO.
        self.assertEqual(chain_plan.t0_epoch_s + chain_plan.window_max_s + driver.WINDOW_SHUTDOWN_GRACE_S, t0+9900)
        self.assertEqual(driver._completion_epoch_s(chain_plan), t0+9900)
        self.assertEqual(chain_plan.t0_epoch_s + chain_plan.window_max_s + driver.COURIER_DEADLINE_S, t0+9900)
        self.assertEqual(driver.deadman_epoch(chain_plan), t0+13500)
        self.assertEqual(reporting.call_args.kwargs['deadman_epoch_s'], t0+13500)
        value = json.loads((fixture.custody/'night/receipt.json').read_bytes())
        self.assertEqual(value['go_epoch_s'], t0+go_offset)
        self.assertEqual(value['bind_deadline_epoch_s'], t0+600)
        self.assertEqual(night_gate.validate_receipt(value), [])
        self.assertTrue((fixture.custody/'night/chain.started').exists())
        self.assertFalse((fixture.custody/'night/refusal.json').exists())

    def test_early_v4_driver_refusal_has_receipt_and_unavailable_attribution(self):
        fixture, plan = self.fixture()
        driver = fixture.driver
        driver._resolve_courier_bin = lambda _bin: (None, 'fixture unavailable', None)
        self.assertEqual(driver.run_night(fixture.plan_path), driver.EXIT_COURIER_FAILED)
        receipt = json.loads((fixture.custody/'night/receipt.json').read_bytes())
        refusal = json.loads((fixture.custody/'night/refusal.json').read_bytes())
        self.assertEqual(night_gate.validate_receipt(receipt), [])
        self.assertEqual(receipt['schema'], night_gate.QUIET_RECEIPT_SCHEMA)
        self.assertIn('attribution_unavailable', refusal['refusal']['evidence'])
        self.assertFalse((fixture.custody/'night/chain.started').exists())

    def test_supervised_worker_is_reaped_on_cancellation(self):
        # The child ACKs its installed SIGTERM handler before fake time moves;
        # delayed exit makes blocking wait/reap mutations observable.
        result = BindSupervisionProcessTests().scenario('term_delay_late')
        self.assertLessEqual(result['returned_after_expiry'], 1.05)
        self.assertTrue(result['receipt']['supervision_residue'])


class BindSupervisionProcessTests(unittest.TestCase):
    """Actual ticker/transport/reaping under a separate 8 s wall-clock watchdog."""
    def scenario(self, name):
        with tempfile.TemporaryDirectory(prefix='jw-bind-fault-') as directory:
            root = Path(directory)
            command = (sys.executable, '-B', str(REPO_ROOT/'tests/night_gate_fixtures/bind_supervision.py'), name, directory)
            worker = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True, start_new_session=True)
            try:
                stdout, stderr = worker.communicate(timeout=8)
            except subprocess.TimeoutExpired:
                self.fail(f'external watchdog (8 s): bind supervisor blocked in {name}')
            finally:
                # Disposable supervisor and independently sessioned workers are
                # reclaimed even when a blocking mutant trips the watchdog.
                registry = root/'workers'
                pids = [int(pid) for pid in registry.read_text().splitlines()] if registry.exists() else []
                for pid in [worker.pid, *pids]:
                    try:
                        os.killpg(pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                if worker.poll() is None:
                    worker.kill()
                worker.communicate(timeout=1)
            self.assertEqual(worker.returncode, 0, stderr)
            result = json.loads(stdout)
        for task in result['tasks']:
            if task['pid'] is not None:
                self.assertTrue(task['reaped'], task)
            self.assertLessEqual(task['max_reads'], 4, task)
            self.assertLessEqual(task['max_bytes'], 65536, task)
            self.assertLessEqual(task['max_buffer'], 262148, task)
        self.assertEqual(result['receipt']['bind_deadline_epoch_s'], 1600)
        return result

    def assert_expired(self, result):
        self.assertEqual(result['receipt']['refusal']['reason'], 'night_refused_bind_expired')
        self.assertEqual(result['now'], 600)
        self.assertIsNone(result['receipt']['go_epoch_s'])

    def test_blocking_join_startup_and_post_publication(self):
        # Each subcase is also available individually to the mutant runner.
        self.test_startup_hang_is_nonblocking()
        self.test_post_send_hang_is_consumed_once_and_reaped()

    def test_startup_hang_is_nonblocking(self):
        result = self.scenario('startup_hang')
        self.assert_expired(result)
        self.assertEqual(result['census_ticks'], list(range(0, 600, 30)))
        self.assertEqual(result['sample_jobs'], 0)
        self.assertEqual([row[0] for row in result['result_probes']], ['startup'])
        self.assertLess(result['result_probes'][0][1], .05)

    def test_header_plus_one_byte_never_blocks_recv(self):
        result = self.scenario('recv_stall_late')
        self.assert_expired(result)
        self.assertEqual(result['samples'][-1]['error_code'], 'night_refused_bind_expired')
        self.assertEqual(result['census_ticks'], list(range(400, 600, 30)))

    def test_partial_header_and_body_eof_are_errors(self):
        for fault in ('partial_header', 'partial_body'):
            with self.subTest(fault=fault):
                result = self.scenario(fault)
                self.assertEqual(result['receipt']['refusal']['reason'], 'night_probe_error')
                self.assertIn('premature EOF', result['samples'][0]['error'])
                self.assertEqual(result['samples'][0]['decision'], 'error')
                self.assertEqual(result['sample_jobs'], 1)

    def test_pre_send_local_timeout_and_late_global_expiry(self):
        result = self.scenario('presend_hang')
        self.assertEqual(result['receipt']['verdict'], 'GO')
        self.assertEqual(result['sample_jobs'], 2)
        self.assertEqual(result['samples'][0]['error_code'], 'night_probe_error')
        self.assertEqual(result['samples'][0]['monotonic_end'], 245)
        self.assertEqual(result['samples'][1]['decision'], 'quiet')
        self.assertEqual(result['receipt']['go_epoch_s'], 1275)
        self.assertEqual(result['census_ticks'], list(range(0, 276, 30)))
        late = self.scenario('presend_hang_late')
        self.assert_expired(late)
        self.assertEqual(late['sample_jobs'], 1)
        self.assertEqual(late['samples'][0]['error_code'], 'night_refused_bind_expired')

    def test_post_send_hang_is_consumed_once_and_reaped(self):
        result = self.scenario('postsend_hang')
        self.assertEqual(result['receipt']['verdict'], 'GO')
        self.assertEqual(result['sample_jobs'], 1)
        self.assertEqual(len(result['samples']), 1)
        self.assertEqual(result['receipt']['go_epoch_s'], 1030)
        sample = next(task for task in result['tasks'] if task['kind'] == 'sample')
        self.assertTrue(sample['ready'])
        self.assertIn({'stage':'published'}, sample['events'])
        self.assertEqual([row[0] for row in result['result_probes']], ['published'])
        self.assertLess(result['result_probes'][0][1], .05)

    def test_exit_without_result_is_error_never_quiet(self):
        result = self.scenario('empty')
        self.assertEqual(result['receipt']['refusal']['reason'], 'night_probe_error')
        self.assertEqual(result['samples'][0]['decision'], 'error')
        self.assertIn('premature EOF', result['samples'][0]['error'])

    def test_oversized_length_and_flood_are_bounded(self):
        result = self.scenario('oversize')
        self.assertEqual(result['receipt']['refusal']['reason'], 'night_probe_error')
        self.assertIn('exceeds cap', result['samples'][0]['error'])
        sample = next(task for task in result['tasks'] if task['kind'] == 'sample')
        self.assertEqual(sample['max_buffer'], 4, 'oversize body was allocated/read')
        self.assertLessEqual(sample['max_bytes'], 4)
        serialized = self.scenario('serialize_oversize')
        self.assertEqual(serialized['receipt']['refusal']['reason'], 'night_probe_error')
        self.assertIn('serialized binding payload exceeds', serialized['samples'][0]['error'])

    def test_slow_chunks_keep_census_and_deadline_fixed(self):
        result = self.scenario('slow')
        self.assertEqual(result['receipt']['verdict'], 'GO')
        self.assertEqual(result['chunk_early'], [[0,False,10],[1,False,20],[2,False,30]])
        self.assertEqual(result['census_ticks'], [0, 30])
        self.assertEqual(result['receipt']['go_epoch_s'], 1030)
        self.assertEqual(result['sample_jobs'], 1)
        self.assertEqual(result['chunk_deadlines'], [[1,600],[2,600],[3,600]])

    def test_blocked_journal_never_blocks_deadline_or_grants_go(self):
        result = self.scenario('journal_block')
        self.assert_expired(result)
        self.assertIn('journal_failure', result['receipt'])
        self.assertEqual(result['census_ticks'], list(range(0, 600, 30)))
        self.assertIsNone(result['receipt']['go_epoch_s'])
        self.assertTrue(result['journal_entered'])

    def test_descendant_descriptor_and_group_cancellation(self):
        for fault in ('descendant_hang_late', 'descendant_exit'):
            with self.subTest(fault=fault):
                result = self.scenario(fault)
                events = [event for task in result['tasks'] for event in task['events'] if 'descendant' in event]
                self.assertEqual(len(events), 1)
                self.assertTrue(events[0]['fd_closed'], 'grandchild inherited result descriptor')
                self.assertIn(result['receipt']['refusal']['reason'], ('night_refused_bind_expired', 'night_probe_error'))
                # The fixture grandchild holds the independent control socket
                # open for its entire life. EOF proves cancellation reached it;
                # no ps permission or same-process mock is involved.
                sample = next(task for task in result['tasks'] if task['kind'] == 'sample')
                self.assertTrue(sample['control_eof'], 'grandchild survived group cancellation')

    def test_census_hit_interrupts_a_real_hung_sample(self):
        result = self.scenario('census_hit')
        self.assertEqual(result['receipt']['refusal']['reason'], 'night_refused_agent_present')
        self.assertEqual(result['now'], 90)
        self.assertEqual(result['census_ticks'], [0,30,60,90])
        self.assertEqual(result['sample_jobs'], 1)

    def test_parent_measures_whole_round_cost(self):
        result = self.scenario('round_cost')
        cost = result['receipt']['observer_cpu_s']
        self.assertGreater(cost, 0)
        self.assertLessEqual(cost, result['measured_cpu'])
        self.assertLess(result['measured_cpu'] - cost, .1)
        self.assertGreaterEqual(sum(task['kind'] == 'hard' for task in result['tasks']), 3)
        self.assertGreaterEqual(sum(task['kind'] == 'census' for task in result['tasks']), 2)
        self.assertEqual(result['receipt']['quiet_samples_lines'], 1)

    def test_large_frame_is_incremental_and_still_bounded(self):
        result = self.scenario('large_frame')
        self.assertEqual(result['receipt']['verdict'], 'GO')
        sample = next(task for task in result['tasks'] if task['kind'] == 'sample')
        self.assertGreater(sample['max_buffer'], 200000)
        self.assertLessEqual(sample['max_reads'], 4)
        self.assertLessEqual(sample['max_bytes'], 65536)

    def test_large_frame_keeps_each_worker_argument_below_linux_limit(self):
        result = self.scenario('large_frame')
        # Linux MAX_ARG_STRLEN is 32 4-KiB pages, including NUL; see execve(2).
        for task in result['tasks']:
            with self.subTest(job_id=task['id'], kind=task['kind']):
                self.assertLess(task['max_arg_bytes'], 131072)
                self.assertGreater(task['max_arg_bytes'], 0)  # the recording must have run

    def test_journal_failure_and_saturation_are_terminal(self):
        for mode, detail in (('journal_error', 'write failure'), ('journal_saturation', 'queue saturated')):
            with self.subTest(mode=mode):
                result = self.scenario(mode)
                self.assertIn('journal_failure', result['receipt'])
                self.assertEqual(result['receipt']['refusal']['reason'], 'night_probe_error')
                self.assertIn(detail, result['receipt']['journal_failure'])
                self.assertIsNone(result['receipt']['go_epoch_s'])
                self.assertTrue(result['journal_entered'])

    def test_journal_system_exit_records_failure_before_thread_exit(self):
        result = self.scenario('journal_system_exit')
        self.assertEqual(result['receipt']['verdict'], 'REFUSED')
        self.assertIn('journal_failure', result['receipt'])
        self.assertIn('SystemExit: injected journal write failure', result['receipt']['journal_failure'])
        self.assertIsNone(result['receipt']['go_epoch_s'])
        self.assertTrue(result['journal_entered'])

    def test_signalled_child_cannot_hold_cleanup_past_budget(self):
        result = self.scenario('term_delay_late')
        self.assert_expired(result)
        self.assertLessEqual(result['returned_after_expiry'], 1.05)
        residue = result['receipt']['supervision_residue']
        self.assertEqual(len(residue), 1)
        self.assertEqual(residue[0]['kind'], 'sample')
        self.assertEqual(residue[0]['state'], 'unreaped')

    def test_pending_exec_returns_receipt_then_launcher_reaps_late_child(self):
        result = self.scenario('launch_pending')
        self.assert_expired(result)
        self.assertEqual(result['census_ticks'], list(range(0,600,30)))
        self.assertLessEqual(result['returned_after_expiry'], 1.05)
        self.assertEqual(result['receipt']['supervision_residue'][0]['job_id'], 'census-1')
        self.assertTrue(any(task['pid'] is not None and task['reaped'] for task in result['tasks']))
        # The versioned validator accepts residue only on a refused v3 receipt.
        receipt = result['receipt']
        for residue in ([], [{'job_id':'x','kind':'sample','pid':True,'state':'unreaped'}]):
            with self.subTest(residue=residue):
                self.assertTrue(night_gate.validate_receipt(dict(receipt, supervision_residue=residue)))
        self.assertTrue(night_gate.validate_receipt(dict(receipt, verdict='GO')))

    def test_production_worker_argv_are_exact(self):
        driver = _load_driver()
        self.assertEqual(driver._bind_argv('sample', 'sample-1', 42,
            {'interval': 30, 'observer_pid': 7}),
            (sys.executable, '-B', '-m', 'joulewise.quiet_admission', '--observation',
             '--sample-interval-s', '30', '--observer-pid', '7', '--job-id', 'sample-1', '--result-fd', '42'))
        for kind in ('census', 'static', 'hard', 'smoke-hard'):
            self.assertEqual(driver._bind_argv(kind, kind+'-1', 42, {}),
                (sys.executable, '-B', str(SCRIPT_PATH), '_bind-worker', '--kind', kind,
                 '--job-id', kind+'-1', '--result-fd', '42', '--request', '{}'))

    def test_stalled_census_does_not_suppress_later_census(self):
        result = self.scenario('census_stall_hit')
        self.assertEqual(result['receipt']['refusal']['reason'], 'night_refused_agent_present')
        self.assertEqual(result['now'], 90)
        self.assertEqual(result['census_ticks'], [0,30,60,90])
        self.assertIsNone(result['receipt']['go_epoch_s'])

    def test_final_hard_checks_follow_delayed_journal_ack(self):
        result = self.scenario('journal_late_power')
        self.assertEqual(result['receipt']['refusal']['reason'], 'night_refused_not_quiet')
        self.assertGreaterEqual(result['now'], 60)
        self.assertEqual(result['sample_jobs'], 1)
        self.assertIsNone(result['receipt']['go_epoch_s'])


def campaign_chain_path():
    from joulewise.quiet_predicate_campaign import CHAIN_PATH
    return CHAIN_PATH


class EvidenceProbeTests(unittest.TestCase):
    def setUp(self):
        from tests.test_gen_evidence_night import EvidenceFixture
        from scripts import gen_evidence_night, run_night
        self.driver = run_night
        self.f = EvidenceFixture()
        self.addCleanup(self.f.close)
        gen_evidence_night.generate(self.f.plan_path)
        # Publication now belongs to the real courier's prelaunch boundary.
        # These fixtures never publish to a remote results branch.
        publication = mock.patch.object(self.driver, '_durable_record', return_value=None)
        self.publication = publication.start()
        self.addCleanup(publication.stop)

    def test_R8_the_sealed_wrapper_exports_a_fixed_set_without_the_replay_key(self):
        """R8 (half): `gen_evidence_night` emits a FIXED literal export set.

        The armed night's environment comes from the tracked launchd template
        (pinned separately) and from this wrapper.  Neither has anywhere to put
        a free-form variable, which is what makes the bench replay's switch
        unreachable from an arm -- so the export set is pinned by enumeration,
        not merely searched for the one key.
        """

        from scripts import run_night
        text = Path(self.f.plan.chain_path).read_text()
        exports = re.findall(r"^export ([A-Z_0-9]+)=", text, re.MULTILINE)
        self.assertEqual(set(exports), {
            "NIGHT_PAYLOAD_KIND", "PYTHONDONTWRITEBYTECODE", "EVIDENCE_PLAN_PATH",
            "EVIDENCE_MANIFEST_PATH", "EVIDENCE_MANIFEST_SHA256",
            "EVIDENCE_CHAIN_SOURCE_SHA256", "PY", "PYTHONPATH"})
        self.assertNotIn(run_night.REPLAY_RECORDER_ENV, text)
        self.assertNotIn("POWER_RECORDER", text)
        # And the chain source the wrapper execs carries none of it either.
        chain = Path(self.f.plan.measurement_root) / campaign_chain_path()
        self.assertNotIn(run_night.REPLAY_RECORDER_ENV, chain.read_text())

    @unittest.skipUnless(Path('/bin/zsh').is_file(), 'zsh required for shell probe fixture')
    def test_worker_verify_only_round_trip_never_starts_collection(self):
        from joulewise import night_agent_install as installer
        from types import SimpleNamespace
        receipt = self.f.custody / 'night_probe_receipt.json'
        progress = self.f.custody / 'progress.json'
        with mock.patch.dict(os.environ, {'JOULEWISE_LAUNCHD_LABEL': installer.probe_label(self.f.plan.plan_id)}):
            code = self.driver._probe_worker(self.f.plan_path, receipt, progress, time.monotonic() + 30)
        self.assertEqual(code, 0, receipt.read_text())
        value = json.loads(receipt.read_text())
        self.assertEqual(value['schema'], 'joulewise.night_evidence_probe_receipt.v1')
        self.assertTrue(value['verify_only'])
        self.assertIs(value['collect_started'], False)
        self.assertIs(value['load_started'], False)
        self.assertFalse(set(value) & {'custody_budget_s', 'custody_elapsed_s', 'observations'})
        self.assertFalse(list(self.f.root.rglob('rounds.jsonl')))
        self.assertFalse(list(self.f.root.rglob('evidence_processes.jsonl')))
        # Worker cleanup is supervisor-owned. Supply its proven fixture result.
        value['cleanup_proven'] = True
        receipt.write_text(json.dumps(value))
        prepared = SimpleNamespace(plan=self.f.plan, plan_path=self.f.plan_path, python=sys.executable)
        self.assertEqual(installer.validate_probe_receipt(prepared), value)

    def test_worker_rejects_ambiguous_payload_before_bindings_or_chain(self):
        path = Path(self.f.plan.chain_path)
        original = path.read_text()
        for extra in ('export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n', 'export CALIBRATION_LEDGER=/tmp/ledger\n'):
            path.write_text(original + extra)
            receipt = self.f.custody / 'refused.json'
            with mock.patch('joulewise.night_agent_install.probe_bindings') as calibration, mock.patch.object(self.driver.subprocess, 'Popen') as launch:
                rc = self.driver._probe_worker(self.f.plan_path, receipt, self.f.custody / 'progress.json', time.monotonic()+10)
            self.assertEqual(rc, 2)
            self.assertEqual(json.loads(receipt.read_text())['refusal_code'], 'probe payload kind ambiguous')
            calibration.assert_not_called()
            launch.assert_not_called()

    @unittest.skipUnless(Path('/bin/zsh').is_file(), 'zsh required for shell probe fixture')
    def test_supervisor_preserves_typed_evidence_receipt_without_custody_fields(self):
        from joulewise import night_agent_install as installer
        receipt = self.f.custody / 'night_probe_receipt.json'
        with mock.patch.dict(os.environ, {'JOULEWISE_LAUNCHD_LABEL': installer.probe_label(self.f.plan.plan_id)}), \
                mock.patch.object(self.driver, '_stop_probe_group', return_value=True):
            # Fixture-only census seam: the real worker and verify-only chain
            # finish and are reaped by communicate; no host census is claimed.
            self.assertEqual(self.driver.probe_night(self.f.plan_path, receipt, timeout_s=30), 0)
        value = json.loads(receipt.read_text())
        self.assertEqual(value['schema'], 'joulewise.night_evidence_probe_receipt.v1')
        self.assertFalse(set(value) & {'custody_budget_s','custody_elapsed_s','observations'})
        self.assertEqual(installer.validate_probe_receipt(types.SimpleNamespace(
            plan=self.f.plan, plan_path=self.f.plan_path, python=sys.executable)), value)

    def test_missing_or_duplicate_verify_marker_refuses(self):
        from joulewise import night_agent_install as installer
        bindings = installer.evidence_probe_bindings(self.f.plan, self.f.plan_path, sys.executable)
        marker = 'VERIFY_ONLY_OK manifest=' + bindings['manifest_sha256']
        for output in ('', marker + '\n' + marker + '\n', 'VERIFY_ONLY_OK manifest=wrong\n'):
            receipt = self.f.custody / 'refused.json'
            with mock.patch.object(installer, 'evidence_probe_bindings', return_value=bindings), mock.patch.object(self.driver.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, output, '')):
                rc = self.driver._evidence_probe_worker(self.f.plan, self.f.plan_path, receipt, time.monotonic()+10, lambda *args: None)
            self.assertEqual(rc, 2)
            self.assertIn('expected one matching', json.loads(receipt.read_text())['refusal_code'])

    def test_artifact_inventory_includes_each_envelope_and_raw_power(self):
        night = self.f.custody / 'night'
        for index in (1, 2):
            out = night / 'evidence' / f'envelope-{index:02d}'
            (out / 'raw').mkdir(parents=True)
            for name in ('rounds.jsonl', 'session.json', 'summary.json', 'summary.md', 'raw/power.plist'):
                (out / name).write_text(str(index))
        (night / 'evidence_busy_cores.jsonl').write_text('{}\n')
        paths = [x['path'] for x in self.driver._artifact_list(self.f.custody, night)]
        self.assertEqual(len(paths), 11)
        self.assertIn('night/evidence/envelope-02/raw/power.plist', paths)

    def admitted_night(self, plan=None, evidence=True):
        from tests.test_night_gate import EvidenceRegistrationTests, FakeProbeSource
        plan = plan or self.f.plan
        source = EvidenceRegistrationTests().source() if evidence else FakeProbeSource()
        # Authenticate with the gate fixture, then keep the actual plan identity.
        from tests.test_night_gate import make_plan
        receipt = json.loads(night_gate.evaluate_night(make_plan(), source.probes()).to_json_bytes())
        receipt['plan_id'] = plan.plan_id
        self.assertEqual(night_gate.validate_receipt(receipt), [])
        night = self.f.custody / 'night'
        night.mkdir(exist_ok=True)
        (night / 'receipt.json').write_text(json.dumps(receipt))
        (night / 'chain.started').write_text('{}')
        return night

    def deliver(self, plan=None):
        # REAL courier control path; only external delivery and liveness are fake.
        with mock.patch.object(self.driver.subprocess, 'Popen') as launch, \
                mock.patch.object(self.driver, '_wait_for_courier', return_value=(True, True)), \
                mock.patch.object(self.driver, '_watchdog_liveness_for_courier', return_value=('fixture', 0, 'idle')):
            result = self.driver.run_courier(self.f.custody, plan or self.f.plan, Path('/tmp/fixture-courier'))
        self.assertEqual(result['attempted'], 1, result)
        self.assertTrue(result['sent'], result)
        launch.assert_called_once()
        return launch.call_args.args[0]

    def test_successful_evidence_night_courier_reads_existing_executor_cleanup(self):
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        # Same producer the real executor calls; one immutable record.
        cleanup = campaign.cleanup_record(night)
        self.assertTrue(cleanup['cleanup_proven'])
        (night / 'evidence_outcome.json').write_text(json.dumps({'outcome':'complete'}))
        before = (night / 'evidence_cleanup.json').read_bytes()
        with mock.patch.object(campaign, 'cleanup_groups', side_effect=AssertionError('must read existing record')):
            argv = self.deliver()
            self.deliver()
        self.assertIn('Read this existing record', argv[2])
        self.assertEqual((night / 'evidence_cleanup.json').read_bytes(), before)

    def test_preexecute_manifest_mismatch_writes_typed_refusal_and_courier_runs(self):
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        manifest = self.f.custody / 'evidence_manifest.json'
        manifest.write_text(manifest.read_text() + ' ')
        env = self.driver._chain_environment(self.f.plan, night)
        env.update(EVIDENCE_PLAN_PATH=str(self.f.plan_path), EVIDENCE_MANIFEST_SHA256='0'*64)
        with mock.patch.dict(os.environ, env), mock.patch.object(campaign, 'execute') as execute:
            self.assertEqual(campaign.main(['run']), 2)
        execute.assert_not_called()
        self.assertFalse((night / 'evidence_processes.jsonl').exists())
        refusal = json.loads((night / 'refusal.json').read_text())
        self.assertEqual(self.driver.validate_refusal(refusal), [])
        self.assertIn('manifest_sha256 mismatch', refusal['refusal']['detail'])
        self.deliver()
        self.assertTrue(json.loads((night / 'evidence_cleanup.json').read_text())['cleanup_proven'])

    def test_cleanup_import_error_never_suppresses_the_courier(self):
        # Fresh-eyes record 71 S1: an ImportError inside _evidence_cleanup_error
        # (three deferred imports) must become a diagnostic, never a lost delivery.
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        (night / 'evidence_outcome.json').write_text(json.dumps({'outcome': 'complete'}))
        with mock.patch.object(campaign, 'cleanup_record', side_effect=ImportError('simulated')):
            argv = self.deliver()
        self.assertTrue(argv)
        self.assertIn('evidence outcome/cleanup unavailable: ImportError', (self.f.custody / 'night.log').read_text())

    def _repaired(self, raw_bytes):
        # Consult record 76: any malformed outcome becomes the refused mapping
        # with exactly one schema-valid refusal document; the courier launches.
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        campaign.cleanup_record(night)
        if raw_bytes is None:
            (night / 'evidence_outcome.json').unlink(missing_ok=True)
        else:
            (night / 'evidence_outcome.json').write_bytes(raw_bytes)
        argv = self.deliver()
        self.assertTrue(argv)
        outcome = json.loads((night / 'evidence_outcome.json').read_text())
        self.assertEqual(outcome, {'outcome': 'refused', 'error': 'chain ended without evidence outcome',
                                   'cleanup_proven': True})
        refusals = self.driver._refusal_paths(night)
        self.assertEqual(len(refusals), 1, refusals)
        self.assertEqual(self.driver.validate_refusal(json.loads(refusals[0].read_text())), [])
        return night

    def test_missing_evidence_outcome_is_repaired(self):
        self._repaired(None)

    def test_invalid_json_evidence_outcome_is_repaired(self):
        for raw in (b'{not-json', b'\xff'):
            with self.subTest(raw=raw):
                self._repaired(raw)

    def test_list_evidence_outcome_is_repaired(self):
        self._repaired(b'[]')

    def test_missing_outcome_state_is_repaired(self):
        self._repaired(b'{}')

    def test_list_outcome_state_is_repaired(self):
        self._repaired(json.dumps({'outcome': []}).encode())

    def test_numeric_outcome_state_is_repaired(self):
        self._repaired(json.dumps({'outcome': 5}).encode())

    def test_unknown_outcome_state_is_repaired(self):
        self._repaired(json.dumps({'outcome': 'weird'}).encode())

    def _untouched(self, state):
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        campaign.cleanup_record(night)
        raw = json.dumps({'outcome': state, 'error': None}).encode()
        (night / 'evidence_outcome.json').write_bytes(raw)
        self.deliver()
        self.assertEqual((night / 'evidence_outcome.json').read_bytes(), raw)
        return night

    def test_complete_outcome_is_untouched(self):
        night = self._untouched('complete')
        self.assertEqual(self.driver._refusal_paths(night), [])

    def test_partial_outcome_is_untouched(self):
        night = self._untouched('partial')
        self.assertEqual(self.driver._refusal_paths(night), [])

    def test_refused_outcome_and_existing_refusal_are_untouched(self):
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        campaign.cleanup_record(night)
        raw = json.dumps({'outcome': 'refused', 'error': 'executor said so'}).encode()
        (night / 'evidence_outcome.json').write_bytes(raw)
        campaign.write_refusal(night, self.f.plan, 'executor said so')
        before = [p.read_bytes() for p in self.driver._refusal_paths(night)]
        self.assertEqual(len(before), 1)
        self.deliver()
        self.assertEqual((night / 'evidence_outcome.json').read_bytes(), raw)
        self.assertEqual([p.read_bytes() for p in self.driver._refusal_paths(night)], before)

    def test_evidence_identity_dispatches_cleanup_without_reading_wrapper(self):
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        Path(self.f.plan.chain_path).unlink()
        with mock.patch.object(campaign, 'cleanup_groups', return_value={'cleanup_proven':True, 'residue':[]}) as cleanup:
            self.deliver()
        cleanup.assert_called_once()
        self.assertTrue((night / 'evidence_cleanup.json').exists())

    def test_rehearsal_and_wrapper_missing_calibration_always_deliver(self):
        from dataclasses import replace
        from joulewise import quiet_predicate_campaign as campaign
        Path(self.f.plan.chain_path).unlink()
        for kind in ('REHEARSAL_STUB', 'DIAGNOSTIC_NO_PACK'):
            with self.subTest(kind=kind):
                plan = replace(self.f.plan, receipt_class=kind)
                self.admitted_night(plan, evidence=False)
                with mock.patch.object(campaign, 'cleanup_groups', side_effect=AssertionError('not evidence')):
                    self.deliver(plan)
                self.assertFalse((self.f.custody / 'night/evidence_cleanup.json').exists())

    def test_cleanup_residue_is_reported_and_does_not_suppress_courier(self):
        from joulewise import quiet_predicate_campaign as campaign
        night = self.admitted_night()
        with mock.patch.object(campaign, 'cleanup_groups', return_value={'cleanup_proven':False,'residue':[99999999]}):
            self.deliver()
        self.assertFalse(json.loads((night / 'evidence_cleanup.json').read_text())['cleanup_proven'])
        self.assertEqual(json.loads((night / 'evidence_outcome.json').read_text())['outcome'], 'refused')

    def test_evidence_worker_crash_progress_keeps_typed_failure_schema(self):
        progress = self.f.custody / 'progress.json'
        with mock.patch.object(self.driver, '_evidence_probe_worker', side_effect=RuntimeError('fixture crash')):
            with self.assertRaisesRegex(RuntimeError, 'fixture crash'):
                self.driver._probe_worker(self.f.plan_path, self.f.custody/'receipt.json', progress, time.monotonic()+10)
        self.assertEqual(json.loads(progress.read_text())['record']['schema'], 'joulewise.night_evidence_probe_receipt.v1')


@unittest.skipUnless(Path('/bin/zsh').is_file(), 'zsh required for calibration probe fixture')
class CourierDeliveryBoundaryTests(unittest.TestCase):
    setUp = EvidenceProbeTests.setUp
    admitted_night = EvidenceProbeTests.admitted_night

    def run_terminated_night(self, after_chain=lambda night: None, *, wait=True,
                             termination_proven=True):
        """Seat-78 chain fixture; real result, inventory, argv and courier flow."""
        from tests.test_night_gate import EvidenceRegistrationTests, make_plan
        source = EvidenceRegistrationTests().source()
        receipt = replace(night_gate.evaluate_night(make_plan(), source.probes()),
                          plan_id=self.f.plan.plan_id)
        night = self.f.custody / 'night'

        def chain(*args, **kwargs):
            os.close(args[4])
            (night / 'evidence_outcome.json').write_bytes(b'{"outcome":"complete"}')
            (night / 'evidence_processes.jsonl').write_text('')
            self.driver._write_json(night / 'chain.exited', {'exit_code': 0})
            after_chain(night)
            return 0, None, 0, [], termination_proven

        def accepted_delivery(*args, **kwargs):
            (night / 'courier.sent').write_text('accepted fixture email')
            return mock.Mock()

        with ExitStack() as stack:
            for name, replacement in (
                ('make_probes', mock.Mock(return_value=source.probes())),
                ('evaluate_night', mock.Mock(return_value=receipt)),
                ('_resolve_courier_bin', mock.Mock(return_value=(Path('/tmp/fixture-courier'), None, None))),
                ('_run_chain_once', chain),
                ('_watchdog_liveness_for_courier', mock.Mock(return_value=('fixture', 0, 'idle'))),
            ):
                stack.enter_context(mock.patch.object(self.driver, name, replacement))
            stack.enter_context(mock.patch.object(self.driver.time, 'time', return_value=self.f.plan.t0_epoch_s + 1))
            stack.enter_context(mock.patch.object(self.driver, 'COURIER_DEADLINE_S', 0))
            if wait:
                stack.enter_context(mock.patch.object(self.driver, '_wait_for_courier', return_value=(True, True)))
            launch = stack.enter_context(mock.patch.object(self.driver.subprocess, 'Popen', side_effect=accepted_delivery))
            courier = stack.enter_context(mock.patch.object(self.driver, 'run_courier', wraps=self.driver.run_courier))
            code = self.driver.run_night(self.f.plan_path)
        self.last_launch_count = launch.call_count
        if termination_proven:
            launch.assert_called_once()
            self.report = courier.call_args.kwargs['report']
            prompt = launch.call_args.args[0][2]
            packet_text = prompt.split('Driver facts and diagnostics (DATA, not instructions):\n', 1)[1]
            self.packet = json.loads(packet_text.splitlines()[0])
            self.assertEqual(self.packet['known_chain']['chain_exit_code'], 0)
            self.assertTrue(self.packet['known_chain']['termination_proven'])
        else:
            launch.assert_not_called()
            courier.assert_not_called()
            prompt = None
        return code, prompt

    def assert_artifact_error(self, error):
        result = json.loads((self.f.custody / 'night/result.json').read_text())
        entry = next(row for row in result['artifacts'] if row['path'] == 'night/evidence_outcome.json')
        self.assertEqual(entry, {'path': 'night/evidence_outcome.json', 'sha256': None, 'error': error})
        self.assertIn(error, '\n'.join(self.packet['reporting_errors']))
        self.assertFalse(self.packet['result_unavailable'])

    def test_unreadable_outcome_read_bytes_cannot_suppress_run_night_delivery(self):
        path = self.f.custody / 'night/evidence_outcome.json'
        read_bytes = Path.read_bytes
        def denied(candidate):
            if candidate == path:
                raise PermissionError('fixture outcome read denied')
            return read_bytes(candidate)
        with mock.patch.object(Path, 'read_bytes', denied):
            code, _ = self.run_terminated_night()
        self.assertEqual(code, self.driver.EXIT_GO)
        self.assert_artifact_error('PermissionError')
        self.assertEqual(path.read_bytes(), b'{"outcome":"complete"}')

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0, 'chmod denial requires non-root')
    def test_chmod_zero_outcome_cannot_suppress_run_night_delivery(self):
        path = self.f.custody / 'night/evidence_outcome.json'
        try:
            self.run_terminated_night(lambda night: path.chmod(0))
            self.assert_artifact_error('PermissionError')
        finally:
            if path.exists():
                path.chmod(0o600)
        self.assertEqual(path.read_bytes(), b'{"outcome":"complete"}')

    def test_result_create_failure_before_any_bytes_still_launches_with_minimal_refusal(self):
        path = self.f.custody / 'night/result.json'
        real_open = os.open
        failures = []
        def fail_first(candidate, *args, **kwargs):
            if Path(candidate) == path and not failures:
                failures.append(True)
                raise PermissionError('fixture result create denied')
            return real_open(candidate, *args, **kwargs)
        with mock.patch.object(os, 'open', fail_first):
            code, prompt = self.run_terminated_night()
        result = json.loads(path.read_text())
        self.assertEqual(code, self.driver.EXIT_REFUSED)
        self.assertEqual(result['verdict'], 'REFUSED')
        self.assertTrue(result['result_unavailable'])
        self.assertEqual(result['chain_exit_code'], 0)
        self.assertTrue(result['termination_proven'])
        self.assertIn('post-chain result: PermissionError', result['reporting_errors'][0])
        self.assertTrue(self.packet['result_unavailable'])
        self.assertIn('result publication failed', prompt)

    def assert_obstructed_result_preserved(self, directory):
        path = self.f.custody / 'night/result.json'
        partial = b'{"verdict":"GO",'
        def obstruct(night):
            if directory:
                path.mkdir()
                (path / 'foreign').write_bytes(partial)
            else:
                path.write_bytes(partial)
        code, _ = self.run_terminated_night(obstruct)
        self.assertEqual(code, self.driver.EXIT_REFUSED)
        self.assertEqual((path / 'foreign' if directory else path).read_bytes(), partial)
        self.assertTrue(self.packet['result_unavailable'])
        errors = '\n'.join(self.packet['reporting_errors'])
        self.assertIn('post-chain result: FileExistsError', errors)
        self.assertIn('minimal result persistence: FileExistsError', errors)

    def test_result_directory_blocks_both_writers_but_not_delivery(self):
        self.assert_obstructed_result_preserved(True)

    def test_partial_result_blocks_both_writers_but_is_preserved_and_delivered(self):
        self.assert_obstructed_result_preserved(False)

    def test_fixed_outcome_directory_is_reported_instead_of_silently_omitted(self):
        path = self.f.custody / 'night/evidence_outcome.json'
        def obstruct(night):
            path.unlink()
            path.mkdir()
        self.run_terminated_night(obstruct)
        self.assert_artifact_error('IsADirectoryError')
        self.assertTrue(path.is_dir())
        self.assertIn('evidence outcome/cleanup unavailable', '\n'.join(self.packet['reporting_errors']))

    def test_outcome_replaced_after_stat_cannot_abort_inventory_or_delivery(self):
        path = self.f.custody / 'night/evidence_outcome.json'
        read_bytes = Path.read_bytes
        def replace_before_read(candidate):
            if candidate == path and candidate.is_file():
                candidate.unlink()
                candidate.mkdir()
            return read_bytes(candidate)
        with mock.patch.object(Path, 'read_bytes', replace_before_read):
            self.run_terminated_night()
        self.assert_artifact_error('IsADirectoryError')

    def test_failed_evidence_discovery_is_an_explicit_incomplete_inventory(self):
        evidence = self.f.custody / 'night/evidence'
        scandir = os.scandir
        def denied(path):
            if path == str(evidence):
                raise PermissionError('fixture traversal denied')
            return scandir(path)
        with mock.patch.object(os, 'scandir', denied):
            self.run_terminated_night(lambda night: evidence.mkdir())
        result = json.loads((self.f.custody / 'night/result.json').read_text())
        entry = next(row for row in result['artifacts'] if row['path'] == 'night/evidence')
        self.assertEqual(entry['diagnostic'], 'evidence discovery incomplete')
        self.assertEqual(entry['error'], 'PermissionError')
        self.assertIn('evidence discovery incomplete', '\n'.join(self.packet['reporting_errors']))

    def test_publication_failure_after_go_preserves_the_result_and_exit_code(self):
        self.publication.return_value = 'durable record failed: fixture publication unavailable'
        code, _ = self.run_terminated_night()
        self.assertEqual(code, self.driver.EXIT_GO)
        result = json.loads((self.f.custody / 'night/result.json').read_text())
        self.assertEqual(result['verdict'], 'GO')
        self.assertFalse(self.packet['result_unavailable'])
        self.assertIn(self.publication.return_value, self.packet['reporting_errors'])

    def test_post_delivery_publication_failure_reaches_the_night_log(self):
        # Re-audit 81 R2: the prompt was issued before the second publication
        # ran, so its failure must survive in night.log (GO and delivery intact).
        self.publication.side_effect = [None, 'durable record failed: fixture second push']
        code, _ = self.run_terminated_night()
        self.assertEqual(code, self.driver.EXIT_GO)
        self.assertEqual(self.publication.call_count, 2)
        self.assertNotIn('fixture second push', '\n'.join(self.packet['reporting_errors']))
        self.assertIn('durable record failed: fixture second push', (self.f.custody / 'night.log').read_text())
        self.assertEqual(json.loads((self.f.custody / 'night/result.json').read_text())['verdict'], 'GO')

    def test_late_unreadable_artefact_omission_reaches_the_prompt(self):
        # Re-audit 81 R1 end to end: the publisher (real inventory) names an
        # artefact that became unreadable after the result was written, and
        # that name reaches the courier prompt before the launch.
        self.publication.side_effect = [
            'durable record omitted unreadable artefacts: night/chain.exited (PermissionError)', None]
        code, _ = self.run_terminated_night()
        self.assertEqual(code, self.driver.EXIT_GO)
        self.assertIn('durable record omitted unreadable artefacts: night/chain.exited (PermissionError)',
                      self.packet['reporting_errors'])

    def test_result_log_failure_does_not_relabel_a_published_go_result(self):
        def obstruct(night):
            path = self.f.custody / 'night.log'
            path.unlink()
            path.mkdir()
        code, _ = self.run_terminated_night(obstruct)
        self.assertEqual(code, self.driver.EXIT_GO)
        self.assertFalse(self.packet['result_unavailable'])
        self.assertIn('post-chain result: IsADirectoryError', '\n'.join(self.packet['reporting_errors']))
        self.assertEqual(json.loads((self.f.custody / 'night/result.json').read_text())['verdict'], 'GO')

    def test_result_publication_failure_never_authorizes_unproven_chain_delivery(self):
        self.run_terminated_night(lambda night: (night / 'result.json').mkdir(), termination_proven=False)
        self.assertFalse(json.loads((self.f.custody / 'night/courier.json').read_text())['sent'])

    def test_optional_prelaunch_failures_individually_and_together_still_reach_popen(self):
        class BrokenDiagnostic(Exception):
            def __str__(self):
                raise ValueError('broken exception string')

        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        (night / 'evidence_outcome.json').write_text('{"outcome":"complete"}')
        prompt_path = self.driver.REPO_ROOT / 'docs/process/NIGHT_COURIER_PROMPT.md'
        cases = ('prompt decode', 'prompt import', 'heartbeat', 'log', 'publication', 'broken diagnostic', 'lock metadata')
        for faults in [(name,) for name in cases] + [cases]:
            with self.subTest(faults=faults), ExitStack() as stack:
                expected = []
                if 'heartbeat' in faults:
                    path = night / 'courier.heartbeat'
                    path.mkdir()
                    stack.callback(path.rmdir)
                    # macOS unlink(directory) reports EPERM; Linux uses EISDIR.
                    expected.append('heartbeat reset: ')
                if 'log' in faults:
                    path = self.f.custody / 'night.log'
                    path.unlink(missing_ok=True)
                    path.mkdir()
                    stack.callback(path.rmdir)
                    expected.append('night log: IsADirectoryError')
                if 'prompt decode' in faults:
                    read_text = Path.read_text
                    def fail_decode(path, *args, **kwargs):
                        if path == prompt_path:
                            raise UnicodeError('fixture prompt decode')
                        return read_text(path, *args, **kwargs)
                    stack.enter_context(mock.patch.object(Path, 'read_text', fail_decode))
                    expected.append('courier prompt: UnicodeError')
                if 'prompt import' in faults:
                    stack.enter_context(mock.patch.object(self.driver, '_watchdog_liveness_for_courier', side_effect=ImportError('fixture import')))
                    if 'prompt decode' not in faults:
                        expected.append('courier prompt: ImportError')
                if 'publication' in faults:
                    stack.enter_context(mock.patch.object(self.driver, '_durable_record', side_effect=RuntimeError('fixture publication')))
                    expected.append('durable record: RuntimeError')
                if 'broken diagnostic' in faults:
                    stack.enter_context(mock.patch.object(self.driver, '_evidence_cleanup_error', side_effect=BrokenDiagnostic()))
                    expected.append('evidence repair: diagnostic formatting failed')
                if 'lock metadata' in faults:
                    refresh = self.driver._refresh_courier_lock
                    calls = []
                    def fail_refresh(fd):
                        calls.append(fd)
                        if len(calls) > 1:
                            raise OSError('fixture metadata refresh')
                        return refresh(fd)
                    stack.enter_context(mock.patch.object(self.driver, '_refresh_courier_lock', side_effect=fail_refresh))
                    expected.append('lock metadata: OSError')
                # Ensure even the log-only case has a diagnostic to log.
                report = {'facts': {'chain_exit_code': 0}, 'diagnostics': ['fixture limitation'],
                          'result_unavailable': False, 'base_exit_code': 0, 'prepared': False}
                launch = stack.enter_context(mock.patch.object(self.driver.subprocess, 'Popen'))
                stack.enter_context(mock.patch.object(self.driver, '_wait_for_courier', return_value=(True, True)))
                outcome = self.driver.run_courier(self.f.custody, self.f.plan, Path('/tmp/fixture-courier'), report=report)
                self.assertEqual((outcome['attempted'], outcome['sent']), (1, True))
                launch.assert_called_once()
                argv = launch.call_args.args[0]
                self.assertEqual(argv[:2], ('/tmp/fixture-courier', '-p'))
                self.assertEqual(argv[3:], ('--output-format', 'text', '--allowedTools', self.driver.COURIER_ALLOWED_TOOLS))
                for diagnostic in expected:
                    self.assertIn(diagnostic, argv[2])
                if 'prompt decode' in faults or 'prompt import' in faults:
                    self.assertIn('Prompt/watchdog context unavailable', argv[2])
                    self.assertIn(self.driver.COURIER_RECIPIENT, argv[2])

    def test_delivered_email_survives_outcome_journal_and_sent_fsync_failures(self):
        def obstruct(night):
            (night / 'courier.json').mkdir()
            (night / 'courier.attempts.jsonl').mkdir()
        with mock.patch.object(self.driver, '_fsync_path', side_effect=PermissionError('fixture sent fsync')):
            code, _ = self.run_terminated_night(obstruct, wait=False)
        self.assertEqual(code, self.driver.EXIT_GO)
        self.assertTrue((self.f.custody / 'night/courier.sent').is_file())
        errors = '\n'.join(self.report['diagnostics'])
        self.assertIn('sent marker persistence: PermissionError', errors)
        self.assertIn('courier attempt journal: IsADirectoryError', errors)
        self.assertIn('courier outcome: FileExistsError', errors)

    def test_lock_refused_caller_does_no_repair_or_heartbeat_work_and_only_winner_launches(self):
        from concurrent.futures import ThreadPoolExecutor
        night = self.admitted_night()
        (night / 'evidence_processes.jsonl').write_text('')
        (night / 'evidence_outcome.json').write_text('{"outcome":"refused","error":"executor refused"}')
        heartbeat = night / 'courier.heartbeat'
        heartbeat.write_bytes(b'previous heartbeat')
        entered, release = threading.Event(), threading.Event()
        repair = self.driver._evidence_cleanup_error
        def hold_owner(*args):
            entered.set()
            if not release.wait(5):
                raise RuntimeError('winner was not released')
            return repair(*args)
        def call():
            return self.driver.run_courier(self.f.custody, self.f.plan, Path('/tmp/fixture-courier'))
        with mock.patch.object(self.driver, '_evidence_cleanup_error', side_effect=hold_owner) as repairs, \
                mock.patch.object(self.driver.subprocess, 'Popen') as launch, \
                mock.patch.object(self.driver, '_wait_for_courier', return_value=(True, True)), \
                ThreadPoolExecutor(max_workers=2) as pool:
            winner = pool.submit(call)
            try:
                self.assertTrue(entered.wait(5))
                # Owner is paused after acquisition, before any evidence repair.
                # No barrier in write_refusal: the loser must never reach it.
                is_file = Path.is_file
                def reject_heartbeat_inspection(path):
                    if path == heartbeat:
                        raise AssertionError('loser inspected heartbeat')
                    return is_file(path)
                with mock.patch.object(Path, 'is_file', reject_heartbeat_inspection):
                    loser = pool.submit(call).result(timeout=5)
                self.assertEqual((loser['attempted'], loser['sent']), (0, False))
                self.assertEqual(heartbeat.read_bytes(), b'previous heartbeat')
                repairs.assert_called_once()
                launch.assert_not_called()
                self.assertEqual(self.driver._refusal_paths(night), [])
            finally:
                release.set()
            won = winner.result(timeout=5)
        self.assertEqual((won['attempted'], won['sent']), (1, True))
        self.assertEqual(len(self.driver._refusal_paths(night)), 1)
        launch.assert_called_once()
        self.last_concurrent_counts = {'winner': won, 'loser': loser, 'refusals': 1, 'launches': launch.call_count}

    def test_fallback_recipient_constant_matches_the_courier_template(self):
        import re
        template = (REPO_ROOT / 'docs/process/NIGHT_COURIER_PROMPT.md').read_text()
        # The prompt may follow the address with a comma or a period; match
        # the address itself, not up to the last dot on the line.
        address = re.search(r'Email Ed at ([\w.+-]+@[\w-]+(?:\.[\w-]+)+)', template).group(1)
        self.assertEqual(self.driver.COURIER_RECIPIENT, address)

    def test_durable_publication_skips_error_entries_and_returns_safe_diagnostics(self):
        # Exercise the real inventory and publisher against a fake git transport.
        from scripts import run_night
        # The original function is available from the patcher's module source load.
        real_publish = _load_driver()._durable_record
        night = self.f.custody / 'night'
        night.mkdir()
        (night / 'evidence_outcome.json').mkdir()
        (night / 'receipt.json').write_text('{}')
        def git(argv, **kwargs):
            if argv[:4] == ['git', 'clone', '--depth', '1']:
                Path(argv[-1]).mkdir()
            return types.SimpleNamespace(stdout='fixture-origin\n')
        with mock.patch.object(run_night.subprocess, 'run', side_effect=git):
            diagnostic = real_publish(self.f.custody, night, self.f.plan)
        # Re-audit 81 R1: the omission is published as a diagnostic, not silently.
        self.assertEqual(diagnostic,
                         'durable record omitted unreadable artefacts: night/evidence_outcome.json (IsADirectoryError)')
        destination = self.f.custody / 'results-clone/docs/process_traces/night-results' / self.f.plan.plan_id
        self.assertTrue((destination / 'receipt.json').is_file())
        self.assertFalse((destination / 'evidence_outcome.json').exists())
        (night / 'evidence_outcome.json').rmdir()
        (night / 'evidence_outcome.json').write_text('{"outcome": "complete"}')
        with mock.patch.object(run_night.subprocess, 'run', side_effect=git):
            self.assertIsNone(real_publish(self.f.custody, night, self.f.plan))
        with mock.patch.object(run_night.subprocess, 'run', side_effect=UnicodeError('decode')):
            self.assertIn('UnicodeError', real_publish(self.f.custody, night, self.f.plan))


class CalibrationProbeByteCompatibilityTests(unittest.TestCase):
    def test_calibration_worker_preserves_part1_fields_with_cadence(self):
        import ast
        from scripts import run_night as driver
        from joulewise import night_agent_install as installer
        fixture = NightProbeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        baseline = types.ModuleType('stagea_part1_probe_baseline')
        # Compile only the unchanged calibration worker from the pinned base;
        # all other dependencies are the same fixture and current pure helpers.
        raw = subprocess.check_output(['git','show','3e4acc59:scripts/run_night.py'],cwd=REPO_ROOT,text=True)
        node = next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='_probe_worker')
        namespace = dict(driver.__dict__)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<part1-probe>','exec'),namespace)
        # A frozen wall clock yields a literal byte comparison; no changing
        # PID/temp path is a field in the worker's calibration receipt.
        receipts=[]
        for worker in (namespace['_probe_worker'],driver._probe_worker):
            target=fixture.root/('base.json' if not receipts else 'current.json')
            with mock.patch.object(driver.time,'time',return_value=1800000000.), mock.patch.dict(os.environ,{'JOULEWISE_LAUNCHD_LABEL':installer.probe_label(fixture.plan.plan_id)}):
                self.assertEqual(worker(fixture.plan_path,target,fixture.root/'progress.json',time.monotonic()+20),0)
            receipts.append(target.read_bytes())
        baseline_record, current_record = map(json.loads, receipts)
        self.assertEqual("joulewise.night_probe_receipt.v2", current_record.pop("schema"))
        cadence = current_record.pop("cadence")
        self.assertTrue(cadence["passed"])
        self.assertEqual(300, cadence["count"])
        self.assertGreater(current_record.pop("powermetrics_pgid"), 1)
        baseline_record.pop("schema")
        self.assertEqual(baseline_record, current_record)


class EvidenceProbeFailureTests(unittest.TestCase):
    # Reuse fixture setup, but expose only the additional producer branches.
    setUp = EvidenceProbeTests.setUp
    def test_chain_failure_timeout_and_mutation_cannot_produce_success(self):
        from joulewise import night_agent_install as installer
        bindings = installer.evidence_probe_bindings(self.f.plan,self.f.plan_path,sys.executable)
        marker = 'VERIFY_ONLY_OK manifest='+bindings['manifest_sha256']+'\n'
        receipt = self.f.custody/'failure.json'
        for result in (subprocess.CompletedProcess([],2,marker,'chain failed'),
                       subprocess.TimeoutExpired(['fixture'],1)):
            with mock.patch.object(installer,'evidence_probe_bindings',return_value=bindings), \
                    mock.patch.object(self.driver.subprocess,'run',side_effect=result if isinstance(result,Exception) else None,return_value=result):
                self.assertEqual(self.driver._evidence_probe_worker(self.f.plan,self.f.plan_path,receipt,time.monotonic()+2,lambda *args:None),2)
            self.assertNotEqual(json.loads(receipt.read_text())['outcome'],'ok')
        with mock.patch.object(installer,'evidence_probe_bindings',side_effect=[bindings,{**bindings,'plan_sha256':'0'*64}]), \
                mock.patch.object(self.driver.subprocess,'run',return_value=subprocess.CompletedProcess([],0,marker,'')):
            self.assertEqual(self.driver._evidence_probe_worker(self.f.plan,self.f.plan_path,receipt,time.monotonic()+2,lambda *args:None),2)
        self.assertIn('changed during',json.loads(receipt.read_text())['refusal_code'])
