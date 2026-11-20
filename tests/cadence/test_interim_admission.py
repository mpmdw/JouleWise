"""Fast guards for the stage-1 admission validator (RL-184 section 3.3). Every input is generated; nothing here
reads custody, and no energy-bearing file exists.

Under RL-194 stage 1 admits by content address (``custody_pins``) and this grammar validator runs behind the pins
as defense in depth. The frozen packet's black-box matrix (``test_interim_admission_closure``) no longer gates; these
tests run the validator in-process over the packet's writer productions and a sample of its cases, without numpy.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

from joulewise.cadence_looks import admission as A, admission_journals as J, admission_kits as K, admission_shape as S
from tests.cadence import interim_admission_accounting as ACC

REPO = Path(__file__).resolve().parents[2]
try:
    from tests.cadence import test_interim_admission_closure as T
except ModuleNotFoundError:                           # pragma: no cover - the frozen packet is part of the checkout
    T = None
CORRECTED = frozenset(ACC.load_corrections()["expect_admit"])


def admitted_as_ruled(case):
    """The suite's expectation with the committed correction applied (tests/cadence/interim_admission_corrections.json)."""
    return T.admits(case) or case.name in CORRECTED


class Mem:
    """A span's files held in memory: bytes by relative path."""

    def __init__(self, files):
        self.files = dict(files)

    def read(self, rel):
        return self.files.get(rel)

    def exists(self, rel):
        return rel in self.files


def verdict(files):
    """None when admitted, else the refusal's message."""
    try:
        A.validate_span(Mem(files), "span")
    except S.Refusal as exc:
        return str(exc)
    return None


def render(docs, mutated=None, file=None):
    files = {name: T.doc_bytes(name, doc) for name, doc in docs.items()}
    if mutated is not None:
        files[file] = mutated
    return files


class StrictDecoding(unittest.TestCase):
    def test_what_the_writers_serialize_decodes(self):
        self.assertEqual(S.decode(b'{"a": 1, "b": [true, null, 1.5, "x"]}\n', "f"), {"a": 1, "b": [True, None, 1.5, "x"]})
        self.assertEqual(S.decode(b'  {"b":1,\n"a":2}  \r\n', "f"), {"b": 1, "a": 2})        # layout is not shape

    def test_every_encoding_or_syntax_no_writer_emits_refuses(self):
        for label, raw in (("duplicate member", b'{"a":1,"a":1}'), ("nan", b'{"a":NaN}'), ("infinity", b'{"a":Infinity}'),
                           ("negative infinity", b'{"a":-Infinity}'), ("overflow", b'{"a":1e999}'),
                           ("comment", b'{"a":1}/*x*/'), ("two documents", b'{"a":1}{"a":1}'),
                           ("trailing comma", b'{"a":1,}'), ("byte order mark", b'\xef\xbb\xbf{"a":1}'),
                           ("utf-16", '{"a":1}'.encode("utf-16")), ("not utf-8", b'{"a":"\xff"}'),
                           ("truncated", b'{"a":'), ("empty", b""), ("single quotes", b"{'a':1}")):
            with self.subTest(label), self.assertRaises(S.Refusal):
                S.decode(raw, "f")

    def test_journals_are_one_object_per_complete_record(self):
        self.assertEqual(S.decode_lines(b'{"a":1}\n{"a":2}\n', "f"), [{"a": 1}, {"a": 2}])
        self.assertEqual(S.decode_lines(b'  {"a":1} \r\n{"a":2}\r\n', "f"), [{"a": 1}, {"a": 2}])
        self.assertEqual(S.decode_lines(b"", "f"), [])
        for label, raw in (("cut final record", b'{"a":1}\n{"a":'), ("no final line end", b'{"a":1}\n{"a":2}'),
                           ("blank record", b'{"a":1}\n\n{"a":2}\n'), ("array record", b"[1]\n"),
                           ("scalar record", b"1\n"), ("duplicate member", b'{"a":1,"a":2}\n'),
                           ("two records on a line", b'{"a":1}{"a":2}\n')):
            with self.subTest(label), self.assertRaises(S.Refusal):
                S.decode_lines(raw, "f")


