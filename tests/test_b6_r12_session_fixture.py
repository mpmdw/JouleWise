"""Source-only R12 bootstrap tests. All paths and readings are synthetic."""
import hashlib
import importlib.util
import json
import os
import plistlib
import shutil
import struct
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from b6_r12_session_fixture import command, prepare, export_chain_inputs, prepare_interpreters
from b6_r12_runtime import SharedClock
from b6_r12_chain_fixture import PIN


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r12-session-")
        self.addCleanup(self.temp.cleanup)
        self.root = prepare(Path(self.temp.name).resolve() / "fixture")

    def test_pinned_children_share_clock_without_wall_wait(self):
        """Predict: pinned SystemClock advances 60+30 s across fresh children in <10 wall s."""
        started = time.monotonic()
        rows = []
        for seconds in (60, 30):
            p = subprocess.run(command(self.root, "probe", seconds), capture_output=True, text=True, timeout=20)
            self.assertEqual(p.returncode, 0, p.stderr)
            rows.append(json.loads(p.stdout))
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual(rows[0]["after"], rows[1]["before"])
        self.assertEqual(rows[1]["after"]["epoch_s"] - rows[0]["before"]["epoch_s"], 90)
        manifest = json.loads((self.root / "manifest.json").read_text())
        path = Path(rows[0]["source"])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest["source_sha256"]["joulewise/clock.py"])

    def test_guard_rejects_metadata_probes_exec_and_escaping_write(self):
        """Predict: six denials occur before native metadata access, exec or file creation."""
        result = subprocess.run(command(self.root, "guard-probe"), capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 6)
        self.assertFalse((self.root.parent / "R12-outside-write").exists())

    def test_bootstrap_never_arms_native_diagnostic_watchdog(self):
        """Predict: even the legacy trace flag cannot arm a native traceback watchdog/handler or leave a diagnostic file; the source program exits 0. This excludes an agent diagnostic, not a chain judgment."""
        script = f'''
import faulthandler, sys
from unittest.mock import patch
sys.path.insert(0, {str(REPO / "scripts")!r})
from b6_r12_runtime import bootstrap
sys.path.insert(0, sys.argv[1])
def native_probe(*args, **kwargs):
    raise AssertionError("native diagnostic watchdog reached")
with patch.object(faulthandler, "register", native_probe), patch.object(faulthandler, "dump_traceback_later", native_probe):
    raise SystemExit(bootstrap(["--root", sys.argv[1], "code", "pass"]))
'''
        result = subprocess.run([sys.executable, "-B", "-c", script, str(self.root)],
                                capture_output=True, text=True,
                                env={**os.environ, "R12_TRACE_STACKS": "1"}, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.root.glob("debug-stack-*.txt")), [])

    def test_real_timer_uses_injected_clock_without_native_alarm(self):
        """Predict: a 60 s ITIMER_REAL expires after 120 injected seconds, without calling the native timer."""
        bootstrap = self.root / "bootstrap.py"
        bootstrap.write_text("import signal\n"
            "def forbidden_native_timer(*args):\n"
            "    raise AssertionError('native ITIMER_REAL reached')\n"
            "signal.setitimer = forbidden_native_timer\n" + bootstrap.read_text())
        code = '''import signal, time
from runtime import REAL_MONOTONIC, REAL_SLEEP
fired = []
signal.signal(signal.SIGALRM, lambda *args: fired.append(time.monotonic()))
try:
    assert signal.setitimer(signal.ITIMER_REAL, 60) == (0.0, 0.0)
    time.sleep(120)
    deadline = REAL_MONOTONIC() + 1
    while not fired and REAL_MONOTONIC() < deadline:
        REAL_SLEEP(.005)
    assert fired == [1120.0], fired
    assert signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)
finally:
    signal.setitimer(signal.ITIMER_REAL, 0)
print('logical_alarm')
'''
        result = subprocess.run(command(self.root, "code", code), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "logical_alarm")

    def test_default_term_reaches_child_without_clock_reads(self):
        """Predict: declared TERM terminates an owned stdin-blocked child with returncode -15, without native signals or child clock reads."""
        bootstrap = self.root / "bootstrap.py"
        bootstrap.write_text("import os\n"
            "original_kill = os.kill\n"
            "def no_native_signal(pid, signum):\n"
            "    if signum: raise AssertionError('native signal reached')\n"
            "    return original_kill(pid, 0)\n"
            "os.kill = os.killpg = no_native_signal\n" + bootstrap.read_text())
        prepare_interpreters(self.root)
        code = '''import subprocess, sys, os, signal
from pathlib import Path
from runtime import REAL_MONOTONIC, REAL_SLEEP
root = Path(sys.argv[1])
p = subprocess.Popen([str(root/'pin/.venv/bin/python'), '-B', '-c',
    "import sys;print('ready',flush=True);sys.stdin.buffer.read(1)"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
assert p.stdout.readline().strip() == b'ready'
os.killpg(p.pid, signal.SIGTERM)
deadline = REAL_MONOTONIC() + 1
while p.poll() is None and REAL_MONOTONIC() < deadline:
    REAL_SLEEP(.005)
observed = p.poll()
if observed is None:
    p.stdin.close()
    deadline = REAL_MONOTONIC() + 5
    while p.poll() is None and REAL_MONOTONIC() < deadline:
        REAL_SLEEP(.005)
    assert p.poll() == 0, p.poll()
else:
    p.stdin.close()
assert observed == -signal.SIGTERM, observed
print('default_term')
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "default_term")

    @unittest.skipUnless(hasattr(time, "CLOCK_UPTIME_RAW"), "macOS uptime source")
    def test_original_sleep_reader_uses_coherent_uptime_input(self):
        """Predict: original sleep reader observes zero sleep and no flags across a 75 s injected wait."""
        code = '''from joulewise.b6 import sleep_guard
