"""D-188 AUTH-IO: the passive read recorder and the success-only grammar-verdict memo (L7).

Synthetic bytes only.  The memo may only remove repeated strict parses of bytes
already parsed successfully under the same (sha256, effective grammar,
governed-vocabulary flag); every failure must re-parse and raise its own type,
message and position, registration must be unchanged, and the recorder must
never change what a read returns or raises.
"""
from __future__ import annotations

import contextvars
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import authentication_io as aio
from joulewise.authentication_io import (
    V2_AUTHENTICATION_INPUT_CHANGED,
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
)
from tests.hazards import refusal_census as census


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


# (name, suffix, bytes, expected reason) for every strict-grammar refusal.
GRAMMAR_FAILURES = (
    ("duplicate_key", ".json", b'{"a": 1, "a": 2}', "v2_authentication_duplicate_json_key"),
    ("nan", ".json", b'{"a": NaN}', "v2_authentication_nonfinite_json_number"),
    ("infinity", ".json", b'{"a": -Infinity}', "v2_authentication_nonfinite_json_number"),
    ("float_overflow", ".json", b'{"a": 1e999}', "v2_authentication_nonfinite_json_number"),
    ("int_overflow", ".json", b'{"a": ' + b"9" * 400 + b"}", "v2_authentication_nonfinite_json_number"),
    ("invalid_json", ".json", b'{"a": 1,}', "v2_authentication_invalid_json"),
    ("invalid_utf8_json", ".json", b'{"a": "\xff"}', "v2_authentication_invalid_json"),
    ("forbidden_key", ".json", b'{"x": [{"estimator_registration": 1}]}',
     "v2_authentication_forbidden_json_key"),
    ("jsonl_bad_line", ".jsonl", b'{"a": 1}\n\n{"b": 2}\n{"c": }\n', "v2_authentication_invalid_json"),
    ("jsonl_invalid_utf8", ".jsonl", b'{"a": 1}\n\xfe\n', "v2_authentication_invalid_jsonl"),
    ("jsonl_forbidden", ".jsonl", b'{"a": 1}\n{"estimator_registration": 2}\n',
     "v2_authentication_forbidden_json_key"),
    ("jsonl_duplicate", ".jsonl", b'{"a": 1}\n{"b": 1, "b": 1}\n', "v2_authentication_duplicate_json_key"),
)
GOOD_JSON = b'{"alpha": [1, 2.5, {"beta": "gamma"}], "delta": null}'
GOOD_JSONL = b'{"alpha": 1}\n{"beta": [2, 3]}\n'


def _signature(exc: BaseException) -> tuple:
    cause = exc.__cause__
    return (type(exc), getattr(exc, "reason", None), getattr(exc, "detail", None), str(exc),
            type(cause) if cause is not None else None, str(cause) if cause is not None else None)


class _Tmp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="authio-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()

    def write(self, name: str, raw: bytes) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path


def _run_session_reads(paths, *, label_prefix="input", memo_on: bool, allow=()):
    """Read every path in order in one session; return (outcomes, records, parse calls)."""

    outcomes = []
    calls = []
    real = aio._parse_strict

    def counting(raw, grammar, label, **kwargs):
        calls.append((sha(raw), grammar, kwargs.get("allow_governed_spec_vocabulary", False)))
        return real(raw, grammar, label, **kwargs)

    with mock.patch.object(aio, "_parse_strict", counting):
        if memo_on:
            with arc.analysis_run_caches():
                records = _session_body(paths, label_prefix, outcomes, allow)
        else:
            assert arc.current() is None, "the memo-off control must run outside an analysis run"
            records = _session_body(paths, label_prefix, outcomes, allow)
    return outcomes, records, calls


def _session_body(paths, label_prefix, outcomes, allow):
    with V2AuthenticationReadSession() as session:
        for path in allow:
            session.allow_governed_extraction_spec(path)
        for index, (path, grammar) in enumerate(paths):
            try:
                raw = aio.read_authentication_input(path, grammar=grammar, label=f"{label_prefix} {index}")
            except V2AuthenticationInputError as exc:
                outcomes.append((index, "raise", _signature(exc)))
            else:
                outcomes.append((index, "ok", sha(raw)))
        return dict(session.records)


