"""Qualification launcher regressions and comparison with the admitted pin."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.cadence import legs, queue
from scripts import cadence_legs_runner as runner, cadence_queue, launch_cadence_span as launcher
from tests.cadence import test_kit_v11 as v11_tests
from tests.cadence.fixtures import make_runner_checkout

ROOT = runner.ROOT
PIN = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
AUDIT = "09c77ae4fc9ae66526dbf752fbd283d8030469a5"
COMMITMENTS = "59557d6e8e00fcba6a2bdb2bfa4189bd6d7aee98"
CAMPAIGN = "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
T0_LOCAL = "2026-11-19T00:30"
T0 = int(datetime.fromisoformat(T0_LOCAL).replace(tzinfo=legs.LOCAL_ZONE).timestamp())
NS = 1_000_000_000
QUAL_KIT = ROOT / "docs/process/cadence/kits/cl-qual-01.v1.1.json"
QUAL_ROSTER = [f"L{i:03}" for i in range(1, 7)]


class QualificationGates(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def test_checklist_keeps_window_opt_in(self):
        observations = self.root / "observations.json"
        frozen = json.loads(QUAL_KIT.read_bytes())["frozen"]
        observations.write_text(json.dumps({**v11_tests.FreeT0Checklist.GOOD, "t0_epoch_s": T0,
                                             "measurement_head": frozen["commit"],
                                             "frozen_path_sha256": frozen["paths"],
                                             "end_by_epoch_s": T0 + 26210 + 1950}))
        argv = ["checklist", "--kit", str(QUAL_KIT), "--observations", str(observations),
                "--kit-sha256", "f" * 64]
        for extra, expected in (([], 0), (["--batch-window", "02:00-02:35"], 1)):
            with self.subTest(extra=extra), redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(cadence_queue.main(argv + extra), expected, stdout.getvalue())
                self.assertIn("CHECKLIST PASS" if expected == 0 else "CHECKLIST FAIL", stdout.getvalue())

    def test_launcher_requires_ledger_and_reproves_exact_close_while_locked(self):
        receipt = self.root / "previous.json"
        close_ns = T0 * NS - 1
        receipt.write_text(json.dumps({"span_id": "previous", "ended": {"epoch_ns": close_ns},
                                       "restore_readbacks": {"synthetic": True}}))
        ledger = self.root / "attempts.json"
        prior = {"sequence": 1, "span_id": "previous", "close_receipt": str(receipt)}
        original = {"attempts": [prior]}
        ledger.write_text(json.dumps(original))
        output = self.root / "output"
        fence_root = self.root / "fence"
        checkout = self.root / "measurement"
        kit_path = self.root / "synthetic-qualification.json"
        kit_path.write_text(json.dumps({**json.loads(QUAL_KIT.read_text()), "frozen": make_runner_checkout(checkout)}))
        self.enterContext(patch.object(launcher, "subprocess", SimpleNamespace(**vars(subprocess))))
        args = SimpleNamespace(kit=kit_path, span_id="qual-01-s01", t0_not_before_ns=close_ns,
                               attempt_ledger=None, previous_close_receipt=None,
                               magistrate_pid=234, deadline=T0 + 30000, output=output,
                               legs=",".join(QUAL_ROSTER), batch_window=None, repo=checkout,
                               python_bin=Path(sys.executable), custody_root=fence_root,
                               exit_wait_seconds=180, disk_path=self.root, pgrep_bin="stub-pgrep",
                               kill_bin="stub-kill", pmset_bin="stub-pmset", launchctl_bin="stub-launchctl")

        with patch.object(launcher.base, "pid_alive", side_effect=AssertionError("host probe")):
            with self.assertRaisesRegex(ValueError, "ledger-backed launch requires"):
                launcher.launch(args)
        self.assertFalse(fence_root.exists())

        args.attempt_ledger, args.previous_close_receipt = ledger, str(receipt)
        actual_lock = launcher.base.fence_lock

        @contextmanager
        def change_close_under_lock(root):
            with actual_lock(root):
                receipt.write_text(json.dumps({"span_id": "previous", "ended": {"epoch_ns": close_ns - 1},
                                               "restore_readbacks": {"synthetic": True}}))
                yield

        with (patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=T0),
              patch.object(launcher.base, "fence_lock", side_effect=change_close_under_lock),
              patch.object(launcher.base, "write_fence") as fence,
              patch.object(launcher.subprocess, "run") as service):
            with self.assertRaisesRegex(ValueError, "close proof changed before launch"):
                launcher.launch(args)
        fence.assert_not_called()
        service.assert_not_called()
        self.assertEqual(json.loads(ledger.read_text()), original)

        args.t0_not_before_ns = close_ns - 1
        pending = {"sequence": 2, "span_id": args.span_id, "close_receipt": str(output / runner.RECEIPT_NAME)}

        def synthetic_service(command, **_kwargs):
            self.assertEqual(command[0], "stub-launchctl")
            if command[1] == "bootstrap":
                self.assertEqual(json.loads(ledger.read_text())["attempts"], [prior, pending])
                raise subprocess.CalledProcessError(19, command)
            self.assertEqual(command[1], "bootout")
            return subprocess.CompletedProcess(command, 0, b"", b"")

        stale = self.root / "stale"
        make_runner_checkout(stale, b"# stale qualification runner\n")
        with (patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=T0),
              patch.object(launcher.subprocess, "run", side_effect=synthetic_service) as service):
            args.repo = stale
            with self.assertRaisesRegex(ValueError, "is not the kit's frozen commit"):
                launcher.launch(args)
            service.assert_not_called()
            self.assertEqual(json.loads(ledger.read_text()), original)
            args.repo = checkout
            with self.assertRaises(subprocess.CalledProcessError):
                launcher.launch(args)
        self.assertEqual(json.loads(ledger.read_text())["attempts"], [prior, pending])
        self.assertIsNone(launcher.base.read_fence(fence_root))

    def test_launcher_handoff_keeps_nanosecond_t0_guard(self):
        close_ns = T0 * NS + 125_000_000
        output = self.root / "output"
        argv = ["launch", "--kit", str(QUAL_KIT), "--repo", str(ROOT), "--python-bin", sys.executable,
                "--output", str(output), "--disk-path", str(self.root), "--custody-root", str(self.root),
                "--magistrate-pid", "234", "--deadline", str(T0 + 30000), "--legs", ",".join(QUAL_ROSTER),
                "--authorized-t0-date", T0_LOCAL[:10], "--t0-not-before", str(T0),
                "--t0-before", str(T0 + 60), "--t0-not-before-ns", str(close_ns)]
        with (patch.object(runner.RealClock, "arm_anchor_ns", return_value=(close_ns, NS, NS)),
              patch.object(launcher, "launch") as launch):
            self.assertEqual(launcher.main(argv), 0)
        child = launcher.runner_argv(launch.call_args.args[0])
        self.assertIn("--t0-anchor", child)
        self.assertEqual(child[child.index("--t0-not-before-ns") + 1], str(close_ns))
        clock = runner.FakeClock(T0)
        deps = runner.mock_deps(output, clock)
        with (patch.object(runner, "production_deps", return_value=deps),
              patch.object(clock, "epoch_and_monotonic_ns", return_value=(close_ns - 1, NS)),
              redirect_stderr(io.StringIO()) as stderr):
            self.assertEqual(runner.main(child[2:]), 3)
        self.assertIn("t0 clocks must agree on authority", stderr.getvalue())
        self.assertFalse(output.exists())
        self.assertEqual(deps.host.calls, [])


@unittest.skipUnless(os.environ.get("JW_COMPARE_QUALIFICATION_PIN") == "1",
                     "opt in with the audit, registration and qualification git objects available")
class QualificationPinEquivalence(unittest.TestCase):
    def git_blob(self, commit, path):
        return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, timeout=60)

    def inputs(self):
        commitments = json.loads(self.git_blob(COMMITMENTS,
            "docs/process/cadence/looks/qualification-kit-commitments.json"))["lm-qual-01"]
        self.assertEqual(commitments["runner_pin"], PIN)
        for block, digest in commitments["kit_sha256_by_block"].items():
            name = f"cl-{block}"
            yield name, f"item-drafts-1118/kits/{name}.v1.1.json", digest, [
                QUAL_ROSTER, [f"L{i:03}" for i in range(7, 13)]]
        yield "f2-stab-01", "f2-stab/f2-stab-01.v1.1.json", (
            "dbad9c7b79088bb6f06aac1c1148c3631a0c616fd2ece596bab0f56657ce70fe"), [
                [f"L{i:03}"] for i in range(1, 13)]
        yield "f2-inst-01", "item-drafts-f2/f2-inst-01.v1.1.json", (
            "651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b"), [
                [f"L{i:03}"] for i in range(4, 13)]

    def cli(self, repo, cache_prefix, script, *args):
        env = {**os.environ, "TZ": "UTC"}
        # Compare fresh source on both sides, even if the working checkout has compiled caches.
        command = [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache_prefix}",
                   f"scripts/{script}.py", *map(str, args)]
        result = subprocess.run(command, cwd=repo, env=env, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, (command, result.stdout, result.stderr))
        # Python 3.14 includes the absolute source path in compiler warnings.
        stderr = result.stderr.replace(os.fsencode(repo) + b"/", b"<CHECKOUT>/")
        return result.stdout, stderr

    def test_non_ctl_kits_equal_qualification_pin(self):
        scratch = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        base = scratch / "base"
        base.mkdir()
        snapshot = subprocess.check_output(["git", "archive", PIN, "joulewise", "scripts"], cwd=ROOT, timeout=60)
        with tarfile.open(fileobj=io.BytesIO(snapshot)) as tar:
            tar.extractall(base, filter="data")
        for name, path, digest, rosters in self.inputs():
            with self.subTest(kit=name):
                raw = self.git_blob(AUDIT, f"{CAMPAIGN}/{path}")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                kit = scratch / f"{name}.json"
                kit.write_bytes(raw)
                spans = [{"seq": i, "span_id": f"{name}-s{i:02}", "block_id": name,
                          "kit": {"path": kit.name, "sha256": digest}, "legs": roster,
                          "attempt": 1, "not_before": T0_LOCAL[:10]}
                         for i, roster in enumerate(rosters, 1)]
                queue_path = scratch / f"{name}-synthetic-queue.json"
                queue_path.write_text(json.dumps({"schema": queue.SCHEMA, "queue_id": f"cq-{name}",
                                                  "expires_at": "2026-11-20T00:00:00Z",
                                                  "halt": None, "standing_notice": None, "spans": spans}))
                for args in (("validate-kit", kit), ("validate-queue", queue_path, "--kits-root", scratch)):
                    self.assertEqual(self.cli(ROOT, scratch / "pycache", "cadence_queue", *args),
                                     self.cli(base, scratch / "pycache", "cadence_queue", *args))
                for index, roster in enumerate(rosters, 1):
                    with self.subTest(span=index):
                        self.compare_span(scratch, base, kit, name, index, roster)

    def compare_span(self, scratch, base, kit, name, index, roster):
        common = ("--kit", kit, "--legs", ",".join(roster))
        cache_prefix = scratch / "pycache"
        self.assertEqual(self.cli(ROOT, cache_prefix, "cadence_legs_runner", "plan", *common, "--t0", T0),
                         self.cli(base, cache_prefix, "cadence_legs_runner", "plan", *common, "--t0", T0))
        evidence = []
        for tag, repo in (("candidate", ROOT), ("pin", base)):
            output = scratch / tag / f"{name}-s{index:02}"
            output.parent.mkdir(exist_ok=True)
            streams = self.cli(repo, cache_prefix, "cadence_legs_runner", "mock", *common,
                               "--t0-local", T0_LOCAL, "--output", output)
            # The CLI mock's receipt/table paths and the span receipt's feed/step paths are absolute.
            # Replace the differing output directory only; all synthetic timestamps stay in the comparison.
            def mask(data):
                return data.replace(os.fsencode(output), b"<MOCK_OUTPUT>")
            files = {p.relative_to(output): mask(p.read_bytes()) for p in output.rglob("*") if p.is_file()}
            evidence.append((tuple(map(mask, streams)), files))
        (candidate_streams, candidate), (pin_streams, pin) = evidence
        self.assertEqual(candidate_streams, pin_streams)
        self.assertEqual(candidate.keys(), pin.keys())
        for path in sorted(candidate):
            self.assertEqual(candidate[path], pin[path], str(path))