class ClosedShapes(unittest.TestCase):
    def refuses(self, check, value):
        with self.assertRaises(S.Refusal):
            check(value, "where")

    def test_json_kinds_are_kept_apart(self):
        for value in (True, False, 1.0, "1", "١", None, [], {}):
            with self.subTest(integer=value):
                self.refuses(S.INT, value)
        for value in (1, True, None, "1.0", "١.٥"):
            with self.subTest(float=value):
                self.refuses(S.FLOAT, value)
        for value in (True, "2", "٢", None, [], float("nan"), float("inf")):
            with self.subTest(number=value):
                self.refuses(S.NUM, value)
        for value in (-1, 1.5, True):
            with self.subTest(count=value):
                self.refuses(S.NAT, value)
        S.INT(2, "w"), S.FLOAT(2.0, "w"), S.NUM(2, "w"), S.NUM(2.5, "w"), S.NAT(0, "w")

    def test_objects_are_closed_in_both_directions(self):
        check = S.obj({"a": S.INT}, {"b": S.STR})
        check({"a": 1}, "w")
        check({"a": 1, "b": "x"}, "w")
        for value in ({}, {"a": 1, "c": 1}, {"a": "1"}, {"a": 1, "b": 1}, [], None, {"b": "x"}):
            with self.subTest(value=value):
                self.refuses(check, value)

    def test_enumerations_and_patterns_compare_exact_kinds(self):
        self.refuses(S.enum(0, 2), False)
        self.refuses(S.enum(0, 2), 0.0)
        self.refuses(S.enum("a"), "a\n")
        self.refuses(S.rx(r"L[0-9]{3}"), "L٠٠١")
        self.refuses(S.rx(r"L[0-9]{3}"), "L001\n")
        self.refuses(S.DIGEST, "A" * 64)
        self.refuses(S.DIGEST, "a" * 63)

    def test_a_refusal_never_carries_a_value(self):
        sentinel = "SENTINEL-4242-value"
        for check, value in ((S.INT, sentinel), (S.enum("x"), sentinel), (S.rx(r"L[0-9]+"), sentinel),
                             (S.obj({"a": S.INT}), {"a": sentinel}), (S.obj({}), {sentinel: 1}),
                             (S.arr(S.INT), [sentinel])):
            with self.subTest(check=check), self.assertRaises(S.Refusal) as caught:
                check(value, "where")
            self.assertNotIn(sentinel, str(caught.exception))