class GrammarFailureEquivalence(_Tmp):
    def test_every_grammar_failure_raises_identically_with_memo_on_and_off(self):
        for name, suffix, raw, reason in GRAMMAR_FAILURES:
            with self.subTest(name=name):
                path = self.write(f"{name}{suffix}", raw)
                off, _, _ = _run_session_reads([(path, "raw")], memo_on=False)
                # Memo on, and warmed twice: a failure is never memoized.
                with arc.analysis_run_caches():
                    first = second = None
                    for attempt in range(2):
                        with V2AuthenticationReadSession() as session:
                            with self.assertRaises(V2AuthenticationInputError) as caught:
                                session.read(path, grammar="raw", label="input 0")
                        if attempt == 0:
                            first = _signature(caught.exception)
                        else:
                            second = _signature(caught.exception)
                    table = arc.memo(aio.GRAMMAR_VERDICT_MEMO)
                    self.assertEqual(table, {}, "a failed parse must never be memoized")
                self.assertEqual(off, [(0, "raise", first)])
                self.assertEqual(first, second)
                self.assertEqual(first[1], reason)

    def test_failure_position_in_a_read_sequence_is_unchanged(self):
        good = self.write("good.json", GOOD_JSON)
        good_copy = self.write("copy/good.json", GOOD_JSON)  # same bytes, other identity: a memo hit
        lines = self.write("rows.jsonl", GOOD_JSONL)
        bad = self.write("bad.json", b'{"k": 1, "k": 2}')
        sequence = [(good, "json"), (lines, "jsonl"), (good_copy, "raw"), (good, "json"), (bad, "json"),
                    (good_copy, "json")]
        off, records_off, calls_off = _run_session_reads(sequence, memo_on=False)
        on, records_on, calls_on = _run_session_reads(sequence, memo_on=True)
        self.assertEqual(on, off)
        self.assertEqual(records_on, records_off)
        self.assertEqual([item[0] for item in off if item[1] == "raise"], [4])
        # The memo removes only repeated successful parses: good.json bytes parse once.
        self.assertEqual(len(calls_off), 6)
        self.assertEqual(calls_on, [(sha(GOOD_JSON), "json", False), (sha(GOOD_JSONL), "jsonl", False),
                                    (sha(b'{"k": 1, "k": 2}'), "json", False)])

    def test_key_separates_grammar_and_vocabulary_flag(self):
        spec_bytes = b'{"estimator_registration": {"x": 1}}'
        spec = self.write("governed/spec.json", spec_bytes)
        other = self.write("plain/spec.json", spec_bytes)
        two_objects = b'{"a": 1}\n{"b": 2}\n'
        as_jsonl = self.write("two.jsonl", two_objects)
        as_json = self.write("two.json", two_objects)
        with arc.analysis_run_caches():
            with V2AuthenticationReadSession() as session:
                session.allow_governed_extraction_spec(spec)
                session.read(spec, grammar="json", label="governed spec")
                with self.assertRaises(V2AuthenticationInputError) as forbidden:
                    session.read(other, grammar="json", label="plain spec")
                session.read(as_jsonl, grammar="jsonl", label="rows")
                with self.assertRaises(V2AuthenticationInputError) as invalid:
                    session.read(as_json, grammar="raw", label="rows as json")
            table = arc.memo(aio.GRAMMAR_VERDICT_MEMO)
        self.assertEqual(forbidden.exception.reason, "v2_authentication_forbidden_json_key")
        self.assertEqual(invalid.exception.reason, "v2_authentication_invalid_json")
        self.assertEqual(set(table), {(sha(spec_bytes), "json", True), (sha(two_objects), "jsonl", False)})

    def test_memo_is_absent_outside_a_run_and_never_counted(self):
        path = self.write("a.json", GOOD_JSON)
        self.assertIsNone(arc.memo(aio.GRAMMAR_VERDICT_MEMO))
        with arc.analysis_run_caches():
            for _ in range(3):
                with V2AuthenticationReadSession() as session:
                    session.read(path, grammar="json", label="a")
            # Blinding: the verdict memo keeps no hit/miss counters.
            self.assertEqual(arc.stats(), {"hits": {}, "misses": {}})
            self.assertEqual(set(arc.memo(aio.GRAMMAR_VERDICT_MEMO)), {(sha(GOOD_JSON), "json", False)})