import time
first = sleep_guard.safe_sleep_reading()
time.sleep(75)
last = sleep_guard.safe_sleep_reading()
assert 'error' not in first, first
assert 'error' not in last, last
assert sleep_guard.slept_ns(first, last) == 0
assert last['uptime_raw_ns'] - first['uptime_raw_ns'] == 75_000_000_000
assert sleep_guard.run_sleep_flags(first, last) == []
print('coherent_no_sleep')
'''
        result = subprocess.run(command(self.root, "code", code), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "coherent_no_sleep")

    def test_smc_source_types_pass_original_current_parser(self):
        """Predict: original SMC battery parser accepts integer 0 mA and a positive integer 12000 mV, with no source errors."""
        code = '''from pathlib import Path
from runtime import install_sources, SharedClock
from joulewise.hazards import smc, battery
import sys
root = Path(sys.argv[1])
clock = SharedClock(root/'clock.bin')
install_sources(root, clock)
sample = smc.Reader().read()
assert sample['errors'] == {}
assert battery.smc_current(sample) == (0, None), sample
assert type(sample['values']['B0AV']) is int and sample['values']['B0AV'] == 12000
print('typed_smc')
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "typed_smc")

    def test_subprocess_deadline_uses_child_logical_clock(self):
        """Predict: a child that advances 5 logical seconds then waits for stdin exceeds a 1 s parent deadline before 1 wall second."""
        prepare_interpreters(self.root)
        code = '''import subprocess, sys, time
from pathlib import Path
from runtime import REAL_MONOTONIC
root = Path(sys.argv[1])
child = "import sys,time;print('booted',flush=True);sys.stdin.buffer.read(1);time.sleep(5);print('ready',flush=True);sys.stdin.buffer.read(1)"
process = subprocess.Popen([str(root/'pin/.venv/bin/python'),'-B','-c',child],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
assert process.stdout.readline().strip() == b'booted'
probe = subprocess.run(['/usr/sbin/sysctl','-n','hw.model'], capture_output=True, text=True)
assert probe.stdout.strip() == 'Mac15,9'
before_probe_wait = time.monotonic()
time.sleep(17)
assert time.monotonic() == before_probe_wait
started = REAL_MONOTONIC()
original_deadline_clock = subprocess._time
released = False
def deadline_clock():
    global released
    value = original_deadline_clock()
    # Release only after the parent's deadline base was read. Otherwise the
    # child may finish its entire advance before wait() establishes a budget.
    if not released:
        released = True
        process.stdin.write(b'a');process.stdin.flush()
    return value
subprocess._time = deadline_clock
try:
    process.wait(timeout=1)
    raise AssertionError('shared logical deadline did not fire')
except subprocess.TimeoutExpired:
    assert REAL_MONOTONIC() - started < 1.0
    assert time.monotonic() == 1005.0
finally:
    process.stdin.write(b'x');process.stdin.flush()
    assert process.wait(timeout=1) == 0
print('logical_timeout')
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "logical_timeout")

    def test_synthetic_inputs_keep_canonical_suite_bindings(self):
        """Predict: every synthetic suite config binds the pinned canonicalizer's actual digest, with production 57.6 s idle inputs."""
        export_chain_inputs(self.root)
        (self.root / "source-policy.json").write_text('{"volume":"reduced"}\n')
        made = subprocess.run(command(self.root, "make-inputs"), capture_output=True, text=True, timeout=120)
        self.assertEqual(made.returncode, 0, made.stderr)
        code = '''import json
from pathlib import Path
from joulewise.suite import canonical_effective_manifest, suite_manifest_sha256
from runtime import source_root
root = Path(__import__('sys').argv[1])
pin = source_root(root)
count = 0
for path in (pin / 'configs/campaigns').rglob('*.json'):
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or 'hardware_target' not in value:
        continue
    assert value['sampling']['idle_seconds'] == 57.6
    profile = value.get('workload_profile', {})
    if profile.get('suite_manifest_ref'):
        data = json.loads((pin / profile['suite_manifest_ref']).read_text())
        assert profile['suite_manifest_sha256'] == suite_manifest_sha256(canonical_effective_manifest(data)), str(path)
        count += 1
