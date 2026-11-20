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
            "a prefix too short to bind": text.replace(
                doc["spans"][0]["offload_manifest_sha256"], doc["spans"][0]["offload_manifest_sha256"][:7] + "…"),
        }
        for label, changed in cases.items():
            with self.subTest(label):
                self.assertTrue(P.check_chain_problems(doc, changed))
        moved = copy.deepcopy(doc)
        moved["spans"][0]["check_item"] = doc["spans"][1]["check_item"]        # points at the other span's Check
        self.assertTrue(P.check_chain_problems(moved, text))

    def test_an_item_runs_from_its_head_to_the_next_item_s_head(self):
        text = "320. **Later.** x\n\n3. sub-step with 317. inside\n\n317. **Check.** digest here\n1. step\n\n316. **Earlier.** y\n"
        self.assertEqual(P.run_state_item(text, 317), "317. **Check.** digest here\n1. step\n\n")
        self.assertIsNone(P.run_state_item(text, 3))
        self.assertIsNone(P.run_state_item(text, 999))


class FirstAct(unittest.TestCase):
    SPANS = ("dev-01-s01", "dev-01-s03")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pins-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "custody"
        for sid in self.SPANS:
            write_span(self.root, sid)
        self.doc = pins(self.SPANS)

    def custody(self, doc=None, roster=None):
        return P.PinnedCustody(doc or self.doc, roster or self.SPANS, lambda sid: self.root / sid)

    def refused(self, pattern, doc=None):
        custody = self.custody(doc)
        with self.assertRaisesRegex(P.PinRefusal, pattern):
            custody.verify()
        self.assertEqual(custody.opened, [])                    # nothing was served: no other read happened

    def test_the_pinned_copy_is_admitted_and_counted(self):
        count, total = self.custody().verify()
        self.assertEqual(count, sum(len(files_for(sid)) for sid in self.SPANS))
        self.assertEqual(total, sum(len(data) for sid in self.SPANS for data in files_for(sid).values()))

    def test_a_changed_file_refuses(self):
        path = self.root / "dev-01-s03/legs/L001/runtime/run/power_trace.csv"
        data = path.read_bytes()
        path.write_bytes(bytes([data[0] ^ 1]) + data[1:])       # one flipped bit, the same length
        self.refused(r"dev-01-s03/legs/L001/runtime/run/power_trace\.csv: its bytes are not its pin")

    def test_a_file_of_another_length_refuses(self):
        path = self.root / "dev-01-s01/runner_receipt.json"
        path.write_bytes(path.read_bytes() + b" ")
        self.refused(r"dev-01-s01/runner_receipt\.json: its bytes are not its pin")

    def test_a_missing_file_refuses(self):
        (self.root / "dev-01-s01/hazards/meter/stream-0001.jsonl").unlink()
        self.refused(r"dev-01-s01/hazards/meter/stream-0001\.jsonl: a pinned file is missing")

    def test_an_extra_file_refuses(self):
        for rel in ("hazards/meter/stream-0002.jsonl", "notes.txt", "legs/L002/leg_record.json"):
            path = self.root / "dev-01-s01" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"unpinned\n")
            with self.subTest(rel):
                self.refused(rf"dev-01-s01/{rel}: a file that is not pinned".replace(".", r"\."))
            path.unlink()

    def test_a_substituted_file_refuses(self):
        """Two pinned files with their contents exchanged: each name still exists and each digest is still pinned."""
        first = self.root / "dev-01-s01/legs/L001/runtime/run/power_trace.csv"
        second = self.root / "dev-01-s01/hazards/meter/stream-0001.jsonl"
        a, b = first.read_bytes(), second.read_bytes()
        first.write_bytes(b)
        second.write_bytes(a)
        self.refused("its bytes are not its pin")
        first.write_bytes(a)
        second.write_bytes(b)
        other = self.root / "dev-01-s03/runner_receipt.json"                 # another span's file under this name
        other.write_bytes(b'{"roster": ["L009"]}\n')
        self.refused(r"dev-01-s03/runner_receipt\.json: its bytes are not its pin")

    def test_a_symlink_refuses_whatever_it_points_at(self):
        target = self.root / "dev-01-s01/legs/L001/runtime/run/power_trace.csv"
        kept = self.root.parent / "kept.csv"
        kept.write_bytes(target.read_bytes())                   # the link resolves to the very bytes that are pinned
        target.unlink()
        target.symlink_to(kept)
        self.refused(r"dev-01-s01/legs/L001/runtime/run/power_trace\.csv: a symlink")
        target.unlink()
        target.write_bytes(kept.read_bytes())
        directory = self.root / "dev-01-s01/hazards"
        moved = self.root.parent / "hazards-kept"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
        self.refused(r"dev-01-s01/hazards: a symlink")
        directory.unlink()
        moved.rename(directory)
        span = self.root / "dev-01-s03"
        elsewhere = self.root.parent / "span-kept"
        span.rename(elsewhere)
        span.symlink_to(elsewhere, target_is_directory=True)
        self.refused("dev-01-s03: the span directory is a symlink")

    def test_a_missing_span_and_a_roster_the_pins_do_not_match_refuse(self):
        with self.assertRaisesRegex(P.PinRefusal, "not the same spans"):
            self.custody(roster=("dev-01-s01",))
        with self.assertRaisesRegex(P.PinRefusal, "not the same spans"):
            self.custody(roster=(*self.SPANS, "dev-02-s02"))
        with self.assertRaisesRegex(P.PinRefusal, "not the same spans"):
            self.custody(roster=("dev-01-s01", "dev-01-s01"))
        import shutil
        shutil.rmtree(self.root / "dev-01-s03")
        self.refused("dev-01-s03: no span directory")

    def test_every_refusal_comes_before_any_file_is_served(self):
        """The inventory of every span is checked before the first byte of any span is hashed."""
        (self.root / "dev-01-s03/notes.txt").write_bytes(b"x")
        custody = self.custody()
        with self.assertRaises(P.PinRefusal):
            custody.verify()
        self.assertEqual(custody._bytes, {})


