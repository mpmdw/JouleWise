"""Fast guards for the stage-1 admission validator (RL-184 section 3.3). Every input is generated; nothing here
reads custody, and no energy-bearing file exists.

The full black-box matrix is ``test_interim_admission_closure`` (101,889 generated cases through the real CLI, run
in its own CI job). These tests run the same validator in-process over the same frozen corpus, so a regression in the
grammar shows up in the ordinary suite within seconds and without numpy.
"""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path
import sys
import unittest

from joulewise.cadence_looks import admission as A, admission_kits as K, admission_shape as S

REPO = Path(__file__).resolve().parents[2]
try:
    from tests.cadence import test_interim_admission_closure as T
except ModuleNotFoundError:                           # pragma: no cover - the frozen packet is part of the checkout
    T = None


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
        admits = [case for case in self.cases if T.admits(case)]
        self.assertEqual({case.family for case in admits}, {"admit", "F1", "F2", "F3", "F5"})
        for case in admits:
            with self.subTest(case.name):
                self.assertIsNone(verdict(self.files(case)))

    def test_a_sample_of_every_mutation_class_is_refused(self):
        """The first case of each family, then every 37th: all families, a few percent of the cases."""
        refusing = [case for case in self.cases if not T.admits(case)]
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
                    self.assertEqual(verdict(self.files(case)) is None, T.admits(case))

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
