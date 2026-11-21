"""RL-194 condition 4: the twin's pin-checking wrapper, and the reviewed child behind it. Generated inputs only."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.cadence import custody_pin_fixture as PF

REPO = Path(__file__).resolve().parents[2]
WRAPPER = REPO / "scripts/cadence_interim_twin_pins.py"
CHILD = REPO / "scripts/cadence_interim_twin.py"
REVIEWED_CHILD_SHA256 = "91ca54ab8747ede3d0fe8826e1b7d06ef721bce94de52969b9508a3eac890aab"      # the #816 review
SPANS = ("dev-01-s01", "dev-01-s03")
FILES = {"runner_receipt.json": b"{}\n", "legs/L001/leg_record.json": b"{}\n",
         "legs/L001/runtime/run/power_trace.csv": b"generated trace\n",
         "hazards/meter/stream-0001.jsonl": b"generated stream\n"}
ECHO_CHILD = ("import json, sys\n"
              "print(json.dumps({'argv': sys.argv[1:], 'isolated': bool(sys.flags.isolated),\n"
              "                  'no_bytecode': bool(sys.flags.dont_write_bytecode)}))\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ReviewedChild(unittest.TestCase):
    def test_the_child_is_byte_identical_to_its_review_and_the_manifest_pins_it(self):
        manifest = json.loads((REPO / "docs/process/cadence/looks/lm-interim-01.json").read_text(encoding="utf-8"))
        self.assertEqual(sha(CHILD.read_bytes()), REVIEWED_CHILD_SHA256)
        self.assertEqual(manifest["fit"]["twin"], {"path": "scripts/cadence_interim_twin.py",
                                                   "sha256": REVIEWED_CHILD_SHA256})
        pinned = {ref["path"]: ref["sha256"] for ref in manifest["fit"]["code"]}
        self.assertEqual(pinned.get("scripts/cadence_interim_twin_pins.py"), sha(WRAPPER.read_bytes()))

    def test_the_wrapper_imports_no_look_code_and_no_decoder(self):
        imported = set()
        for node in ast.walk(ast.parse(WRAPPER.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported, {"hashlib", "json", "os", "pathlib", "re", "sys"})


class Wrapper(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="twin-wrapper-")
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "docs").mkdir()
        self.wrapper = self.repo / "scripts/cadence_interim_twin_pins.py"
        shutil.copyfile(WRAPPER, self.wrapper)
        self.child = self.repo / "scripts/child.py"
        self.child.write_text(ECHO_CHILD)
        self.custody = self.tmp / "custody"
        for sid in SPANS:
            for name, data in FILES.items():
                path = self.custody / sid / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data + sid.encode())
        self.doc = PF.synthetic_pins({sid: self.custody / sid for sid in SPANS})
        self.pins = self.repo / "docs/pins.json"
        self.pins.write_bytes(PF.dump(self.doc))
        self.stage1 = self.tmp / "stage1.json"
        self.manifest = self.tmp / "manifest.json"
        self.write(allow_draft=False)

    def write(self, *, allow_draft, spans=SPANS):
        self.stage1.write_text(json.dumps({"roster": {"spans": [{"span_id": sid} for sid in spans]},
                                           "allow_draft": allow_draft}))
        self.manifest.write_text(json.dumps({
            "fit": {"twin": {"path": "scripts/child.py", "sha256": sha(self.child.read_bytes())}},
            "inputs": {"pins": {"path": "docs/pins.json", "sha256": sha(self.pins.read_bytes())}}}))

    def child_args(self):
        return ["--manifest", str(self.manifest), "--manifest-sha256", sha(self.manifest.read_bytes()),
                "--ledger-commit", "0" * 40, "--stage1", str(self.stage1), "--stage1-sha256",
                sha(self.stage1.read_bytes()), "--custody", str(self.custody), "--coefficients", "c.json",
                "--coefficients-sha256", "1" * 64, "--fit", "fit.json", "--step3", "step3.json"]

    def run_wrapper(self, *own, args=None, isolated=True):
        flags = ["-I", "-B"] if isolated else ["-B"]
        return subprocess.run([sys.executable, *flags, str(self.wrapper), *own, *(args or self.child_args())],
                              capture_output=True, text=True, cwd=self.tmp)

    def refused(self, done, name="ValueError"):
        self.assertEqual((done.returncode, done.stdout, done.stderr), (1, "", f"stage2_error\n{name}\n"))

    def test_with_every_pin_met_it_becomes_the_child_with_the_child_s_arguments_untouched(self):
        done = self.run_wrapper()
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        self.assertEqual(json.loads(done.stdout), {"argv": self.child_args(), "isolated": True, "no_bytecode": True})

    def test_a_custody_file_that_is_not_its_pin_ends_it_before_the_child_starts(self):
        span = self.custody / "dev-01-s03"
        trace, stream = span / "legs/L001/runtime/run/power_trace.csv", span / "hazards/meter/stream-0001.jsonl"

        def flip(path):
            data = path.read_bytes()
            path.write_bytes(bytes([data[0] ^ 1]) + data[1:])

        def exchange():
            a, b = trace.read_bytes(), (span / "runner_receipt.json").read_bytes()
            trace.write_bytes(b)
            (span / "runner_receipt.json").write_bytes(a)

        def link():
            kept = self.tmp / "kept"
            trace.rename(kept)
            trace.symlink_to(kept)
        faults = {"a changed stream": lambda: flip(trace), "a changed receipt": lambda: flip(span / "runner_receipt.json"),
                  "a missing stream": stream.unlink, "an extra file": lambda: (span / "notes.txt").write_bytes(b"x"),
                  "two files exchanged": exchange, "a symlinked stream": link,
                  "a longer stream": lambda: stream.write_bytes(stream.read_bytes() + b" ")}
        for label, change in faults.items():
            shutil.rmtree(span)
            (self.tmp / "kept").unlink(missing_ok=True)
            for name, data in FILES.items():
                path = span / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data + b"dev-01-s03")
            self.assertEqual(self.run_wrapper().returncode, 0)
            change()
            with self.subTest(label):
                self.refused(self.run_wrapper())

    def test_the_pin_list_the_roster_and_the_child_are_each_bound(self):
        cases = {
            "the pin list is not the manifest's": lambda: self.pins.write_bytes(self.pins.read_bytes() + b"\n"),
            "the roster names another span": lambda: self.write(allow_draft=False, spans=(*SPANS, "dev-02-s02")),
            "the roster lacks a pinned span": lambda: self.write(allow_draft=False, spans=SPANS[:1]),
            "the child is not at its pin": lambda: self.child.write_text(ECHO_CHILD + "# changed\n"),
        }
        for label, change in cases.items():
            self.pins.write_bytes(PF.dump(self.doc))
            self.child.write_text(ECHO_CHILD)
            self.write(allow_draft=False)
            self.assertEqual(self.run_wrapper().returncode, 0)
            change()
            with self.subTest(label):
                self.refused(self.run_wrapper())
        self.pins.write_bytes(PF.dump(self.doc))
        self.child.write_text(ECHO_CHILD)
        self.write(allow_draft=False)
        forged = json.loads(json.dumps(self.doc))
        forged["spans"][0]["files"][0]["sha256"] = "0" * 64         # the pins no longer rebuild their offload manifest
        self.pins.write_bytes(PF.dump(forged))
        self.write(allow_draft=False)
        self.refused(self.run_wrapper())

    def test_only_a_draft_look_may_name_its_own_pin_list(self):
        own = self.tmp / "own-pins.json"
        own.write_bytes(PF.dump(self.doc))
        flags = ("--custody-pins", str(own), "--custody-pins-sha256", sha(own.read_bytes()))
        self.refused(self.run_wrapper(*flags))                           # the stage-1 file is not a draft's
        self.write(allow_draft=True)
        done = self.run_wrapper(*flags)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["argv"], self.child_args())   # its own two options are not passed on
        self.refused(self.run_wrapper("--custody-pins", str(own), "--custody-pins-sha256", "0" * 64))
        self.refused(self.run_wrapper("--custody-pins", str(own)))

    def test_it_requires_the_isolated_interpreter_and_a_span_that_is_a_directory(self):
        self.refused(self.run_wrapper(isolated=False))
        moved = self.tmp / "moved"
        (self.custody / "dev-01-s01").rename(moved)
        (self.custody / "dev-01-s01").symlink_to(moved, target_is_directory=True)
        self.refused(self.run_wrapper())
        (self.custody / "dev-01-s01").unlink()
        self.refused(self.run_wrapper())
        done = self.run_wrapper(args=[*self.child_args(), "--span-dir", f"dev-01-s01={moved}"])
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