class MemoRegistration(_Tmp):
    def test_a_memo_hit_registers_the_same_digest_and_counts(self):
        path = self.write("a.json", GOOD_JSON)
        rows = self.write("b.jsonl", GOOD_JSONL)
        sequence = [(path, "json"), (rows, "jsonl"), (path, "raw"), (rows, "raw"), (path, "json")]
        _, records_off, _ = _run_session_reads(sequence, memo_on=False)
        with arc.analysis_run_caches():
            # Warm the memo in an earlier session, as another program scope would.
            with V2AuthenticationReadSession() as warm:
                warm.read(path, grammar="json", label="warm a")
                warm.read(rows, grammar="jsonl", label="warm b")
            with mock.patch.object(aio, "_parse_strict", side_effect=AssertionError("parsed on a hit")):
                with V2AuthenticationReadSession() as session:
                    for item, grammar in sequence:
                        aio.read_authentication_input(item, grammar=grammar, label="x")
                    records_on = dict(session.records)
        self.assertEqual(records_on, records_off)
        record = records_on[str(path)]
        self.assertEqual((record.sha256, record.grammar, record.read_count, record.strict_parse_succeeded),
                         (sha(GOOD_JSON), "json", 3, True))

    def test_nofollow_read_uses_the_memo_and_registers_identically(self):
        self.write("dir/sub/a.json", GOOD_JSON)
        results = []
        for memo_on in (False, True):
            if memo_on:
                with arc.analysis_run_caches(), V2AuthenticationReadSession() as session:
                    for _ in range(2):
                        aio.read_authentication_input_nofollow(self.root / "dir", "sub/a.json", grammar="raw",
                                                               label="nf")
                    results.append(dict(session.records))
                    table = arc.memo(aio.GRAMMAR_VERDICT_MEMO)
            else:
                with V2AuthenticationReadSession() as session:
                    for _ in range(2):
                        aio.read_authentication_input_nofollow(self.root / "dir", "sub/a.json", grammar="raw",
                                                               label="nf")
                    results.append(dict(session.records))
        self.assertEqual(results[0], results[1])
        self.assertEqual(set(table), {(sha(GOOD_JSON), "json", False)})

    def test_changed_bytes_under_one_identity_still_refuse_at_the_same_read(self):
        def run(memo_on: bool, replacement: bytes):
            path = self.write("moving.json", GOOD_JSON)
            other = self.write("other.json", replacement)  # the replacement bytes, pre-warmed
            outcomes = []

            def body():
                if replacement != b"{,}":
                    with V2AuthenticationReadSession() as warm:
                        warm.read(other, grammar="json", label="warm")
                with V2AuthenticationReadSession() as session:
                    for index in range(4):
                        if index == 2:
                            path.write_bytes(replacement)
                        try:
                            session.read(path, grammar="json", label=f"read {index}")
                        except V2AuthenticationInputError as exc:
                            outcomes.append((index, _signature(exc)))
                            break
                        outcomes.append((index, "ok"))

            if memo_on:
                with arc.analysis_run_caches():
                    body()
            else:
                body()
            return outcomes

        for replacement in (b'{"alpha": 2}', b"{,}"):
            with self.subTest(replacement=replacement):
                off = run(False, replacement)
                on = run(True, replacement)
                self.assertEqual(on, off)
                self.assertEqual(on[-1][0], 2)
                expected = (V2_AUTHENTICATION_INPUT_CHANGED if replacement != b"{,}"
                            else "v2_authentication_invalid_json")
                self.assertEqual(on[-1][1][1], expected)