print(count)
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(int(result.stdout.strip()), 50)

    @unittest.skipUnless(sys.platform == "darwin", "pinned USB protocol uses CommonCrypto")
    def test_source_pruning_preserves_raw_instrument_bytes(self):
        """Predict: waveform pruning and notification polling preserve complete plist bytes and every meter poll byte against unpruned, unthrottled inputs."""
        reference = prepare(Path(self.temp.name).resolve() / "unpruned-reference")
        source = (reference / "runtime.py").read_text()
        source = source.replace('                    self.intervals = [row for row in self.intervals if row["end_ns"] > clock.ns - 180_000_000]\n', '')
        source = source.replace('            intervals = [row for row in intervals if row["end_ns"] > endpoint]\n', '')
        gate = 'if (self.stop_callbacks and not self.stop_delivered\n                and REAL_MONOTONIC() >= self.next_control_check):'
        self.assertIn(gate, source)
        source = source.replace(gate, 'if not self.stop_delivered:')
        (reference / "runtime.py").write_text(source)
        waves = [dict(start_ns=999_000_000_000, end_ns=999_500_000_000, power_mw=8000),
                 dict(start_ns=1_000_000_000_000, end_ns=1_000_500_000_000, power_mw=4000),
                 dict(start_ns=1_001_000_000_000, end_ns=1_001_500_000_000, power_mw=8000)]
        payloads, plists = [], []
        relative = "scripts/km003c_monitor.py"
        meter_source = subprocess.check_output(["git", "show", f"{PIN}:{relative}"], cwd=REPO)
        for root in (self.root, reference):
            (root / "source-policy.json").write_text('{"volume":"prerequisite"}\n')
            (root / "engine-intervals.jsonl").write_text(''.join(json.dumps(row) + '\n' for row in waves))
            script = root / "pin" / relative
            script.parent.mkdir(exist_ok=True)
            script.write_bytes(meter_source)
            meter = subprocess.run(command(root, "meter-probe"), capture_output=True, text=True, timeout=30)
            self.assertEqual(meter.returncode, 0, meter.stderr)
            payloads.append([line for line in (root / "source-only-meter.jsonl").read_bytes().splitlines()
                             if json.loads(line).get("k") == "b"])
            # A second independent source timeline, not a generated session.
            (root / "clock.bin").write_bytes(struct.pack("!Q", 1_000_000_000_000))
            sampler = subprocess.run(command(root, "sampler", "/usr/bin/powermetrics", "-i", "100", "-n", "20",
                "-o", root / "source.plist"), capture_output=True, text=True, timeout=30)
            self.assertEqual(sampler.returncode, 0, sampler.stderr)
            plists.append((root / "source.plist").read_bytes())
        self.assertEqual(payloads[0], payloads[1])
        self.assertEqual(plists[0], plists[1])

    def test_notification_polling_does_not_cache_clock_values(self):
        """Predict: 500 clock reads plus 60/30 s advances match the unthrottled reference byte for byte; another clock's advance is visible immediately."""
        from types import MethodType
        current = SharedClock(self.root / "clock.bin")
        reference = SharedClock.create(self.root / "reference-clock.bin")
        self.addCleanup(current.close)
        self.addCleanup(reference.close)
        def old_frontier(clock):
            # Exact prior input-free read path; no chain function is replaced.
            if not clock.stop_delivered and ((clock.path.parent / "source-stop.json").exists()
                    or (clock.path.parent / "signal-inputs" / f"{os.getpid()}-{os.environ.get('R12_PROCESS_TOKEN','top')}.json").exists()):
                raise AssertionError("this reference has no notification input")
            with clock.lock():
                return struct.unpack("!Q", clock.map[:])[0]
        reference.frontier = MethodType(old_frontier, reference)
        outputs = []
        for clock in (current, reference):
            data = [clock.monotonic_ns() for _ in range(500)]
            for seconds in (60, 30):
                clock.sleep(seconds)
                data.append(clock.monotonic_ns())
            outputs.append(b''.join(struct.pack('!Q', value) for value in data))
        self.assertEqual(outputs[0], outputs[1])
        other = SharedClock(self.root / "clock.bin")
        self.addCleanup(other.close)
        before = current.monotonic_ns()
        other.sleep(1)
        self.assertEqual(current.monotonic_ns(), before + 1_000_000_000)

    def test_public_model_input_drives_declared_science_sensor_script(self):
        """Predict: declared science input emits busy GPU/6 W; reference input emits clean GPU/0 W, using only raw source inputs."""
        (self.root / "source-policy.json").write_text('{"volume":"reduced","gpu_busy_science":true}\n')
        for name, idle, power in (("Qwen3-1.7B-4bit", 0., 6000.), ("Qwen2.5-1.5B-Instruct-4bit", .999, 0.)):
            (self.root / "source-stop.json").unlink(missing_ok=True)
            (self.root / f"model-source-{os.getpid()}.json").write_text(json.dumps({"source": str(self.root / name)}))
            output = self.root / (name + ".plist")
            process = subprocess.Popen(command(self.root, "sampler", "/usr/bin/powermetrics", "-i", "100", "-o", output),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            deadline = time.monotonic() + 10
            ready = self.root / f"sampler-ready-{process.pid}"
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(.005)
            self.assertTrue(ready.exists())
            clock = SharedClock(self.root / "clock.bin")
            try:
                clock.sleep(1)
            finally:
                clock.close()
            (self.root / "source-stop.json").write_text("{}\n")
            out, error = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, error.decode())
            records = [plistlib.loads(raw) for raw in output.read_bytes().split(b'\0') if raw]
            self.assertGreaterEqual(len(records), 10)
            self.assertTrue(all(row['gpu']['idle_ratio'] == idle for row in records))
            self.assertTrue(all(row['processor']['gpu_power'] == power for row in records))

    @unittest.skipUnless(sys.platform == "darwin", "pinned USB protocol uses CommonCrypto")
    def test_real_meter_writer_uses_synthetic_libusb_object(self):
        """Predict: unchanged meter writes 11 polls/110 samples at the registered 28 V EPR midpoint and a duration trailer; no native USB load."""
        relative = "scripts/km003c_monitor.py"
        source = subprocess.check_output(["git", "show", f"{PIN}:{relative}"], cwd=REPO)
        script = self.root / "pin" / relative
        script.parent.mkdir(exist_ok=True)
        script.write_bytes(source)
        result = subprocess.run(command(self.root, "meter-probe"), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in (self.root / "source-only-meter.jsonl").read_text().splitlines()]
        self.assertEqual(rows[0]["status"], "streaming")
        self.assertEqual(rows[0]["init_errors"], [])
        self.assertEqual(rows[-1]["stop_reason"], "duration")
        polls = [row for row in rows if row["k"] == "b"]
        self.assertEqual(len(polls), 11)
        self.assertEqual(sum(row["n"] for row in polls), 110)
        self.assertTrue(all(len(bytes.fromhex(row["p"])) == 200 for row in polls))
        from joulewise.external.km003c_parse import SAMPLE, VBUS_BAND_V
        volts = [point[2] / 1e6 for row in polls for point in SAMPLE.iter_unpack(bytes.fromhex(row["p"]))]
        self.assertEqual(set(volts), {28.0})
        self.assertTrue(all(VBUS_BAND_V[0] <= value <= VBUS_BAND_V[1] for value in volts))
        from b6_r12_verify import meter_facts
        facts = meter_facts((self.root / "source-only-meter.jsonl").read_bytes())
        self.assertEqual(facts["samples"], 110)
        self.assertEqual(facts["step_ms"], 20)
        self.assertEqual(facts["span_s"], 2.18)
        self.assertEqual(facts["drops"]["dropped"], 0)
        self.assertEqual(facts["duplicates"], 0)

    def test_original_verdict_publisher_retains_no_clobber_and_root_fence(self):
        """Predict: the pinned publisher writes exact bytes under its real lock, refuses overwrite, and an escaping hard link is denied before creation."""
        export_chain_inputs(self.root)
        code = '''import os,runpy,sys
from pathlib import Path
root=Path(sys.argv[1])
module=runpy.run_path(str(root/'pin/scripts/run_campaign.py'),run_name='r12_original_campaign')
token=module['acquire_campaign_lock'](root/'writer-input')
target=root/'writer-input/verdict.json';payload=b'{"unit":"original-publisher"}\\n'
try:
    module['_publish_whole_window_verdict_output'](target,payload,lock_token=token)
    assert target.read_bytes()==payload
    try:
        module['_publish_whole_window_verdict_output'](target,b'different',lock_token=token)
    except FileExistsError:
        pass
    else:
        raise AssertionError('original no-clobber judgment was bypassed')
    assert target.read_bytes()==payload
    outside=root.parent/'R12-outside-hardlink'
    try:
        os.link(target,outside,follow_symlinks=False)
    except PermissionError:
        pass
    else:
        raise AssertionError('hard link escaped fixture root')
    assert not outside.exists()
finally:
    module['release_campaign_lock'](token)
print('original_publisher_and_root_fence')
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "original_publisher_and_root_fence")

    def test_pinned_j1_schema_mismatch_is_reported_without_patch(self):
        """Predict: f31's real producer/reader disagree on J1 schema; reader returns verdict_schema_mismatch."""
        relative = "scripts/b5_window_calibration_verdict.py"
        source = subprocess.check_output(["git", "show", f"{PIN}:{relative}"], cwd=REPO)
        script = self.root / "pin" / relative
        script.parent.mkdir(exist_ok=True)
        script.write_bytes(source)
        result = subprocess.run(command(self.root, "j1-schema-probe"), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertNotEqual(record["producer"], record["consumer"])
        self.assertEqual(record["miss"], {"reason": "verdict_schema_mismatch"})

    @unittest.skipUnless(sys.platform == "darwin", "pinned USB protocol uses CommonCrypto")
    def test_declared_signal_reaches_original_meter_shutdown_handler(self):
        """Predict: declared owned-child TERM executes no native signal; the real meter writes its signal trailer and exits 0."""
        export_chain_inputs(self.root)
        (self.root / "source-policy.json").write_text('{"volume":"reduced"}\n')
        code = '''import json,os,signal,subprocess,sys,time
