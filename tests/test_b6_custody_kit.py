"""scripts/b6_custody_kit.py on synthetic archives only; no study path is read.

Every test states its expected result first. Refusal tests assert the exact
refusal code, so removing any one refusal from the kit makes a test fail
(the mutant kill table is in docs/run_reports/2026-11-12-b6-custody-kit.md).
B6_CUSTODY_KIT_UNDER_TEST, if set, names a mutant copy of the kit to test.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = Path(os.environ.get("B6_CUSTODY_KIT_UNDER_TEST") or ROOT / "scripts/b6_custody_kit.py")
_spec = importlib.util.spec_from_file_location("b6_custody_kit_under_test", KIT_PATH)
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)

MARKER = "PLANTED-CONTENT-MARKER-7f3c"
FAMILIES = kit.FAMILIES


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*argv):
    argv = [str(a) for a in argv]
    if argv[0] == "manifest" and "--source-host" not in argv:
        argv += ["--source-host", "mbp-test"]   # tests run source and copy on one machine
    if argv[0] == "manifest" and "--loop-state" not in argv and "--no-loop-state" not in argv:
        argv += ["--no-loop-state"]
    return run_raw(*argv)


def run_raw(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = kit.main([str(a) for a in argv])
    return rc, out.getvalue(), err.getvalue()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def mini_archive(parent, name, *, log="inside", marker=False, big=False):
    """A small sealed archive in the production layout (synthetic content only)."""
    a = parent / name
    planted = MARKER if marker else "plain"
    write(a / "sources/meter/stream-1.jsonl", json.dumps({"t": 1, "w": 10.0, "note": planted}) + "\n")
    write(a / "sources/meter/stream-2.jsonl", "".join(json.dumps({"t": i, "w": 11.0, "n": planted}) + "\n"
                                                    for i in range(200)))
    write(a / "sources/monitor/contention.jsonl", '{"k": 1}\n')
    write(a / "sources/monitor/clock.jsonl", '{"c": 1}\n')
    write(a / "sources/runs/r1/data.bin", "x" * 300)
    if big:   # multi-chunk files: larger than the kit's 1 MiB read chunk, plain and compressed
        (a / "sources/runs/r1/big.bin").write_bytes(big_bytes(b"plain"))
        (a / "sources/runs/r1/big-z.bin").write_bytes(big_bytes(b"packed"))
    sources = sorted(p for p in (a / "sources").rglob("*") if p.is_file())
    write(a / "sources/SHA256SUMS", "".join(f"{sha(p)}  {p.relative_to(a / 'sources')}\n" for p in sources))
    write(a / "derived/b6-acceptance.json", '{"verdict": "ACCEPTED"}\n')
    write(a / "derived/flags.jsonl", '{"code": "x"}\n')
    write(a / "withheld/spans.json", '{"spans": {}}\n')
    write(a / "harvest.json", json.dumps({"outputs": {}, "note": planted}) + "\n")
    stream = a / "sources/meter/stream-2.jsonl"
    subprocess.run(["zstd", "-q", "-1", "-T1", "-f", str(stream), "-o", str(stream) + ".zst"], check=True)
    row = json.dumps({"event": "compress", "path": str(stream), "sha256": sha(stream)}) + "\n"
    stream.unlink()
    if big:
        packed = a / "sources/runs/r1/big-z.bin"
        subprocess.run(["zstd", "-q", "-1", "-T1", "-f", str(packed), "-o", str(packed) + ".zst"], check=True)
        packed.unlink()
    if log == "inside":
        write(a / "compression.jsonl", row)
    elif log == "adjacent":
        write(Path(str(a) + ".desk/compression.jsonl"), row)
    return a


BIG = 3 * (1 << 20) + 5


def big_bytes(seed):
    """BIG incompressible, deterministic bytes: three full 1 MiB chunks and a short tail."""
    out, counter = bytearray(), 0
    while len(out) < BIG:
        out += hashlib.sha256(seed + str(counter).encode()).digest()
        counter += 1
    return bytes(out[:BIG])


def mapping_for(copy_paths):
    one = {"meter_streams": ["sources/meter/stream-1.jsonl", "sources/meter/stream-2.jsonl"],
           "contention_journal": "sources/monitor/contention.jsonl",
           "clock_journal": "sources/monitor/clock.jsonl",
           "copied_records": {f: ["derived/flags.jsonl"] for f in FAMILIES}}
    return {"sessions": {c: json.loads(json.dumps(one)) for c in copy_paths}}


class Mini(unittest.TestCase):
    """Two small archives (one compression log inside, one adjacent), copied and verified."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="b6-custody-kit-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.src, self.dst = self.base / "src", self.base / "dst"
        self.a = mini_archive(self.src, "b6-alpha-r1", log="inside")
        self.b = mini_archive(self.src, "b6-beta-r1", log="adjacent")
        self.attempts = self.src / "attempts.jsonl"
        write(self.attempts, '{"session_id": "s"}\n')
        self.manifest = self.base / "manifest.json"
        rc, out, err = run("manifest", "--session", self.a, "--session", self.b,
                           "--loop-attempts", self.attempts, "--out", self.manifest)
        self.assertEqual((rc, err), (0, ""))
        self.msha = out.strip().rsplit("=", 1)[1]
        shutil.copytree(self.src, self.dst, symlinks=True)
        self.receipt = self.base / "receipt.json"
        self.ca, self.cb = self.dst / "b6-alpha-r1", self.dst / "b6-beta-r1"

    def verify(self, out=None, msha=None, manifest=None):
        return run("verify", "--manifest", manifest or self.manifest, "--manifest-sha256", msha or self.msha,
                   "--root", self.dst, "--loop-dir", self.dst, "--out", out or self.receipt)

    def assertRefused(self, result, code):
        rc, out, err = result
        self.assertEqual((rc, err.strip()), (4, "refused: " + code))

    def inputs(self, mapping, out=None, receipt=None, extra=()):
        path = self.base / ("mapping-%d.json" % len(list(self.base.glob("mapping-*.json"))))
        path.write_text(json.dumps(mapping))
        return run("inputs", *self.ia(receipt=receipt),
                   "--mapping", path, "--l9-audit", "not_run", "--out", out or self.base / "run-inputs.json", *extra)

    def ia(self, receipt=None, manifest=None):
        """The five pinning arguments of `inputs` (cold review M3): both out-of-band digests."""
        receipt = receipt or self.receipt
        return ["--manifest", manifest or self.manifest, "--manifest-sha256", sha(manifest or self.manifest),
                "--verify-receipt", receipt, "--verify-receipt-sha256", sha(receipt)]

    def verified(self):
        rc, out, err = self.verify()
        self.assertEqual((rc, err), (0, ""))

    # -- manifest and verify happy path --

    def test_verify_clean_copy_exits_zero_with_counts_only_receipt(self):
        # Expected: exit 0; the receipt holds counts and bytes only; one compressed row per archive.
        rc, out, err = self.verify()
        self.assertEqual((rc, err), (0, ""))
        receipt = json.loads(self.receipt.read_bytes())
        self.assertEqual(receipt["verdict"], "verified")
        self.assertEqual(set(receipt["sessions"]["b6-alpha-r1"]),
                         {"files", "bytes", "sums_rows", "sums_rows_compressed", "desk_files"})
        self.assertEqual(receipt["sessions"]["b6-alpha-r1"]["sums_rows_compressed"], 1)
        self.assertEqual(receipt["sessions"]["b6-beta-r1"]["desk_files"], 1)
        self.assertEqual(receipt["totals"]["sums_rows"], 10)

    def test_manifest_prints_its_own_digest(self):
        # Expected: the printed digest is the SHA-256 of the manifest file's bytes.
        self.assertEqual(self.msha, sha(self.manifest))

    # -- digest checks the mutants showed untested (cold review M5) --

    def test_flipped_byte_in_withheld_file(self):
        # Expected: digest_mismatch for a withheld/ file (bound by the source manifest, outside SHA256SUMS).
        p = self.ca / "withheld/spans.json"
        p.write_bytes(p.read_bytes().replace(b"spans", b"spanz"))
        self.assertRefused(self.verify(), "digest_mismatch")

    def test_flipped_byte_in_harvest(self):
        # Expected: digest_mismatch for harvest.json.
        p = self.ca / "harvest.json"
        p.write_bytes(p.read_bytes().replace(b"outputs", b"outputz"))
        self.assertRefused(self.verify(), "digest_mismatch")

    def test_desk_folder_missing_its_file(self):
        # Expected: desk_file_set_mismatch exactly, for an emptied desk folder and for a removed one.
        desk = Path(str(self.cb) + ".desk")
        (desk / "compression.jsonl").unlink()
        self.assertRefused(self.verify(), "desk_file_set_mismatch")
        desk.rmdir()
        self.assertRefused(self.verify(out=self.base / "r2.json"), "desk_file_set_mismatch")

    def test_inputs_pins_never_rehash_the_copy(self):
        # Expected: after verify, every pinned file on the copy is changed (harvest, acceptance, flags, withheld
        # spans, the loop file); inputs exits 0 and each pin equals the SOURCE digest. A pin rehashed from the
        # copy would carry the changed digest.
        self.verified()
        changed = ("harvest.json", "derived/b6-acceptance.json", "derived/flags.jsonl", "withheld/spans.json")
        for name in changed:
            (self.ca / name).write_text("changed on the copy\n")
        (self.dst / "attempts.jsonl").write_text("changed on the copy\n")
        out = self.base / "pins.json"
        rc, _, err = self.inputs(mapping_for(["b6-alpha-r1", "b6-beta-r1"]), out=out)
        self.assertEqual((rc, err), (0, ""))
        doc = json.loads(out.read_bytes())
        pin = doc["sessions"][str(self.ca)]
        self.assertEqual(pin["harvest_sha256"], sha(self.a / "harvest.json"))
        self.assertEqual(pin["acceptance_sha256"], sha(self.a / "derived/b6-acceptance.json"))
        self.assertEqual(pin["files"], {n: sha(self.a / n) for n in
                                        ("derived/b6-acceptance.json", "derived/flags.jsonl", "withheld/spans.json")})
        self.assertEqual(doc["external"], {"loop_attempts": sha(self.attempts)})
        for name in changed:
            self.assertNotEqual(sha(self.ca / name), sha(self.a / name))

    # -- verify refusals (brief witnesses) --

    def test_flipped_byte_in_listed_source_file(self):
        # Expected: refused digest_mismatch.
        p = self.ca / "sources/runs/r1/data.bin"
        p.write_bytes(b"y" + p.read_bytes()[1:])
        self.assertRefused(self.verify(), "digest_mismatch")

    def test_flipped_byte_in_derived_file(self):
        # Expected: refused digest_mismatch (files outside SHA256SUMS are bound by the source manifest).
        p = self.ca / "derived/flags.jsonl"
        p.write_bytes(p.read_bytes().replace(b"x", b"y"))
        self.assertRefused(self.verify(), "digest_mismatch")

    def test_flipped_byte_in_desk_log(self):
        # Expected: refused digest_mismatch.
        p = Path(str(self.cb) + ".desk/compression.jsonl")
        p.write_bytes(p.read_bytes().replace(b"compress", b"compresz"))
        self.assertRefused(self.verify(), "digest_mismatch")

    def test_corrupt_zst(self):
        # Expected: refused decompression_failed (zstd frame checksum).
        p = self.ca / "sources/meter/stream-2.jsonl.zst"
        data = bytearray(p.read_bytes())
        data[len(data) // 2] ^= 0xFF
        p.write_bytes(bytes(data))
        self.assertRefused(self.verify(), "decompression_failed")

    def test_zst_whose_stream_differs(self):
        # Expected: refused digest_mismatch (a valid frame with different decompressed bytes).
        p = self.ca / "sources/meter/stream-2.jsonl.zst"
        other = self.base / "other.jsonl"
        other.write_text('{"t": 0}\n')
        subprocess.run(["zstd", "-q", "-f", str(other), "-o", str(p)], check=True)
        self.assertRefused(self.verify(), "digest_mismatch")

    def test_recompressed_zst_changes_bytes(self):
        # Expected: refused tree_size_mismatch (same stream, different compressed bytes).
        p = self.ca / "sources/meter/stream-2.jsonl.zst"
        plain = self.base / "plain.jsonl"
        subprocess.run(["zstd", "-q", "-d", "-f", str(p), "-o", str(plain)], check=True)
        subprocess.run(["zstd", "-q", "-19", "-f", "--no-check", str(plain), "-o", str(p)], check=True)
        self.assertNotEqual(p.stat().st_size, (self.a / "sources/meter/stream-2.jsonl.zst").stat().st_size)
        self.assertRefused(self.verify(), "tree_size_mismatch")

    def test_extra_file_in_sources(self):
        # Expected: refused unlisted_extra_file.
        write(self.ca / "sources/runs/r1/extra.txt", "e")
        self.assertRefused(self.verify(), "unlisted_extra_file")

    def test_extra_file_in_derived(self):
        # Expected: refused unlisted_extra_file.
        write(self.ca / "derived/extra.json", "{}")
        self.assertRefused(self.verify(), "unlisted_extra_file")

    def test_missing_listed_source_file(self):
        # Expected: refused listed_file_missing.
        (self.ca / "sources/monitor/clock.jsonl").unlink()
        self.assertRefused(self.verify(), "listed_file_missing")

    def test_missing_derived_file(self):
        # Expected: refused listed_file_missing.
        (self.ca / "withheld/spans.json").unlink()
        self.assertRefused(self.verify(), "listed_file_missing")

    def test_missing_sha256sums(self):
        # Expected: refused listed_file_missing.
        (self.ca / "sources/SHA256SUMS").unlink()
        self.assertRefused(self.verify(), "listed_file_missing")

    def test_edited_sha256sums(self):
        # Expected: refused sums_digest_mismatch, even when the edit matches a changed file.
        p = self.ca / "sources/runs/r1/data.bin"
        p.write_text("z" * 300)
        sums = self.ca / "sources/SHA256SUMS"
        sums.write_text(sums.read_text().replace(sha(self.a / "sources/runs/r1/data.bin"), sha(p)))
        self.assertRefused(self.verify(), "sums_digest_mismatch")

    def test_wrong_manifest_sha256(self):
        # Expected: refused manifest_digest_mismatch.
        self.assertRefused(self.verify(msha="0" * 64), "manifest_digest_mismatch")

    def test_manifest_schema(self):
        # Expected: refused manifest_schema_invalid for a JSON file that is not a kit manifest.
        other = self.base / "not-a-manifest.json"
        other.write_text('{"sessions": []}')
        self.assertRefused(self.verify(manifest=other, msha=sha(other)), "manifest_schema_invalid")

    def test_symlink_in_copy(self):
        # Expected: refused symlink (a file replaced by a link to identical bytes).
        p = self.ca / "sources/monitor/contention.jsonl"
        target = self.base / "outside.jsonl"
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
        self.assertRefused(self.verify(), "symlink")

    def test_symlinked_copy_root(self):
        # Expected: refused symlink when a path component of the copy is a link.
        self.dst.rename(self.base / "real-dst")
        self.dst.symlink_to(self.base / "real-dst")
        self.assertRefused(self.verify(), "symlink")

    def test_fifo_in_copy(self):
        # Expected: refused not_regular_file; the FIFO is never opened.
        os.mkfifo(self.ca / "derived/pipe")
        self.assertRefused(self.verify(), "not_regular_file")

    def test_session_missing_on_copy(self):
        # Expected: refused session_missing.
        shutil.rmtree(self.cb)
        self.assertRefused(self.verify(), "session_missing")

    def test_desk_file_set(self):
        # Expected: refused desk_file_set_mismatch when the desk folder gains a file.
        write(Path(str(self.cb) + ".desk/other.log"), "o")
        self.assertRefused(self.verify(), "desk_file_set_mismatch")

    def verify_with_edited_sums(self, edit):
        """Edit the copy's SHA256SUMS and re-issue the manifest's digest for it, as a forged source would:
        verify's own SHA256SUMS parsing is then the only guard (the real manifest step refuses these at the source)."""
        sums = self.ca / "sources/SHA256SUMS"
        sums.write_text(edit(sums.read_text()))
        document = json.loads(self.manifest.read_bytes())
        document["sessions"][0]["sha256sums_sha256"] = sha(sums)
        forged = self.base / "forged-manifest.json"
        forged.write_text(json.dumps(document))
        return self.verify(manifest=forged, msha=sha(forged), out=self.base / "forged-receipt.json")

    def test_sums_line_invalid(self):
        # Expected: verify refuses sums_line_invalid for a malformed row, even with a matching manifest digest;
        # the manifest step refuses the same file at the source.
        self.assertRefused(self.verify_with_edited_sums(lambda t: t + "nothex  sources/x\n"), "sums_line_invalid")
        sums = self.a / "sources/SHA256SUMS"
        sums.write_text(sums.read_text() + "nothex  sources/x\n")
        self.assertRefused(self.manifest_run(self.a), "sums_line_invalid")

    def test_sums_duplicate_row(self):
        # Expected: sums_line_invalid for a repeated path, at verify and at the manifest step.
        self.assertRefused(self.verify_with_edited_sums(lambda t: t + t.splitlines()[0] + "\n"), "sums_line_invalid")
        sums = self.a / "sources/SHA256SUMS"
        sums.write_text(sums.read_text() + sums.read_text().splitlines()[0] + "\n")
        self.assertRefused(self.manifest_run(self.a), "sums_line_invalid")

    def test_sums_path_escapes(self):
        # Expected: path_invalid for a '..' row, at verify and at the manifest step.
        self.assertRefused(self.verify_with_edited_sums(lambda t: t + "0" * 64 + "  ../harvest.json\n"), "path_invalid")
        sums = self.a / "sources/SHA256SUMS"
        sums.write_text(sums.read_text() + "0" * 64 + "  ../harvest.json\n")
        self.assertRefused(self.manifest_run(self.a), "path_invalid")

    def remanifest_and_verify(self):
        shutil.rmtree(self.dst)
        shutil.copytree(self.src, self.dst, symlinks=True)
        self.manifest.unlink()
        rc, out, err = run("manifest", "--session", self.a, "--session", self.b,
                           "--loop-attempts", self.attempts, "--out", self.manifest)
        self.assertEqual(rc, 0)
        return self.verify(msha=out.strip().rsplit("=", 1)[1])

    def test_zstd_unavailable(self):
        # Expected: refused zstd_unavailable when no zstd binary is on PATH.
        with mock.patch.object(kit.shutil, "which", return_value=None):
            self.assertRefused(self.verify(), "zstd_unavailable")

    def test_zstd_version_fails(self):
        # Expected: refused zstd_unavailable when 'zstd --version' fails.
        failed = subprocess.CompletedProcess([], 1, "", "")
        with mock.patch.object(kit.subprocess, "run", return_value=failed):
            self.assertRefused(self.verify(), "zstd_unavailable")

    def test_verify_out_exists_before_any_read(self):
        # Expected: refused out_exists before the (absent) manifest is read.
        self.receipt.write_text("{}")
        self.assertRefused(run("verify", "--manifest", self.base / "absent.json", "--manifest-sha256", "0" * 64,
                               "--root", self.dst, "--loop-dir", self.dst, "--out", self.receipt), "out_exists")

    # -- loop files (cold review M4) --

    def loop_manifest(self, *extra, state=True):
        state_file = self.src / "state.json"
        write(state_file, '{"state": 1}\n')
        out = self.base / ("loop-manifest-%d.json" % len(list(self.base.glob("loop-manifest-*"))))
        flag = ["--loop-state", state_file] if state else []
        return out, run("manifest", "--session", self.a, "--loop-attempts", self.attempts, *flag, *extra, "--out", out)

    def test_manifest_requires_a_loop_state_decision(self):
        # Expected (M4): usage error (exit 2) when neither --loop-state nor --no-loop-state is given;
        # both together are also a usage error.
        for extra in ([], ["--loop-state", self.attempts, "--no-loop-state"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                run_raw("manifest", "--session", str(self.a), "--loop-attempts", str(self.attempts), *extra,
                        "--source-host", "h", "--out", str(self.base / "x.json"))
            self.assertEqual(caught.exception.code, 2)

    def test_no_loop_state_is_recorded_and_inputs_carry_none(self):
        # Expected: the manifest records loop_state_waived true and no loop_state; inputs `external` has only attempts.
        document = json.loads(self.manifest.read_bytes())
        self.assertIs(document["loop_state_waived"], True)
        self.assertEqual(set(document["loop"]), {"loop_attempts"})

    def test_loop_state_is_digested_and_verified_on_the_copy(self):
        # Expected: with --loop-state the manifest records both files; verify refuses a missing and a changed copy.
        out, (rc, mout, err) = self.loop_manifest()
        self.assertEqual((rc, err), (0, ""))
        document = json.loads(out.read_bytes())
        self.assertEqual(document["loop"]["loop_state"], {"name": "state.json", "sha256": sha(self.src / "state.json")})
        self.assertIs(document["loop_state_waived"], False)
        msha = mout.strip().rsplit("=", 1)[1]
        shutil.copyfile(self.src / "state.json", self.dst / "state.json")
        self.assertEqual(self.verify(manifest=out, msha=msha, out=self.base / "lr1.json")[0], 0)
        (self.dst / "state.json").write_text('{"state": 2}\n')
        self.assertRefused(self.verify(manifest=out, msha=msha, out=self.base / "lr2.json"), "digest_mismatch")
        (self.dst / "state.json").unlink()
        self.assertRefused(self.verify(manifest=out, msha=msha, out=self.base / "lr3.json"), "loop_file_missing")

    def test_attempts_file_missing_or_changed_on_the_copy(self):
        # Expected (M4): loop_file_missing, then digest_mismatch, for the attempts file.
        (self.dst / "attempts.jsonl").write_text('{"session_id": "t"}\n')
        self.assertRefused(self.verify(), "digest_mismatch")
        (self.dst / "attempts.jsonl").unlink()
        self.assertRefused(self.verify(out=self.base / "r9.json"), "loop_file_missing")

    def test_loop_files_in_two_directories_are_refused(self):
        # Expected: loop_files_split, so a single --loop-dir covers both files.
        other = self.base / "other-loop"
        write(other / "state.json", "{}\n")
        rc = run("manifest", "--session", self.a, "--loop-attempts", self.attempts, "--loop-state", other / "state.json",
                 "--out", self.base / "split.json")
        self.assertRefused(rc, "loop_files_split")

    def test_verify_requires_loop_dir(self):
        # Expected: usage error (exit 2) without --loop-dir.
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            run("verify", "--manifest", self.manifest, "--manifest-sha256", self.msha, "--root", self.dst,
                "--out", self.base / "x.json")
        self.assertEqual(caught.exception.code, 2)

    # -- source versus copy (cold review M2) --

    def test_verify_refuses_the_source_tree(self):
        # Expected: copy_is_source when <root>/<copy_path> is the manifest's source_path, and no receipt.
        rc = run("verify", "--manifest", self.manifest, "--manifest-sha256", self.msha, "--root", self.src,
                 "--loop-dir", self.src, "--out", self.base / "src-receipt.json")
        self.assertRefused(rc, "copy_is_source")
        self.assertFalse((self.base / "src-receipt.json").exists())

    def test_verify_refuses_manifest_made_on_this_host(self):
        # Expected: copy_on_source_host for a manifest that records this host (re-running `manifest` on the copy).
        local = self.base / "local-manifest.json"
        rc, out, err = run_raw("manifest", "--session", self.ca, "--session", self.cb,
                               "--loop-attempts", self.attempts, "--no-loop-state", "--out", local)
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(json.loads(local.read_bytes())["host"], kit.host_name())
        self.assertRefused(self.verify(manifest=local, msha=sha(local)), "copy_on_source_host")

    def test_self_check_rehashes_source_and_writes_nothing(self):
        # Expected: exit 0 on the source tree with the same-host manifest rule off, no file created;
        # a changed source byte is refused digest_mismatch; --out is refused.
        before = sorted(p.name for p in self.base.iterdir())
        rc, out, err = run("verify", "--self-check", "--manifest", self.manifest, "--manifest-sha256", self.msha,
                           "--root", self.src, "--loop-dir", self.src)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("no receipt written", out)
        self.assertEqual(sorted(p.name for p in self.base.iterdir()), before)
        self.assertRefused(run("verify", "--self-check", "--manifest", self.manifest, "--manifest-sha256", self.msha,
                               "--root", self.src, "--loop-dir", self.src, "--out", self.base / "r.json"), "self_check_writes_no_receipt")
        p = self.a / "sources/runs/r1/data.bin"
        p.write_bytes(b"y" + p.read_bytes()[1:])
        self.assertRefused(run("verify", "--self-check", "--manifest", self.manifest, "--manifest-sha256", self.msha,
                               "--root", self.src, "--loop-dir", self.src), "digest_mismatch")

    def test_verify_needs_out_unless_self_check(self):
        # Expected: verify_out_missing.
        self.assertRefused(run("verify", "--manifest", self.manifest, "--manifest-sha256", self.msha,
                               "--root", self.dst, "--loop-dir", self.dst), "verify_out_missing")

    # -- manifest refusals --

    def manifest_run(self, *sessions, out=None, attempts=None):
        args = ["manifest"]
        for s in sessions:
            args += ["--session", s]
        return run(*args, "--loop-attempts", attempts or self.attempts, "--out", out or self.base / "m2.json")

    def test_manifest_refuses_symlink_inside_source(self):
        # Expected: refused symlink.
        (self.a / "sources/link").symlink_to(self.a / "harvest.json")
        self.assertRefused(self.manifest_run(self.a), "symlink")

    def test_manifest_refuses_symlinked_session_root(self):
        # Expected: refused symlink.
        link = self.base / "alias"
        link.symlink_to(self.a)
        self.assertRefused(self.manifest_run(link), "symlink")

    def test_manifest_refuses_symlinked_desk(self):
        # Expected: refused symlink for a desk folder that is a link.
        desk = Path(str(self.b) + ".desk")
        desk.rename(self.base / "real-desk")
        desk.symlink_to(self.base / "real-desk")
        self.assertRefused(self.manifest_run(self.b), "symlink")

    def test_manifest_refuses_fifo_loop_file(self):
        # Expected: refused not_regular_file; the FIFO open does not block.
        fifo = self.base / "attempts.fifo"
        os.mkfifo(fifo)
        self.assertRefused(self.manifest_run(self.a, attempts=fifo), "not_regular_file")

    def test_manifest_refuses_existing_out_before_reading(self):
        # Expected: refused out_exists even though the session does not exist.
        self.assertRefused(self.manifest_run(self.base / "absent", out=self.manifest), "out_exists")

    def test_write_refuses_out_created_after_check(self):
        # Expected: refused out_exists from the exclusive create, not only the early check.
        (self.base / "m2.json").write_text("{}")
        with mock.patch.object(kit.os.path, "lexists", return_value=False):
            self.assertRefused(self.manifest_run(self.a), "out_exists")

    def test_manifest_refuses_missing_session(self):
        # Expected: refused session_missing.
        self.assertRefused(self.manifest_run(self.base / "absent"), "session_missing")

    def test_manifest_refuses_repeated_session(self):
        # Expected: refused session_repeated.
        self.assertRefused(self.manifest_run(self.a, self.a), "session_repeated")

    def test_manifest_refuses_missing_pinned_file(self):
        # Expected: refused required_file_missing without the acceptance record.
        (self.a / "derived/b6-acceptance.json").unlink()
        self.assertRefused(self.manifest_run(self.a), "required_file_missing")

    def test_manifest_refuses_two_compression_logs(self):
        # Expected: refused compression_log_ambiguous with both an inside and an adjacent log.
        write(Path(str(self.a) + ".desk/compression.jsonl"), "{}\n")
        self.assertRefused(self.manifest_run(self.a), "compression_log_ambiguous")

    def test_manifest_refuses_stray_file_in_sources(self):
        # Expected (M1): unlisted_extra_file for a .DS_Store that Finder leaves in sources/.
        write(self.a / "sources/.DS_Store", "x")
        self.assertRefused(self.manifest_run(self.a), "unlisted_extra_file")

    def test_manifest_refuses_missing_listed_file(self):
        # Expected (M1): listed_file_missing when a SHA256SUMS row has neither the file nor its .zst.
        (self.a / "sources/monitor/clock.jsonl").unlink()
        self.assertRefused(self.manifest_run(self.a), "listed_file_missing")

    def test_manifest_refuses_row_present_plain_and_compressed(self):
        # Expected (M1): unlisted_extra_file when a row has both the plain file and its .zst.
        write(self.a / "sources/meter/stream-2.jsonl", "plain twin")
        self.assertRefused(self.manifest_run(self.a), "unlisted_extra_file")

    def test_copy_path_ambiguous(self):
        # Expected: refused copy_path_ambiguous when three trailing names still collide.
        x = mini_archive(self.base / "p/a/b", "archive")
        y = mini_archive(self.base / "q/a/b", "archive")
        self.assertRefused(self.manifest_run(x, y), "copy_path_ambiguous")

    # -- inputs --

    def test_inputs_digests_come_from_source_manifest(self):
        # Expected: exit 0; every pinned digest equals the SOURCE file's digest even after the copy is
        # changed post-verify (the kit never rehashes the copy for a pin); keys are absolute copy paths.
        self.verified()
        (self.ca / "harvest.json").write_text("{}\n")
        out = self.base / "run-inputs.json"
        rc, stdout, err = self.inputs(mapping_for(["b6-alpha-r1", "b6-beta-r1"]), out=out)
        self.assertEqual((rc, err), (0, ""))
        doc = json.loads(out.read_bytes())
        self.assertEqual(stdout.strip().rsplit("=", 1)[1], sha(out))
        self.assertEqual((doc["host"], doc["l9_audit"]), ("Air", "not_run"))
        self.assertEqual(doc["external"], {"loop_attempts": sha(self.attempts)})
        pin = doc["sessions"][str(self.ca)]
        self.assertEqual(pin["harvest_sha256"], sha(self.a / "harvest.json"))
        self.assertNotEqual(pin["harvest_sha256"], sha(self.ca / "harvest.json"))
        self.assertEqual(pin["sha256sums_sha256"], sha(self.a / "sources/SHA256SUMS"))
        self.assertEqual(pin["acceptance_sha256"], sha(self.a / "derived/b6-acceptance.json"))
        self.assertEqual(pin["files"], {n: sha(self.a / n) for n in
                                        ("derived/b6-acceptance.json", "derived/flags.jsonl", "withheld/spans.json")})
        self.assertEqual(pin["compression"], {"path": "compression.jsonl", "sha256": sha(self.a / "compression.jsonl")})
        desk = doc["sessions"][str(self.cb)]["compression"]
        self.assertEqual(desk, {"external_path": str(self.cb) + ".desk/compression.jsonl",
                                "sha256": sha(str(self.b) + ".desk/compression.jsonl"),
                                "relocations": {str(self.b): "."}})

    def test_list_names(self):
        # Expected: exit 0; SHA256SUMS rows as sources/... plus manifest-digested names; no content.
        self.verified()
        rc, out, err = run("inputs", *self.ia(),
                           "--list-names", "b6-alpha-r1")
        self.assertEqual((rc, err), (0, ""))
        names = out.splitlines()
        self.assertIn("sources/meter/stream-2.jsonl", names)
        self.assertIn("derived/flags.jsonl", names)
        # Exactly: 5 SHA256SUMS rows, the 3 emitted files, harvest.json and sources/SHA256SUMS.
        self.assertNotIn("compression.jsonl", names)
        self.assertEqual(sorted(names), sorted(["sources/" + n for n in (
            "meter/stream-1.jsonl", "meter/stream-2.jsonl", "monitor/contention.jsonl", "monitor/clock.jsonl",
            "runs/r1/data.bin")] + ["derived/b6-acceptance.json", "derived/flags.jsonl", "withheld/spans.json",
            "harvest.json", "sources/SHA256SUMS"]))

    def test_list_names_unknown_session(self):
        # Expected: refused session_unknown.
        self.verified()
        self.assertRefused(run("inputs", *self.ia(),
                               "--list-names", "nope"), "session_unknown")

    def test_inputs_arguments_missing(self):
        # Expected: refused inputs_arguments_missing without --mapping.
        self.verified()
        self.assertRefused(run("inputs", *self.ia(),
                               "--l9-audit", "not_run", "--out", self.base / "x.json"), "inputs_arguments_missing")

    def test_inputs_out_exists_before_mapping_read(self):
        # Expected: refused out_exists before the (absent) mapping is read.
        self.verified()
        out = self.base / "exists.json"
        out.write_text("{}")
        self.assertRefused(run("inputs", *self.ia(),
                               "--mapping", self.base / "absent.json", "--l9-audit", "not_run", "--out", out),
                           "out_exists")

    def test_mapping_path_not_in_sha256sums(self):
        # Expected: refused mapping_path_unlisted.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-beta-r1"]["copied_records"]["arm_host"] = ["sources/monitor/not-there.json"]
        self.assertRefused(self.inputs(m), "mapping_path_unlisted")

    def test_mapping_path_hashed_but_not_emitted(self):
        # Expected: refused mapping_path_unlisted for the inside desk log, which the manifest hashes but
        # does not emit in `files` and which is not a pinned file (RL-100).
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["copied_records"]["arm_host"] = ["compression.jsonl"]
        self.assertRefused(self.inputs(m), "mapping_path_unlisted")

    def test_mapping_may_cite_pinned_files(self):
        # Expected: exit 0 when copied records cite harvest.json and sources/SHA256SUMS (pinned files).
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["copied_records"]["attempt_history"] = ["harvest.json", "sources/SHA256SUMS"]
        rc, _, err = self.inputs(m)
        self.assertEqual((rc, err), (0, ""))

    def test_mapping_path_escapes(self):
        # Expected: refused path_invalid for '..'.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["contention_journal"] = "sources/../harvest.json"
        self.assertRefused(self.inputs(m), "path_invalid")

    def test_mapping_path_not_string(self):
        # Expected: refused path_invalid.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["meter_streams"] = [7]
        self.assertRefused(self.inputs(m), "path_invalid")

    def test_empty_required_family(self):
        # Expected: refused family_empty.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["copied_records"]["g10_history"] = []
        self.assertRefused(self.inputs(m), "family_empty")

    def test_missing_required_family(self):
        # Expected: refused family_set_invalid.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        del m["sessions"]["b6-alpha-r1"]["copied_records"]["monitor_cost"]
        self.assertRefused(self.inputs(m), "family_set_invalid")

    def test_meter_streams_empty(self):
        # Expected: refused meter_streams_empty.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["meter_streams"] = []
        self.assertRefused(self.inputs(m), "meter_streams_empty")

    def test_contention_journal_missing(self):
        # Expected: refused contention_journal_missing.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        del m["sessions"]["b6-alpha-r1"]["contention_journal"]
        self.assertRefused(self.inputs(m), "contention_journal_missing")

    def test_mapping_key_unknown(self):
        # Expected: refused mapping_key_unknown.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["files"] = {}
        self.assertRefused(self.inputs(m), "mapping_key_unknown")

    def test_mapping_session_mismatch(self):
        # Expected: refused mapping_session_mismatch.
        self.verified()
        self.assertRefused(self.inputs(mapping_for(["b6-alpha-r1"])), "mapping_session_mismatch")

    def test_relocation_conflict(self):
        # Expected: refused relocation_conflict when the person remaps the archive's own source path.
        self.verified()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-beta-r1"]["relocations"] = {str(self.b): "sources"}
        self.assertRefused(self.inputs(m), "relocation_conflict")

    def test_relocations_without_log(self):
        # Expected: refused relocations_without_log for a session that has no compression log.
        (self.a / "compression.jsonl").unlink()
        self.remanifest_and_verify()
        m = mapping_for(["b6-alpha-r1", "b6-beta-r1"])
        m["sessions"]["b6-alpha-r1"]["relocations"] = {"/old": "."}
        self.assertRefused(self.inputs(m), "relocations_without_log")

    def test_receipt_not_verified(self):
        # Expected: refused receipt_not_verified.
        self.verified()
        r = json.loads(self.receipt.read_bytes())
        r["verdict"] = "pending"
        bad = self.base / "receipt-pending.json"
        bad.write_text(json.dumps(r))
        self.assertRefused(self.inputs(mapping_for(["b6-alpha-r1", "b6-beta-r1"]), receipt=bad),
                           "receipt_not_verified")

    def test_receipt_for_other_manifest(self):
        # Expected: refused receipt_manifest_mismatch.
        self.verified()
        r = json.loads(self.receipt.read_bytes())
        r["manifest_sha256"] = "0" * 64
        bad = self.base / "receipt-other.json"
        bad.write_text(json.dumps(r))
        self.assertRefused(self.inputs(mapping_for(["b6-alpha-r1", "b6-beta-r1"]), receipt=bad),
                           "receipt_manifest_mismatch")

    def test_receipt_session_set_differs(self):
        # Expected: refused receipt_manifest_mismatch.
        self.verified()
        r = json.loads(self.receipt.read_bytes())
        del r["sessions"]["b6-beta-r1"]
        bad = self.base / "receipt-partial.json"
        bad.write_text(json.dumps(r))
        self.assertRefused(self.inputs(mapping_for(["b6-alpha-r1", "b6-beta-r1"]), receipt=bad),
                           "receipt_manifest_mismatch")

    def test_inputs_refuses_wrong_manifest_digest(self):
        # Expected (M3): manifest_digest_mismatch when --manifest-sha256 is not the manifest's digest.
        self.verified()
        args = self.ia()
        args[args.index("--manifest-sha256") + 1] = "0" * 64
        self.assertRefused(run("inputs", *args, "--list-names", "b6-alpha-r1"), "manifest_digest_mismatch")

    def test_inputs_refuses_wrong_receipt_digest(self):
        # Expected (M3): receipt_digest_mismatch when the receipt is not the file whose digest was carried out of band.
        self.verified()
        args = self.ia()
        args[args.index("--verify-receipt-sha256") + 1] = "0" * 64
        self.assertRefused(run("inputs", *args, "--list-names", "b6-alpha-r1"), "receipt_digest_mismatch")

    def test_inputs_requires_both_digests(self):
        # Expected (M3): argparse usage error (exit 2) when either out-of-band digest is omitted.
        self.verified()
        for flag in ("--manifest-sha256", "--verify-receipt-sha256"):
            args = self.ia()
            i = args.index(flag)
            del args[i:i + 2]
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                run("inputs", *args, "--list-names", "b6-alpha-r1")
            self.assertEqual(caught.exception.code, 2)

    def test_inputs_refuses_hand_written_receipt(self):
        # Expected (M3): a receipt with the right schema, verdict, manifest digest and root but nothing verify wrote
        # (empty session bodies) is refused receipt_invalid, even with its own digest supplied; the copy has a
        # changed source file that this receipt would have waved through.
        (self.ca / "sources/runs/r1/data.bin").write_bytes(b"changed")
        fake = self.base / "fake-receipt.json"
        fake.write_text(json.dumps({"schema": kit.RECEIPT_SCHEMA, "verdict": "verified", "manifest_sha256": self.msha,
                                    "root": str(self.dst), "sessions": {"b6-alpha-r1": {}, "b6-beta-r1": {}}}))
        self.assertRefused(run("inputs", *self.ia(receipt=fake), "--list-names", "b6-alpha-r1"), "receipt_invalid")

    def test_inputs_refuses_receipt_without_producer_or_with_other_counts(self):
        # Expected (M3): receipt_invalid for a copied verify receipt with the producer mark removed, and for one whose
        # file count differs from the manifest's.
        self.verified()
        good = json.loads(self.receipt.read_bytes())
        for name, edit in (("producer", lambda r: r.pop("produced_by")),
                           ("count", lambda r: r["sessions"]["b6-alpha-r1"].update(files=1))):
            r = json.loads(json.dumps(good))
            edit(r)
            bad = self.base / ("receipt-" + name + ".json")
            bad.write_text(json.dumps(r))
            self.assertRefused(run("inputs", *self.ia(receipt=bad), "--list-names", "b6-alpha-r1"), "receipt_invalid")

    def test_sha256sums_changed_after_verify(self):
        # Expected: refused sums_digest_mismatch when inputs reads the name column.
        self.verified()
        sums = self.ca / "sources/SHA256SUMS"
        sums.write_text(sums.read_text() + "0" * 64 + "  extra\n")
        self.assertRefused(self.inputs(mapping_for(["b6-alpha-r1", "b6-beta-r1"])), "sums_digest_mismatch")

    def test_repeated_basename_uses_two_names_and_exact_pins(self):
        # Expected: exit 0; copy paths '<id>/archive'; pins keyed by absolute copy path.
        src, dst = self.base / "rep-src", self.base / "rep-dst"
        x, y = mini_archive(src / "S1", "archive", log="adjacent"), mini_archive(src / "S2", "archive")
        manifest = self.base / "rep-manifest.json"
        rc, out, _ = run("manifest", "--session", x, "--session", y, "--loop-attempts", self.attempts,
                         "--out", manifest)
        self.assertEqual(rc, 0)
        self.assertEqual([s["copy_path"] for s in json.loads(manifest.read_bytes())["sessions"]],
                         ["S1/archive", "S2/archive"])
        shutil.copytree(src, dst, symlinks=True)
        shutil.copyfile(self.attempts, dst / "attempts.jsonl")
        receipt = self.base / "rep-receipt.json"
        rc, _, err = run("verify", "--manifest", manifest, "--manifest-sha256", out.strip().rsplit("=", 1)[1],
                         "--root", dst, "--loop-dir", dst, "--out", receipt)
        self.assertEqual((rc, err), (0, ""))
        mapping = self.base / "rep-mapping.json"
        mapping.write_text(json.dumps(mapping_for(["S1/archive", "S2/archive"])))
        doc = self.base / "rep-inputs.json"
        rc, _, err = run("inputs", "--manifest", manifest, "--manifest-sha256", sha(manifest), "--verify-receipt", receipt,
                         "--verify-receipt-sha256", sha(receipt), "--mapping", mapping, "--l9-audit", "completed", "--out", doc)
        self.assertEqual((rc, err), (0, ""))
        pins = json.loads(doc.read_bytes())["sessions"]
        self.assertEqual(set(pins), {str(dst / "S1/archive"), str(dst / "S2/archive")})
        self.assertEqual(pins[str(dst / "S1/archive")]["compression"]["external_path"],
                         str(dst / "S1/archive.desk/compression.jsonl"))

    def test_rsync_relative_form_lands_verifiable_layout(self):
        # Expected (cold review H1): the runbook's `cd <sessions> && rsync -aR <id>/archive [<id>/archive.desk] <dest>/`
        # lands <dest>/<id>/archive[.desk], and verify on that tree exits 0 (the absolute-path form did not).
        if shutil.which("rsync") is None:
            self.skipTest("no rsync")
        src, dst = self.base / "rs-src", self.base / "rs-dst"
        x, y = mini_archive(src / "S1", "archive", log="adjacent"), mini_archive(src / "S2", "archive")
        manifest = self.base / "rs-manifest.json"
        rc, out, _ = run("manifest", "--session", x, "--session", y, "--loop-attempts", self.attempts,
                         "--out", manifest)
        self.assertEqual(rc, 0)
        dst.mkdir()
        for session in ("S1", "S2"):
            parts = [session + "/archive"] + ([session + "/archive.desk"] if (src / session / "archive.desk").is_dir() else [])
            done = subprocess.run(["rsync", "-aR", *parts, str(dst) + "/"], cwd=src, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(sorted(p.name for p in dst.iterdir()), ["S1", "S2"])
        done = subprocess.run(["rsync", "-a", str(self.attempts), str(dst) + "/"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        rc, _, err = run("verify", "--manifest", manifest, "--manifest-sha256", out.strip().rsplit("=", 1)[1],
                         "--root", dst, "--loop-dir", dst, "--out", self.base / "rs-receipt.json")
        self.assertEqual((rc, err), (0, ""))


class MultiChunk(unittest.TestCase):
    """Files larger than the kit's read chunk (cold review M5): a digest of the first chunk alone must not pass."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="b6-custody-big-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.src, self.dst = self.base / "src", self.base / "dst"
        self.a = mini_archive(self.src, "b6-big-r1", big=True)
        attempts = self.src / "attempts.jsonl"
        write(attempts, '{"loop": 1}\n')
        self.manifest = self.base / "manifest.json"
        rc, out, err = run("manifest", "--session", self.a, "--loop-attempts", attempts, "--out", self.manifest)
        self.assertEqual((rc, err), (0, ""))
        self.msha = out.strip().rsplit("=", 1)[1]
        shutil.copytree(self.src, self.dst, symlinks=True)
        self.ca = self.dst / "b6-big-r1"

    def verify(self, name="receipt.json"):
        return run("verify", "--manifest", self.manifest, "--manifest-sha256", self.msha, "--root", self.dst,
                   "--loop-dir", self.dst, "--out", self.base / name)

    def test_helpers_hash_every_chunk(self):
        # Expected: hash_file and hash_zst equal hashlib over the whole 3 MiB + 5 byte content.
        data = big_bytes(b"plain")
        self.assertGreater(len(data), 3 * kit.CHUNK)
        self.assertEqual(kit.hash_file(self.a / "sources/runs/r1/big.bin"), (hashlib.sha256(data).hexdigest(), len(data)))
        self.assertEqual(kit.hash_zst(self.a / "sources/runs/r1/big-z.bin.zst", shutil.which("zstd")),
                         hashlib.sha256(big_bytes(b"packed")).hexdigest())

    def test_clean_multichunk_copy_verifies(self):
        # Expected: exit 0 with one compressed row among the big files.
        rc, _, err = self.verify()
        self.assertEqual((rc, err), (0, ""))

    def test_last_byte_flipped_in_plain_multichunk_file(self):
        # Expected: digest_mismatch (the changed byte is past the first chunk).
        p = self.ca / "sources/runs/r1/big.bin"
        data = bytearray(p.read_bytes())
        data[-1] ^= 1
        p.write_bytes(bytes(data))
        self.assertRefused(self.verify())

    def test_last_byte_flipped_in_compressed_multichunk_file(self):
        # Expected: digest_mismatch (a valid frame whose decompressed stream differs past the first chunk).
        data = bytearray(big_bytes(b"packed"))
        data[-1] ^= 1
        plain = self.base / "tampered.bin"
        plain.write_bytes(bytes(data))
        subprocess.run(["zstd", "-q", "-1", "-T1", "-f", str(plain), "-o", str(self.ca / "sources/runs/r1/big-z.bin.zst")],
                       check=True)
        self.assertRefused(self.verify())

    def assertRefused(self, result, code="digest_mismatch"):
        rc, out, err = result
        self.assertEqual((rc, err.strip()), (4, "refused: " + code))



class NoContentLeak(unittest.TestCase):
    def test_no_output_contains_session_content(self):
        # Expected: the marker planted in a meter stream (plain and compressed), harvest.json and the
        # derived record appears in no stdout, stderr or file the kit writes, on success or refusal.
        with tempfile.TemporaryDirectory(prefix="b6-custody-leak-") as tmp:
            base = Path(tmp).resolve()
            src, dst = base / "src", base / "dst"
            a = mini_archive(src, "b6-alpha-r1", marker=True)
            write(a / "derived/flags.jsonl", json.dumps({"code": MARKER}) + "\n")
            attempts = src / "attempts.jsonl"
            write(attempts, '{"loop": 1}\n')
            self.assertIn(MARKER.encode(), (a / "harvest.json").read_bytes())
            self.assertIn(MARKER.encode(), (a / "sources/meter/stream-1.jsonl").read_bytes())
            streams = []
            manifest, receipt, doc = base / "m.json", base / "r.json", base / "i.json"
            streams.append(run("manifest", "--session", a, "--loop-attempts", attempts, "--out", manifest))
            msha = streams[-1][1].strip().rsplit("=", 1)[1]
            shutil.copytree(src, dst, symlinks=True)
            streams.append(run("verify", "--manifest", manifest, "--manifest-sha256", msha, "--root", dst,
                               "--loop-dir", dst, "--out", receipt))
            pins = ["--manifest", manifest, "--manifest-sha256", msha, "--verify-receipt", receipt,
                    "--verify-receipt-sha256", sha(receipt)]
            streams.append(run("inputs", *pins, "--list-names", "b6-alpha-r1"))
            mapping = base / "map.json"
            mapping.write_text(json.dumps(mapping_for(["b6-alpha-r1"])))
            streams.append(run("inputs", *pins, "--mapping", mapping,
                               "--l9-audit", "not_run", "--out", doc))
            self.assertEqual([s[0] for s in streams], [0, 0, 0, 0])
            # Refusals while reading planted files: a flipped byte and a corrupt stream.
            p = dst / "b6-alpha-r1/sources/meter/stream-1.jsonl"
            p.write_bytes(p.read_bytes().replace(b"PLANTED", b"PLANTEX"))
            streams.append(run("verify", "--manifest", manifest, "--manifest-sha256", msha, "--root", dst,
                               "--loop-dir", dst, "--out", base / "r2.json"))
            self.assertEqual(streams[-1][0], 4)
            outputs = b"".join((s[1] + s[2]).encode() for s in streams)
            outputs += b"".join(f.read_bytes() for f in (manifest, receipt, doc))
            self.assertNotIn(MARKER.encode(), outputs)
            self.assertNotIn(b"PLANTEX", outputs)
            self.assertNotIn(b"PLANTED", outputs)


class EndToEnd(unittest.TestCase):
    """Seat-7 production-shaped synthetic block (ten archives) through the kit and the recompute."""

    @classmethod
    def setUpClass(cls):
        if os.environ.get("JW_B5_SYNTHETIC_ONLY") != "1":
            raise unittest.SkipTest("needs JW_B5_SYNTHETIC_ONLY=1")
        from tests.independent_recompute.support_b6_production import production_block, b6
        cls.b6 = b6
        cls.tmp = tempfile.TemporaryDirectory(prefix="b6-custody-e2e-")
        base = cls.base = Path(cls.tmp.name).resolve()
        cls.archives, cls.attempts, cls.document = production_block(base / "src")
        cls.fixture = cls.recompute(cls.archives, cls.attempts, cls.document, "fixture")
        manifest = base / "manifest.json"
        cls.manifest_run = run("manifest", *[x for a in cls.archives for x in ("--session", a)],
                               "--loop-attempts", cls.attempts, "--out", manifest)
        msha = cls.manifest_run[1].strip().rsplit("=", 1)[1]
        copy = base / "copy"
        copy.mkdir()
        for a in cls.archives:
            shutil.copytree(a, copy / a.name, symlinks=True)
        attempts = copy / "attempts.jsonl"
        shutil.copyfile(cls.attempts, attempts)
        receipt = base / "receipt.json"
        cls.verify_run = run("verify", "--manifest", manifest, "--manifest-sha256", msha, "--root", copy,
                             "--loop-dir", copy, "--out", receipt)
        sealed = json.loads(cls.document.read_bytes())["sessions"]
        mapping = {"sessions": {name: {k: pin[k] for k in ("meter_streams", "contention_journal",
                                                             "clock_journal", "copied_records") if k in pin}
                                for name, pin in sealed.items()}}
        (base / "mapping.json").write_text(json.dumps(mapping))
        cls.kit_doc = base / "run-inputs.json"
        cls.inputs_run = run("inputs", "--manifest", manifest, "--manifest-sha256", msha, "--verify-receipt", receipt,
                             "--verify-receipt-sha256", sha(receipt), "--mapping", base / "mapping.json", "--l9-audit", "not_run", "--out", cls.kit_doc)
        cls.kit = cls.recompute([copy / a.name for a in cls.archives], attempts, cls.kit_doc, "kit")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def recompute(cls, archives, attempts, document, stem):
        r, p = cls.base / (stem + "-restricted.json"), cls.base / (stem + "-public.json")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cls.b6.main(["block", *[x for a in archives for x in ("--session", str(a))], "--closed",
                              "--loop-attempts", str(attempts), "--inputs", str(document),
                              "--inputs-sha256", sha(document), "--workers", "1",
                              "--restricted-out", str(r), "--public-out", str(p)])
        return {"rc": rc, "stderr": err.getvalue(), "restricted": r.read_bytes() if r.exists() else b"",
                "public": p.read_bytes() if p.exists() else b""}

    def test_kit_steps_exit_zero(self):
        # Expected: manifest, verify (2 compressed rows in the first archive) and inputs all exit 0.
        self.assertEqual([x[0] for x in (self.manifest_run, self.verify_run, self.inputs_run)], [0, 0, 0])
        receipt = json.loads((self.base / "receipt.json").read_bytes())
        self.assertEqual(receipt["totals"]["sums_rows_compressed"], 2)
        self.assertEqual(len(receipt["sessions"]), 10)

    def test_recompute_on_kit_inputs_agrees(self):
        # Expected: both runs exit 0 with the comparator agreeing (option_c pass, no stop).
        for run_ in (self.fixture, self.kit):
            self.assertEqual((run_["rc"], run_["stderr"]), (0, ""))
            restricted = json.loads(run_["restricted"])
            self.assertIs(restricted["block"]["option_c"]["pass"], True)
            self.assertIs(restricted["comparison_stopped"], False)
            self.assertEqual(restricted["inputs"]["host"], "Air")

    def test_public_output_identical_up_to_run_input_digest(self):
        # Expected: the restricted outputs differ ONLY in inputs.run_inputs_sha256 (two different
        # run-input documents by construction), so the public outputs differ only in restricted_sha256;
        # with those two fields removed both are byte-identical.
        f, k = json.loads(self.fixture["restricted"]), json.loads(self.kit["restricted"])
        self.assertNotEqual(f["inputs"].pop("run_inputs_sha256"), k["inputs"].pop("run_inputs_sha256"))
        self.assertEqual(json.dumps(f, sort_keys=True).encode(), json.dumps(k, sort_keys=True).encode())
        fp, kp = json.loads(self.fixture["public"]), json.loads(self.kit["public"])
        fp.pop("restricted_sha256"), kp.pop("restricted_sha256")
        self.assertEqual(json.dumps(fp, sort_keys=True).encode(), json.dumps(kp, sort_keys=True).encode())
        stripped = [self.fixture["public"].replace(json.loads(self.fixture["public"])["restricted_sha256"].encode(), b""),
                    self.kit["public"].replace(json.loads(self.kit["public"])["restricted_sha256"].encode(), b"")]
        self.assertEqual(stripped[0], stripped[1])


if __name__ == "__main__":
    unittest.main()
