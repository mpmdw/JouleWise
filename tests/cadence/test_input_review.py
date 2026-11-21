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

from joulewise.cadence_looks import custody_pins, manifest as M
from scripts import cadence_look_input_review as RV
from tests.cadence import custody_pin_fixture as PF

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
        self.pins = PF.synthetic_pins({sid: self.root / sid for sid in SPANS})
        self.sha = hashlib.sha256(PF.dump(self.pins)).hexdigest()
        self.run_state = PF.run_state(self.pins)

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
        """RL-194a section 2: the full digest, the abbreviation exactly as printed, and the Check item number."""
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
        self.assertEqual(self.problems(record, abbreviated), [])
        record["spans"][0]["check"]["second_record"] = "the MBP-side sums file, RUN_STATE item 318"
        self.assertEqual(self.problems(record, abbreviated), [])
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

    def test_the_check_command_reads_the_run_state_it_is_given(self):
        record = self.review()
        for row in record["spans"]:
            row["verdicts"]["desk"] = "admissible"
        check = record["spans"][0]["check"]
        check.update(as_printed=f"{check['as_printed'][:8]}…{check['as_printed'][-4:]}", form="abbreviated")
        path, state = self.root / "record.json", self.root / "RUN_STATE.md"
        path.write_bytes(RV.dump(record))
        state.write_text(self.run_state, encoding="utf-8")
        import contextlib
        import io
        import unittest.mock
        printed = io.StringIO()
        with unittest.mock.patch.object(RV, "_load", return_value=(self.pins, self.sha, "m" * 64)), \
                contextlib.redirect_stdout(printed):
            code = RV.main(["check", str(path), "--manifest", "unused", "--repo", "unused", "--run-state", str(state)])
        self.assertEqual(code, 1, printed.getvalue())
        self.assertIn("REFUSE dev-01-s01: check.as_printed and check.form are not what Check item", printed.getvalue())

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
        self.pins = PF.synthetic_pins({s: self.root / s for s in SPANS})
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

    def test_a_span_the_validator_refuses_is_the_seat_s_inadmissible_with_the_member_named(self):
        path = self.root / "dev-01-s01/runner_receipt.json"
        receipt = json.loads(path.read_bytes())
        receipt["unissued_member"] = True
        path.write_bytes(T.doc_bytes(T.RECEIPT, receipt))
        self.pins = PF.synthetic_pins({sid: self.root / sid for sid in SPANS})
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