class GuardedReads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pins-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "custody"
        write_span(self.root, "dev-01-s01")
        self.custody = P.PinnedCustody(pins(), ("dev-01-s01",), lambda sid: self.root / sid)
        self.custody.verify()
        self.span = self.root / "dev-01-s01"

    def test_the_bytes_parsed_are_the_bytes_hashed(self):
        """After the first act the file on disk is not read again: what a reader gets is what was hashed."""
        trace = self.span / "legs/L001/runtime/run/power_trace.csv"
        pinned = trace.read_bytes()
        trace.write_bytes(b"changed after the check\n")
        with self.custody.guard():
            self.assertEqual(trace.read_bytes(), pinned)
            with open(trace, "rb") as handle:
                self.assertEqual(handle.read(), pinned)
            with open(str(trace)) as handle:
                self.assertEqual(handle.read(), pinned.decode())
            with trace.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(handle.readline(), pinned.decode())
            self.assertEqual(json.loads((self.span / "runner_receipt.json").read_text()), {"roster": ["L001"]})
            self.assertEqual(hashlib.file_digest(io.open(trace, "rb"), "sha256").hexdigest(), sha(pinned))
        self.assertEqual(trace.read_bytes(), b"changed after the check\n")     # outside the stage, the disk again
        self.assertEqual(self.custody.opened[0], ("dev-01-s01", "legs/L001/runtime/run/power_trace.csv"))

    def test_an_open_of_a_roster_file_outside_the_pin_list_refuses(self):
        added = self.span / "hazards/meter/stream-0002.jsonl"
        added.write_bytes(b"appeared after the check\n")
        with self.custody.guard():
            with self.assertRaisesRegex(P.PinRefusal, "outside the pin list"):
                added.read_bytes()
            with self.assertRaisesRegex(P.PinRefusal, "outside the pin list"):
                open(added)

    def test_an_absent_optional_file_is_absent_and_a_directory_is_a_directory(self):
        with self.custody.guard():
            with self.assertRaises(FileNotFoundError):
                open(self.span / "legs/L001/runtime/run/outputs/align_runtime_events.jsonl", "rb")
            with self.assertRaises(IsADirectoryError):
                open(self.span / "legs")
            self.assertTrue((self.span / "runner_receipt.json").is_file())

    def test_a_roster_file_cannot_be_opened_for_writing(self):
        with self.custody.guard():
            for mode in ("w", "a", "r+", "wb", "x"):
                with self.subTest(mode), self.assertRaisesRegex(P.PinRefusal, "for writing"):
                    open(self.span / "runner_receipt.json", mode)
        self.assertEqual((self.span / "runner_receipt.json").read_bytes(), FILES["runner_receipt.json"])

    def test_a_raw_open_that_bypasses_the_served_bytes_refuses(self):
        """os.open does not go through ``open``; the audit backstop refuses it for a roster path."""
        with self.custody.guard():
            with self.assertRaisesRegex(P.PinRefusal, "outside the verified bytes"):
                os.open(self.span / "runner_receipt.json", os.O_RDONLY)
        os.close(os.open(self.span / "runner_receipt.json", os.O_RDONLY))      # inert once the stage is over

    def test_other_paths_are_untouched_and_a_span_reached_by_another_spelling_is_still_guarded(self):
        outside = self.root.parent / "outside.txt"
        with self.custody.guard():
            with open(outside, "w") as handle:
                handle.write("ok")
            self.assertEqual(outside.read_text(), "ok")
            spelled = self.root / "dev-01-s01" / "legs" / ".." / "runner_receipt.json"
            self.assertEqual(open(spelled, "rb").read(), FILES["runner_receipt.json"])
            link = self.root.parent / "alias"
            link.symlink_to(self.root, target_is_directory=True)
            self.assertEqual((link / "dev-01-s01/runner_receipt.json").read_bytes(), FILES["runner_receipt.json"])


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
        P.PinnedCustody(written, ("dev-01-s01", "dev-01-s03"), lambda sid: self.custody / sid).verify()

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