from pathlib import Path
root=Path(sys.argv[1])
p=subprocess.Popen([sys.executable,'-B',str(root/'pin/scripts/km003c_monitor.py'),
                    '--out',str(root/'meter-signal.jsonl')])
time.sleep(2)
os.killpg(p.pid,signal.SIGTERM)
assert p.wait(timeout=3) == 0
rows=[json.loads(line) for line in (root/'meter-signal.jsonl').read_text().splitlines()]
assert rows[-1]['k'] == 't'
print(json.dumps(rows[-1]))
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        trailer = json.loads(result.stdout)
        self.assertIn("signal", str(trailer["stop_reason"]).lower())
        calls = [json.loads(line) for path in self.root.glob("source-calls-*.jsonl")
                 for line in path.read_text().splitlines()]
        actions = [row for row in calls if row["argv"][0] == "os.killpg"]
        self.assertEqual(len(actions), 1)
        self.assertFalse(actions[0]["executed"])
        self.assertEqual(actions[0]["returncode"], 0)

    def test_declared_signal_closes_both_original_monitor_threads(self):
        """Predict: declared owned-child TERM stops both original monitor loops, writes session_end and exits 0 without native signaling."""
        export_chain_inputs(self.root)
        (self.root / "source-policy.json").write_text('{"volume":"reduced"}\n')
        code = '''import json,os,signal,subprocess,sys,time
from pathlib import Path
from joulewise.hazards.monitor import build_config
root=Path(sys.argv[1]); custody=root/'monitor-custody'
config=build_config(custody_dir=custody,tree_roots=[os.getpid()],disk_targets=[])
path=root/'monitor-input.json';path.write_text(json.dumps(config))
p=subprocess.Popen([sys.executable,'-B',str(root/'pin/scripts/hazard_monitor.py'),'--config',str(path)])
time.sleep(2)
os.killpg(p.pid,signal.SIGTERM)
assert p.wait(timeout=3) == 0
rows=[json.loads(line) for line in (custody/'hazards/monitor/monitor.jsonl').read_text().splitlines()]
assert rows[-1]['kind'] == 'session_end'
print(rows[-1]['values']['reason'])
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "signal 15")

    def test_original_harvest_readiness_uses_declared_absent_group(self):
        """Predict: original readiness accepts a terminal synthetic unit input with an absent group; source returns ESRCH, never EPERM or a substituted verdict."""
        code = '''import json,os,sys
