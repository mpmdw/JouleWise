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
        """Predict: pruning expired waveform inputs preserves complete plist bytes and all meter poll bytes against the unpruned source."""
        reference = prepare(Path(self.temp.name).resolve() / "unpruned-reference")
        source = (reference / "runtime.py").read_text()
        source = source.replace('                    self.intervals = [row for row in self.intervals if row["end_ns"] > clock.ns - 180_000_000]\n', '')
        source = source.replace('            intervals = [row for row in intervals if row["end_ns"] > endpoint]\n', '')
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
        """Predict: unchanged meter writes streaming header, 11 polls/110 samples and duration trailer; no native USB load."""
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
        from b6_r12_verify import meter_facts
        facts = meter_facts((self.root / "source-only-meter.jsonl").read_bytes())
        self.assertEqual(facts["samples"], 110)
        self.assertEqual(facts["step_ms"], 20)
        self.assertEqual(facts["span_s"], 2.18)
        self.assertEqual(facts["drops"]["dropped"], 0)
        self.assertEqual(facts["duplicates"], 0)

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
        self.assertTrue(self.evidence("r12-gamma-cross")["cross_session_gamma"])

    def test_denied_action_ordinary_session(self):
        """Predict r12-denied-action: single-session option (c) exits 0/agrees; normal session retains network_time.off_output and arm action rc 126 (RL-49 rule 2)."""
        value = self.evidence("r12-denied-action")
        self.assertIn("network_time.off_output", value["flags"])
        self.assertEqual(value["off_action_returncode"], 126)
        self.assertTrue(value["real_loop_attempt"])

    def test_full_volume_member_and_instrument_census(self):
        """Predict full ALPHA/BETA/GAMMA: 125/125/107 members, >=334 s per primary at 10 Hz with 16 CPUs; continuous 50 Hz meter with no drops (RL-48 item 5)."""
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


if __name__ == "__main__":
    unittest.main()
