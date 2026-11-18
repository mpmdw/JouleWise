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
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from joulewise.cadence_looks.manifest_dispatch import validate_v2
from joulewise.cadence_looks.transfer_release import HASHES, run_transfer_worker

root, mode, draft = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])

def preflight():
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
    if mode == "empty":
        return {"synthetic": None}, "not_evaluable"
    print("buffered fixture output", end="")
    with (root / "synthetic-input.json").open("rb") as source:
        mark_read()
        value = json.load(source)
    (root / "saw-read").touch()
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

if __name__ == "__main__":
    ledger = {"draft-ledger": "draft", "spent-ledger": "failed"}.get(mode, "stage1_committed")
    raise SystemExit(run_transfer_worker(
        restricted=root / "private" / "synthetic-result",
        public=root / "public" / "PUBLIC.json",
        execution_host="synthetic-authority",
        local_host="synthetic-other" if mode == "wrong-host" else "synthetic-authority",
        ledger_status=ledger, preflight=preflight, score=score,
    ))
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

    def test_success_closes_three_names_and_one_public_file(self):
        root = self.fixture("success")
        output = self.worker(root, "success")
        self.assertEqual((output.returncode, output.stdout, output.stderr), (0, b"", b""))
        restricted = root / "private" / "synthetic-result"
        self.assertEqual({item.name for item in restricted.iterdir()}, CUSTODY_NAMES)
        self.assertEqual(json.loads((restricted / "scores.json").read_bytes()), {"synthetic": 123.456})
        self.assertIn(b"buffered fixture output", (restricted / "stdout").read_bytes())
        self.assertIn(b"fixture shutdown\n", (restricted / "stdout").read_bytes())
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