from pathlib import Path
from types import SimpleNamespace
from joulewise.b5.harvest import Seams,group_alive,readiness
root=Path(sys.argv[1]);night=root/'readiness-unit-input';night.mkdir()
(night/'chain.started').write_text(json.dumps({'pgid':987654319}))
(night/'result.json').write_text('{}')
assert group_alive(987654319) is False
result=readiness(SimpleNamespace(night_dir=night),Seams())
assert result == {'chain_started':True,'terminal_record':True,'group_alive':False}
print('ready')
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ready")

    def test_actual_git_blob_transport_preserves_bytes_and_fresh_refs(self):
        """Predict: native/batch bytes, errors and pinned digest agree; fresh commits are read, replace refs denied, and SystemExit(4) survives transport atexit cleanup."""
        code = '''import hashlib,json,subprocess,sys
from pathlib import Path
from runtime import REAL_RUN
from joulewise.arm_readiness import committed_pack_tree_sha256
root=Path(sys.argv[1]);repo=root/'git-input-unit';pack=repo/'configs/campaigns/tiny'
pack.mkdir(parents=True);path=pack/'config.json';path.write_bytes(b'{"unit":1}\\n')
prefix=['git','-C',str(repo)]
def run(args,**kw):
    return subprocess.run(prefix+args,capture_output=True,check=True,**kw)
run(['init','-q']);run(['config','user.name','R12 unit']);run(['config','user.email','r12@invalid'])
run(['config','commit.gpgsign','false']);run(['add','.']);run(['commit','-qm','unit input one'])
oid=run(['rev-parse','HEAD:configs/campaigns/tiny/config.json'],text=True).stdout.strip()
argv=prefix+['cat-file','blob',oid]
native=REAL_RUN(argv,capture_output=True,check=False);batched=subprocess.run(argv,capture_output=True,check=False)
assert (native.returncode,native.stdout,native.stderr)==(batched.returncode,batched.stdout,batched.stderr)
optimized=subprocess.run;subprocess.run=REAL_RUN
expected=committed_pack_tree_sha256(pack)
subprocess.run=optimized
assert committed_pack_tree_sha256(pack)==expected
future=b'{"unit":2}\\n';future_oid=hashlib.sha1(b'blob '+str(len(future)).encode()+b'\\0'+future).hexdigest()
missing=prefix+['cat-file','blob',future_oid]
a=REAL_RUN(missing,capture_output=True);b=subprocess.run(missing,capture_output=True)
assert (a.returncode,a.stdout,a.stderr)==(b.returncode,b.stdout,b.stderr)
path.write_bytes(future);run(['add','.']);run(['commit','-qm','unit input two'])
new_oid=run(['rev-parse','HEAD:configs/campaigns/tiny/config.json'],text=True).stdout.strip()
assert new_oid==future_oid and new_oid!=oid
assert run(['cat-file','blob',new_oid]).stdout==future
assert committed_pack_tree_sha256(pack)!=expected
try:
    run(['replace',oid,new_oid])
except PermissionError:
    pass
else:
    raise AssertionError('replace refs were not denied')
print('native_bytes_and_fresh_refs')
raise SystemExit(4)
'''
        result = subprocess.run(command(self.root, "code", code, self.root), capture_output=True,
                                text=True, timeout=60)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertEqual(result.stdout.strip(), "native_bytes_and_fresh_refs")
        receipts = [json.loads(line) for path in self.root.glob("git-blob-input-queries-*.jsonl")
                    for line in path.read_text().splitlines()]
        self.assertGreater(len(receipts), 2)
        self.assertTrue(all(row["result_cached"] is False for row in receipts))

    @unittest.skipUnless(Path("/bin/zsh").is_file(), "rendered chain requires zsh")
    def test_shell_and_python_use_same_clock(self):
        """Predict: unedited zsh date/sleep commands and pinned child see the same 75 s advance."""
        script = self.root / "synthetic-shell-input.zsh"
        script.write_text('/bin/date +%s\n/bin/sleep 75\n/bin/date +%s\n')
        p = subprocess.run(["/bin/zsh", "-f", str(self.root / "shell.zsh"), str(script)],
                           capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stderr)
        first, last = map(int, p.stdout.splitlines())
        self.assertEqual(last - first, 75)
        child = subprocess.run(command(self.root, "probe", 0), capture_output=True, text=True, timeout=20)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(json.loads(child.stdout)["before"]["epoch_s"], last)


