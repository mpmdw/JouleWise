"""RL-194: the look's custody inputs are admitted by content address. Every byte here is generated; no custody,
energy, meter or restricted file is read."""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import unittest.mock

from joulewise.cadence_looks import custody_pins as P

COMMIT = "b4b6aeb192da60d895a7529311b06599efff5be4"
FILES = {
    "runner_receipt.json": b'{"roster": ["L001"]}\n',
    "legs/L001/leg_record.json": b'{"result": {"bundle": "run"}}\n',
    "legs/L001/runtime/run/events.jsonl": b'{"event_type": "token"}\n',
    "legs/L001/runtime/run/power_trace.csv": b"synthetic trace bytes\n",
    "hazards/meter/stream-0001.jsonl": b"synthetic stream bytes\n",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def offload_manifest(files):
    return "".join(f"{sha(data)}  ./{name}\n" for name, data in files.items()).encode()


def files_for(sid):
    """One span's files: the shared set and one that differs by span, so no two spans share an offload manifest."""
    return {**FILES, "soak/soak_reference.json": json.dumps({"span": sid}).encode() + b"\n"}


def write_span(root, sid, files=None):
    for name, data in (files or files_for(sid)).items():
        path = Path(root) / sid / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def pins(spans=("dev-01-s01",), files=None, check=317):
    return {"schema": P.SCHEMA, "spans": [
        P.span_pins(sid, offload_manifest(files or files_for(sid)),
                    {name: len(data) for name, data in (files or files_for(sid)).items()},
                    runner_commit=COMMIT, close_item=check + 1, check_item=check + index)
        for index, sid in enumerate(spans)]}


def run_state(doc, abbreviated=False):
    """A RUN_STATE whose Check items name each span's offload manifest digest, newest item first."""
    items = []
    for span in doc["spans"]:
        digest = span["offload_manifest_sha256"]
        named = f"{digest[:8]}…{digest[-3:]}" if abbreviated else digest
        items.append(f"{span['check_item']}. **Check of {span['span_id']}.** Offload manifest `{named}` "
                     f"({len(span['files'])} files).\n\n1. a sub-step\n2. another\n")
    return "# State\n\n" + "\n".join(reversed(items))


class PinList(unittest.TestCase):
    def test_a_span_s_pins_are_its_offload_manifest_s_lines_and_rebuild_its_digest(self):
        doc = pins()
        span = doc["spans"][0]
        self.assertEqual(P.pin_list_problems(doc, complete=True), [])
        files = files_for("dev-01-s01")
        self.assertEqual(P.offload_manifest_bytes(span), offload_manifest(files))
        self.assertEqual(span["offload_manifest_sha256"], sha(offload_manifest(files)))
        self.assertEqual([entry["path"] for entry in span["files"]], list(files))
        self.assertEqual(span["files"][0], {"path": "runner_receipt.json", "sha256": sha(FILES["runner_receipt.json"]),
                                            "size": len(FILES["runner_receipt.json"])})

    def test_a_pin_not_chained_to_the_offload_manifest_is_found_from_the_pin_list_alone(self):
        """A changed, added, dropped or reordered pin no longer rebuilds the digest the span names."""
        changes = {
            "a changed digest": lambda s: s["files"][1].update(sha256="0" * 64),
            "a changed path": lambda s: s["files"][1].update(path="legs/L001/leg_record.json.bak"),
            "an added pin": lambda s: s["files"].append({"path": "extra.bin", "sha256": "1" * 64, "size": 1}),
            "a dropped pin": lambda s: s["files"].pop(),
            "a reordered pin": lambda s: s["files"].reverse(),
            "another offload manifest": lambda s: s.update(offload_manifest_sha256="2" * 64),
        }
        for label, change in changes.items():
            doc = pins()
            change(doc["spans"][0])
            with self.subTest(label):
                self.assertTrue(any("not the lines of the offload manifest" in problem
                                    for problem in P.pin_list_problems(doc, complete=True)))
        doc = pins()
        doc["spans"][0]["files"][0]["size"] += 1               # a size is outside the chain: the bytes check it
        self.assertEqual(P.pin_list_problems(doc, complete=True), [])

    def test_the_pin_list_s_own_shape_is_closed(self):
        for label, change in {
            "an unknown span member": lambda d: d["spans"][0].update(note="x"),
            "an unknown file member": lambda d: d["spans"][0]["files"][0].update(mode=0),
            "an unknown top member": lambda d: d.update(extra=1),
            "another schema": lambda d: d.update(schema="other"),
            "a span twice": lambda d: d["spans"].append(copy.deepcopy(d["spans"][0])),
            "a path that climbs": lambda d: d["spans"][0]["files"][0].update(path="../x"),
            "an absolute path": lambda d: d["spans"][0]["files"][0].update(path="/etc/passwd"),
            "a path twice": lambda d: d["spans"][0]["files"].append(copy.deepcopy(d["spans"][0]["files"][0])),
            "a short commit": lambda d: d["spans"][0].update(runner_commit="b4b6aeb19"),
            "a boolean size": lambda d: d["spans"][0]["files"][0].update(size=True),
            "a text item number": lambda d: d["spans"][0].update(check_item="317"),
            "no file": lambda d: d["spans"][0].update(files=[]),
        }.items():
            doc = pins()
            change(doc)
            with self.subTest(label):
                self.assertTrue(P.pin_list_problems(doc, complete=True))
        empty = {"schema": P.SCHEMA, "spans": []}
        self.assertEqual(P.pin_list_problems(empty, complete=False), [])         # a draft may still be unfilled
        self.assertTrue(P.pin_list_problems(empty, complete=True))

    def test_an_offload_manifest_that_its_lines_do_not_rebuild_is_refused_at_pinning(self):
        sizes = {name: len(data) for name, data in FILES.items()}
        raw = offload_manifest(FILES)
        for label, bad in {"no final line feed": raw[:-1], "CRLF": raw.replace(b"\n", b"\r\n"),
                           "a blank line": raw + b"\n", "one space": raw.replace(b"  ./", b" ./", 1),
                           "no ./": raw.replace(b"  ./", b"  ", 1), "a path twice": raw + raw.splitlines(True)[0],
                           "empty": b"", "a path that climbs": raw + b"0" * 64 + b"  ./../x\n"}.items():
            with self.subTest(label), self.assertRaises(P.PinRefusal):
                P.span_pins("dev-01-s01", bad, sizes, runner_commit=COMMIT, close_item=318, check_item=317)
        with self.assertRaisesRegex(P.PinRefusal, "listed but absent"):
            P.span_pins("dev-01-s01", raw, {k: v for k, v in list(sizes.items())[1:]}, runner_commit=COMMIT,
                        close_item=318, check_item=317)
        with self.assertRaisesRegex(P.PinRefusal, "present but unlisted"):
            P.span_pins("dev-01-s01", raw, {**sizes, "extra": 1}, runner_commit=COMMIT, close_item=318, check_item=317)

    def test_the_pin_file_is_one_strict_json_document(self):
        raw = json.dumps(pins()).encode()
        self.assertEqual(P.load_pin_list(raw), pins())
        for label, bad in {"a duplicate member": raw.replace(b'{"schema"', b'{"schema": "x", "schema"', 1),
                           "not JSON": b"{", "not UTF-8": b"\xff", "a second document": raw + raw}.items():
            with self.subTest(label), self.assertRaises(P.PinRefusal):
                P.load_pin_list(bad)


class CheckChain(unittest.TestCase):
    def test_each_span_s_check_item_names_its_offload_manifest(self):
        doc = pins(("dev-01-s01", "dev-01-s03"))
        for abbreviated in (False, True):
            text = run_state(doc, abbreviated)
            self.assertEqual(P.check_chain_problems(doc, text), [])
            self.assertEqual(set(P.chain_link(doc, text).values()), {"abbreviated" if abbreviated else "full"})

    def test_a_pin_not_chained_to_its_check_is_found(self):
        doc = pins(("dev-01-s01", "dev-01-s03"))
        text = run_state(doc)
        cases = {
            "the Check names another digest": text.replace(doc["spans"][0]["offload_manifest_sha256"], "0" * 64),
            "the digest is in another item only": text.replace(
                f"{doc['spans'][0]['check_item']}. **Check", "999. **Check"),
            "no such item": text.replace(f"{doc['spans'][1]['check_item']}. **", "x. **"),
            "the item twice": text + text,
            "an abbreviation of another digest": text.replace(
                doc["spans"][0]["offload_manifest_sha256"], "00000000…000"),
            "an abbreviation too short to bind": text.replace(
                doc["spans"][0]["offload_manifest_sha256"], doc["spans"][0]["offload_manifest_sha256"][:7] + "…"),
        }
        for label, changed in cases.items():
            with self.subTest(label):
                self.assertTrue(P.check_chain_problems(doc, changed))
        moved = copy.deepcopy(doc)
        moved["spans"][0]["check_item"] = doc["spans"][1]["check_item"]        # points at the other span's Check
        self.assertTrue(P.check_chain_problems(moved, text))

    def test_an_abbreviation_binds_when_every_printed_character_matches(self):
        """RL-194a section 2: prefix and suffix exactly as the Check prints them."""
        doc = pins()
        span = doc["spans"][0]
        digest, number = span["offload_manifest_sha256"], span["check_item"]
        item = lambda printed: f"{number}. **Check.** enc sha256 `00000000…000`, manifest `{printed}` (5 files)\n"
        other = "0" if digest[-1] != "0" else "1"
        for printed, form in ((digest, "full"), (f"{digest[:8]}…{digest[-3:]}", "abbreviated"),
                              (f"{digest[:8]}...{digest[-7:]}", "abbreviated"), (f"{digest[:8]}…", "abbreviated"),
                              (f"{digest[:5]}…{digest[-3:]}", "abbreviated"),
                              (f"{digest[:7]}{other if digest[7] != other else 'f'}…{digest[-3:]}", "absent"),
                              (f"{digest[:8]}…{digest[-3:-1]}{other}", "absent"),
                              (f"{digest[:4]}…{digest[-3:]}", "absent"),          # seven digits printed: too few
                              (digest[:20], "absent")):                           # a bare prefix is not an abbreviation
            with self.subTest(printed=printed):
                got = P.check_binding(span, item(printed))
                self.assertEqual(got["form"], form)
                self.assertEqual(got["as_printed"], printed if form != "absent" else None)
                self.assertEqual(got["check_item"], number)
                self.assertEqual(bool(P.check_chain_problems(doc, item(printed))), form == "absent")

    def test_an_item_runs_from_its_head_to_the_next_item_s_head(self):
        text = "320. **Later.** x\n\n3. sub-step with 317. inside\n\n317. **Check.** digest here\n1. step\n\n316. **Earlier.** y\n"
        self.assertEqual(P.run_state_item(text, 317), "317. **Check.** digest here\n1. step\n\n")
        self.assertIsNone(P.run_state_item(text, 3))
        self.assertIsNone(P.run_state_item(text, 999))


TRACE = "legs/L001/runtime/run/power_trace.csv"
STREAM = "hazards/meter/stream-0001.jsonl"
RECEIPT = "runner_receipt.json"
RECORD = "legs/L001/leg_record.json"
VERIFIER = Path(__file__).resolve().parents[2] / "scripts/cadence_look_verify_inputs.py"


class _Custody(unittest.TestCase):
    SPANS = ("dev-01-s01", "dev-01-s03")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pins-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "custody"
        for sid in self.SPANS:
            write_span(self.root, sid)
        self.doc = pins(self.SPANS)
        self.pin_file = Path(self.tmp.name) / "pins.json"
        self.pin_file.write_text(json.dumps(self.doc))

    def faults(self):
        """label -> (change to the custody, the path the refusal names, the verifier's word for it)."""
        s1, s3 = self.root / "dev-01-s01", self.root / "dev-01-s03"

        def flip(path):
            data = path.read_bytes()
            path.write_bytes(bytes([data[0] ^ 1]) + data[1:])

        def exchange(a, b):
            x, y = a.read_bytes(), b.read_bytes()
            a.write_bytes(y)
            b.write_bytes(x)

        def link(path):
            kept = Path(self.tmp.name) / "kept"
            path.rename(kept)                       # the link resolves to the very bytes that are pinned
            path.symlink_to(kept, target_is_directory=kept.is_dir())
        return {
            "a changed stream (one bit, same length)": (lambda: flip(s3 / TRACE), f"dev-01-s03/{TRACE}", "mismatch"),
            "a changed operational file": (lambda: flip(s1 / RECEIPT), f"dev-01-s01/{RECEIPT}", "mismatch"),
            "a stream of another length": (lambda: (s1 / STREAM).write_bytes((s1 / STREAM).read_bytes() + b" "),
                                           f"dev-01-s01/{STREAM}", "mismatch"),
            "a missing stream": ((s1 / STREAM).unlink, f"dev-01-s01/{STREAM}", "missing"),
            "a missing operational file": ((s3 / RECORD).unlink, f"dev-01-s03/{RECORD}", "missing"),
            "an extra stream": (lambda: (s1 / "hazards/meter/stream-0002.jsonl").write_bytes(b"x"),
                                "dev-01-s01/hazards/meter/stream-0002.jsonl", "not_pinned"),
            "two streams exchanged": (lambda: exchange(s1 / TRACE, s1 / STREAM), f"dev-01-s01/{STREAM}", "mismatch"),
            "a symlinked stream": (lambda: link(s1 / TRACE), f"dev-01-s01/{TRACE}", "symlink"),
            "a symlinked directory": (lambda: link(s1 / "hazards"), "dev-01-s01/hazards", "symlink"),
            "a symlinked span": (lambda: link(s3), "dev-01-s03", "symlink"),
        }

    def run_verifier(self, out=None):
        import subprocess
        import sys
        out = out or Path(self.tmp.name) / "verification.json"
        argv = [sys.executable, "-I", "-B", str(VERIFIER), "--pins", str(self.pin_file), "--pins-sha256",
                sha(self.pin_file.read_bytes()), "--out", str(out)]
        for sid in self.SPANS:
            argv += ["--span", f"{sid}={self.root / sid}"]
        done = subprocess.run(argv, capture_output=True, text=True)
        return done, (json.loads(out.read_bytes()) if out.exists() else None)


class Verifier(_Custody):
    """RL-194a section 1: the separate hash-only process that runs first."""

    def test_it_passes_the_pinned_copy_and_writes_words_and_hashes_only(self):
        done, result = self.run_verifier()
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))
        self.assertEqual(set(result), {"schema", "result", "files"})
        self.assertEqual((result["schema"], result["result"]), (P.VERIFICATION_SCHEMA, "pass"))
        self.assertEqual(len(result["files"]), sum(len(files_for(sid)) for sid in self.SPANS))
        for row in result["files"]:
            self.assertEqual(set(row), {"span_id", "path", "pinned", "observed", "state"})
            self.assertEqual((row["state"], row["observed"]), ("match", row["pinned"]))
        self.assertEqual(P.verification_problems(self.doc, result), [])

        def leaves(node):
            if isinstance(node, dict):
                for value in node.values():
                    yield from leaves(value)
            elif isinstance(node, list):
                for value in node:
                    yield from leaves(value)
            else:
                yield node
        self.assertTrue(all(isinstance(leaf, str) or leaf is None for leaf in leaves(result)))   # no size, count, float

    def test_it_holds_no_decoder_and_imports_no_look_code(self):
        import ast
        tree = ast.parse(VERIFIER.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported, {"hashlib", "json", "os", "stat", "sys"})

    def test_each_fault_fails_with_the_path_and_both_digests(self):
        for label, (change, named, word) in self.faults().items():
            for sid in self.SPANS:
                shutil.rmtree(self.root / sid, ignore_errors=True)
                (self.root / sid).unlink(missing_ok=True)
                write_span(self.root, sid)
            shutil.rmtree(Path(self.tmp.name) / "kept", ignore_errors=True)
            (Path(self.tmp.name) / "kept").unlink(missing_ok=True)
            change()
            done, result = self.run_verifier()
            with self.subTest(label):
                self.assertEqual((done.returncode, result["result"]), (1, "fail"))
                bad = [row for row in result["files"] if row["state"] != "match"]
                self.assertTrue(any(f"{row['span_id']}/{row['path']}".startswith(named) and row["state"] == word
                                    for row in bad), bad)
                for row in bad:
                    self.assertIn(row["state"], ("mismatch", "missing", "not_pinned", "symlink"))
                    if row["state"] == "mismatch":
                        self.assertNotEqual(row["observed"], row["pinned"])
                        self.assertRegex(row["observed"], "^[0-9a-f]{64}$")
                    else:
                        self.assertIsNone(row["observed"])            # a missing, linked or unpinned file is not read
                problems = P.verification_problems(self.doc, result)
                self.assertTrue(problems and problems[0].startswith(named.split("/")[0]), problems)

    def test_it_runs_only_as_asked(self):
        import subprocess
        import sys
        base = [sys.executable, "-I", "-B", str(VERIFIER)]
        spans = [arg for sid in self.SPANS for arg in ("--span", f"{sid}={self.root / sid}")]
        out = Path(self.tmp.name) / "o.json"
        good = ["--pins", str(self.pin_file), "--pins-sha256", sha(self.pin_file.read_bytes()), "--out", str(out)]
        for label, argv in {"another pin list digest": [*good[:3], "0" * 64, *good[4:], *spans],
                            "a span the pins do not name": [*good, *spans, "--span", f"other={self.root}"],
                            "a pinned span not named": [*good, *spans[:2]],
                            "an unknown option": [*good, *spans, "--decode", "x"]}.items():
            with self.subTest(label):
                self.assertEqual(subprocess.run(base + argv, capture_output=True).returncode, 2)
                self.assertFalse(out.exists())

    def test_a_result_that_is_not_the_whole_pin_list_passing_is_refused_by_the_stage(self):
        _, result = self.run_verifier()
        changes = {
            "a row dropped": lambda r: r["files"].pop(),
            "a row for another path": lambda r: r["files"][0].update(path="other.json"),
            "a pass that lists a mismatch": lambda r: r["files"][0].update(observed="0" * 64, state="mismatch"),
            "a fail with every row matching": lambda r: r.update(result="fail"),
            "a row with a size": lambda r: r["files"][0].update(size=3),
            "another schema": lambda r: r.update(schema="x"),
        }
        for label, change in changes.items():
            changed = json.loads(json.dumps(result))
            change(changed)
            with self.subTest(label):
                self.assertTrue(P.verification_problems(self.doc, changed))