class PinnedAndIngestMemo(_Tmp):
    def test_pinned_read_checks_the_pin_before_any_memo_or_parse(self):
        self.write("d/a.json", GOOD_JSON)
        bad = b'{"a": 1, "a": 1}'
        self.write("d/bad.json", bad)
        with arc.analysis_run_caches():
            with V2AuthenticationReadSession() as warm:
                warm.read(self.root / "d/a.json", grammar="json", label="warm")
            with mock.patch.object(aio, "_parse_strict", side_effect=AssertionError("parsed on a hit")):
                with V2AuthenticationReadSession() as session:
                    session.read_nofollow_pinned(self.root / "d", "a.json", expected_sha256=sha(GOOD_JSON),
                                                 grammar="json", label="pinned")
                    with self.assertRaises(V2AuthenticationInputError) as pin:
                        session.read_nofollow_pinned(self.root / "d", "bad.json", expected_sha256=sha(GOOD_JSON),
                                                     grammar="json", label="pinned bad")
            self.assertEqual(pin.exception.reason, aio.V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH)
            for _ in range(2):
                with V2AuthenticationReadSession() as session:
                    with self.assertRaises(V2AuthenticationInputError) as grammar:
                        session.read_nofollow_pinned(self.root / "d", "bad.json", expected_sha256=sha(bad),
                                                     grammar="json", label="pinned bad")
                self.assertEqual(grammar.exception.reason, "v2_authentication_duplicate_json_key")
            self.assertEqual(set(arc.memo(aio.GRAMMAR_VERDICT_MEMO)), {(sha(GOOD_JSON), "json", False)})

    def test_git_ingest_uses_the_memo_and_registers_identically(self):
        outcomes = []
        for memo_on in (False, True):
            def body():
                with V2AuthenticationReadSession() as session:
                    for _ in range(2):
                        aio.ingest_git_authentication_input("c/x.json", GOOD_JSON, grammar="raw", label="g")
                    with self.assertRaises(V2AuthenticationInputError) as caught:
                        aio.ingest_git_authentication_input("c/y.json", b"[1,]", label="g")
                    return dict(session.records), _signature(caught.exception)
            if memo_on:
                with arc.analysis_run_caches():
                    outcomes.append(body())
                    self.assertEqual(set(arc.memo(aio.GRAMMAR_VERDICT_MEMO)), {(sha(GOOD_JSON), "json", False)})
            else:
                outcomes.append(body())
        self.assertEqual(outcomes[0], outcomes[1])


class RecordedCapabilityPath(_Tmp):
    """Session-less capability-path reads (BundleReader.path -> reducer read_bytes) are recorded."""

    def test_plain_path_without_recorder_and_recorded_path_with_one(self):
        self.write("b/m.json", GOOD_JSON)
        plain = aio.v2_authentication_path(self.root / "b")
        self.assertIs(type(plain), type(Path()))
        with aio.recording_authentication_reads() as rows:
            recorded = aio.v2_authentication_path(self.root / "b")
            child = recorded / "m.json"
            self.assertEqual(child, self.root / "b/m.json")
            self.assertEqual(child.read_bytes(), GOOD_JSON)
            self.assertEqual(child.read_text(), GOOD_JSON.decode())
            with child.open("rb") as handle:
                self.assertEqual(handle.read(), GOOD_JSON)
            with child.open() as handle:
                self.assertEqual(handle.read(), GOOD_JSON.decode())
            self.assertTrue(child.exists())
        self.assertEqual([row.api for row in rows],
                         ["v2_path.read_bytes", "v2_path.read_text", "v2_path.open", "v2_path.open"])
        for row in rows:
            self.assertEqual((row.identity, row.sha256, row.grammar, row.caller_grammar, row.in_session,
                              row.grammar_verified), (str(self.root / "b/m.json"), sha(GOOD_JSON), "json", "raw",
                                                      False, False))
        with V2AuthenticationReadSession():
            self.assertIsInstance(aio.v2_authentication_path(self.root / "b"), aio.V2AuthenticationPath)

    def test_recorded_path_never_routes_through_a_later_session(self):
        bad = b'{"a": 1, "a": 2}'
        self.write("b/bad.json", bad)
        with aio.recording_authentication_reads() as rows:
            path = aio.v2_authentication_path(self.root / "b") / "bad.json"
        with V2AuthenticationReadSession() as session:
            self.assertEqual(path.read_bytes(), bad)  # a plain Path would not parse either
            self.assertEqual(session.records, {})
        self.assertEqual(rows, [])  # no recorder in scope any more: nothing recorded

    def test_recorded_path_writes_and_errors_match_path(self):
        with aio.recording_authentication_reads() as rows:
            base = aio.v2_authentication_path(self.root)
            with (base / "out.txt").open("w") as handle:
                handle.write("x")
            for call in (lambda p: p.read_bytes(), lambda p: p.read_text(), lambda p: p.open("rb"),
                         lambda p: p.open()):
                for target in ("missing.json", ""):
                    with self.subTest(target=target):
                        errors = []
                        for candidate in (Path(self.root) / target, base / target):
                            try:
                                call(candidate)
                            except OSError as exc:
                                errors.append((type(exc), exc.errno, str(exc)))
                        self.assertEqual(len(errors), 2)
                        self.assertEqual(errors[0], errors[1])
        self.assertEqual(rows, [])
        self.assertEqual((self.root / "out.txt").read_text(), "x")


