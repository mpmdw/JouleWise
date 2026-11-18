"""Execute the RL-183 boundary in synthetic workers with real descriptor capture."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.cadence_looks.transfer_release import CUSTODY_NAMES, HASHES, WORDS

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / (
    "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/"
    "looks/lm-transfer-01.manifest.json"
)
REFUSAL = b"REFUSE transfer look before read\n"

_WORKER = r"""
import argparse
import atexit
from contextlib import nullcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

from joulewise.cadence_looks import transfer_release as release
from joulewise.cadence_looks.manifest_dispatch import validate_v2
from joulewise.cadence_looks.transfer_release import HASHES, run_transfer_worker

root, mode, draft = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
step = mode.removeprefix("inject-") if mode.startswith("inject-") else None


class InjectedFailure(BaseException):
    pass


def fail(*args, **kwargs):
    raise InjectedFailure("synthetic injected failure")


def fail_when(original, predicate):
    def inject(*args, **kwargs):
        if predicate(*args, **kwargs):
            fail()
        return original(*args, **kwargs)
    return inject

def preflight():
    if step == "preflight":
        fail()
    if mode == "pre-systemexit":
        sys.exit(1)
    if mode == "pre-custom-base":
        raise type("FixturePrivateExit", (BaseException,), {})("fixture private exit")
    if mode == "draft":
        validate_v2(draft.read_bytes(), final=True)
    if mode == "contended":
        # Both workers pass the initial existence check before either calls mkdir.
        (root / f"ready-{os.getpid()}").touch()
        deadline = time.monotonic() + 5
        while len(list(root.glob("ready-*"))) < 2:
            if time.monotonic() >= deadline:
                raise TimeoutError("fixture barrier")
            time.sleep(0.01)
    return {key: sha256(key.encode()).hexdigest() for key in HASHES}

def score(mark_read):
    (root / "score-entered").touch()
    if mode == "empty":
        return {"synthetic": None}, "not_evaluable"
    print("buffered fixture output", end="")
    if step == "score-before-read":
        fail()
    with (root / "synthetic-input.json").open("rb") as source:
        mark_read()
        (root / "saw-read").touch()
        if step == "consume":
            fail()
        value = json.load(source)
    if step == "score-after-read":
        fail()
    os.write(2, b"fixture diagnostic\n")
    atexit.register(os.write, 1, b"fixture shutdown\n")
    if mode == "post-systemexit":
        sys.exit(2)
    if mode == "post-argparse":
        argparse.ArgumentParser(prog="synthetic-scorer").parse_args(["--unknown"])
    if mode == "post-keyboardinterrupt":
        raise KeyboardInterrupt("fixture interruption without a signal")
    if mode == "post-custom-base":
        raise type("FixturePrivateExit", (BaseException,), {})("fixture private exit")
    if mode == "builtin":
        raise RuntimeError("fixture canary 123.456")
    if mode in ("unlisted", "impostor"):
        cls = (
            type("RuntimeError", (Exception,), {"__module__": "builtins"})
            if mode == "impostor" else type("Leak_123_456", (Exception,), {})
        )
        raise cls("fixture canary 123.456")
    if mode == "json":
        json.loads("invalid-json")
    if mode == "bad-public":
        return {"synthetic": value}, 0.4
    if mode == "extra-private":
        (root / "private" / "synthetic-result" / "unlisted.txt").write_text("fixture canary")
    if mode == "success":
        subprocess.run([sys.executable, "-B", "-c",
                        "import os; os.write(2, b'fixture child\\n')"], check=True)
    return {"synthetic": value}, "estimated"