class StageAct(_Custody):
    """The stage's own act: each span directory by name, and the operational bytes it parses. No stream is opened."""

    def custody(self, doc=None, roster=None, streams="pass"):
        return P.PinnedCustody(doc or self.doc, roster or self.SPANS, lambda sid: self.root / sid, streams=streams)

    def test_it_reads_the_operational_files_once_and_opens_no_stream(self):
        for sid in self.SPANS:                                   # a stream that cannot be opened is still admitted
            for name in (TRACE, STREAM):
                os.chmod(self.root / sid / name, 0)
        try:
            custody = self.custody()
            count, total = custody.verify()
        finally:
            for sid in self.SPANS:
                for name in (TRACE, STREAM):
                    os.chmod(self.root / sid / name, 0o600)
        operational = [name for name in files_for("dev-01-s01") if P.is_operational_path(name)]
        self.assertEqual(sorted(operational), sorted([RECEIPT, RECORD, "legs/L001/runtime/run/events.jsonl",
                                                      "soak/soak_reference.json"]))
        self.assertEqual(count, len(operational) * len(self.SPANS))
        self.assertEqual(total, sum(len(files_for(sid)[name]) for sid in self.SPANS for name in operational))
        self.assertEqual(sorted(rel for _, rel in custody._bytes), sorted(operational * len(self.SPANS)))

    def test_each_fault_the_stage_itself_can_see_refuses_before_anything_is_served(self):
        seen_by_stage = {"a changed operational file": "its bytes are not its pin",
                         "a missing stream": "a pinned file is missing",
                         "a missing operational file": "a pinned file is missing",
                         "an extra stream": "a file that is not pinned",
                         "a symlinked stream": "a symlink", "a symlinked directory": "a symlink",
                         "a symlinked span": "the span directory is a symlink"}
        for label, (change, named, _) in self.faults().items():
            for sid in self.SPANS:
                shutil.rmtree(self.root / sid, ignore_errors=True)
                (self.root / sid).unlink(missing_ok=True)
                write_span(self.root, sid)
            shutil.rmtree(Path(self.tmp.name) / "kept", ignore_errors=True)
            (Path(self.tmp.name) / "kept").unlink(missing_ok=True)
            change()
            custody = self.custody()
            with self.subTest(label):
                if label in seen_by_stage:
                    with self.assertRaisesRegex(P.PinRefusal, named.replace(".", r"\.") + ".*" + seen_by_stage[label]):
                        custody.verify()
                else:                       # a stream's bytes are the verifier process's to check, never the stage's
                    custody.verify()
                self.assertEqual(custody.opened, [])

    def test_the_pins_name_exactly_the_roster_s_spans(self):
        for roster in (("dev-01-s01",), (*self.SPANS, "dev-02-s02"), ("dev-01-s01", "dev-01-s01")):
            with self.subTest(roster=roster), self.assertRaisesRegex(P.PinRefusal, "not the same spans"):
                self.custody(roster=roster)
        shutil.rmtree(self.root / "dev-01-s03")
        with self.assertRaisesRegex(P.PinRefusal, "dev-01-s03: no span directory"):
            self.custody().verify()