class EnsureGrammarVerdict(_Tmp):
    def test_raises_exactly_what_session_read_raises(self):
        for name, suffix, raw, _ in GRAMMAR_FAILURES:
            with self.subTest(name=name):
                path = self.write(f"{name}{suffix}", raw)
                identity = str(path.resolve(strict=False))
                with V2AuthenticationReadSession() as session:
                    with self.assertRaises(V2AuthenticationInputError) as by_read:
                        session.read(path, grammar="raw", label="lbl")
                with arc.analysis_run_caches():
                    with self.assertRaises(V2AuthenticationInputError) as by_function:
                        aio.ensure_grammar_verdict(raw, sha(raw), aio.forced_grammar(identity, "raw"), False, "lbl")
                    with V2AuthenticationReadSession() as session:
                        with self.assertRaises(V2AuthenticationInputError) as by_bridge:
                            session.ensure_grammar_verdict(identity, raw, caller_grammar="raw", label="lbl")
                    self.assertEqual(arc.memo(aio.GRAMMAR_VERDICT_MEMO), {})
                self.assertEqual(_signature(by_function.exception), _signature(by_read.exception))
                self.assertEqual(_signature(by_bridge.exception), _signature(by_read.exception))

    def test_success_is_recorded_and_then_serves_session_reads(self):
        path = self.write("a.json", GOOD_JSON)
        with arc.analysis_run_caches():
            aio.ensure_grammar_verdict(GOOD_JSON, sha(GOOD_JSON), "json", False, "bridge")
            self.assertEqual(set(arc.memo(aio.GRAMMAR_VERDICT_MEMO)), {(sha(GOOD_JSON), "json", False)})
            with mock.patch.object(aio, "_parse_strict", side_effect=AssertionError("parsed on a hit")):
                with V2AuthenticationReadSession() as session:
                    session.read(path, grammar="json", label="a")

    def test_a_mismatched_sha_neither_reads_nor_writes_the_memo(self):
        with arc.analysis_run_caches():
            aio.ensure_grammar_verdict(GOOD_JSON, "0" * 64, "json", False, "bridge")
            self.assertEqual(arc.memo(aio.GRAMMAR_VERDICT_MEMO), {})
            table = arc.memo(aio.GRAMMAR_VERDICT_MEMO)
            table[("0" * 64, "json", False)] = True  # a poisoned entry under the claimed sha
            with self.assertRaises(V2AuthenticationInputError):
                aio.ensure_grammar_verdict(b"{,}", "0" * 64, "json", False, "bridge")

    def test_bridge_uses_the_consumers_forced_grammar_not_the_recorded_one(self):
        # A session-less fill read invalid JSON bytes under a non-JSON name with caller grammar raw.
        raw = b'{"a": 1, "a": 2}'
        fill_path = self.write("fill/payload.dat", raw)
        with aio.recording_authentication_reads() as rows:
            aio.read_authentication_input(fill_path, grammar="raw", label="fill")
        (row,) = rows
        self.assertEqual((row.grammar, row.caller_grammar, row.grammar_verified, row.in_session),
                         ("raw", "raw", False, False))
        consumer_identity = str((self.root / "consumer" / "payload.json").resolve(strict=False))
        with arc.analysis_run_caches(), V2AuthenticationReadSession() as session:
            # The recorded grammar would wave the bytes through ...
            aio.ensure_grammar_verdict(raw, row.sha256, row.grammar, row.vocabulary_flag, "fill")
            # ... the consumer's own forced grammar refuses them, exactly as its read would.
            with self.assertRaises(V2AuthenticationInputError) as caught:
                session.ensure_grammar_verdict(consumer_identity, raw, caller_grammar=row.caller_grammar,
                                               label="consumer", sha256=row.sha256)
        self.assertEqual(caught.exception.reason, "v2_authentication_duplicate_json_key")
        self.assertEqual(aio.forced_grammar(consumer_identity, row.caller_grammar), "json")

    def test_bridge_uses_the_consumers_vocabulary_flag(self):
        raw = b'{"estimator_registration": 1}'
        spec = self.write("spec.json", raw)
        identity = str(spec.resolve(strict=False))
        with arc.analysis_run_caches():
            with V2AuthenticationReadSession() as session:
                with self.assertRaises(V2AuthenticationInputError):
                    session.ensure_grammar_verdict(identity, raw, caller_grammar="json", label="spec")
            with V2AuthenticationReadSession() as session:
                session.allow_governed_extraction_spec(spec)
                self.assertTrue(session.vocabulary_flag(identity))
                self.assertEqual(session.ensure_grammar_verdict(identity, raw, caller_grammar="raw", label="spec"),
                                 "json")
                self.assertEqual(session.records, {}, "the bridge registers nothing")