@unittest.skipIf(T is None, "the frozen admission packet is absent")
class FrozenCorpus(unittest.TestCase):
    """The same validator over the frozen corpus, in-process. The CLI matrix is the full proof; this is its fast
    projection: every unmodified production is admitted, and a stride sample of every mutation class is refused."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = T.load_corpus()
        cls.cases = [case for case in T.cases() if case.family != "audit-3"]

    def files(self, case):
        docs = T.document_set(case.writer, case.branch, self.corpus)
        files = {name: T.doc_bytes(name, doc) for name, doc in docs.items()}
        if case.op in ("control", "relocate", "alias-copy"):
            changed = files[case.file]
        else:
            changed = T.mutate(case, docs)
        if changed is None:
            files.pop(case.file)
        else:
            files[case.file] = changed
        if case.op in ("relocate", "alias-copy"):
            files[T.ROOT_ALIAS] = files[case.file]
            if case.op == "relocate":
                files.pop(case.file)
        return files

    def test_every_unmodified_production_is_admitted(self):
        admits = [case for case in self.cases if admitted_as_ruled(case)]
        self.assertEqual({case.family for case in admits}, {"admit", "F1", "F2", "F3", "F5", "missing-key"})
        for case in admits:
            with self.subTest(case.name):
                self.assertIsNone(verdict(self.files(case)))

    def test_a_sample_of_every_mutation_class_is_refused(self):
        """The first case of each family, then every 37th: all families, a few percent of the cases."""
        refusing = [case for case in self.cases if not admitted_as_ruled(case)]
        families = {}
        for case in refusing:
            families.setdefault(case.family, []).append(case)
        self.assertGreater(len(families), 40)
        for family, cases in families.items():
            for case in cases[::37]:
                with self.subTest(case.name):
                    self.assertIsNotNone(verdict(self.files(case)), family)

    def test_the_lead_rulings_each_refuse_and_admit_as_ruled(self):
        for case in self.cases:
            if case.family in ("F2", "F4", "F5"):
                with self.subTest(case.name):
                    self.assertEqual(verdict(self.files(case)) is None, admitted_as_ruled(case))

    def test_the_five_audit_three_reproductions_refuse(self):
        docs = T.document_set("b4b6aeb19", "normal", self.corpus)
        receipt, journals = docs[T.RECEIPT], T.document_set("b4b6aeb19", "journals", self.corpus)
        events_file = next(name for name in journals if name.endswith("/events.jsonl"))
        mutations = {
            "failed restore, span rc 0": lambda r: (r["steps"].append(
                {"name": "restore", "rc": 2, "error": "ValueError: generated cleanup failure"}), r.update(rc=0)),
            "unregistered schema": lambda r: r.update(schema="unregistered"),
            "unknown member": lambda r: r.update(unissued_member=True),
            "explicit null error": lambda r: r.update(error=None)}
        for label, change in mutations.items():
            doc = json.loads(json.dumps(receipt))
            change(doc)
            with self.subTest(label):
                self.assertIsNotNone(verdict({**render(docs), T.RECEIPT: T.doc_bytes(T.RECEIPT, doc)}))
        rows = json.loads(json.dumps(journals[events_file]))
        del next(row for row in rows if row["event_type"] == "phase_start")["metadata"]
        with self.subTest("phase_start without metadata"):
            self.assertIsNotNone(verdict({**render(journals), events_file: T.doc_bytes(events_file, rows)}))

    def test_a_written_receipt_carrying_the_generators_flag_refuses(self):
        docs = T.document_set("b4b6aeb19", "normal", self.corpus)
        marked = json.loads(json.dumps(docs[T.RECEIPT]))
        marked["synthetic"] = True
        message = verdict({**render(docs), T.RECEIPT: T.doc_bytes(T.RECEIPT, marked)})
        self.assertIsNotNone(message)           # the generator's closed shape is not a pinned writer's


@unittest.skipIf(T is None, "the frozen admission packet is absent")
class SignalWithoutResult(unittest.TestCase):
    """The three corrected cases (lead, PR #795 NEEDS_SPEC): an interrupted soak step that has an error and no result."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = T.load_corpus()
        cls.cases = {case.name: case for case in T.cases() if case.name in CORRECTED}

    def mutated(self, pin, branch="interrupt-after-result", step="soak"):
        docs = T.document_set(pin, branch, self.corpus)
        receipt = json.loads(json.dumps(docs[T.RECEIPT]))
        row = next(row for row in receipt["steps"] if row["name"] == step)
        return docs, receipt, row

    @staticmethod
    def without_stamps(receipt):
        """The receipt with every clock stamp removed: the only thing that tells two interruptions apart."""
        doc = json.loads(json.dumps(receipt))
        doc.pop("ended", None)
        for row in doc["steps"]:
            row.pop("started", None)
            row.pop("ended", None)
        return doc

    def test_exactly_the_three_pins_are_corrected(self):
        self.assertEqual(len(self.cases), 3)
        self.assertEqual({name.split("/")[1] for name in self.cases}, {"b4b6aeb19", "2d347f721", "6e9d42f1d"})
        for name, case in self.cases.items():
            self.assertFalse(T.admits(case))                    # the suite's own expectation is unchanged
            self.assertEqual((case.family, case.branch, case.file, case.op),
                             ("missing-key", "interrupt-after-result", T.RECEIPT, "remove"))
            self.assertEqual(name.rsplit("/", 5)[-5:], ["runner_receipt.json", "steps", "13", "result", "remove"])

    def test_each_is_a_receipt_the_writer_can_produce(self):
        """Removing the result leaves rc 130, 'SystemExit: 130' and no result: the signal-130 receipt at another time."""
        for pin in ("b4b6aeb19", "2d347f721", "6e9d42f1d"):
            with self.subTest(pin=pin):
                docs, receipt, row = self.mutated(pin)
                self.assertEqual((row["rc"], row["error"], row["result"]["rc"]), (130, "SystemExit: 130", 0))
                del row["result"]
                self.assertIsNone(verdict({**render(docs), T.RECEIPT: T.doc_bytes(T.RECEIPT, receipt)}))
                signal = T.document_set(pin, "signal-130", self.corpus)[T.RECEIPT]
                self.assertEqual(self.without_stamps(receipt), self.without_stamps(signal))
                self.assertGreater(row["ended"]["monotonic_ns"] - row["started"]["monotonic_ns"], 1_000 * 10 ** 9)

    def test_every_other_receipt_check_still_applies(self):
        for pin in ("b4b6aeb19", "2d347f721", "6e9d42f1d"):
            docs, receipt, row = self.mutated(pin)
            del row["result"]
            changes = {
                "the code no longer matches its error": lambda r, s: s.update(rc=0),
                "the span code no longer matches": lambda r, s: r.update(rc=2),
                "the error is gone": lambda r, s: s.pop("error"),
                "the error is null": lambda r, s: s.update(error=None),
                "another signal's error": lambda r, s: s.update(error="SystemExit: 143"),
                "an unknown member": lambda r, s: s.update(unissued=True),
                "a result of the wrong kind": lambda r, s: s.update(result=[]),
                "a step after the stop": lambda r, s: r["steps"].insert(
                    r["steps"].index(s) + 1, dict(name="L001.a1", rc=0, started=s["started"], ended=s["ended"],
                                                  result={"rc": 0})),
                "a soak reference the soak never returned": lambda r, s: r.update(soak_reference="span/soak/x.json"),
            }
            for label, change in changes.items():
                doc = json.loads(json.dumps(receipt))
                change(doc, next(item for item in doc["steps"] if item["name"] == "soak"))
                with self.subTest(pin=pin, label=label):
                    self.assertIsNotNone(verdict({**render(docs), T.RECEIPT: T.doc_bytes(T.RECEIPT, doc)}))


class Accounting(unittest.TestCase):
    """The frozen packet's files and case list are the published ones, and the correction is the lead's three IDs."""

    @unittest.skipIf(T is None, "the frozen admission packet is absent")
    def test_the_frozen_files_and_the_case_list_match_the_published_hashes(self):
        self.assertEqual(ACC.verify_frozen(), [])
        cases, problems = ACC.verify_case_list(T)
        self.assertEqual((problems, len(cases)), ([], 101889))

    def test_a_changed_frozen_file_or_an_extra_one_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "corpus").mkdir()
            (root / "suite.py").write_bytes(b"suite\n")
            (root / "corpus" / "a.json").write_bytes(b"a\n")
            manifest = root / "frozen.sha256"
            manifest.write_text("".join(f"{ACC.sha256_bytes(root.joinpath(name).read_bytes())}  {name}\n"
                                        for name in ("suite.py", "corpus/a.json")))
            with unittest.mock.patch.multiple(ACC, ROOT=root, FROZEN=manifest, CORPUS=root / "corpus"):
                self.assertEqual(ACC.verify_frozen(), [])
                (root / "corpus" / "extra.json").write_bytes(b"x\n")
                self.assertEqual(ACC.verify_frozen(), ["corpus/extra.json: in the frozen corpus directory but not in the manifest"])
                (root / "corpus" / "extra.json").unlink()
                (root / "suite.py").write_bytes(b"edited\n")
                self.assertEqual(ACC.verify_frozen(), ["suite.py: differs from the frozen hash"])
                (root / "suite.py").unlink()
                self.assertEqual(ACC.verify_frozen(), ["suite.py: absent"])

    @unittest.skipIf(T is None, "the frozen admission packet is absent")
    def test_the_committed_manifest_is_the_suites_own_test_side_lines(self):
        lines = ACC.FROZEN.read_text().splitlines()
        self.assertEqual(len(lines), 25)
        self.assertTrue(all(line.partition("  ")[2].startswith("tests/cadence/") for line in lines))
        self.assertIn(f"{hashlib.sha256((REPO / 'tests/cadence/test_interim_admission_closure.py').read_bytes()).hexdigest()}"
                      "  tests/cadence/test_interim_admission_closure.py", lines)

    @unittest.skipIf(T is None, "the frozen admission packet is absent")
    def test_a_changed_case_list_or_a_stale_correction_is_found(self):
        real = ACC.load_corrections()
        cases = T.cases()                                    # generated once; each variant only re-hashes the list
        admitted = next(c.name for c in cases if T.admits(c))
        for label, change, text in (
                ("case ids", {"case_id_sha256": "0" * 64}, "ordered case IDs"),
                ("original oracle", {"original_oracle_sha256": "0" * 64}, "original expectations"),
                ("corrected oracle", {"corrected_oracle_sha256": "0" * 64}, "corrected expectations"),
                ("total", {"total_cases": 101888}, "not 101888"),
                ("unknown id", {"expect_admit": real["expect_admit"] + ["no/such/case"]}, "not in the suite"),
                ("already admitted", {"expect_admit": real["expect_admit"] + [admitted]}, "already admitted")):
            with self.subTest(label), unittest.mock.patch.object(T, "cases", return_value=cases), \
                    unittest.mock.patch.object(ACC, "load_corrections", return_value={**real, **change}):
                self.assertTrue(any(text in problem for problem in ACC.verify_case_list(T)[1]))