class GuardedReads(_Custody):
    SPANS = ("dev-01-s01",)

    def admitted(self, streams):
        custody = P.PinnedCustody(self.doc, self.SPANS, lambda sid: self.root / sid, streams=streams)
        custody.verify()
        return custody

    def setUp(self):
        super().setUp()
        self.span = self.root / "dev-01-s01"

    def test_the_operational_bytes_parsed_are_the_bytes_hashed(self):
        """After the stage's act an operational file is never read from disk again."""
        for streams in ("pass", "verify"):
            write_span(self.root, "dev-01-s01")
            custody = self.admitted(streams)
            receipt = self.span / RECEIPT
            pinned = receipt.read_bytes()
            receipt.write_bytes(b"changed after the check\n")
            with self.subTest(streams=streams), custody.guard():
                self.assertEqual(receipt.read_bytes(), pinned)
                with open(receipt, "rb") as handle:
                    self.assertEqual(handle.read(), pinned)
                with open(str(receipt)) as handle:
                    self.assertEqual(handle.read(), pinned.decode())
                with receipt.open(encoding="utf-8", newline="") as handle:
                    self.assertEqual(handle.readline(), pinned.decode())
                self.assertEqual(json.loads(receipt.read_text()), {"roster": ["L001"]})
                self.assertEqual(hashlib.file_digest(io.open(receipt, "rb"), "sha256").hexdigest(), sha(pinned))
            self.assertEqual(receipt.read_bytes(), b"changed after the check\n")     # outside the stage, the disk
            self.assertEqual(custody.opened[0], ("dev-01-s01", RECEIPT))

    def test_stage_1_reads_a_pinned_stream_from_disk_and_keeps_none_of_it(self):
        custody = self.admitted("pass")
        with custody.guard():
            self.assertEqual((self.span / TRACE).read_bytes(), FILES[TRACE])
            with open(self.span / STREAM, newline="") as handle:
                self.assertEqual(handle.read(), FILES[STREAM].decode())
        self.assertEqual(custody.opened, [("dev-01-s01", TRACE), ("dev-01-s01", STREAM)])
        self.assertFalse([key for key in custody._bytes if not P.is_operational_path(key[1])])

    def test_stage_2_checks_a_stream_s_pin_at_each_open_before_it_is_decoded(self):
        custody = self.admitted("verify")
        trace = self.span / TRACE
        with custody.guard():
            self.assertEqual(trace.read_bytes(), FILES[TRACE])
            with open(trace) as handle:
                self.assertEqual(handle.read(), FILES[TRACE].decode())
            os.chmod(trace, 0o600)
            import subprocess
            import sys
            flip = "import sys; p = sys.argv[1]; d = open(p, 'rb').read(); open(p, 'wb').write(bytes([d[0] ^ 1]) + d[1:])"
            subprocess.run([sys.executable, "-c", flip, str(trace)], check=True)     # changed after the verifier's pass
            with self.assertRaisesRegex(P.PinRefusal, r"power_trace\.csv: its bytes are not its pin"):
                trace.read_bytes()
            with self.assertRaisesRegex(P.PinRefusal, r"power_trace\.csv: its bytes are not its pin"):
                open(trace, "rb")
        self.assertEqual(custody.opened, [("dev-01-s01", TRACE)] * 2)           # the refused reads served nothing

    def test_an_open_of_a_roster_file_outside_the_pin_list_refuses(self):
        for streams in ("pass", "verify"):
            custody = self.admitted(streams)
            added = self.span / "hazards/meter/stream-0002.jsonl"
            added.write_bytes(b"appeared after the check\n")
            with self.subTest(streams=streams), custody.guard():
                with self.assertRaisesRegex(P.PinRefusal, "outside the pin list"):
                    added.read_bytes()
                with self.assertRaisesRegex(P.PinRefusal, "outside the pin list"):
                    open(added)
            added.unlink()

    def test_an_absent_optional_file_is_absent_and_a_directory_is_a_directory(self):
        with self.admitted("pass").guard():
            with self.assertRaises(FileNotFoundError):
                open(self.span / "legs/L001/runtime/run/outputs/align_runtime_events.jsonl", "rb")
            with self.assertRaises(IsADirectoryError):
                open(self.span / "legs")
            self.assertTrue((self.span / RECEIPT).is_file())

    def test_a_roster_file_cannot_be_opened_for_writing(self):
        with self.admitted("pass").guard():
            for name in (RECEIPT, TRACE):
                for mode in ("w", "a", "r+", "wb", "x"):
                    with self.subTest(name=name, mode=mode), self.assertRaisesRegex(P.PinRefusal, "for writing"):
                        open(self.span / name, mode)
        self.assertEqual((self.span / RECEIPT).read_bytes(), FILES[RECEIPT])

    def test_a_raw_open_that_bypasses_the_pinned_reads_refuses(self):
        """os.open does not go through ``open``; the audit backstop refuses it for a roster path."""
        for streams in ("pass", "verify"):
            with self.subTest(streams=streams), self.admitted(streams).guard():
                for name in (RECEIPT, TRACE):
                    with self.assertRaisesRegex(P.PinRefusal, "outside the pinned reads"):
                        os.open(self.span / name, os.O_RDONLY)
        os.close(os.open(self.span / RECEIPT, os.O_RDONLY))                    # inert once the stage is over

    def test_other_paths_are_untouched_and_a_span_reached_by_another_spelling_is_still_guarded(self):
        outside = self.root.parent / "outside.txt"
        with self.admitted("pass").guard():
            with open(outside, "w") as handle:
                handle.write("ok")
            self.assertEqual(outside.read_text(), "ok")
            spelled = self.root / "dev-01-s01" / "legs" / ".." / RECEIPT
            self.assertEqual(open(spelled, "rb").read(), FILES[RECEIPT])
            link = self.root.parent / "alias"
            link.symlink_to(self.root, target_is_directory=True)
            self.assertEqual((link / "dev-01-s01" / RECEIPT).read_bytes(), FILES[RECEIPT])