class DeskInputBoundaryTests(unittest.TestCase):
    def test_loop_identity_uses_copied_plan_without_suffix_guess(self):
        """Predict: a copied plan binds its outer loop ID to a distinct bracket ID; the original attempt matches only after that authenticated binding. A mismatching bracket refuses association."""
        from tests.independent_recompute.support_b6 import b6
        with tempfile.TemporaryDirectory(prefix="r12-plan-identity-") as directory:
            archive = Path(directory).resolve()
            plan = archive / "sources/night-custody/night_plan.json"
            plan.parent.mkdir(parents=True)
            plan.write_text(json.dumps({"plan_id": "outer-loop-name",
                "hazard_window": {"bindings": {"bracket_session_id": "distinct-ledger-name"}}}))
            flags = []
            session = b6.Session.__new__(b6.Session)
            session.archive, session.session_id = archive, "distinct-ledger-name"
            session.reader = b6.Reader("ALPHA", session.session_id, flags)
            attempt = {"session_id": "outer-loop-name", "round": 2}
            self.assertEqual(session.loop_attempt([attempt]), attempt)
            self.assertEqual(session.session_id, "outer-loop-name")
            self.assertEqual(session.reader.session, "outer-loop-name")
            self.assertEqual(flags, [])
            session.session_id = "wrong-ledger-name"
            self.assertIsNone(session.loop_attempt([attempt]))
            self.assertIn("acceptance_session_mismatch", {flag["code"] for flag in flags})

    def test_open_block_prints_noncomputable_registered_summaries(self):
        """Predict: with no eligible sessions, every registered block summary prints n=0 and null mean/sd; coverage still rejects a missing required session key. No session or counting judgment is simulated here."""
        from tests.independent_recompute.support_b6 import b6
        lines = b6.block_lines({}, {})
        b6.require_production_coverage({}, lines)
        for pack in b6.PACKS:
            values = lines["between_session"][pack]["values"]
            self.assertTrue(values)
            self.assertTrue(all(row["n"] == 0 and row["mean"] is None and row["sd"] is None
                                for row in values.values()))
            self.assertEqual(lines["short"][pack]["counting"], 0)
        with self.assertRaisesRegex(b6.InputRefusal, "comparison_session_coverage_mismatch"):
            b6.require_production_coverage({"missing": {"pack": "ALPHA", "quantities": {}}}, lines)

    def test_noncomputable_single_step_keeps_registered_projection(self):
        """Predict: insufficient-unit diagnostic rows retain their null result without adding unregistered comparison interval keys. This is a projection regression, not a generated session."""
        from tests.independent_recompute.support_b6 import b6
        result = {"pack": "ALPHA", "lines": {"df-ph-decode-qwen3-1p7b": {
            "single_step_reconstruction": {"status": "below_registered_minimum",
                "mean_j": None, "h_j": None, "n_r": 0, "n_b": 0,
                "lower_j": None, "upper_j": None}}}}
        quantities = b6.session_quantities(result)
        prefix = "lines/single_step_reconstruction/qwen3-1p7b/decode/"
        self.assertEqual({key.removeprefix(prefix): value for key, value in quantities.items()
                          if key.startswith(prefix)},
                         {"mean_j": None, "h_j": None, "n_r": 0, "n_b": 0})
        self.assertIn("lower_j", result["lines"]["df-ph-decode-qwen3-1p7b"]["single_step_reconstruction"])

    def test_pool_reader_refuses_unpinned_sibling_before_read(self):
        """Predict: a pinned worker refuses an out-of-archive synthetic sibling before reading any of its bytes."""
        from types import SimpleNamespace
        from unittest import mock
        from tests.independent_recompute.support_b6 import b6
        with tempfile.TemporaryDirectory(prefix="r12-pool-boundary-") as directory:
            root = Path(directory).resolve()
            archive = root / "archive"
            archive.mkdir()
            outside = root / "synthetic-unpinned.json"
            outside.write_text('{"synthetic":true}\n')
            reads = []
            original_read = Path.read_bytes
            def observed_read(path):
                if path == outside:
                    reads.append(path)
                return original_read(path)
            def exercise_reader(_pool):
                # Replace only worker transport startup. Exercise the real
                # scoped Reader class installed at the fork boundary.
                reader = b6.B5.Reader("ALPHA", [])
                with self.assertRaisesRegex(b6.InputRefusal, "input_outside_archive"):
                    reader.raw(outside, "synthetic-scope")
            pool = b6.MemberPool(2, [SimpleNamespace(archive=archive)])
            with mock.patch.object(b6.B5.MemberPool, "_start", exercise_reader), \
                    mock.patch.object(Path, "read_bytes", observed_read):
                pool._start()
            self.assertEqual(reads, [])

    @unittest.skipUnless(shutil.which("zstd"), "synthetic production input regression requires zstd")
    def test_production_archives_with_repeated_basename_use_distinct_pins(self):
        """Predict: option (c) exits 0 for ten toy regression archives named archive, each explicitly pinned by absolute path."""
        # These older handwritten toy archives exercise input routing only;
        # they are not generated-chain R12 fixture evidence.
        from tests.independent_recompute.support_b6_production import production_block, b6
        with tempfile.TemporaryDirectory(prefix="r12-pin-routing-") as directory:
            root = Path(directory).resolve()
            archives, attempts, document = production_block(root / "toy")
            value = json.loads(document.read_text())
            pins, relocated = {}, []
            for archive in archives:
                target = root / "relocated" / archive.name / "archive"
                target.parent.mkdir(parents=True)
                archive.rename(target)
                pins[str(target)] = value["sessions"][archive.name]
                relocated.append(target)
            value["sessions"] = pins
            document.write_text(json.dumps(value) + "\n")
            result = b6.main(["block", *[v for path in relocated for v in ("--session", str(path))],
                "--loop-attempts", str(attempts), "--closed", "--inputs", str(document),
                "--inputs-sha256", hashlib.sha256(document.read_bytes()).hexdigest(),
                "--restricted-out", str(root / "numbers.json"), "--public-out", str(root / "public.json")])
            self.assertEqual(result, 0)
            output = json.loads((root / "numbers.json").read_bytes())
            self.assertEqual(len(output["inputs"]["census"]), 10)
            self.assertTrue(output["block"]["option_c"]["pass"])

    @unittest.skipUnless(shutil.which("zstd"), "real desk compression requires zstd")
    def test_real_desk_log_can_be_pinned_without_editing_archive(self):
        """Predict: the B6 reader authenticates the real desk's adjacent log without copying it into the immutable archive."""
        from joulewise import desk_compress
        from joulewise.b6_analysis_inputs import AuthenticatedInputs, InputRefusal
        with tempfile.TemporaryDirectory(prefix="r12-desk-boundary-") as directory:
            root = Path(directory).resolve()
            archive, custody = root / "archive", root / "custody"
            (archive / "derived").mkdir(parents=True)
            (archive / "sources").mkdir()
            (custody / "night").mkdir(parents=True)
            (custody / "night/chain.exited").write_text("{}")
            payload = archive / "sources/payload.jsonl"
            raw = b'{"synthetic_unit_test":true}\n' * 100
            payload.write_bytes(raw)
            sums = archive / "sources/SHA256SUMS"
            sums.write_text(hashlib.sha256(raw).hexdigest() + "  payload.jsonl\n")
            (archive / "harvest.json").write_text('{"verdict":"COLLECTED","outputs":{}}\n')
            (archive / "derived/b6-acceptance.json").write_text("{}\n")
            code, result = desk_compress.compress(archive=archive, custody=custody, min_bytes=100)
            self.assertEqual(code, 0, result)
            self.assertEqual(result["files"], 1)
            log = root / "archive.desk/compression.jsonl"
            sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            pin = {"harvest_sha256": sha(archive / "harvest.json"),
                   "acceptance_sha256": sha(archive / "derived/b6-acceptance.json"),
                   "sha256sums_sha256": sha(sums),
                   "compression": {"external_path": str(log), "sha256": sha(log),
                                   "relocations": {str(archive): "."}}}
            reader = AuthenticatedInputs(archive, pin)
            self.assertEqual(reader.read(payload), raw)
            self.assertFalse((archive / "compression.jsonl").exists())
            reader.verify_census()
            # Re-verification must reread the external log, not cache it.
            with log.open("ab") as stream:
                stream.write(b"\n")
            with self.assertRaisesRegex(InputRefusal, "input_digest_mismatch"):
                reader.verify_census()