class Recorder(_Tmp):
    def _fixture(self):
        self.write("bundle/meta.json", GOOD_JSON)
        self.write("bundle/rows.jsonl", GOOD_JSONL)
        self.write("bundle/trace.csv", b"timestamp_s,power_w\r\n1,2\r\n3,4\n")
        self.write("bundle/nested/deep/blob.bin", b"\x00\x01binary")

    def _reads(self, base: Path):
        """Every authentication_io read API, against paths under ``base`` (may be relative)."""

        out = []
        out.append(aio.read_authentication_input(base / "meta.json", grammar="json", label="meta"))
        out.append(aio.read_authentication_text(base / "rows.jsonl", grammar="jsonl", label="rows"))
        out.append(aio.read_authentication_text(base / "trace.csv", grammar="raw", label="trace text",
                                                encoding="utf-8", errors="strict"))
        with aio.open_authentication_input(base / "trace.csv", grammar="raw", label="trace", newline="") as h:
            out.append(h.read())
        with aio.open_authentication_input(base / "trace.csv", "rb", grammar="raw", label="trace b") as h:
            out.append(h.read())
        out.append(aio.read_authentication_input_nofollow(base, "nested/deep/blob.bin", grammar="raw",
                                                          label="blob"))
        out.append(aio.read_authentication_input_nofollow(base / "nested", "deep/blob.bin", grammar="raw",
                                                          label="blob 2"))
        out.append(aio.sha256_authentication_input(base / "nested/deep/blob.bin", label="blob digest"))
        out.append(aio.ingest_git_authentication_input("configs/x.json", GOOD_JSON, label="git x"))
        return out

    def test_recorder_is_inert_when_unset(self):
        self._fixture()
        self.assertIsNone(aio._READ_RECORDER.get())
        self.assertFalse(aio.authentication_read_recording_active())
        plain = self._reads(self.root / "bundle")
        with aio.recording_authentication_reads() as rows:
            recorded = self._reads(self.root / "bundle")
        self.assertEqual(recorded, plain)
        self.assertEqual(len(rows), 9)
        self.assertIsNone(aio._READ_RECORDER.get())
        # Outside a recording scope nothing accumulates anywhere.
        self._reads(self.root / "bundle")
        self.assertEqual(len(rows), 9)

    def test_sessionless_rows_carry_absolute_identities_including_nofollow_dir_fd(self):
        self._fixture()
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        with aio.recording_authentication_reads() as rows:
            self._reads(Path("bundle"))
        bundle = self.root / "bundle"
        expected = [
            ("read_authentication_input", bundle / "meta.json", sha(GOOD_JSON), "json", "json", None),
            ("read_authentication_text", bundle / "rows.jsonl", sha(GOOD_JSONL), "jsonl", "jsonl", None),
            ("read_authentication_text", bundle / "trace.csv", None, "raw", "raw", None),
            ("open_authentication_input", bundle / "trace.csv", None, "raw", "raw", None),
            ("open_authentication_input", bundle / "trace.csv", None, "raw", "raw", None),
            ("read_authentication_input_nofollow", bundle / "nested/deep/blob.bin", None, "raw", "raw",
             "nested/deep/blob.bin"),
            ("read_authentication_input_nofollow", bundle / "nested/deep/blob.bin", None, "raw", "raw",
             "deep/blob.bin"),
            ("sha256_authentication_input", bundle / "nested/deep/blob.bin", None, "raw", "raw", None),
        ]
        for row, (api, path, digest, grammar, caller, relative) in zip(rows, expected):
            self.assertEqual(row.api, api)
            self.assertTrue(os.path.isabs(row.identity), row)
            self.assertEqual(row.identity, str(path))
            self.assertEqual(row.sha256, digest or sha(path.read_bytes()))
            self.assertEqual((row.grammar, row.caller_grammar, row.relative), (grammar, caller, relative))
            self.assertEqual((row.in_session, row.grammar_verified, row.vocabulary_flag), (False, False, False))
        self.assertEqual(rows[-1].identity, "git:HEAD:configs/x.json")
        self.assertEqual(rows[-1].grammar, "json")

    def test_session_rows_carry_absolute_identities_and_verified_grammar(self):
        self._fixture()
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        with aio.recording_authentication_reads() as rows, V2AuthenticationReadSession() as session:
            plain = self._reads(Path("bundle"))
            session.read_nofollow_pinned(Path("bundle"), "nested/deep/blob.bin",
                                         expected_sha256=sha(b"\x00\x01binary"), grammar="raw", label="pinned")
            records = dict(session.records)
        apis = [row.api for row in rows]
        self.assertEqual(apis, ["session.read", "session.read", "session.read", "session.read", "session.read",
                                "session.read_nofollow", "session.read_nofollow", "session.sha256_streaming_raw",
                                "session.ingest", "session.read_nofollow_pinned"])
        for row in rows:
            self.assertTrue(row.identity.startswith("git:") or os.path.isabs(row.identity), row)
            self.assertTrue(row.in_session and row.grammar_verified)
            self.assertEqual(records[row.identity].sha256, row.sha256)
            self.assertEqual(records[row.identity].grammar, row.grammar)
        self.assertEqual(rows[5].relative, "nested/deep/blob.bin")
        self.assertEqual(rows[6].relative, "deep/blob.bin")
        self.assertEqual(len(plain), 9)

    def test_nested_scopes_each_receive_rows_and_failed_reads_record_nothing(self):
        self._fixture()
        bad = self.write("bundle/bad.json", b"{,}")
        with aio.recording_authentication_reads() as outer:
            aio.read_authentication_input(self.root / "bundle/meta.json", grammar="json", label="m")
            with aio.recording_authentication_reads() as inner:
                aio.read_authentication_input(self.root / "bundle/rows.jsonl", grammar="jsonl", label="r")
                with V2AuthenticationReadSession() as session:
                    with self.assertRaises(V2AuthenticationInputError):
                        session.read(bad, grammar="json", label="bad")
                with self.assertRaises(FileNotFoundError):
                    aio.read_authentication_input(self.root / "missing.json", grammar="json", label="gone")
        self.assertEqual([row.api for row in outer], ["read_authentication_input"] * 2)
        self.assertEqual(inner, [outer[1]])

    def test_a_fresh_context_does_not_inherit_the_recorder(self):
        self._fixture()
        with aio.recording_authentication_reads() as rows:
            contextvars.Context().run(aio.read_authentication_input, self.root / "bundle/meta.json",
                                      grammar="json", label="m")
            contextvars.copy_context().run(aio.read_authentication_input, self.root / "bundle/meta.json",
                                           grammar="json", label="m")
        self.assertEqual(len(rows), 1)


