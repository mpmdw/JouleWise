"""RL-194: the look's custody inputs are admitted by content address. Every byte here is generated; no custody,
energy, meter or restricted file is read."""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
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
        }
        for label, changed in cases.items():
            with self.subTest(label):
                self.assertTrue(P.check_chain_problems(doc, changed))
        moved = copy.deepcopy(doc)
        moved["spans"][0]["check_item"] = doc["spans"][1]["check_item"]        # points at the other span's Check
        self.assertTrue(P.check_chain_problems(moved, text))

    def test_an_abbreviation_binds_when_every_printed_character_matches(self):
        """RL-194a section 2: prefix and suffix exactly as the Check prints them, however many they are. The rule is
        character matching: it sets no least number of digits (audit 1 on 2082c1a51, LOW: seven correct digits were
        read as no digest at all)."""
        doc = pins()
        span = doc["spans"][0]
        digest, number, sid = span["offload_manifest_sha256"], span["check_item"], span["span_id"]
        item = lambda printed: (f"{number}. **Check of {sid}.** enc sha256 `00000000…000`, "
                                f"manifest `{printed}` (5 files)\n")
        other = "0" if digest[-1] != "0" else "1"
        for printed, form in ((digest, "full"), (f"{digest[:8]}…{digest[-3:]}", "abbreviated"),
                              (f"{digest[:8]}...{digest[-7:]}", "abbreviated"), (f"{digest[:8]}…", "abbreviated"),
                              (f"{digest[:5]}…{digest[-3:]}", "abbreviated"),
                              (f"{digest[:7]}…", "abbreviated"),                  # seven digits, as the audit printed
                              (f"{digest[:4]}…{digest[-3:]}", "abbreviated"),
                              (f"{digest[:7]}{other if digest[7] != other else 'f'}…{digest[-3:]}", "mismatch"),
                              (f"{digest[:8]}…{digest[-3:-1]}{other}", "mismatch"),
                              (f"{digest[:40]}…{digest[-40:]}", "mismatch"),      # more than a digest's characters
                              (digest[:20], "absent")):                           # a bare prefix is not an abbreviation
            with self.subTest(printed=printed):
                got = P.check_binding(span, item(printed))
                self.assertEqual(got["form"], form)
                self.assertEqual(got["as_printed"], printed if form != "absent" else None)
                self.assertEqual(got["check_item"], number)
                self.assertEqual(bool(P.check_chain_problems(doc, item(printed))), form in ("absent", "mismatch"))

    def test_only_a_digest_labelled_as_the_manifest_s_binds(self):
        """Audit 1 on 2082c1a51: the Check printed a wrong offload manifest digest and, under the archive's label, an
        abbreviation that matched the pinned one. Any matching token bound the span. A digest binds only where the
        item prints it as the span's manifest."""
        doc = pins(("dev-01-s01", "dev-01-s03"))
        ids = [span["span_id"] for span in doc["spans"]]
        for span in doc["spans"]:
            digest, number, sid = span["offload_manifest_sha256"], span["check_item"], span["span_id"]
            wrong = ("0" if digest[0] != "0" else "1") + digest[1:]
            short = f"{digest[:8]}…{digest[-4:]}"
            texts = {
                "the audit's item": (f"Offload manifest `{wrong}`; archive `{short}`.", "mismatch", wrong),
                "an archive's digest alone": (f"Encrypted archive 110,295,072 bytes, sha256 `{digest}`.", "absent", None),
                "an enc digest after a file count": (f"manifest 64 files, enc sha256 `{short}`;", "absent", None),
                "a marker's digest": (f"manifest listed. Marker `{digest}`.", "absent", None),
                "a commit-like word": (f"kit `cl-dev-01.v1.1` `{short}`", "absent", None),
                "a digest after another sentence": (f"It has a manifest. The archive is `{digest}`.", "absent", None),
                "the right digest, then a wrong one under the label": (
                    f"Archive `{digest}`, manifest `{wrong[:8]}…`.", "mismatch", f"{wrong[:8]}…"),
            }
            for label, (body, form, printed) in texts.items():
                text = f"{number}. **Check of {sid}.** {body}\n"
                with self.subTest(span=sid, case=label):
                    got = P.check_binding(span, text, ids)
                    self.assertEqual((got["form"], got["as_printed"]), (form, printed))
                    self.assertTrue(any(problem.startswith(sid) and "held" in problem
                                        for problem in P.check_chain_problems(doc, text)))

    def test_the_phrasings_public_check_items_use_bind(self):
        """The ways the public RUN_STATE prints a span's manifest digest, with generated digests in their place."""
        doc = pins(("dev-01-s01",))
        span = doc["spans"][0]
        digest, number = span["offload_manifest_sha256"], span["check_item"]
        short = f"{digest[:8]}…{digest[-7:]}"
        other = hashlib.sha256(b"another directory's manifest").hexdigest()
        phrasings = {
            "manifest, then the count": (
                f"iCloud Drive `JouleWise-offload/cq-dev-01-s01-a1`, round trip 302 entries, enc sha256 "
                f"`05cb21ec…2172c88`, manifest `{short}` (224 files); caught up", "abbreviated", short),
            "manifest, the count, the digest": (
                f"iCloud `JouleWise-offload/cq-dev-01-s01-a1/`, enc sha256 `1756d499…b3d`, manifest 256 files "
                f"`{short}`, cloud hash OK", "abbreviated", short),
            "manifest, the count, sha256": (
                f"`cq-dev-01-s01-a1/`. Encrypted archive 110,295,072 bytes, sha256 `bf34a938…01ae3`; manifest 226 "
                f"files, sha256 `{short}`; cloud copy hash check OK", "abbreviated", short),
            "manifest_sha256=": (
                f"`cq-dev-01-s01-a1-20261114T224427Z` (files=122 manifest_sha256={digest})", "full", digest),
            "the span's, then another directory's": (
                f"`dev-01-s01` OUT (226 files, manifest sha256 `{digest}`) and a second OUT `r1-partc-f0` (133 "
                f"files, manifest sha256 `{other}`) copied", "full", digest),
            "a prefix alone": (
                f"dev-01-s01 copy done (`copy_span.sh --go`, 222 files manifest `{digest[:8]}…`, second Part C "
                f"131 files manifest `{other[:8]}…`)", "abbreviated", f"{digest[:8]}…"),
            "the sums file by name": (
                f"`cq-dev-01-s01-a1-20261117T080153Z.mbp.SHA256SUMS` (255 files, sha256 `{digest}`)", "full", digest),
            "Manifest SHA-256": (f"dev-01-s01. Manifest SHA-256 `{digest}`.", "full", digest),
        }
        for label, (body, form, printed) in phrasings.items():
            with self.subTest(label):
                got = P.check_binding(span, f"{number}. **Lead.** {body}\n")
                self.assertEqual((got["form"], got["as_printed"]), (form, printed))

    def test_a_digest_printed_for_another_span_binds_nothing(self):
        """Audit 1 on 2082c1a51: one Check item named two spans and their two digests. Exchanging the two spans'
        whole pin inventories left every check silent, because each digest was somewhere in the item."""
        doc = pins(("dev-01-s01", "dev-01-s03"))
        first, second = doc["spans"]
        number = second["check_item"] = first["check_item"]
        text = f"{number}. **Check.** " + ". ".join(
            f"{span['span_id']} offload manifest `{span['offload_manifest_sha256']}`" for span in doc["spans"]) + ".\n"
        self.assertEqual(P.check_chain_problems(doc, text), [])
        self.assertEqual(P.chain_link(doc, text), {"dev-01-s01": "full", "dev-01-s03": "full"})
        for key in ("files", "offload_manifest_sha256"):
            first[key], second[key] = second[key], first[key]
        self.assertEqual(P.pin_list_problems(doc, complete=True), [])          # each inventory still rebuilds a digest
        problems = P.check_chain_problems(doc, text)
        self.assertEqual(len(problems), 2, problems)
        self.assertTrue(all("held" in problem for problem in problems))
        self.assertEqual(P.chain_link(doc, text), {"dev-01-s01": "mismatch", "dev-01-s03": "mismatch"})
        # an item that names only the other span is not this span's Check
        alone = pins(("dev-01-s01", "dev-01-s03"))
        target = alone["spans"][0]
        item = (f"{target['check_item']}. **Check of dev-01-s03.** Offload manifest "
                f"`{target['offload_manifest_sha256']}`.\n")
        self.assertEqual(P.check_binding(target, item, ["dev-01-s01", "dev-01-s03"])["form"], "absent")
        self.assertEqual(P.check_binding(target, item.replace("of dev-01-s03", "of this span"))["form"], "absent")
        # the span's name inside a longer name is that span (the offload directory is cq-<span>-a1); a longer id wins
        named = item.replace("Check of dev-01-s03", "Check, `JouleWise-offload/cq-dev-01-s01-a1`")
        self.assertEqual(P.check_binding(target, named, ["dev-01-s01", "dev-01-s03"])["form"], "full")
        longer = item.replace("Check of dev-01-s03", "Check of dev-01-s01-a2")
        self.assertEqual(P.check_binding(target, longer, ["dev-01-s01", "dev-01-s01-a2"])["form"], "absent")

    def test_every_manifest_digest_the_check_prints_for_the_span_must_match(self):
        """RL-194a section 2: one mismatched character holds the span. A Check that prints the span's manifest
        twice, once wrongly, is not bound by the other."""
        doc = pins()
        span = doc["spans"][0]
        digest, number, sid = span["offload_manifest_sha256"], span["check_item"], span["span_id"]
        both = (f"{number}. **Check of {sid}.** Offload manifest `{digest}`. Read back: {sid} manifest "
                f"`{digest[:8]}…{digest[-4:]}`.\n")
        self.assertEqual(P.check_binding(span, both)["form"], "full")
        wrong = both.replace(f"{digest[:8]}…", f"{digest[:7]}{'0' if digest[7] != '0' else '1'}…")
        got = P.check_binding(span, wrong)
        self.assertEqual(got["form"], "mismatch")
        self.assertNotEqual(got["as_printed"], digest)
        self.assertTrue(P.check_chain_problems(doc, wrong))

    def test_an_outer_sha256_never_binds(self):
        """RL-195 section 2.2: the close-time outer.sha256 is a custody-side file with no public, dated witness. It
        may be cited as a second record and never binds a span, however a Check item prints it."""
        doc = pins()
        span = doc["spans"][0]
        digest, number, sid = span["offload_manifest_sha256"], span["check_item"], span["span_id"]
        for printed in (digest, f"{digest[:8]}…{digest[-4:]}"):
            for phrase in (f"outer.sha256 `{printed}`", f"`outer.sha256` {printed}", f"outer sha256 `{printed}`",
                           f"outer manifest `{printed}`", f"outer.sha256 (manifest) `{printed}`",
                           f"the outer.sha256 file, manifest: {printed}", f"Outer manifest sha256 `{printed}`"):
                text = f"{number}. **Check of {sid}.** {phrase}.\n"
                with self.subTest(phrase):
                    self.assertEqual(P.check_binding(span, text)["form"], "absent")
                    self.assertEqual(P.held_spans(doc, text), [sid])
        # beside it, the manifest's own digest still binds
        text = f"{number}. **Check of {sid}.** Offload manifest `{digest}`; outer.sha256 `{'0' * 64}`.\n"
        self.assertEqual(P.check_binding(span, text)["form"], "full")

    def test_reading_a_long_item_is_one_pass(self):
        import time
        doc = pins()
        span = doc["spans"][0]
        digest, number, sid = span["offload_manifest_sha256"], span["check_item"], span["span_id"]
        for filler in (" , " * 20000, "1," * 40000, "abc… " * 20000, "manifest " * 20000):
            text = f"{number}. **Check of {sid}.** {filler} manifest `{digest}`\n"
            started = time.process_time()
            P.check_binding(span, text)
            self.assertLess(time.process_time() - started, 5.0)

    def test_an_item_runs_from_its_head_to_the_next_item_s_head(self):
        text = "320. **Later.** x\n\n3. sub-step with 317. inside\n\n317. **Check.** digest here\n1. step\n\n316. **Earlier.** y\n"
        self.assertEqual(P.run_state_item(text, 317), "317. **Check.** digest here\n1. step\n\n")
        self.assertIsNone(P.run_state_item(text, 3))
        self.assertIsNone(P.run_state_item(text, 999))