class VerifierInventoryTests(unittest.TestCase):
    def _unit_manifest(self, root):
        """Metadata-only unit root; no session, archive or loop record exists."""
        (root / "runtime.py").write_bytes((REPO / "scripts/b6_r12_runtime.py").read_bytes())
        manifest = {"synthetic_only": True, "source_sha256": {}, "seams": {},
            "runtime_sha256": hashlib.sha256((root / "runtime.py").read_bytes()).hexdigest(),
            "generator_commit": subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                         cwd=REPO, text=True).strip()}
        (root / "manifest.json").write_text(json.dumps(manifest) + "\n")

    def test_manifest_names_actual_dependency_and_harvest_default_seams(self):
        """Predict: final attestation names version-reader values from the hash-bound copied runtime and the killpg constructor default. This is a manifest unit, not a collected fixture."""
        from b6_r12_verify import finalize_manifest
        with tempfile.TemporaryDirectory(prefix="r12-source-seam-unit-") as directory:
            root = Path(directory).resolve()
            self._unit_manifest(root)
            finalize_manifest(root)
            value = json.loads((root / "manifest.json").read_bytes())
            versions = value["seams"]["importlib.metadata.version"]
            self.assertEqual(versions["packages"], {name: "r12-synthetic" for name in (
                "mlx", "mlx-lm", "mlx-metal", "numpy", "safetensors", "tokenizers", "transformers")})
            self.assertEqual(value["seams"]["joulewise.b5.harvest.Seams.__init__.__defaults__"]["field"], "killpg")
            self.assertEqual(value["source_seam_provenance"]["runtime_sha256"], value["runtime_sha256"])

    def test_manifest_refuses_runtime_bytes_different_from_pre_run_hash(self):
        """Predict: changing a metadata unit's copied runtime after its declared hash refuses final attestation, even if the version declarations did not change."""
        from b6_r12_verify import finalize_manifest
        with tempfile.TemporaryDirectory(prefix="r12-source-digest-unit-") as directory:
            root = Path(directory).resolve()
            self._unit_manifest(root)
            with (root / "runtime.py").open("ab") as stream:
                stream.write(b"\n# deliberately changed metadata-unit bytes\n")
            with self.assertRaisesRegex(ValueError, "generator runtime digest mismatch"):
                finalize_manifest(root)

    def test_prediction_sources_use_bound_git_blobs(self):
        """Predict: later working-file edits cannot change the manifest's original committed prediction/doc hashes. The temporary Git repo is a provenance unit, not a chain fixture."""
        from b6_r12_verify import prediction_sources
        with tempfile.TemporaryDirectory(prefix="r12-prediction-source-") as directory:
            repo = Path(directory)
            paths = {"tests/test_b6_r12_session_fixture.py":
                b'class DeclaredShapeTests:\n    def test_shape(self):\n        """Predict before collection: exit 0."""\n',
                "docs/run_reports/2026-11-11-p1-b6-r12-r3.md": b"Original pre-run prediction.\n"}
            for name, data in paths.items():
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=R12 unit",
                "-c", "user.email=r12-unit@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "-qm", "Declare unit prediction"], check=True)
            commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            for name in paths:
                (repo / name).write_text("Later working-file content must not be used.\n")
            value = prediction_sources(commit, repo)
            self.assertEqual(value["test_docstrings"], {"test_shape": "Predict before collection: exit 0."})
            self.assertEqual(value["source_sha256"], {name: hashlib.sha256(data).hexdigest() for name, data in paths.items()})

    def test_finisher_refuses_live_generators_before_hashing(self):
        """Predict: DONE alone cannot authorize receipt hashing while a generator parent is still live. Unit state stubs are not collected loop records or fixture evidence."""
        from unittest.mock import patch
        import b6_r12_finish as finisher
        with tempfile.TemporaryDirectory(prefix="r12-finish-boundary-") as directory:
            root = Path(directory)
            denied = root / "denied"
            (root / "loop").mkdir()
            (denied / "loop").mkdir(parents=True)
            (root / "loop/state.json").write_text(json.dumps({"state": "DONE"}))
            (denied / "loop/attempts.jsonl").write_text(json.dumps({"session_id": "r1-alpha"}) + "\n")
            for missing in (root, denied):
                for parent in (root, denied):
                    (parent / "generator-parent-exit.txt").write_text("0\n")
                (missing / "generator-parent-exit.txt").unlink()
                with self.subTest(missing=str(missing)), patch.object(finisher, "finalize_manifest",
                        side_effect=AssertionError("hashing live writer")) as hashing:
                    with self.assertRaisesRegex(RuntimeError, "generator parent"):
                        finisher.finish(root, denied)
                    hashing.assert_not_called()

    def test_empty_gamma_pairing_never_becomes_cross_session_evidence(self):
        """Predict: empty/self pairings or no kept GAMMA unit never count as cross-session evidence. Receipt stubs test the join, not a chain fixture."""
        from unittest.mock import patch
        import b6_r12_verify as verifier
        with tempfile.TemporaryDirectory(prefix="r12-pairing-guard-") as directory:
            root = Path(directory)
            denied = root / "denied"
            denied.mkdir()
            archive = str(root / "archive")
            receipt = {"archives": [archive], "exit_code": 0,
                       "option_c": {"comparator": {"pass": True}}}
            for path in (root / "option-c-receipt.json", root / "option-c-skips-receipt.json",
                         denied / "option-c-denied-receipt.json"):
                path.write_text(json.dumps(receipt))
            kept = {"decode": {"abba": ["unit-1"]}}
            for pairing, units, expected in (({}, kept, False),
                    ({"ALPHA": {"session_id": "r1-gamma"}}, kept, False),
                    ({"ALPHA": {"session_id": "r1-alpha"}}, kept, True),
                    ({"ALPHA": {"session_id": "r1-alpha"}}, {}, False)):
                gamma = {"pack": "GAMMA", "round": 1, "session_id": "r1-gamma",
                         "pairing": pairing, "kept_units": units}
                (root / "option-c-numbers.json").write_text(json.dumps({"sessions": {"r1-gamma": gamma}}))
                with patch.object(verifier, "session_facts", return_value={"archive": archive, "off_actions": []}), \
                     patch.object(verifier, "volume_facts", return_value={}):
                    values = verifier.write_observations(root, denied)
                self.assertIs(values["r12-gamma-cross"]["cross_session_gamma"], expected, pairing)

    def test_actual_smoke_inventory_excludes_attached_calibrations(self):
        """Predict: captured f31 smoke inventory yields four executed primaries; its four calibration copies and validation captures never inflate volume."""
        from b6_r12_verify import primary_plist_names
        value = json.loads((REPO / "tests/fixtures/b6_r12_smoke_primary_inventory.json").read_text())
        expected = ["sources/claim-runs/" + bundle + "/raw/powermetrics.plist" for bundle in (
            "d117fq31p7-df-ph-decode-abs-r01", "d117fq31p7-df-ph-prefill-p2048-abs-r01",
            "neg8-window-end-r1", "neg8-window-start-r1")]
        self.assertEqual(primary_plist_names(value["paths"]), expected)
        self.assertEqual(value["pin"], PIN)


