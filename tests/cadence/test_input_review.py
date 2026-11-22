"""RL-194's one-time review record, on generated spans only. The spans are the frozen admission packet's writer
productions written to disk with invented trace and meter files beside them; nothing here is a measurement."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

from joulewise.cadence_looks import admission, custody_pins, manifest as M
from scripts import cadence_look_input_review as RV
from tests.cadence import custody_pin_fixture as PF, look_minirepo as MR
from tests.git_fixture import init_git_fixture

try:
    from tests.cadence import test_interim_admission_closure as T
except ModuleNotFoundError:                           # pragma: no cover - the frozen packet is part of the checkout
    T = None

PROTECTED = ("legs/L001/runtime/runs/cadence-leg/power_trace.csv", "legs/L001/runtime/runs/cadence-leg/rich_telemetry.jsonl",
             "legs/L001/runtime/runs/cadence-leg/raw/powermetrics.plist", "hazards/meter/stream-0001.jsonl")
SPANS = {"dev-01-s01": ("b4b6aeb19", "journals"), "dev-03-s01": ("6e9d42f1d", "journals"),
         "dev-03-s02": ("6e9d42f1d", "retry")}


@unittest.skipIf(T is None, "the frozen admission packet is absent")
class ReviewRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = T.load_corpus()

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="input-review-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for sid, (pin, branch) in SPANS.items():
            docs = T.document_set(pin, branch, self.corpus)
            for name, doc in docs.items():
                self.write(sid, name, T.doc_bytes(name, doc))
            for name in PROTECTED:
                self.write(sid, name, f"invented {sid} {name}\n".encode())
        self.pins = self.pinned()
        self.run_state = PF.run_state(self.pins)

    def pinned(self):
        """The generated spans' pins, each span at the runner commit whose writer made its receipt."""
        pins = PF.synthetic_pins({sid: self.root / sid for sid in SPANS})
        for span in pins["spans"]:
            span["runner_commit"] = next(rev for rev in admission.PINS if rev.startswith(SPANS[span["span_id"]][0]))
        self.sha = custody_pins.pin_list_sha256(custody_pins.pin_list_bytes(pins))
        return pins

    def write(self, sid, name, data):
        path = self.root / sid / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def review(self, run_state=None):
        return RV.review(self.pins, self.sha, "m" * 64, lambda sid: self.root / sid, seat_model="seat-model",
                         seat_family="seat-family", command=["cadence_look_input_review.py", "review"],
                         run_state=self.run_state if run_state is None else run_state)

    def problems(self, record, run_state=None):
        return RV.record_problems(record, self.pins, self.sha, "m" * 64,
                                  self.run_state if run_state is None else run_state)

    def test_the_template_carries_the_pins_and_leaves_every_slot_open(self):
        record = RV.template(self.pins, self.sha, "m" * 64)
        self.assertEqual(record["header"]["pin_list_sha256"], self.sha)
        self.assertEqual(record["header"]["seat"], {"model": None, "family": None})
        self.assertEqual([row["span_id"] for row in record["spans"]], sorted(SPANS))
        for row, span in zip(record["spans"], self.pins["spans"]):
            self.assertEqual({key: row[key] for key in custody_pins.SPAN_KEYS}, span)
            self.assertEqual(set(row["receipt"]["shapes"]), set(RV.RULES))
            self.assertEqual(row["verdicts"], {"desk": None, "executing_seat": None, "executing_seat_refusal": None})
            self.assertEqual(row["check"], {"item": span["check_item"], "second_record": None, "as_printed": None,
                                            "offload_manifest_sha256": span["offload_manifest_sha256"], "form": None})
            for slot in row["receipt"]["shapes"].values():
                self.assertEqual((slot["shape"], slot["verdict"]), (None, None))
        self.assertTrue(self.problems(record))        # unfilled: not a record yet

    def test_the_committed_form_is_the_template_with_one_open_span(self):
        path = Path(__file__).resolve().parents[2] / "docs/process/cadence/looks/lm-interim-01.input-review.template.json"
        form = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(form.pop("_template"))
        prototype = {"schema": custody_pins.SCHEMA, "spans": [dict.fromkeys(custody_pins.SPAN_KEYS)]}
        prototype["spans"][0]["files"] = [dict.fromkeys(custody_pins.FILE_KEYS)]
        self.assertEqual(form, RV.template(prototype, None, None))

    def test_the_seat_opens_operational_files_only_each_through_its_pin(self):
        for sid in SPANS:                      # a stream the seat must not open cannot be opened at all
            for name in PROTECTED:
                os.chmod(self.root / sid / name, 0)
        try:
            record = self.review()
        finally:
            for sid in SPANS:
                for name in PROTECTED:
                    os.chmod(self.root / sid / name, 0o600)
        opened = record["header"]["files_opened"]
        self.assertTrue(opened)
        self.assertTrue(all(M.is_operational_path(name.partition("/")[2]) for name in opened))
        self.assertEqual(len(opened), len(set(opened)))                                  # each read once
        self.assertEqual(sorted(opened), sorted(                            # every operational file, and only those
            f"{span['span_id']}/{entry['path']}" for span in self.pins["spans"] for entry in span["files"]
            if M.is_operational_path(entry["path"])))
        for sid in SPANS:
            self.assertIn(f"{sid}/runner_receipt.json", opened)
            self.assertIn(f"{sid}/legs/L001/leg_record.json", opened)
        self.assertEqual(record["header"]["seat"], {"model": "seat-model", "family": "seat-family"})
        self.assertEqual([row["verdicts"]["executing_seat"] for row in record["spans"]], ["admissible"] * 3)

    def test_each_receipt_s_shapes_are_the_writers(self):
        rows = {row["span_id"]: row["receipt"]["shapes"] for row in self.review()["spans"]}
        for sid, shapes in rows.items():
            with self.subTest(sid):
                self.assertEqual({rule: slot["verdict"] for rule, slot in shapes.items()},
                                 {rule: "admissible" for rule in RV.RULES})
                self.assertEqual(shapes["F01"]["shape"], {"bundle_spelling": ["nested"], "locators": ["runs/cadence-leg"]}
                                 if sid != "dev-03-s02" else shapes["F01"]["shape"])
                self.assertEqual(shapes["F05"]["shape"], {"soak_refusals": "absent", "kind_values": []})
        first, third, retried = rows["dev-01-s01"], rows["dev-03-s01"], rows["dev-03-s02"]
        self.assertEqual(first["F02"]["shape"], {"soak_attempts": "absent", "soak_steps": 1})
        self.assertEqual(first["F04"]["shape"], {"history": "one_soak_step", "soak_step_names": ["soak"]})
        self.assertEqual(first["F02"]["writer"], {"file": "scripts/cadence_legs_runner.py", "lines": "365-466"})
        self.assertEqual(third["F02"]["shape"], {"soak_attempts": "one_accepted", "soak_steps": 1})
        self.assertEqual(third["F03"]["shape"], {"attempt_keys": [RV.ATTEMPT_KEYS], "soak_step_rc": ["integer"]})
        self.assertEqual(third["F02"]["writer"], {"file": "scripts/cadence_legs_runner.py", "lines": "453,575-605"})
        self.assertEqual(retried["F02"]["shape"]["soak_attempts"], "refused_then_accepted")
        self.assertEqual(retried["F04"]["shape"], {"history": "one_row_per_soak_step",
                                                   "soak_step_names": ["soak", "soak.a2"]})

    def test_a_shape_the_rule_does_not_admit_is_recorded_as_inadmissible(self):
        receipt = json.loads((self.root / "dev-03-s01/runner_receipt.json").read_bytes())
        records = {"L001": json.loads((self.root / "dev-03-s01/legs/L001/leg_record.json").read_bytes())}
        cases = {
            "F01": lambda r, legs: legs["L001"]["result"].update(bundle="../outside"),
            "F02": lambda r, legs: r.update(soak_attempts=[]),
            "F03": lambda r, legs: r["soak_attempts"][0].update(note="x"),
            "F04": lambda r, legs: r["soak_attempts"].append(dict(r["soak_attempts"][0], attempt=2)) or r["steps"].clear(),
            "F05": lambda r, legs: r.update(soak_refusals=[{"kind": "thermal"}]),
        }
        for rule, change in cases.items():
            changed, legs = copy.deepcopy(receipt), copy.deepcopy(records)
            change(changed, legs)
            with self.subTest(rule):
                self.assertEqual(RV.receipt_shapes(changed, legs, "C")[rule]["verdict"], "inadmissible")
        self.assertEqual(RV.receipt_shapes(dict(receipt, soak_attempts=receipt["soak_attempts"]), records, "B")["F02"]["verdict"],
                         "inadmissible")                         # revision B never wrote the member

    def test_the_record_carries_the_check_s_digest_as_printed_and_holds_a_span_that_does_not_bind(self):
        """RL-194a section 2: the full digest, the abbreviation exactly as printed, and the Check item number. Audit 3,
        rule P2: an abbreviation is recorded as printed and holds the span; only the full hex binds."""
        first = self.pins["spans"][0]
        digest = first["offload_manifest_sha256"]
        printed = f"{digest[:8]}…{digest[-3:]}"
        abbreviated = self.run_state.replace(digest, printed)
        record = self.review(abbreviated)
        self.assertEqual(record["spans"][0]["check"], {"item": first["check_item"], "offload_manifest_sha256": digest,
                                                       "as_printed": printed, "form": "abbreviated",
                                                       "second_record": None})
        self.assertEqual(record["spans"][1]["check"]["form"], "full")
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertEqual(self.problems(record, abbreviated), [
            "dev-01-s01: its Check item does not identify the span's offload manifest in full hex with every character "
            "matching (abbreviated); the span is held and returns to the research lead"])
        bound = self.review()
        for row in bound["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertEqual(self.problems(bound), [])
        record["spans"][0]["check"]["second_record"] = "the MBP-side sums file, RUN_STATE item 318"
        self.assertEqual(len(self.problems(record, abbreviated)), 1)
        wrong = "0" if digest[7] != "0" else "1"
        for label, change in {
                "one printed character differs": lambda c: c.update(as_printed=f"{digest[:7]}{wrong}…{digest[-3:]}"),
                "nothing printed": lambda c: c.update(as_printed=None, form="absent"),
                "another item": lambda c: c.update(item=c["item"] + 1),
                "another full digest": lambda c: c.update(offload_manifest_sha256="0" * 64),
                "an empty second record": lambda c: c.update(second_record="")}.items():
            changed = copy.deepcopy(record)
            change(changed["spans"][0]["check"])
            with self.subTest(label):
                self.assertTrue(any("dev-01-s01" in problem for problem in self.problems(changed, abbreviated)))
        mismatched = self.run_state.replace(digest, "0" * 64)
        held = self.review(mismatched)
        self.assertEqual((held["spans"][0]["check"]["form"], held["spans"][0]["check"]["as_printed"]),
                         ("mismatch", "0" * 64))
        for row in held["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertTrue(any("held" in problem for problem in self.problems(held, mismatched)))
        unlabelled = self.run_state.replace("Offload manifest", "Encrypted archive")
        absent = self.review(unlabelled)
        self.assertEqual([row["check"]["form"] for row in absent["spans"]], ["absent"] * 3)
        for row in absent["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertEqual(sum("held" in problem for problem in self.problems(absent, unlabelled)), 3)

    def test_a_record_cannot_claim_a_spelling_its_check_item_does_not_print(self):
        """Audit 1 on 2082c1a51: the Check printed all 64 digits and the record claimed a matching abbreviation the
        item never carried. The checker judged the claim against itself. It reads the RUN_STATE now."""
        record = self.review()
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertEqual(self.problems(record), [])
        check = record["spans"][0]["check"]
        exact = check["as_printed"]
        claims = {
            "an abbreviation of the printed digest": dict(as_printed=f"{exact[:8]}…{exact[-4:]}", form="abbreviated"),
            "the printed digest called an abbreviation": dict(form="abbreviated"),
            "another spelling of the ellipsis": dict(as_printed=f"{exact[:8]}...{exact[-4:]}", form="abbreviated"),
        }
        for label, claim in claims.items():
            changed = copy.deepcopy(record)
            changed["spans"][0]["check"].update(claim)
            with self.subTest(label):
                self.assertNotIn(changed["spans"][0]["check"]["as_printed"] if label != "the printed digest called an "
                                 "abbreviation" else "…", self.run_state)
                problems = self.problems(changed)
                self.assertTrue(any("dev-01-s01" in problem and "prints" in problem for problem in problems), problems)
        # and the other way: the item prints an abbreviation, the record claims the full digest
        digest = self.pins["spans"][0]["offload_manifest_sha256"]
        abbreviated = self.run_state.replace(digest, f"{digest[:8]}…{digest[-4:]}")
        self.assertTrue(any("dev-01-s01" in problem for problem in self.problems(record, abbreviated)))
        # a record made against one RUN_STATE is not a record of another whose Check names another digest
        self.assertTrue(any("held" in problem for problem in self.problems(record, self.run_state.replace(digest, "0" * 64))))

    def checkout(self, pins):
        """A checkout whose manifest carries ``pins`` and registers the generated custody's root (audit 2), committed
        and published to a local bare origin with its RUN_STATE: the review and its checker read the Check items only
        from origin/main after a fetch (audit 3, rule P3)."""
        repo = Path(os.path.realpath(self.root)).with_name(self.root.name + "-repo")
        self.addCleanup(lambda: __import__("shutil").rmtree(repo, ignore_errors=True))
        manifest = repo / M.INTERIM_MANIFEST_PATH
        manifest.parent.mkdir(parents=True, exist_ok=True)
        doc = json.loads((Path(__file__).resolve().parents[2] / M.INTERIM_MANIFEST_PATH).read_text(encoding="utf-8"))
        doc["custody"]["root"] = os.path.realpath(self.root)
        doc["inputs"]["pins"] = pins
        manifest.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (self.root / M.INTERIM_LOOK_ID).mkdir(exist_ok=True)
        state = repo / "RUN_STATE.md"
        state.write_text(PF.run_state(pins), encoding="utf-8")
        init_git_fixture(repo, "-q", "-b", "main")
        MR.git(repo, "remote", "add", "origin", str(MR.bare_origin(self, repo)))
        MR.git_commit(repo, "a generated checkout")
        return repo, manifest, state

    def cli(self, *argv):
        import contextlib
        import io
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = RV.main([str(word) for word in argv])
        return code, printed.getvalue()

    def test_the_check_command_judges_the_record_against_the_public_run_state(self):
        repo, manifest, state = self.checkout(self.pins)
        record = self.review()
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        record["header"]["manifest_sha256"] = M.sha256_file(manifest)
        check = record["spans"][0]["check"]
        check.update(as_printed=f"{check['as_printed'][:8]}…{check['as_printed'][-4:]}", form="abbreviated")
        (self.root / M.INTERIM_LOOK_ID / "input_review.json").write_bytes(RV.dump(record))
        code, out = self.cli("check", "--repo", repo)
        self.assertEqual(code, 1, out)
        self.assertIn("REFUSE dev-01-s01: check.as_printed and check.form are not what Check item", out)

    def test_the_review_and_its_checker_certify_the_manifest_s_spans_and_no_other_list(self):
        """Audit 2 (HIGH): with three spans pinned in the manifest and two in the on-disk list, check-inputs refused
        while the review and its checker certified "2 of 2". The manifest's list is now the only list: a stale file
        where the old list lived is never read, both certify "3 of 3", and a record of another list refuses."""
        repo, manifest, state = self.checkout(self.pins)
        stale = repo / "docs/process/cadence/looks/lm-interim-01.inputs.json"
        stale.write_bytes(PF.dump(dict(self.pins, spans=self.pins["spans"][:2])))
        code, out = self.cli("review", "--repo", repo, "--seat-model", "seat", "--seat-family",
                             "family")
        self.assertEqual(code, 0, out)
        self.assertIn("3 admissible", out)
        path = self.root / M.INTERIM_LOOK_ID / "input_review.json"
        record = json.loads(path.read_bytes())
        self.assertEqual([row["span_id"] for row in record["spans"]], sorted(SPANS))
        self.assertEqual(record["header"]["pin_list_sha256"], self.sha)
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        path.write_bytes(RV.dump(record))
        code, out = self.cli("check", "--repo", repo)
        self.assertEqual(code, 0, out)
        self.assertIn("ok 3 of 3 spans admissible", out)
        # a record made against a two-span list is not a record of the manifest's three
        two = dict(record, spans=record["spans"][:2])
        two["header"] = dict(record["header"], pin_list_sha256=custody_pins.pin_list_sha256(
            custody_pins.pin_list_bytes(dict(self.pins, spans=self.pins["spans"][:2]))))
        path.write_bytes(RV.dump(two))
        code, out = self.cli("check", "--repo", repo)
        self.assertEqual(code, 1, out)
        self.assertIn("pin_list_sha256 is not the manifest's", out)
        self.assertIn("not the manifest's pinned spans", out)
        # and the review writes its record once: it never replaces one
        code, out = self.cli("review", "--repo", repo, "--seat-model", "seat", "--seat-family",
                             "family")
        self.assertEqual(code, 1, out)
        self.assertIn("never replaced", out)

    def test_audit_3_the_checker_reads_the_check_items_only_from_origin_main_after_a_fetch(self):
        """Audit 3 (HIGH, review_evidence_source.py): the checker certified "3 of 3" from a RUN_STATE path its caller
        named, while origin/main carried none. No command takes a RUN_STATE now. The review and its checker fetch
        origin's main and read RUN_STATE.md from it (``git show origin/main:RUN_STATE.md``): a working tree, a local
        commit and a stale local ref are never the evidence, and a failed fetch certifies nothing."""
        import contextlib
        import io
        repo, manifest, state = self.checkout(self.pins)
        record = self.review()
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        record["header"]["manifest_sha256"] = M.sha256_file(manifest)
        (self.root / M.INTERIM_LOOK_ID / "input_review.json").write_bytes(RV.dump(record))
        code, out = self.cli("check", "--repo", repo)
        self.assertEqual(code, 0, out)
        self.assertIn("ok 3 of 3 spans admissible", out)
        for command in (["check"], ["review", "--seat-model", "seat", "--seat-family", "family"]):
            with self.subTest(command=command[0]):
                err = io.StringIO()
                with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as raised:
                    RV.main([command[0], "--repo", str(repo), "--run-state", str(state), *command[1:]])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn("unrecognized arguments: --run-state", err.getvalue())
        # origin's main now prints every span's digest abbreviated (each span held); this checkout keeps the full
        # items in its working tree, at HEAD and in a local origin/main that has not been fetched
        full = state.read_text(encoding="utf-8")
        held = full
        for span in self.pins["spans"]:
            digest = span["offload_manifest_sha256"]
            held = held.replace(digest, f"{digest[:8]}…{digest[-4:]}")
        state.write_text(held, encoding="utf-8")
        MR.git_commit(repo, "the public Check items, abbreviated")
        MR.git(repo, "reset", "-q", "--hard", "HEAD~1")
        MR.git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.assertEqual(state.read_text(encoding="utf-8"), full)
        code, out = self.cli("check", "--repo", repo)
        self.assertEqual(code, 1, out)
        self.assertEqual(out.count("(abbreviated); the span is held"), 3, out)
        self.assertNotIn("3 of 3", out)
        # with no origin to fetch from, nothing is certified
        MR.git(repo, "remote", "set-url", "origin", str(repo.with_name(repo.name + "-no-such-origin.git")))
        code, out = self.cli("check", "--repo", repo)
        self.assertEqual(code, 1, out)
        self.assertIn("origin/main cannot be fetched", out)

    def test_the_record_cites_the_writer_of_the_span_s_pinned_runner_commit(self):
        """Audit 2 (MED): with the span's runner commit changed to one no writer is pinned at, the review still cited
        writer A from the receipt and the checker found nothing. The writer is the runner commit's, or none."""
        record = self.review()
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertEqual(self.problems(record), [])
        self.pins["spans"][0]["runner_commit"] = "1" * 40
        self.sha = custody_pins.pin_list_sha256(custody_pins.pin_list_bytes(self.pins))
        record = self.review()
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        receipt = record["spans"][0]["receipt"]
        self.assertEqual((receipt["writer_pin"], receipt["kit_frozen_commit_is_runner_commit"]), (None, False))
        problems = self.problems(record)
        self.assertIn("dev-01-s01: the receipt's writer is not the pinned writer of the span's runner commit", problems)
        self.assertIn("dev-01-s01: the receipt's kit commit is not the span's runner commit", problems)

    def test_the_review_refuses_a_linked_directory_a_linked_file_and_any_file_that_is_not_pinned(self):
        """Audit 1 on 2082c1a51: with a span's ``legs`` directory replaced by a link to the same files, the review
        read through it and recorded the span admissible. Its first act is now the stage's: every span directory is
        its pin list by name, no symlink at any depth, before a byte is decoded."""
        sid = sorted(SPANS)[0]
        span = self.root / sid

        def linked(relative):
            def apply():
                kept = self.root / "kept"
                (span / relative).rename(kept)
                (span / relative).symlink_to(kept, target_is_directory=kept.is_dir())
                return lambda: ((span / relative).unlink(), kept.rename(span / relative))
            return apply

        def linked_span():
            kept = self.root / "kept-span"
            span.rename(kept)
            span.symlink_to(kept, target_is_directory=True)
            return lambda: (span.unlink(), kept.rename(span))

        def extra():
            (span / "legs/L001/unlisted.json").write_bytes(b"{}\n")
            return (span / "legs/L001/unlisted.json").unlink

        def missing():
            data = (span / PROTECTED[0]).read_bytes()
            (span / PROTECTED[0]).unlink()
            return lambda: (span / PROTECTED[0]).write_bytes(data)
        cases = {"the legs directory linked": (linked("legs"), "legs: a symlink"),
                 "a bundle directory linked": (linked("legs/L001/runtime"), "legs/L001/runtime: a symlink"),
                 "the receipt linked": (linked("runner_receipt.json"), "runner_receipt.json: a symlink"),
                 "a stream linked": (linked(PROTECTED[0]), PROTECTED[0] + ": a symlink"),
                 "the span directory linked": (linked_span, "the span directory is a symlink"),
                 "a file that is not pinned": (extra, "unlisted.json: a file that is not pinned"),
                 "a pinned stream missing": (missing, "a pinned file is missing")}
        for label, (apply, message) in cases.items():
            undo = apply()
            try:
                with self.subTest(label), self.assertRaisesRegex(custody_pins.PinRefusal, message):
                    self.review()
            finally:
                undo()
        self.assertEqual([row["verdicts"]["executing_seat"] for row in self.review()["spans"]], ["admissible"] * 3)

    def test_the_review_makes_no_number_of_the_idle_baseline_s_mean_power(self):
        """Audit 1 on 2082c1a51: the cold review's validator received events.jsonl's ``power_w_mean`` as a float."""
        from tests.cadence import test_interim_admission as rows
        from joulewise.cadence_looks import admission_shape as shape
        import sys
        rows.RealControllerRows.setUpClass()
        docs = rows.RealControllerRows().leg_journal("6e9d42f1d")
        sid = "dev-03-s01"
        for name, doc in docs.items():
            data = T.doc_bytes(name, doc)
            if name == T.EVENTS:                      # a token no int could be made from: any conversion would raise
                data, count = re.subn(rb'("power_w_mean":)[^,}]+', lambda m: m.group(1) + b"9" * 5000, data)
                self.assertEqual(count, 1)
            self.write(sid, name, data)
        self.pins = self.pinned()
        self.run_state = PF.run_state(self.pins)
        seen = []

        def profile(frame, event, arg):
            if event == "call" and frame.f_code.co_filename == shape.__file__ \
                    and str(frame.f_locals.get("where", "")).endswith("power_w_mean") and "value" in frame.f_locals:
                seen.append(type(frame.f_locals["value"]).__name__)
        sys.setprofile(profile)
        try:
            record = self.review()
        finally:
            sys.setprofile(None)
        row = next(row for row in record["spans"] if row["span_id"] == sid)
        self.assertEqual((row["verdicts"]["executing_seat"], row["verdicts"]["executing_seat_refusal"]),
                         ("admissible", None))
        self.assertTrue(seen)
        self.assertEqual(set(seen), {"_Shielded"})

        def leaves(node):                       # RL-195 condition 1.1: the review record holds no float
            if isinstance(node, dict):
                for value in node.values():
                    yield from leaves(value)
            elif isinstance(node, list):
                for value in node:
                    yield from leaves(value)
            else:
                yield node
        self.assertEqual([value for value in leaves(record) if type(value) is float], [])
        self.assertNotIn("9" * 50, json.dumps(record))

    def test_a_span_the_validator_refuses_is_the_seat_s_inadmissible_with_the_member_named(self):
        path = self.root / "dev-01-s01/runner_receipt.json"
        receipt = json.loads(path.read_bytes())
        receipt["unissued_member"] = True
        path.write_bytes(T.doc_bytes(T.RECEIPT, receipt))
        self.pins = self.pinned()
        row = self.review()["spans"][0]
        self.assertEqual(row["verdicts"]["executing_seat"], "inadmissible")
        self.assertIn("runner_receipt.json", row["verdicts"]["executing_seat_refusal"])

    def test_an_operational_file_that_is_not_its_pin_stops_the_review(self):
        path = self.root / "dev-03-s01/legs/L001/leg_record.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(custody_pins.PinRefusal, r"dev-03-s01/legs/L001/leg_record\.json: its bytes are not its pin"):
            self.review()

    def test_a_filled_record_needs_both_verdicts_on_every_span_and_their_agreement(self):
        record = self.review()
        self.assertTrue(any("desk" in problem for problem in self.problems(record)))
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        self.assertEqual(self.problems(record), [])
        changes = {
            "a disagreement": (lambda r: r["spans"][1]["verdicts"].update(desk="inadmissible"), "disagree"),
            "an inadmissible span both name": (lambda r: r["spans"][1]["verdicts"].update(
                desk="inadmissible", executing_seat="inadmissible"), "count and a shape"),
            "an inadmissible shape": (lambda r: r["spans"][0]["receipt"]["shapes"]["F03"].update(verdict="inadmissible"),
                                      "count and a shape"),
            "another pin list": (lambda r: r["header"].update(pin_list_sha256="0" * 64), "inputs pin"),
            "another manifest": (lambda r: r["header"].update(manifest_sha256="0" * 64), "this manifest"),
            "no seat": (lambda r: r["header"]["seat"].update(model=None), "seat.model"),
            "a stream among the files opened": (lambda r: r["header"]["files_opened"].append(
                "dev-01-s01/" + PROTECTED[0]), "not an operational file"),
            "a changed pin": (lambda r: r["spans"][0]["files"][0].update(sha256="0" * 64), "not the manifest's"),
            "a missing span": (lambda r: r["spans"].pop(), "pinned spans"),
            "a missing writer line": (lambda r: r["spans"][0]["receipt"]["shapes"]["F01"]["writer"].update(lines=None),
                                      "F01 lacks"),
        }
        for label, (change, text) in changes.items():
            changed = copy.deepcopy(record)
            change(changed)
            with self.subTest(label):
                self.assertTrue(any(text in problem for problem in self.problems(changed)),
                                self.problems(changed))


if __name__ == "__main__":
    unittest.main()