@unittest.skipIf(T is None, "the frozen admission packet is absent")
class AuditOne(unittest.TestCase):
    """Audit round 1 of PR #795: four findings reproduced on synthetic inputs, each with its class."""
    PINS = ("b4b6aeb19", "2d347f721", "6e9d42f1d")

    @classmethod
    def setUpClass(cls):
        cls.corpus = T.load_corpus()

    def docs(self, pin, branch="normal"):
        return json.loads(json.dumps(T.document_set(pin, branch, self.corpus)))

    def verdict(self, docs):
        return verdict({name: T.doc_bytes(name, doc) for name, doc in docs.items()})

    # --- H3: display status contradicts its exit status
    def test_the_display_step_s_rc_is_its_exit_status_or_two_when_none_was_observed(self):
        """scripts/run_align_r1_smoke.py:288-290 at all three pins: rc is exit_code, or 2 when exit_code is null."""
        for pin in self.PINS:
            for exit_code, rc, admitted in ((0, 0, True), (None, 2, True), (1, 1, True), (2, 2, True),
                                            (None, 0, False), (2, 0, False), (0, 2, False), (None, 1, False),
                                            (1, 2, False), (0, 1, False)):
                docs = self.docs(pin)
                step = next(step for step in docs[T.RECEIPT]["steps"] if step["name"] == "display")
                step["result"]["exit_code"], step["result"]["rc"], step["rc"] = exit_code, rc, rc
                with self.subTest(pin=pin, exit_code=exit_code, rc=rc):
                    self.assertEqual(self.verdict(docs) is None, admitted)

    def test_a_returned_step_result_is_one_the_writer_s_helper_returns(self):
        """The class of H3: a step result member the writer derives from, or fixes beside, another. Each helper that
        returns a result at the pins (scripts/run_align_r1_smoke.py:78-152, 190-257) returns only these."""
        changes = {
            "a feed start with a nonzero rc": ("start-agents", lambda r: r.update(rc=2)),
            "a volume check with a nonzero rc": ("L001-volumes", lambda r: r.update(rc=3)),
            "a night-agents list that returned nonzero": ("night_agents", lambda r: r.update(rc=1)),
            "a night-agents list with a loaded agent": ("night_agents", lambda r: r.update(stdout="1\t0\tcom.joulewise.night.x\n")),
            "an AC reading without AC power": ("ac_power", lambda r: r.update(stdout="Now drawing from 'Battery Power'\n")),
            "an AC reading that returned nonzero": ("ac_power", lambda r: r.update(rc=1)),
            "a condition-13 commit that is not a revision": ("condition13", lambda r: r.update(executed_commit="HEAD")),
            "a condition-13 check that returned nonzero": ("condition13", lambda r: r.update(rc=128)),
            "a census feed's stop with no proof": ("stop-agents", lambda r: r.update(rc=2, proven_stopped=False)),
            "a meter stop that failed its proof without the group evidence": ("stop-meter", lambda r: r.update(
                rc=2, proven_stopped=False)),
        }
        for pin in self.PINS:
            docs = self.docs(pin)
            self.assertIsNone(self.verdict(docs))
            for label, (name, change) in changes.items():
                changed = json.loads(json.dumps(docs))
                steps = [step for step in changed[T.RECEIPT]["steps"] if step["name"] == name or
                         (name == "L001-volumes" and step["name"].startswith("before-L001"))]
                self.assertTrue(steps, (pin, label))
                for step in steps:
                    change(step["result"])
                    step["rc"] = step["result"].get("rc", 0)
                with self.subTest(pin=pin, label=label):
                    self.assertIsNotNone(self.verdict(changed))

    # --- H2: a controller journal cut before the writer's finalization
    def test_a_controller_journal_that_stops_after_its_failure_refuses(self):
        """The writer flushes the failure and appends run_finalized (controller.py _finish). The eleven rows before
        the finalization call are the same bytes as the first eleven of the twelve; no pinned counter names the
        final row, so the cut journal has nothing to be admitted by (RL-184 F2)."""
        for pin in self.PINS:
            docs = self.docs(pin, "salvaged-failure")
            rows = docs[T.EVENTS]
            self.assertEqual((len(rows), rows[-2]["event_type"], rows[-1]["event_type"]), (12, "failure", "run_finalized"))
            self.assertIsNone(self.verdict(docs))
            cut = json.loads(json.dumps(docs))
            cut[T.EVENTS] = rows[:-1]
            with self.subTest(pin=pin):
                message = self.verdict(cut)
                self.assertIsNotNone(message)
                self.assertIn("finalization", message)

    def test_a_controller_journal_closes_every_stage_it_opened_unless_it_records_a_failure(self):
        """The number of stages is the controller's (the idle sentinel is skipped on a mock backend), so a journal
        that stops at a stage boundary is not refused here; one that stops inside a stage is."""
        for pin in self.PINS:
            docs = self.docs(pin, "controller")
            rows = docs[T.EVENTS]
            self.assertIsNone(self.verdict(docs))
            finalized = {"timestamp_s": rows[-1]["timestamp_s"], "event_type": "run_finalized", "phase": "run",
                         "message": "bundle finalized", "metadata": {}}
            changed = json.loads(json.dumps(docs))
            changed[T.EVENTS] = rows + [finalized]
            with self.subTest(pin=pin, label="finalized after its stages"):
                self.assertIsNone(self.verdict(changed))
            started = [i for i, r in enumerate(rows) if r["event_type"] == "stage_started"]
            for label, cut in (("a stage left open", rows[:started[-1] + 1]),
                               ("a stage left open, then finalized", rows[:started[-1] + 1] + [finalized])):
                changed[T.EVENTS] = cut
                with self.subTest(pin=pin, label=label):
                    self.assertIsNotNone(self.verdict(changed))

    # --- H4: a genuine writer result at the registered deadline
    def deadline_docs(self, pin):
        fixture = json.loads(gzip.decompress((REPO / "tests/cadence/interim_admission_audit1/deadline.json.gz").read_bytes()))
        docs = self.docs(pin, "journals")
        for name, doc in fixture.items():
            docs[f"{T.BUNDLE}/{name}"] = doc
        return docs

    def test_the_writer_s_own_deadline_journals_are_admitted(self):
        """The pinned writer's episode deadman expiring in the one turn: finish_reason and stop_condition
        ``episode.deadman`` with the flag ``episode.deadman:0``. Generated by the writers at all three pins."""
        for pin in self.PINS:
            docs = self.deadline_docs(pin)
            turn = docs[f"{T.BUNDLE}/outputs/align_turns.jsonl"][0]
            self.assertEqual((turn["generation"]["finish_reason"], turn["generation"]["stop_condition"]),
                             ("episode.deadman", "episode.deadman"))
            self.assertIn("episode.deadman:0", turn["flags"])
            with self.subTest(pin=pin):
                self.assertIsNone(self.verdict(docs))

    def test_a_finish_reason_is_the_text_the_runtime_gave_or_null(self):
        """GRAMMAR.md: finish_reason is text or null. The endpoint stores whatever string the runtime's last response
        carried and the deadman's own stop; an empty string or a non-string becomes null before it is stored."""
        for pin in self.PINS:
            for value, admitted in (("stop", True), ("length", True), ("eos", True), ("max_tokens", True),
                                    ("episode.deadman", False), (None, True), ("", False), (0, False), (True, False),
                                    (["stop"], False)):
                docs = self.docs(pin, "journals")
                turn = docs[f"{T.BUNDLE}/outputs/align_turns.jsonl"][0]
                turn["generation"]["finish_reason"] = value
                with self.subTest(pin=pin, finish_reason=value):
                    # the deadman's text is admitted only with its flag
                    self.assertEqual(self.verdict(docs) is None, admitted)
                if value == "episode.deadman":
                    turn["flags"].append("episode.deadman:0")
                    turn["generation"]["stop_condition"] = "episode.deadman"
                    self.assertIsNone(self.verdict(docs))

    def test_a_turn_the_deadman_cut_before_its_provenance_was_built_is_admitted(self):
        """endpoint.py:757-759: DeadmanExpired inside the generation leaves the four-member record whose finish reason
        and stop are the deadman's; an endpoint error leaves both null."""
        for pin in self.PINS:
            for finish, stop, flags, admitted in (
                    ("episode.deadman", "episode.deadman", ["episode.deadman:0"], True),
                    ("episode.deadman", "episode.deadman", [], False),
                    ("episode.deadman", None, ["episode.deadman:0"], False),
                    (None, "episode.deadman", [], False), (None, None, [], True)):
                docs = self.docs(pin, "endpoint-error")
                turn = docs[f"{T.BUNDLE}/outputs/align_turns.jsonl"][0]
                turn["generation"].update(finish_reason=finish, stop_condition=stop)
                turn["flags"] = flags + [f for f in turn["flags"] if f.startswith("endpoint_error")]
                with self.subTest(pin=pin, finish=finish, stop=stop, flags=flags):
                    self.assertEqual(self.verdict(docs) is None, admitted)

    def test_a_failure_row_names_a_reason_the_writer_s_enum_has(self):
        """The class of H4: an enumeration written by hand. joulewise/schemas.py FailureReason at the three pins."""
        writer = ("did_not_fit", "runtime_unavailable", "model_identity_mismatch", "telemetry_unavailable",
                  "format_unavailable", "permission_denied", "transport_unavailable", "unsupported_workload",
                  "cleanup_failed", "unknown_error")
        self.assertEqual(J._FAILURE_REASONS, writer)
        for pin in self.PINS:
            for reason in (*writer, "workload_error", "timeout", "interrupted", "endpoint_error", "thermal_fault"):
                docs = self.docs(pin, "salvaged-failure")
                failure = next(r for r in docs[T.EVENTS] if r["event_type"] == "failure")
                failure["metadata"] = {"failure_reason": reason}
                with self.subTest(pin=pin, reason=reason):
                    self.assertEqual(self.verdict(docs) is None, reason in writer)

    def test_the_failure_reasons_are_the_pinned_enum_when_the_pins_are_present(self):
        import re
        import subprocess
        for pin in self.PINS:
            shown = subprocess.run(["git", "-C", str(REPO), "show", f"{pin}:joulewise/schemas.py"],
                                   capture_output=True, text=True)
            if shown.returncode:
                self.skipTest("the pinned writer revisions are not in this checkout's history")
            body = re.search(r"class FailureReason.*?(?=\n\n\ndef |\nclass )", shown.stdout, re.S).group(0)
            self.assertEqual(tuple(re.findall(r'= "(\w+)"', body)), J._FAILURE_REASONS, pin)