@unittest.skipUnless(os.environ.get("R12_REAL_CHAIN_SET"), "explicit generated R12 set required")
class DeclaredShapeTests(unittest.TestCase):
    """Integration expectations declared before any official named shape run.

    §17-R12: docs/registrations/block6_s17_entries_DRAFT_2026-11-10.md:673.
    A skip here is not evidence of a generated or accepted fixture.
    """

    def evidence(self, name):
        root = Path(os.environ["R12_REAL_CHAIN_SET"])
        if root.is_relative_to("/Users/edr") or "restricted" in root.parts:
            self.fail("forbidden fixture root")
        value = json.loads((root / "observations.json").read_text())[name]
        self.assertEqual(value["production_exit"], 0)
        self.assertTrue(value["comparator_agrees"])
        return value

    def test_waited_attempt_n(self):
        """Predict r12-waited: option (c) exits 0/agrees, idle.waited and attempt >=2 telemetry (§17-R12:673)."""
        value = self.evidence("r12-waited")
        self.assertIn("idle.waited", value["flags"])
        self.assertGreaterEqual(value["max_idle_attempt"], 2)

    def test_wait_cap_and_budget_skips(self):
        """Predict r12-skips: option (c) exits 0/agrees; real idle.wait_cap_skip and idle.wait_budget_skip (§17-R12:673)."""
        value = self.evidence("r12-skips")
        self.assertTrue({"idle.wait_cap_skip", "idle.wait_budget_skip"}.issubset(value["flags"]))

    def test_unbounded_anchor(self):
        """Predict r12-anchor: option (c) exits 0/agrees; member.anchor_not_bounded excludes the source-skewed member (§17-R12:673)."""
        self.assertIn("member.anchor_not_bounded", self.evidence("r12-anchor")["flags"])

    def test_mixed_campaign_rows(self):
        """Predict r12-mixed: option (c) exits 0/agrees and classifies executed-member plus trailing evaluation rows (§17-R12:673)."""
        self.assertEqual(set(self.evidence("r12-mixed")["campaign_row_kinds"]), {"member", "evaluation"})

    def test_desk_compressed_logs_and_plists(self):
        """Predict r12-compressed: option (c) exits 0/agrees reading real desk-compressed campaign logs and plists (§17-R12:673)."""
        value = self.evidence("r12-compressed")
        self.assertGreater(value["compressed_campaign_logs"], 0)
        self.assertGreater(value["compressed_plists"], 0)

    def test_cross_session_gamma(self):
        """Predict r12-gamma-cross: nine-session option (c) exits 0/agrees and records a GAMMA unit paired across sessions (§17-R12:673)."""
        value = self.evidence("r12-gamma-cross")
        self.assertTrue(value["cross_session_gamma"])
        self.assertTrue(value["pairing"])
        self.assertTrue(any(units for strata in value["kept_units"].values() for units in strata.values()))
        for pairing in value["pairing"].values():
            self.assertTrue(pairing.get("session_id"))
            self.assertNotEqual(pairing["session_id"], value["session_id"])

    def test_denied_action_ordinary_session(self):
        """Predict r12-denied-action: single-session option (c) exits 0/agrees; normal session retains network_time.off_output and arm action rc 126 (RL-49 rule 2)."""
        value = self.evidence("r12-denied-action")
        self.assertIn("network_time.off_output", value["flags"])
        self.assertEqual(value["off_action_returncode"], 126)
        self.assertTrue(value["real_loop_attempt"])

    def test_full_volume_member_and_instrument_census(self):
        """Predict full ALPHA/BETA/GAMMA: 125/125/107 members, >=334 s per primary at 10 Hz with 16 CPUs; continuous 50 Hz meter, registered monitor cadences and no source errors (RL-48 item 5)."""
        root = Path(os.environ["R12_REAL_CHAIN_SET"])
        values = json.loads((root / "full-volume-observations.json").read_bytes())
        for sid, expected in (("r3-alpha", 125), ("r1-beta", 125), ("r1-gamma", 107)):
            value = values[sid]
            self.assertEqual(len(value["primary_plists"]), expected, sid)
            for item in value["primary_plists"]:
                self.assertEqual(item["frames"], item["elapsed_fields"], item["path"])
                self.assertGreaterEqual(item["duration_s"], 334, item["path"])
                self.assertEqual(item["cadence_ns"], [100_000_000], item["path"])
                self.assertEqual(item["cpu_fields"], 16 * item["frames"], item["path"])
            self.assertTrue(value["meter"], sid)
            for meter in value["meter"]:
                self.assertEqual(meter["sps"], 50)
                self.assertEqual(meter["step_ms"], 20)
                self.assertEqual(meter["drops"]["dropped"], 0)
                self.assertEqual(meter["drops"]["irregular_gaps"], 0)
                self.assertEqual(meter["duplicates"], 0)
            self.assertTrue(value["monitor"], sid)
            for journal in value["monitor"].values():
                self.assertEqual(journal["errors"], 0, sid)
            base = "sources/night-custody/hazards/monitor/"
            for filename, kind, cadence_key in (("clock.jsonl", "reading", "clock_s"),
                    ("thermal.jsonl", "reading", "thermal_s"),
                    ("battery.jsonl", "reading:smc", "battery_smc_s")):
                series = value["monitor"][base + filename]["kinds"][kind]
                cadence_s = value["registered_monitor_cadence"][cadence_key]
                self.assertEqual(series["cadence_ns"], [round(cadence_s * 1e9)], sid)
                self.assertGreaterEqual(series["span_s"], min(m["span_s"] for m in value["meter"]) - cadence_s, sid)


if __name__ == "__main__":
    unittest.main()