class HeldAndCorrected(unittest.TestCase):
    """RL-195 section 2: a span whose Check does not bind is HELD; its check_item is corrected only to an item that
    names its offload manifest with every printed character matching."""
    SPANS = ("dev-01-s01", "dev-01-s03")

    def setUp(self):
        self.doc = pins(self.SPANS)
        self.first, self.second = self.doc["spans"]
        self.digest = self.first["offload_manifest_sha256"]

    def state(self, *items):
        """A RUN_STATE of the given items, newest first: (number, body) pairs."""
        return "# State\n\n" + "\n".join(f"{n}. **Lead.** {body}\n" for n, body in sorted(items, reverse=True))

    def test_a_span_whose_check_does_not_bind_is_held_and_stays_in_the_pins(self):
        text = self.state((self.first["check_item"], f"Check of dev-01-s01: offload manifest `{self.digest}`."),
                          (self.second["check_item"], "Check of dev-01-s03: archive copied, no digest printed."))
        states = P.check_states(self.doc, text)
        self.assertEqual({sid: state["state"] for sid, state in states.items()},
                         {"dev-01-s01": P.BOUND, "dev-01-s03": P.HELD})
        self.assertEqual(states["dev-01-s03"]["form"], "absent")
        self.assertEqual(P.held_spans(self.doc, text), ["dev-01-s03"])
        self.assertEqual(P.pin_list_problems(self.doc, complete=True), [])       # held, and still pinned
        problems = P.check_chain_problems(self.doc, text)
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("dev-01-s03") and "held" in problems[0])

    def test_check_item_is_corrected_only_to_an_item_that_names_the_span_s_manifest(self):
        cited = self.first["check_item"]
        good, later = cited + 2, cited + 5
        short = f"{self.digest[:8]}…{self.digest[-4:]}"
        wrong = ("0" if self.digest[9] != "0" else "1").join((self.digest[:9], self.digest[10:]))
        text = self.state(
            (cited, "Check of dev-01-s01: copied."),
            (good, f"Copied at once: `cq-dev-01-s01-a1`, enc sha256 `00000000…0000`, manifest `{short}` (6 files)."),
            (later, f"dev-01-s01 read back: manifest sha256 `{self.digest}`."),
            (cited + 1, f"dev-01-s01: Encrypted archive 1,024 bytes, sha256 `{self.digest}`."),
            (cited + 3, f"dev-01-s01 offload manifest `{wrong}`."),
            (cited + 4, f"dev-01-s03 offload manifest `{self.digest}`."),
            (cited + 6, f"dev-01-s01 outer.sha256 `{self.digest}`."),
            (cited + 7, f"dev-01-s01 manifest `{self.digest[:7]}{'f' if self.digest[7] != 'f' else 'e'}…`."))
        self.assertEqual(P.held_spans(self.doc, text), ["dev-01-s01", "dev-01-s03"])
        before = json.dumps(self.doc)
        corrected = P.correct_check(self.doc, "dev-01-s01", good, text)
        self.assertEqual(json.dumps(self.doc), before)                       # the input is not changed
        span = corrected["spans"][0]
        self.assertEqual((span["check_item"], span["check_corrected_from"]), (good, cited))
        self.assertEqual(P.pin_list_problems(corrected, complete=True), [])
        self.assertEqual(P.check_states(corrected, text)["dev-01-s01"],
                         {"state": P.BOUND, "form": "abbreviated", "check_item": good, "as_printed": short,
                          "corrected_from": cited})
        again = P.correct_check(corrected, "dev-01-s01", later, text)          # the item the table cited is kept
        self.assertEqual((again["spans"][0]["check_item"], again["spans"][0]["check_corrected_from"]), (later, cited))
        refusals = {"the archive's digest": cited + 1, "one character wrong": cited + 3,
                    "another span's item": cited + 4, "an outer.sha256": cited + 6,
                    "an abbreviation with a wrong character": cited + 7, "no such item": cited + 50,
                    "the item it already has": good}
        for label, item in refusals.items():
            with self.subTest(label), self.assertRaisesRegex(P.PinRefusal, "dev-01-s01"):
                P.correct_check(corrected, "dev-01-s01", item, text)
        with self.assertRaisesRegex(P.PinRefusal, "not a span of this pin list"):
            P.correct_check(self.doc, "dev-09-s09", good, text)
        for bad in (0, "319", True):
            with self.subTest(item=bad), self.assertRaises(P.PinRefusal):
                P.correct_check(self.doc, "dev-01-s01", bad, text)
        # correcting back to the cited item, once it binds there, clears the record of a correction
        fixed = text.replace("Check of dev-01-s01: copied.", f"Check of dev-01-s01: offload manifest `{self.digest}`.")
        back = P.correct_check(corrected, "dev-01-s01", cited, fixed)
        self.assertEqual((back["spans"][0]["check_item"], back["spans"][0]["check_corrected_from"]), (cited, None))

    def test_the_pin_list_records_a_correction_as_the_cited_item_number(self):
        for value, ok in ((None, True), (self.first["check_item"] + 1, True), (self.first["check_item"], False),
                          (0, False), (True, False), ("317", False), (1.0, False)):
            doc = copy.deepcopy(self.doc)
            doc["spans"][0]["check_corrected_from"] = value
            with self.subTest(value=value):
                self.assertEqual(P.pin_list_problems(doc, complete=True) == [], ok)
        doc = copy.deepcopy(self.doc)
        del doc["spans"][0]["check_corrected_from"]
        self.assertTrue(P.pin_list_problems(doc, complete=True))

    def test_the_list_for_the_research_lead_carries_item_numbers_and_labels_only(self):
        """RL-195 section 2.4: for a HELD span, each record's item number and the label under which a digest is
        printed. No digest."""
        text = self.state(
            (330, f"dev-01-s01 copied: enc sha256 `{self.digest[:8]}…{self.digest[-4:]}`, manifest `{self.digest}`."),
            (331, f"dev-01-s03 offload manifest `{self.digest}`; then dev-01-s01 marker `{'1' * 64}`."),
            (332, "dev-01-s01 closed; nothing printed."))
        found = P.digest_labels("dev-01-s01", text, self.SPANS)
        self.assertEqual(found, [(331, "marker"), (330, "enc"), (330, "manifest")])
        self.assertFalse(any(re.search("[0-9a-f]{8}", str(label or "")) for _, label in found))


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
        self.runs = getattr(self, "runs", 0) + 1                 # the verifier creates its result, never replaces
        out = out or Path(self.tmp.name) / f"verification-{self.runs}.json"
        argv = [sys.executable, "-I", "-B", str(VERIFIER), "--pins", str(self.pin_file), "--pins-sha256",
                sha(self.pin_file.read_bytes()), "--out", str(out)]
        for sid in self.SPANS:
            argv += ["--span", f"{sid}={self.root / sid}"]
        done = subprocess.run(argv, capture_output=True, text=True)
        return done, (json.loads(out.read_bytes()) if done.returncode in (0, 1) else None)


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
                    self.assertIn(row["state"], ("mismatch", "size", "missing", "not_pinned", "symlink"))
                    if row["state"] == "mismatch":
                        self.assertNotEqual(row["observed"], row["pinned"])
                        self.assertRegex(row["observed"], "^[0-9a-f]{64}$")
                    else:
                        self.assertIsNone(row["observed"])            # a missing, linked or unpinned file is not read
                problems = P.verification_problems(self.doc, result)
                self.assertTrue(problems and problems[0].startswith(named.split("/")[0]), problems)

    def test_a_pin_with_the_right_digest_and_another_byte_count_fails_here(self):
        """Audit 1 on 2082c1a51: a stream pinned with its digest and one byte too many passed this check, passed
        stage 1 and was refused by stage 2's read inside the reservation, which spent the look. What stage 2 and the
        twin's wrapper require, this check requires first."""
        for delta in (1, -1):
            doc = copy.deepcopy(self.doc)
            entry = next(e for e in doc["spans"][0]["files"] if e["path"] == TRACE)
            entry["size"] += delta
            self.assertEqual(P.pin_list_problems(doc, complete=True), [])       # a size is outside the digest chain
            self.pin_file.write_text(json.dumps(doc))
            done, result = self.run_verifier()
            with self.subTest(delta=delta):
                self.assertEqual((done.returncode, result["result"]), (1, "fail"))
                bad = [row for row in result["files"] if row["state"] != "match"]
                self.assertEqual([(row["span_id"], row["path"], row["state"]) for row in bad],
                                 [("dev-01-s01", TRACE, "size")])
                self.assertEqual(bad[0]["observed"], bad[0]["pinned"])           # the digest is the pin's: words and hashes only
                self.assertEqual(P.verification_problems(doc, result),
                                 [f"dev-01-s01/{TRACE}: its byte count is not its pin"])
                # the same pin under the stage's own read, which is where the audit met it
                custody = P.PinnedCustody(doc, self.SPANS, lambda sid: self.root / sid, streams="verify")
                custody.verify()
                with custody.guard(), self.assertRaisesRegex(P.PinRefusal, "its bytes are not its pin"):
                    (self.root / "dev-01-s01" / TRACE).read_bytes()

    def test_what_it_passes_the_reservation_s_own_reads_pass(self):
        """The class: the check before the reservation is never weaker than the checks inside it. For every fault
        of the copy and of a pin, the verifier's verdict is the verdict of reading every pinned file the way stage 2
        does (the name inventory, then each file against its digest and byte count)."""
        def reserved_reads(doc):
            custody = P.PinnedCustody(doc, self.SPANS, lambda sid: self.root / sid, streams="verify")
            try:
                custody.verify()
                with custody.guard():
                    for (sid, rel) in custody.pins:
                        with open(self.root / sid / rel, "rb") as handle:
                            handle.read()
            except P.PinRefusal:
                return "refuses"
            return "passes"

        def size(delta, name):
            def change(doc):
                next(e for e in doc["spans"][0]["files"] if e["path"] == name)["size"] += delta
            return change
        cases = {label: (change, None) for label, (change, _, _) in self.faults().items()}
        cases.update({f"pinned size {delta:+d} on {name}": (None, size(delta, name))
                      for delta in (1, -1) for name in (TRACE, STREAM, RECEIPT)})
        cases["the pinned copy"] = (None, None)
        for label, (change_copy, change_pins) in cases.items():
            for sid in self.SPANS:
                shutil.rmtree(self.root / sid, ignore_errors=True)
                (self.root / sid).unlink(missing_ok=True)
                write_span(self.root, sid)
            shutil.rmtree(Path(self.tmp.name) / "kept", ignore_errors=True)
            (Path(self.tmp.name) / "kept").unlink(missing_ok=True)
            doc = copy.deepcopy(self.doc)
            if change_copy:
                change_copy()
            if change_pins:
                change_pins(doc)
            self.pin_file.write_text(json.dumps(doc))
            done, result = self.run_verifier()
            with self.subTest(label):
                before = "passes" if done.returncode == 0 and not P.verification_problems(doc, result) else "refuses"
                self.assertEqual(before, reserved_reads(doc))
                self.assertEqual(before, "passes" if label == "the pinned copy" else "refuses")

    def test_the_result_file_is_created_and_never_replaces_a_file(self):
        """Audit 1 on 2082c1a51: a failed check wrote its result where it was told to, and that was the look's
        public destination. The verifier writes to a new name only; a stage gives it one in a directory of its own."""
        (self.root / "dev-01-s01" / TRACE).write_bytes(b"synthetic copy fault\n")
        taken = Path(self.tmp.name) / "PUBLIC.json"
        for label, prepare, kept in (
                ("an existing file", lambda: taken.write_bytes(b"kept\n"), b"kept\n"),
                ("a link to a file", lambda: (taken.unlink(), (Path(self.tmp.name) / "t").write_bytes(b"kept\n"),
                                              taken.symlink_to(Path(self.tmp.name) / "t")), b"kept\n"),
                ("a link to nothing", lambda: (taken.unlink(), taken.symlink_to(Path(self.tmp.name) / "absent")), None)):
            prepare()
            done, _ = self.run_verifier(out=taken)
            with self.subTest(label):
                self.assertEqual(done.returncode, 2)
                self.assertFalse((Path(self.tmp.name) / "absent").exists())
                if kept is not None:
                    self.assertEqual(taken.read_bytes(), kept)
        taken.unlink()
        done, result = self.run_verifier(out=taken)                     # a new name: the failure is recorded there
        self.assertEqual((done.returncode, result["result"]), (1, "fail"))

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

    def test_a_held_span_is_reported_corrected_only_by_the_rule_and_keeps_the_inputs_from_being_final(self):
        """RL-195 section 2 at the tool: check-inputs names each HELD span with the items and labels under which a
        digest is printed (never a digest), correct-check moves a check_item only where the new item binds, and the
        inputs are final only with no span HELD and every roster span pinned."""
        self.assertEqual(self.pin_inputs("--write")[0], 0)
        self.assertEqual(self.run_cli("pin", self.manifest, "--repo", self.repo, "--write")[0], 0)
        pins = json.loads((self.repo / self.M.INPUTS_PATH).read_text())
        first, second = pins["spans"]
        state = Path(self.tmp.name) / "RUN_STATE.md"
        later = first["check_item"] + 20
        state.write_text(
            f"{later}. **Copied at once.** `cq-{first['span_id']}-a1`, enc sha256 `00000000…0000`, manifest "
            f"`{first['offload_manifest_sha256'][:8]}…{first['offload_manifest_sha256'][-4:]}`.\n\n"
            f"{first['check_item']}. **Check of {first['span_id']}.** Copied; outer.sha256 "
            f"`{first['offload_manifest_sha256']}`.\n\n"
            f"{second['check_item']}. **Check of {second['span_id']}.** Offload manifest "
            f"`{second['offload_manifest_sha256']}`.\n")
        code, out = self.run_cli("check-inputs", self.manifest, "--repo", self.repo, "--run-state", state)
        self.assertEqual(code, 1, out)
        self.assertIn(f"{first['span_id']}: ", out)
        self.assertIn("names it: absent; HELD", out)
        self.assertIn("names it: full; bound", out)
        self.assertIn(f"HELD {first['span_id']}: digests printed after the span is named: item {later} under enc; "
                      f"item {later} under manifest; item {first['check_item']} under no label", out)
        self.assertIn("1 span(s) HELD: the manifest cannot be final", out)
        self.assertNotIn(first["offload_manifest_sha256"][:8] + "…", out)        # labels and items, no digest printed
        self.assertEqual(self.M.inputs_final_problems(self.repo, self.doc, state.read_text())[-1:],
                         [f"inputs: 1 span(s) HELD ({first['span_id']}): the manifest cannot be final while a span is "
                          "held, and a held span stays on the roster (RL-195 section 2.3)"])
        correct = lambda *extra: self.run_cli("correct-check", self.manifest, "--repo", self.repo, "--run-state", state,
                                              "--span", first["span_id"], *extra)
        code, out = correct("--item", second["check_item"])            # another span's Check: refused, still HELD
        self.assertEqual(code, 1, out)
        self.assertIn("the span stays HELD", out)
        before = (self.repo / self.M.INPUTS_PATH).read_bytes()
        code, out = correct("--item", later)                             # dry run
        self.assertEqual(code, 0, out)
        self.assertEqual((self.repo / self.M.INPUTS_PATH).read_bytes(), before)
        code, out = correct("--item", later, "--write")
        self.assertEqual(code, 0, out)
        self.assertIn(f"Check item {first['check_item']} (held) -> {later} (abbreviated; bound)", out)
        fixed = json.loads((self.repo / self.M.INPUTS_PATH).read_text())
        self.assertEqual((fixed["spans"][0]["check_item"], fixed["spans"][0]["check_corrected_from"]),
                         (later, first["check_item"]))
        self.assertEqual([s["span_id"] for s in fixed["spans"]], [first["span_id"], second["span_id"]])
        self.assertEqual(self.run_cli("pin", self.manifest, "--repo", self.repo, "--write")[0], 0)
        doc = json.loads(self.manifest.read_text())
        code, out = self.run_cli("check-inputs", self.manifest, "--repo", self.repo, "--run-state", state)
        self.assertEqual(code, 0, out)
        self.assertIn(f"(corrected from item {first['check_item']}, RL-195 section 2.1) names it: abbreviated; bound", out)
        self.assertEqual(self.M.inputs_final_problems(self.repo, doc, state.read_text(),
                                                      [first["span_id"], second["span_id"]]), [])
        self.assertTrue(any("not exactly the roster's" in problem for problem in self.M.inputs_final_problems(
            self.repo, doc, state.read_text(), [second["span_id"]])))          # no span is dropped to finish
        committed = dict(doc, status="committed")
        self.manifest.write_text(json.dumps(committed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        code, out = correct("--item", first["check_item"] + 30)
        self.assertEqual(code, 1, out)
        self.assertIn("never re-pinned", out)

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
        self.assertIn("dev-01-s03: Check item 316 prints a manifest digest for the span that is not its offload "
                      "manifest's sha256; the span is held", out)
        self.assertIn("names it: mismatch", out)
        # Audit 1 on 2082c1a51, the production command: every Check prints a wrong offload manifest digest and the
        # right abbreviation under the archive's label. Both spans were reported chained and the command exited 0.
        def mislabelled(span):
            digest = span["offload_manifest_sha256"]
            other = ("0" if digest[0] != "0" else "1") + digest[1:]
            return (f"{span['check_item']}. **Check of {span['span_id']}.** Offload manifest `{other}`; archive "
                    f"`{digest[:8]}…{digest[-4:]}`.\n")
        state.write_text("".join(map(mislabelled, pins["spans"])))
        code, out = check()
        self.assertEqual(code, 1, out)
        self.assertEqual(out.count("the span is held"), 2, out)
        self.assertNotIn("each chained to its Check item", out)
        # one Check item for both spans, and the two pin inventories exchanged between the span ids
        state.write_text("400. **Check.** " + ". ".join(
            f"{span['span_id']} offload manifest `{span['offload_manifest_sha256']}`" for span in pins["spans"]) + ".\n")
        shared = json.loads(json.dumps(pins))
        for span in shared["spans"]:
            span["check_item"] = 400
        exchanged = json.loads(json.dumps(shared))
        for key in ("files", "offload_manifest_sha256"):
            exchanged["spans"][0][key], exchanged["spans"][1][key] = shared["spans"][1][key], shared["spans"][0][key]
        for label, document, expected in (("as pinned", shared, 0), ("exchanged", exchanged, 1)):
            (self.repo / self.M.INPUTS_PATH).write_text(json.dumps(document, indent=1) + "\n")
            self.assertEqual(self.run_cli("pin", self.manifest, "--repo", self.repo, "--write")[0], 0)
            code, out = check()
            with self.subTest(label):
                self.assertEqual(code, expected, out)
        (self.repo / self.M.INPUTS_PATH).write_text(json.dumps(pins, indent=1) + "\n")
        self.assertEqual(self.run_cli("pin", self.manifest, "--repo", self.repo, "--write")[0], 0)
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
