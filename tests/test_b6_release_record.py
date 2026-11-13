"""B-5: the Block 5 input probe, the release check and the record, on synthetic runs. No custody is read.

The release-check runs are made by the B-2 launcher on a synthetic git checkout with a stub program; the custody
kit's `verify` is replaced by a stub that counts files and bytes under a synthetic copy root.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import b6_real_run as rr  # noqa: E402
import b6_release_record as rec  # noqa: E402
from tests.independent_recompute.support_b6 import b6  # noqa: E402
from tests.test_b6_structure_probe import sealed_block  # noqa: E402

DECODE = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"
B5_STUB = {"contrasts": {DECODE: {"n": 10, "dbar_j": 0.5}},
           "reported_cells": {"c1": {"model": b6.MODELS["ALPHA"], "phase": "decode", "mean_j": 2.0,
                                     "per_token": {"j_per_token": None}}}}
IDS = ("s1", "s2", "s3")

STUB_PROGRAM = r'''
import hashlib, json, sys
from pathlib import Path
args = sys.argv[1:]
opt = lambda n: args[args.index(n) + 1]
data = b'{"restricted": true}\n'
Path(opt("--restricted-out")).write_bytes(data)
public = {"sessions": {s: {} for s in opt("--stub-ids").split(",")}, "restricted_sha256": hashlib.sha256(data).hexdigest()}
Path(opt("--public-out")).write_text(json.dumps(public))
print("recompute sessions=3 flags=0 comparison_stopped=false restricted_sha256=" + hashlib.sha256(data).hexdigest())
'''

STUB_KIT = r'''
import hashlib, json, sys
from pathlib import Path
args = sys.argv[1:]
opt = lambda n: args[args.index(n) + 1]
manifest = json.loads(Path(opt("--manifest")).read_bytes())
if hashlib.sha256(Path(opt("--manifest")).read_bytes()).hexdigest() != opt("--manifest-sha256"):
    sys.exit(4)
root = Path(opt("--root"))
sessions = {}
for e in manifest["sessions"]:
    files = [p for p in sorted((root / e["copy_path"]).rglob("*")) if p.is_file()]
    sessions[e["copy_path"]] = {"files": len(files), "bytes": sum(p.stat().st_size for p in files)}
out = Path(opt("--out"))
if out.exists():
    sys.exit(4)
out.write_text(json.dumps({"verdict": "verified", "manifest_sha256": opt("--manifest-sha256"), "sessions": sessions,
                           "zstd": {"version": "1.5.7"}}))
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}).stdout.strip()


class Block5Probe(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-b5probe-", dir=os.environ.get("TMPDIR")))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def probe(self, block5, digest=None):
        # The probe imports the program at this checkout; bind the table to these bytes, whatever the line.
        patch = mock.patch.dict(rr.PIN_TABLE, {rr.PROGRAM: sha(ROOT / rr.PROGRAM)})
        patch.start()
        self.addCleanup(patch.stop)
        out = self.tmp / ("probe-" + str(len(list(self.tmp.glob("probe-*")))) + ".json")
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = rec.main(["b5-probe", "--checkout", str(ROOT), "--block5", str(block5), "--block5-sha256",
                           digest or sha(block5), "--out", str(out)])
        return rc, buffer.getvalue().strip(), (json.loads(out.read_text()) if out.exists() else None)

    def test_counts_and_names_without_values_and_equal_to_the_block_run(self):
        path = self.tmp / "b5.json"
        path.write_text(json.dumps(B5_STUB))
        rc, line, doc = self.probe(path)
        self.assertEqual(rc, 0, line)
        self.assertEqual(doc["names"], {"ALPHA": ["reported/qwen3-1p7b/decode/mean_j"], "BETA": [],
                                        "GAMMA": ["contrast/decode/dbar_j"]})
        self.assertEqual((doc["total"], doc["by_pack"]), (2, {"ALPHA": 1, "BETA": 0, "GAMMA": 1}))
        self.assertEqual(line, "b5-probe total=2 ALPHA=1 BETA=0 GAMMA=1")
        self.assertNotIn("2.0", json.dumps(doc))
        self.assertNotIn("0.5", json.dumps(doc))
        # The predeclared count equals what the pinned program then marks block5_included in a block run.
        block = sealed_block(self.tmp / "block", (("ALPHA", 1), ("BETA", 1), ("GAMMA", 1)), block5=B5_STUB)
        self.assertEqual(block["rc"], 0, block["err"])
        restricted = json.loads(block["restricted"].read_text())
        observed = {p: sum(1 for v in row["values"].values() if v["block5_included"])
                    for p, row in restricted["block"]["between_session"].items()}
        self.assertEqual(observed, doc["by_pack"])

    def test_an_empty_block5_file_is_a_hold(self):
        """Opus kit review F3: a pinned `{}` gives a predeclared count of 0, which is a hold."""
        path = self.tmp / "b5-empty.json"
        path.write_text("{}")
        rc, line, doc = self.probe(path)
        self.assertEqual((rc, line, doc["total"]), (5, "b5-probe: hold total=0", 0))

    def test_wrong_digest_refuses(self):
        path = self.tmp / "b5.json"
        path.write_text(json.dumps(B5_STUB))
        rc, line, doc = self.probe(path, "0" * 64)
        self.assertEqual((rc, line, doc), (4, "refused: block5_digest_mismatch", None))


class ReleaseCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="b6-release-", dir=os.environ.get("TMPDIR")))
        self.checkout = self.tmp / "checkout"
        (self.checkout / "scripts").mkdir(parents=True)
        (self.checkout / rr.PROGRAM).write_text(STUB_PROGRAM)
        (self.checkout / "configs/b6").mkdir(parents=True)
        (self.checkout / rec.CATALOG).write_text("{}\n")
        git(self.checkout, "init", "-q")
        git(self.checkout, "add", "-A")
        git(self.checkout, "commit", "-q", "-m", "fixture")
        self.commit = git(self.checkout, "rev-parse", "HEAD")
        table = {rr.PROGRAM: sha(self.checkout / rr.PROGRAM), rec.CATALOG: sha(self.checkout / rec.CATALOG)}
        for patch in (mock.patch.object(rr, "PIN_TABLE", table), mock.patch.object(rec, "NINE", IDS)):
            patch.start()
            self.addCleanup(patch.stop)
        # Synthetic custody copy, manifest, loop files and Block 5 file.
        self.root = self.tmp / "custody"
        for sid in IDS:
            (self.root / sid / "archive/sources").mkdir(parents=True)
            (self.root / sid / "archive/sources/a.txt").write_text(sid)
        self.loop = self.tmp / "loop"
        self.loop.mkdir()
        (self.loop / "attempts.jsonl").write_text("{}\n")
        (self.loop / "state.json").write_text("{}\n")
        self.manifest = self.tmp / "manifest.json"
        self.manifest.write_text(json.dumps({"sessions": [{"copy_path": s + "/archive", "harvest_sha256": "a" * 64}
                                                          for s in IDS]}))
        self.block5 = self.tmp / "block5.json"
        self.block5.write_text("{}\n")
        self.kit = self.tmp / "kit.py"
        self.kit.write_text(STUB_KIT)
        self.run_dir = self.tmp / "run"
        self.run_dir.mkdir(mode=0o700)
        os.chmod(self.run_dir, 0o700)
        subprocess.run([sys.executable, str(self.kit), "--manifest", str(self.manifest), "--manifest-sha256",
                        sha(self.manifest), "--root", str(self.root), "--out", str(self.run_dir / "verify-receipt.json")],
                       check=True)
        for stem in ("gate", "dry"):
            self.launch(stem)

    def launch(self, stem, kind=None):
        """One launcher attempt into RUN/<stem>, then its probe output (structure.json) bound to its digest."""
        kind = kind or ("gate" if stem.startswith("gate") else "dry")
        doc = self.run_dir / ("run-inputs-" + kind + ".json")
        if not doc.exists():
            external = {"loop_attempts": sha(self.loop / "attempts.jsonl"), "loop_state": sha(self.loop / "state.json")}
            if kind == "dry":
                external["block5"] = sha(self.block5)
            doc.write_text(json.dumps({"host": "Air", "external": external, "sessions": {}}))
        out = self.run_dir / stem
        program = ["block", *[x for s in IDS for x in ("--session", str(self.root / s / "archive"))],
                   "--loop-attempts", str(self.loop / "attempts.jsonl"), "--loop-state", str(self.loop / "state.json"),
                   *(["--block5", str(self.block5)] if kind == "dry" else []),
                   "--inputs", str(doc), "--inputs-sha256", sha(doc), "--stub-ids", ",".join(IDS),
                   "--restricted-out", str(out / "restricted.json"), "--public-out", str(out / "public.json")]
        with contextlib.redirect_stdout(io.StringIO()):
            rc = rr.main(["--checkout", str(self.checkout), "--expect-commit", self.commit, "--stem", stem,
                          "--limit-s", "60", "--out-dir", str(out), "--", *program])
        assert rc == 0
        record = json.loads((out / "record.json").read_text())
        (out / "structure.json").write_text(json.dumps({
            "stage": kind + "_run", "checks": {"option_c_pass": {"result": "ok"},
                                               "copied_paths_equal_r3": {"result": "reported", "equal": False},
                                               **({"block5_included": {"result": "ok", "observed": 2, "expected": 2}}
                                                  if kind == "dry" else {})},
            "identity": {"comparison_stopped": False, "inputs": {"l9_audit": "not_run"}},
            "option_c": {"pass": True, "comparator": {"classes": {"neg8": {"compared": 3, "failed": 0, "unmatched": 0,
                                                                           "pass": True}}}},
            "term7": {"result": "pass"}, "digests": {"restricted_file": record["outputs_sha256"]["restricted"]}}))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def check(self, *, cites=None, receipt="verify-receipt-release.json", root=None, extra=()):
        cites = cites if cites is not None else ["1=RUN_STATE 59", "2=RUN_STATE 231", "9=PR #748 merged",
                                                 "10=RUN_STATE RL-6 (d) line", "11=Ed OK on record"]
        argv = ["check", "--run-dir", str(self.run_dir), "--checkout", str(self.checkout), "--expect-commit",
                self.commit, "--manifest", str(self.manifest), "--manifest-sha256", sha(self.manifest), "--block5",
                str(self.block5), "--block5-sha256", sha(self.block5), "--kit", str(self.kit), "--root",
                str(root or self.root), "--receipt-out", str(self.run_dir / receipt),
                *[x for c in cites for x in ("--cite", c)], *extra]
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = rec.main(argv)
        return rc, buffer.getvalue().strip(), json.loads((self.run_dir / "release-record-draft.json").read_text())

    def test_pass_then_record(self):
        rc, line, draft = self.check()
        self.assertEqual((rc, line), (0, "release-check: pass"), json.dumps(draft["conditions"], indent=1))
        self.assertEqual(draft["run_inputs_sha256"]["block"], sha(self.run_dir / "run-inputs-dry.json"))
        self.assertEqual(draft["run_inputs_sha256"]["gate"], sha(self.run_dir / "run-inputs-gate.json"))
        self.assertEqual(len(draft["ledger"]), 2)
        self.assertEqual(draft["zstd"], "1.5.7")
        self.assertEqual(draft["harvest_sha256"], {s + "/archive": "a" * 64 for s in IDS})
        registration = self.tmp / "registration.md"
        registration.write_text("registration\n")
        out = self.tmp / "block6_release_record.md"
        with contextlib.redirect_stdout(io.StringIO()):
            rc = rec.main(["record", "--draft", str(self.run_dir / "release-record-draft.json"), "--out", str(out),
                           "--registration", str(registration), "--main-commit", "c" * 40, "--signed-by", "the lead",
                           "--date", "2026-11-13"])
        self.assertEqual(rc, 0)
        text = out.read_text()
        self.assertIn(sha(registration), text)
        self.assertIn(sha(self.manifest), text)
        self.assertIn("| L9 audit | not run |", text)
        self.assertEqual(text.count("a" * 64), 3)  # the harvest digests, and no other manifest digest
        self.assertTrue(out.with_suffix(".json").is_file())

    def test_one_byte_appended_to_the_public_output_fails_6(self):
        with open(self.run_dir / "dry/public.json", "ab") as stream:
            stream.write(b" ")
        rc, line, draft = self.check()
        self.assertEqual((rc, line), (5, "release-check: fail 6"))
        self.assertFalse(draft["conditions"]["6"]["public_equal"])

    def test_a_touched_custody_file_in_a_copy_of_the_root_fails_7(self):
        copy = self.tmp / "custody-copy"
        shutil.copytree(self.root, copy)
        with open(copy / "s2/archive/sources/a.txt", "a") as stream:
            stream.write("x")
        rc, line, draft = self.check(root=copy)
        self.assertEqual((rc, line), (5, "release-check: fail 7"))
        self.assertFalse(draft["conditions"]["7"]["receipts_agree"])

    def test_a_changed_loop_file_fails_7(self):
        (self.loop / "state.json").write_text("{\"changed\": 1}\n")
        rc, line, draft = self.check()
        self.assertEqual(line, "release-check: fail 7")
        self.assertFalse(draft["conditions"]["7"]["rehash"]["loop_state"])

    def test_missing_cites_fail_and_are_named(self):
        rc, line, draft = self.check(cites=["1=a", "2=b", "9=c", "10=d"])
        self.assertEqual(line, "release-check: fail 11")
        self.assertEqual(draft["conditions"]["1"]["cited"], "a")

    def test_dirty_checkout_fails_8(self):
        (self.checkout / "scripts/extra.py").write_text("x = 1\n")
        rc, line, _ = self.check()
        self.assertEqual(line, "release-check: fail 8")

    def test_term7_stop_fails_5_and_an_unledgered_attempt_fails_3(self):
        path = self.run_dir / "dry/structure.json"
        doc = json.loads(path.read_text())
        doc["term7"]["result"] = "stop"
        path.write_text(json.dumps(doc))
        (self.run_dir / "attempts.jsonl").write_text((self.run_dir / "attempts.jsonl").read_text().splitlines()[1] + "\n")
        rc, line, _ = self.check()
        self.assertEqual(line, "release-check: fail 3,5")

    def edit_structure(self, stem, edit):
        path = self.run_dir / stem / "structure.json"
        doc = json.loads(path.read_text())
        edit(doc)
        path.write_text(json.dumps(doc))

    def test_a_probe_departure_fails_4(self):
        """RL-139 fix 7: a seeded pairing_as_r7 departure in the dry probe fails condition 4."""
        self.edit_structure("dry", lambda d: d["checks"].update(pairing_as_r7={"result": "departs"}))
        rc, line, draft = self.check()
        self.assertEqual((rc, line), (5, "release-check: fail 4"))
        self.assertEqual(draft["conditions"]["4"]["probes"]["dry"]["departs"], ["pairing_as_r7"])

    def test_a_not_checked_row_in_the_gate_probe_fails_4(self):
        self.edit_structure("gate", lambda d: d["checks"].update(run_inputs_sha256={"result": "not_checked"}))
        rc, line, draft = self.check()
        self.assertEqual(line, "release-check: fail 4")
        self.assertEqual(draft["conditions"]["4"]["probes"]["gate"]["not_checked"], ["run_inputs_sha256"])

    def test_a_probe_on_other_bytes_or_the_wrong_stage_fails_4(self):
        for stem, edit in (("gate", lambda d: d["digests"].update(restricted_file="0" * 64)),
                           ("dry", lambda d: d.update(stage="gate_run"))):
            with self.subTest(stem=stem):
                original = (self.run_dir / stem / "structure.json").read_text()
                self.edit_structure(stem, edit)
                receipt = "receipt-" + stem + ".json"
                rc, line, _ = self.check(receipt=receipt)
                self.assertEqual(line, "release-check: fail 4")
                (self.run_dir / stem / "structure.json").write_text(original)

    def test_a_block5_count_of_zero_is_a_hold(self):
        """Opus kit review F3: a predeclared or observed Block 5 count of 0 fails condition 4, even when equal."""
        for i, counts in enumerate(({"observed": 0, "expected": 0}, {"observed": 0, "expected": 2},
                                    {"observed": 2, "expected": 0})):
            with self.subTest(counts=counts):
                self.edit_structure("dry", lambda d: d["checks"]["block5_included"].update(counts))
                rc, line, draft = self.check(receipt="receipt-b5-" + str(i) + ".json")
                self.assertEqual(line, "release-check: fail 4")
                self.assertEqual(draft["conditions"]["4"]["block5_count"], counts)

    def test_a_gate_record_at_exit_4_fails_3(self):
        """RL-139 fix 7: condition 3 needs the gate record at exit 0, status complete."""
        path = self.run_dir / "gate/record.json"
        record = json.loads(path.read_text())
        record.update(exit_code=4, status="refused", code="session_input_unsupplied", **{"class": "A"})
        path.write_text(json.dumps(record))
        rc, line, draft = self.check()
        self.assertEqual(line, "release-check: fail 3")
        self.assertEqual(draft["conditions"]["3"]["gate_exit_code"], 4)

    def test_a_relaunched_dry_run_in_dry2_passes_with_dry_dir(self):
        """RL-139 fix 7: after a relaunch the passing attempt lives in a new directory; --dry-dir names it."""
        with open(self.run_dir / "dry/public.json", "ab") as stream:  # the first attempt no longer verifies
            stream.write(b" ")
        self.launch("dry2", "dry")
        rc, line, _ = self.check(receipt="receipt-default.json")
        self.assertEqual(line, "release-check: fail 6")
        rc, line, draft = self.check(receipt="receipt-dry2.json", extra=("--dry-dir", str(self.run_dir / "dry2")))
        self.assertEqual((rc, line), (0, "release-check: pass"), json.dumps(draft["conditions"], indent=1))
        self.assertEqual(len(draft["ledger"]), 3)

    def test_record_refuses_a_failing_draft(self):
        with open(self.run_dir / "dry/public.json", "ab") as stream:
            stream.write(b" ")
        self.check()
        with contextlib.redirect_stdout(io.StringIO()) as buffer:
            rc = rec.main(["record", "--draft", str(self.run_dir / "release-record-draft.json"), "--out",
                           str(self.tmp / "r.md"), "--registration", str(self.manifest), "--main-commit", "c",
                           "--signed-by", "x", "--date", "d"])
        self.assertEqual((rc, buffer.getvalue().strip()), (4, "refused: draft_not_passing"))


if __name__ == "__main__":
    unittest.main()