def fault_context():
    notice = release.finish_notice
    public_record = release._public_record
    write_json = release._write_json
    lexists = os.path.lexists

    def opened(*args, **kwargs):
        return (root / "saw-read").exists()

    fault = {
        "startup-flush": (release, "finish_notice", fail),
        "save-stderr": (os, "dup", fail),
        "spent-check": (os.path, "lexists", fail),
        "filesystem": (Path, "stat", fail),
        "preflight-hashes": (release, "_public_record", fail),
        "reserve": (Path, "mkdir", fail),
        "redirect": (release, "_redirect", fail),
        "sync": (release, "_sync_directory", fail),
        "result-validation": (release, "_public_record", fail_when(public_record, opened)),
        "scores-write": (release, "_write_json", fail_when(write_json, lambda p, _: p.name == "scores.json")),
        "inventory": (Path, "iterdir", fail),
        "result-staging": (release, "_write_json", fail_when(write_json, lambda p, _: p.name == ".publication")),
        "final-spent-check": (os.path, "lexists", fail_when(lexists, opened)),
        "success-flush": (release, "finish_notice", fail_when(notice, opened)),
        "publish": (Path, "rename", fail),
    }.get(step)
    return patch.object(*fault) if fault is not None else nullcontext()


if __name__ == "__main__":
    ledger = {"draft-ledger": "draft", "spent-ledger": "failed"}.get(mode, "stage1_committed")
    if mode == "buffered-stderr":
        sys.stderr = os.fdopen(2, "w", encoding="utf-8", closefd=False)
        sys.stderr.write("buffered fixture stderr")
        ledger = "draft"
    with fault_context():
        status = run_transfer_worker(
            restricted=root / "private" / "synthetic-result",
            public=root / "public" / "PUBLIC.json",
            execution_host="synthetic-authority",
            local_host="synthetic-other" if mode == "wrong-host" else "synthetic-authority",
            ledger_status=ledger, preflight=preflight, score=score,
        )
    (root / "worker-returned").write_text(str(status))
    raise SystemExit(status)