class KitTable(unittest.TestCase):
    """admission_kits is generated from the repository's kit files and the filler registry; a drift refuses here."""

    def test_the_table_is_what_the_repository_files_give(self):
        kits = {}
        for path in sorted(glob.glob(str(REPO / "docs/process/cadence/kits/*.json"))):
            raw = Path(path).read_bytes()
            doc = json.loads(raw)
            legs = []
            for leg in doc["legs"]:
                def get(key, leg=leg):
                    return leg[key] if key in leg else doc["leg_defaults"][key]
                legs.append((leg["leg_id"], leg["seed"], leg["start_band"], get("prefill_tokens"),
                             get("decode_tokens"), leg.get("g0_shape", "own")))
            kits[hashlib.sha256(raw).hexdigest()] = {
                "campaign_id": doc["campaign_id"], "frozen_commit": doc["frozen"]["commit"],
                "runner_kind": doc["runner"]["kind"], "legs": tuple(legs)}
        self.assertEqual(K.KITS, kits)
        registry = json.loads((REPO / "docs/process/cadence/looks/filler-kit-registry.json").read_bytes())
        self.assertEqual(K.FILLERS, {digest: kit_id for kit_id, digest in registry["kit_sha256_by_id"].items()})
        self.assertFalse(set(K.KITS) & set(K.FILLERS))

    def test_a_receipt_naming_an_unregistered_or_mismatched_kit_refuses(self):
        if T is None:
            self.skipTest("the frozen admission packet is absent")
        docs = T.document_set("b4b6aeb19", "normal", T.load_corpus())
        for label, change in (("unregistered digest", lambda k: k.update(sha256="0" * 64)),
                              ("another campaign", lambda k: k.update(campaign_id="cl-dev-02")),
                              ("another frozen commit", lambda k: k.update(
                                  frozen_commit="2d347f721552fe03bdd19f113e7bad7a7c24908e"))):
            doc = json.loads(json.dumps(docs[T.RECEIPT]))
            change(doc["kit"])
            with self.subTest(label):
                self.assertIsNotNone(verdict({**render(docs), T.RECEIPT: T.doc_bytes(T.RECEIPT, doc)}))


if __name__ == "__main__":
    sys.exit(unittest.main())