class ManifestInputs(unittest.TestCase):
    """The manifest pins one inputs file; the tool writes it from offload manifests and checks its chain."""
    MANIFEST = "docs/process/cadence/looks/lm-interim-01.json"

    def setUp(self):
        from joulewise.cadence_looks import manifest as M
        from scripts import cadence_look_manifest as cli
        self.M, self.cli = M, cli
        self.tmp = tempfile.TemporaryDirectory(prefix="pins-repo-")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.manifest = self.repo / self.MANIFEST
        self.manifest.parent.mkdir(parents=True)
        real = Path(__file__).resolve().parents[2]
        self.doc = json.loads((real / self.MANIFEST).read_text(encoding="utf-8"))
        self.doc["status"] = "draft"
        self.manifest.write_text(json.dumps(self.doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.repo / M.INPUTS_PATH).write_text(json.dumps({"schema": P.SCHEMA, "spans": []}) + "\n")
        self.custody = Path(self.tmp.name) / "custody"
        self.plan = Path(self.tmp.name) / "plan.json"
        rows = []
        for index, sid in enumerate(("dev-01-s01", "dev-01-s03")):
            write_span(self.custody, sid)
            sums = Path(self.tmp.name) / f"{sid}.SHA256SUMS"
            sums.write_bytes(offload_manifest(files_for(sid)))
            rows.append({"span_id": sid, "runner_commit": COMMIT, "close_item": 318 + index, "check_item": 317 - index,
                         "offload_manifest": str(sums), "span_dir": str(self.custody / sid)})
        self.rows = rows
        self.plan.write_text(json.dumps(rows))

    def run_cli(self, *argv):
        buffer = io.StringIO()
        with unittest.mock.patch("sys.stdout", buffer):
            code = self.cli.main([str(a) for a in argv])
        return code, buffer.getvalue()

    def pin_inputs(self, *extra):
        return self.run_cli("pin-inputs", self.manifest, "--repo", self.repo, "--plan", self.plan, *extra)

    def test_the_manifest_names_the_inputs_file_and_cites_the_ruling(self):
        self.M.validate_manifest(self.doc)
        self.assertEqual(self.doc["inputs"]["pins"]["path"], self.M.INPUTS_PATH)
        self.assertIn(("inputs.pins", self.M.INPUTS_PATH, self.doc["inputs"]["pins"]["sha256"]), self.M.code_refs(self.doc))
        self.assertIn("joulewise/cadence_looks/custody_pins.py", self.M.REQUIRED_CODE_PATHS["interim"])
        self.assertIn("joulewise/cadence_looks/custody_pins.py", self.M.STAGE1_CODE)
        for label, change in {"no inputs": lambda d: d.pop("inputs"),
                              "another path": lambda d: d["inputs"]["pins"].update(path="docs/other.json"),
                              "no ruling": lambda d: d["inputs"].update(cite=["RL-184 §3.3"]),
                              "no rule": lambda d: d["inputs"].update(rule=""),
                              "an unknown member": lambda d: d["inputs"].update(spans=[])}.items():
            doc = json.loads(json.dumps(self.doc))
            change(doc)
            with self.subTest(label), self.assertRaises(self.M.ManifestError):
                self.M.validate_manifest(doc)

    def test_a_committed_look_s_pin_list_is_filled(self):
        with self.assertRaisesRegex(self.M.ManifestError, "empty"):
            self.M.input_pins(self.repo, self.doc, complete=True)
        pins, digest = self.M.input_pins(self.repo, self.doc, complete=False)
        self.assertEqual((pins["spans"], digest), ([], sha((self.repo / self.M.INPUTS_PATH).read_bytes())))

    def test_pin_inputs_writes_each_span_s_offload_lines_and_hashes_nothing_in_custody(self):
        for path in self.custody.rglob("*"):                    # a custody file that cannot be opened is still pinned
            if path.is_file():
                os.chmod(path, 0)
        try:
            code, out = self.pin_inputs()
            self.assertEqual(code, 0, out)
            self.assertIn("(dry run", out)
            self.assertEqual(json.loads((self.repo / self.M.INPUTS_PATH).read_text())["spans"], [])
            code, out = self.pin_inputs("--write")
        finally:
            for path in self.custody.rglob("*"):
                if path.is_file():
                    os.chmod(path, 0o600)
        self.assertEqual(code, 0, out)
        written = json.loads((self.repo / self.M.INPUTS_PATH).read_text())
        self.assertEqual(written, {"schema": P.SCHEMA, "spans": [
            P.span_pins(sid, offload_manifest(files_for(sid)), {n: len(d) for n, d in files_for(sid).items()},
                        runner_commit=COMMIT, close_item=318 + i, check_item=317 - i)
            for i, sid in enumerate(("dev-01-s01", "dev-01-s03"))]})
        self.assertEqual(P.pin_list_problems(written, complete=True), [])
        P.PinnedCustody(written, ("dev-01-s01", "dev-01-s03"), lambda sid: self.custody / sid, streams="pass").verify()

    def test_pin_inputs_refuses_a_span_directory_that_is_not_its_offload_manifest(self):
        span = self.custody / "dev-01-s03"
        cases = {
            "an extra file": (lambda: (span / "notes.txt").write_bytes(b"x"), "present but unlisted"),
            "a missing file": (lambda: (span / "runner_receipt.json").unlink(), "listed but absent"),
            "a symlink": (lambda: (span / "link").symlink_to(span / "runner_receipt.json"), "a symlink"),
        }
        for label, (change, text) in cases.items():
            shutil.rmtree(span)
            write_span(self.custody, "dev-01-s03")
            change()
            code, out = self.pin_inputs("--write")
            with self.subTest(label):
                self.assertEqual(code, 1, out)
                self.assertIn(text, out)
                self.assertEqual(json.loads((self.repo / self.M.INPUTS_PATH).read_text())["spans"], [])
        self.plan.write_text(json.dumps([dict(self.rows[0], note="x")]))
        self.assertEqual(self.pin_inputs("--write")[0], 1)
        self.plan.write_text(json.dumps(self.rows))
        self.manifest.write_text(json.dumps(dict(self.doc, status="committed")))
        code, out = self.pin_inputs("--write")
        self.assertEqual(code, 1)
        self.assertIn("never re-pinned", out)

    def test_check_inputs_follows_the_chain_from_each_pin_to_its_public_check(self):
        self.assertEqual(self.pin_inputs("--write")[0], 0)
        self.assertEqual(self.run_cli("pin", self.manifest, "--repo", self.repo, "--write")[0], 0)
        doc = json.loads(self.manifest.read_text())
        self.assertEqual(doc["inputs"]["pins"]["sha256"], sha((self.repo / self.M.INPUTS_PATH).read_bytes()))
        pins = json.loads((self.repo / self.M.INPUTS_PATH).read_text())
        state = Path(self.tmp.name) / "RUN_STATE.md"
        roster = Path(self.tmp.name) / "roster.json"
        roster.write_text(json.dumps([{"span_id": "dev-01-s03"}, {"span_id": "dev-01-s01"}]))
        check = lambda *extra: self.run_cli("check-inputs", self.manifest, "--repo", self.repo, "--run-state", state, *extra)
        state.write_text(run_state(pins))
        code, out = check("--roster", roster)
        self.assertEqual(code, 0, out)
        self.assertIn("names it: full", out)
        self.assertIn("2 spans", out)
        state.write_text(run_state(pins, abbreviated=True))
        code, out = check()
        self.assertEqual(code, 0, out)
        self.assertIn("names it: abbreviated", out)
        state.write_text(run_state(pins).replace(pins["spans"][1]["offload_manifest_sha256"], "0" * 64))
        code, out = check()
        self.assertEqual(code, 1, out)
        self.assertIn("dev-01-s03: Check item 316 does not name its offload manifest's sha256", out)
        state.write_text(run_state(pins))
        roster.write_text(json.dumps([{"span_id": "dev-01-s01"}]))
        code, out = check("--roster", roster)
        self.assertEqual(code, 1, out)
        self.assertIn("not exactly the roster's spans", out)
        # the inputs file edited after the manifest pinned it
        path = self.repo / self.M.INPUTS_PATH
        path.write_text(path.read_text() + "\n")
        code, out = check()
        self.assertEqual(code, 1, out)
        self.assertIn("differs from the manifest's pin", out)


if __name__ == "__main__":
    unittest.main()