"""


class TransferReleaseTests(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="rl183-transfer-")))

    def fixture(self, name, *, value=123.456):
        root = self.scratch / name
        (root / "private").mkdir(parents=True)
        (root / "public").mkdir()
        if value is not None:
            (root / "synthetic-input.json").write_text(json.dumps(value))
        return root

    def command(self, root, mode):
        return [sys.executable, "-B", "-c", _WORKER, str(root), mode, str(DRAFT)]

    def worker(self, root, mode):
        return subprocess.run(self.command(root, mode), cwd=ROOT, capture_output=True, check=False)

    def worker_with_notice_pipe(self, root, mode, *, connected, unbuffered):
        environment = os.environ.copy()
        if unbuffered:
            environment["PYTHONUNBUFFERED"] = "1"
        else:
            environment.pop("PYTHONUNBUFFERED", None)
        reader, writer = os.pipe()
        if not connected:
            os.close(reader)
            reader = None
        try:
            with os.fdopen(writer, "wb") as sink:
                result = subprocess.run(self.command(root, mode), cwd=ROOT, stdout=subprocess.PIPE,
                                        stderr=sink, env=environment, check=False)
            return result, os.read(reader, 4096) if reader is not None else None
        finally:
            if reader is not None:
                os.close(reader)

    def test_success_closes_three_names_and_one_public_file(self):
        root = self.fixture("success")
        output = self.worker(root, "success")
        self.assertEqual((output.returncode, output.stdout, output.stderr), (0, b"", b""))
        restricted = root / "private" / "synthetic-result"
        self.assertEqual({item.name for item in restricted.iterdir()}, CUSTODY_NAMES)
        self.assertEqual(json.loads((restricted / "scores.json").read_bytes()), {"synthetic": 123.456})
        self.assertIn(b"buffered fixture output", (restricted / "stdout").read_bytes())
        self.assertNotIn(b"fixture shutdown\n", (restricted / "stdout").read_bytes())
        self.assertFalse((root / "worker-returned").exists())
        self.assertIn(b"fixture child\n", (restricted / "stderr").read_bytes())
        public = root / "public"
        self.assertEqual([item.name for item in public.iterdir()], ["PUBLIC.json"])
        report = json.loads((public / "PUBLIC.json").read_bytes())
        self.assertEqual(report, {**{key: sha256(key.encode()).hexdigest() for key in HASHES},
                                  "transfer_interval": "estimated", "stage2_error": "no"})
        self.assertEqual(report.keys(), set(HASHES) | WORDS.keys())

    def test_empty_roster_can_report_no_interval_without_a_scoring_input(self):
        root = self.fixture("empty", value=None)
        output = self.worker(root, "empty")
        self.assertEqual((output.returncode, output.stdout, output.stderr), (0, b"", b""))
        report = json.loads((root / "public" / "PUBLIC.json").read_bytes())
        self.assertEqual(report["transfer_interval"], "not_evaluable")

    def test_transfer_exit_statuses(self):
        self.check_pre_read_refusals_exit_two()
        self.check_read_failures_emit_exact_notice()

    def test_transfer_status_survives_lost_notice_consumer(self):
        for mode, status, notice, entered, read_started in (
            ("draft-ledger", 2, REFUSAL, False, False),
            ("missing-input", 2, REFUSAL, True, False),
            ("post-systemexit", 1, b"stage2_error\nSystemExit\n", True, True),
        ):
            for connected in (True, False):
                for unbuffered in (False, True):
                    with self.subTest(mode=mode, connected=connected, unbuffered=unbuffered):
                        value = None if mode == "missing-input" else 123.456
                        root = self.fixture(f"{mode}-{connected}-{unbuffered}", value=value)
                        result, delivered = self.worker_with_notice_pipe(
                            root, mode, connected=connected, unbuffered=unbuffered
                        )
                        self.assertEqual((result.returncode, result.stdout), (status, b""))
                        self.assertFalse((root / "worker-returned").exists())
                        self.assertEqual(delivered, notice if connected else None)
                        self.assertEqual((root / "score-entered").exists(), entered)
                        self.assertEqual((root / "saw-read").exists(), read_started)
                        self.assertEqual(list((root / "public").iterdir()), [])
                        self.assertEqual((root / "private" / "synthetic-result").exists(), entered)

    def test_transfer_status_survives_initial_buffered_stream_failure(self):
        for unbuffered in (False, True):
            with self.subTest(unbuffered=unbuffered):
                root = self.fixture(f"buffered-stderr-{unbuffered}")
                result, delivered = self.worker_with_notice_pipe(
                    root, "buffered-stderr", connected=False, unbuffered=unbuffered
                )
                self.assertEqual((result.returncode, result.stdout, delivered), (2, b"", None))
                self.assertFalse((root / "score-entered").exists())
                self.assertEqual(list((root / "public").iterdir()), [])

    def test_transfer_boundary_contains_arbitrary_exceptions_at_each_step(self):
        steps_by_status = {
            2: ("startup-flush", "save-stderr", "spent-check", "filesystem", "preflight",
                "preflight-hashes", "reserve", "redirect", "sync", "score-before-read"),
            1: ("consume", "score-after-read", "result-validation", "scores-write", "inventory",
                "result-staging", "final-spent-check", "success-flush", "publish"),
        }
        for status, steps in steps_by_status.items():
            for step in steps:
                with self.subTest(step=step, status=status):
                    mode = f"inject-{step}"
                    root = self.fixture(mode)
                    result = self.worker(root, mode)
                    notice = REFUSAL if status == 2 else b"stage2_error\nOtherError\n"
                    self.assertEqual((result.returncode, result.stdout, result.stderr), (status, b"", notice))
                    self.assertFalse((root / "worker-returned").exists())
                    self.assertEqual((root / "saw-read").exists(), status == 1)
                    self.assertEqual(list((root / "public").iterdir()), [])

    def test_transfer_python_exits_follow_first_read(self):
        for mode in ("pre-systemexit", "pre-custom-base"):
            with self.subTest(mode=mode):
                root = self.fixture(mode)
                output = self.worker(root, mode)
                self.assertEqual((output.returncode, output.stdout, output.stderr), (2, b"", REFUSAL))
                self.assertFalse((root / "saw-read").exists())
                self.assertEqual(list((root / "private").iterdir()), [])
                self.assertEqual(list((root / "public").iterdir()), [])

        for mode, error_type in (
            ("post-systemexit", "SystemExit"),
            ("post-argparse", "SystemExit"),
            ("post-keyboardinterrupt", "KeyboardInterrupt"),
            ("post-custom-base", "OtherError"),
        ):
            with self.subTest(mode=mode):
                root = self.fixture(mode)
                output = self.worker(root, mode)
                notice = f"stage2_error\n{error_type}\n".encode("ascii")
                self.assertEqual((output.returncode, output.stdout, output.stderr), (1, b"", notice))
                self.assertTrue((root / "saw-read").exists())
                self.assertEqual(list((root / "public").iterdir()), [])
                restricted = root / "private" / "synthetic-result"
                stderr = (restricted / "stderr").read_bytes()
                self.assertIn(b"fixture diagnostic", stderr)
                if mode == "post-argparse":
                    self.assertIn(b"unrecognized arguments: --unknown", stderr)
                retry = self.worker(root, mode)
                self.assertEqual((retry.returncode, retry.stdout, retry.stderr), (2, b"", REFUSAL))
                self.assertEqual((restricted / "stderr").read_bytes(), stderr)

    def check_pre_read_refusals_exit_two(self):
        for mode in ("draft", "draft-ledger", "wrong-host", "spent-ledger", "missing-input"):
            with self.subTest(mode=mode):
                root = self.fixture(mode, value=None if mode == "missing-input" else 123.456)
                output = self.worker(root, mode)
                self.assertEqual((output.returncode, output.stdout, output.stderr), (2, b"", REFUSAL))
                self.assertEqual(list((root / "public").iterdir()), [])
                restricted = root / "private" / "synthetic-result"
                self.assertEqual(restricted.exists(), mode == "missing-input")
                if restricted.exists():
                    self.assertEqual(self.worker(root, mode).returncode, 2)

    def check_read_failures_emit_exact_notice(self):
        for mode, name in (
            ("builtin", "RuntimeError"), ("unlisted", "OtherError"), ("impostor", "OtherError"),
            ("json", "JSONDecodeError"), ("bad-public", "ValueError"), ("extra-private", "ValueError"),
        ):
            with self.subTest(mode=mode):
                root = self.fixture(mode)
                output = self.worker(root, mode)
                self.assertEqual((output.returncode, output.stdout, output.stderr),
                                 (1, b"", f"stage2_error\n{name}\n".encode()))
                self.assertEqual(list((root / "public").iterdir()), [])
                restricted = root / "private" / "synthetic-result"
                self.assertIn(b"fixture diagnostic", (restricted / "stderr").read_bytes())
                prior = (restricted / "stderr").read_bytes()
                self.assertEqual(self.worker(root, mode).returncode, 2)
                self.assertEqual((restricted / "stderr").read_bytes(), prior)

    def test_public_result_is_invariant_when_private_values_change_without_word_flip(self):
        roots = (self.fixture("world1", value=12.5), self.fixture("world2", value=-4.1))
        for root in roots:
            self.assertEqual(self.worker(root, "success").returncode, 0)
        public = [root / "public" / "PUBLIC.json" for root in roots]
        self.assertEqual(public[0].read_bytes(), public[1].read_bytes())
        scores = [root / "private" / "synthetic-result" / "scores.json" for root in roots]
        self.assertNotEqual(scores[0].read_bytes(), scores[1].read_bytes())

    def test_existing_public_result_refuses_and_preserves_bytes(self):
        root = self.fixture("published")
        public = root / "public" / "PUBLIC.json"
        public.write_bytes(b"fixture previous publication\n")
        output = self.worker(root, "success")
        self.assertEqual((output.returncode, output.stdout, output.stderr), (2, b"", REFUSAL))
        self.assertEqual(public.read_bytes(), b"fixture previous publication\n")
        self.assertEqual(list((root / "private").iterdir()), [])

    def test_only_one_concurrent_worker_can_reserve(self):
        root = self.fixture("contended")
        with subprocess.Popen(self.command(root, "contended"), cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as first:
            second = self.worker(root, "contended")
            stdout, stderr = first.communicate()
        self.assertCountEqual([(first.returncode, stdout, stderr), (second.returncode, second.stdout, second.stderr)],
                              [(0, b"", b""), (2, b"", REFUSAL)])
        self.assertTrue((root / "public" / "PUBLIC.json").is_file())


if __name__ == "__main__":
    unittest.main()