class RecorderSessionlessSemantics(_Tmp):
    """With the recorder set, session-less reads return and raise exactly as without it."""

    def _both(self, call):
        results = []
        for recording in (False, True):
            try:
                if recording:
                    with aio.recording_authentication_reads():
                        value = call()
                else:
                    value = call()
            except Exception as exc:  # noqa: BLE001 - the comparison is the point
                results.append(("raise", type(exc), str(exc), getattr(exc, "errno", None),
                                getattr(exc, "filename", None)))
            else:
                results.append(("ok", type(value), value))
        return results

    def test_text_reads_decode_and_fail_identically(self):
        cases = {
            "crlf.txt": b"a\r\nb\rc\nd",
            "bom.txt": b"\xef\xbb\xbfhello",
            "latin.txt": "café".encode("latin-1"),
            "badutf8.txt": b"ok\n\xff\xfe tail",
        }
        for name, raw in cases.items():
            self.write(name, raw)
        for name in cases:
            for kwargs in ({}, {"encoding": "utf-8"}, {"encoding": "latin-1"}, {"encoding": "utf-8-sig"},
                           {"encoding": "utf-8", "errors": "replace"}):
                with self.subTest(name=name, kwargs=kwargs):
                    plain, recorded = self._both(lambda: aio.read_authentication_text(
                        self.root / name, grammar="raw", label="t", **kwargs))
                    self.assertEqual(recorded, plain)

    def test_open_handles_serve_identical_content(self):
        self.write("trace.csv", b"h1,h2\r\n1,2\r\n3,4\n5,6")
        for mode, kwargs in (("r", {"newline": ""}), ("r", {}), ("rt", {"encoding": "utf-8"}), ("rb", {})):
            with self.subTest(mode=mode, kwargs=kwargs):
                def call():
                    with aio.open_authentication_input(self.root / "trace.csv", mode, grammar="raw", label="t",
                                                       **kwargs) as handle:
                        first = handle.readline()
                        return first, handle.read()
                plain, recorded = self._both(call)
                self.assertEqual(recorded, plain)

    def test_missing_directory_and_unreadable_inputs_raise_identically(self):
        directory = self.root / "adir"
        directory.mkdir()
        locked = self.write("locked.json", GOOD_JSON)
        locked.chmod(0)
        self.addCleanup(locked.chmod, 0o600)
        calls = []
        for target in (self.root / "missing.json", directory, locked):
            calls.extend([
                lambda t=target: aio.read_authentication_input(t, grammar="json", label="x"),
                lambda t=target: aio.read_authentication_text(t, grammar="json", label="x"),
                lambda t=target: aio.open_authentication_input(t, grammar="json", label="x"),
                lambda t=target: aio.open_authentication_input(t, "rb", grammar="json", label="x"),
                lambda t=target: aio.sha256_authentication_input(t, label="x"),
            ])
        calls.append(lambda: aio.read_authentication_input_nofollow(self.root, "missing.json", grammar="json",
                                                                    label="x"))
        calls.append(lambda: aio.read_authentication_input_nofollow(self.root, "adir", grammar="raw", label="x"))
        calls.append(lambda: aio.read_authentication_input_nofollow(self.root, "../x", grammar="raw", label="x"))
        calls.append(lambda: aio.open_authentication_input(self.root / "x", "w", grammar="raw", label="x"))
        for index, call in enumerate(calls):
            with self.subTest(index=index):
                plain, recorded = self._both(call)
                self.assertEqual(plain[0], "raise")
                self.assertEqual(recorded, plain)

    def test_symlinked_nofollow_component_refuses_identically(self):
        self.write("real/a.json", GOOD_JSON)
        (self.root / "link").symlink_to(self.root / "real")
        plain, recorded = self._both(lambda: aio.read_authentication_input_nofollow(
            self.root, "link/a.json", grammar="json", label="x"))
        self.assertEqual(plain[0], "raise")
        self.assertEqual(recorded, plain)


class HazardRefusalSites(unittest.TestCase):
    def test_raise_site_counts_and_guards_match_the_allowlist(self):
        file = "joulewise/authentication_io.py"
        sites = census.scan([file])
        document = json.loads(census.ALLOWLIST.read_text(encoding="utf-8"))
        entries = {(e["file"], e["function"], e["kind"], e["detail"]): e
                   for e in document["sites"] if e["file"] == file}
        counts = census.site_counts(sites)
        guards = census.site_guards(sites)
        self.assertEqual(set(counts), set(entries))
        for key, entry in entries.items():
            self.assertEqual((counts[key], guards[key]), (entry["count"], entry["guard"]), key)
        self.assertEqual(sum(counts.values()), 19)
        # The new public surface adds no raise of its own.
        for function in ("ensure_grammar_verdict", "forced_grammar", "_parse_strict_memoized",
                         "recording_authentication_reads", "_record_read", "_record_sessionless",
                         "_absolute_identity", "V2AuthenticationReadSession.ensure_grammar_verdict",
                         "V2AuthenticationReadSession.vocabulary_flag"):
            self.assertFalse([key for key in counts if key[1] == function], function)


if __name__ == "__main__":
    unittest.main()
