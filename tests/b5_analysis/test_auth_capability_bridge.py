"""D-188 AUTH-IO-2 (Sol #3): session-less recording represents capability reads.

``authentication_io.RECORDS_CAPABILITY_READS`` lets the run-scoped store bridge a
session-less fill into a V2 session.  These tests check, on synthetic trees and
on the committed synthetic S10 ALPHA members only:

* every read an active session would register is recorded session-less with the
  same identity, digest, effective grammar and label, in the same order,
  including capability-path reads (``BundleReader.path`` and the reducer's
  derived calibration reads) and ``V2AuthenticationPath`` instances;
* a recording scope is marked ``unrepresented`` wherever session-less code
  cannot stand for the in-session computation, and such a fill never serves a
  session;
* a bridged hit re-runs the strict grammar check under the consumer's own
  grammar and vocabulary flag, so a duplicate-key or forbidden-key JSON that
  session-less parsing accepted refuses exactly as the serial in-session read;
* tracers: for every real leaf (L1, L2, L3, L5, L6) on S10 members, and for a
  floor-extraction replay over two cells (strict validation, reduction,
  calibration verification and environment refusals through the whole-window
  extraction checks), the session's registrations equal the session-less rows.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import authentication_io as aio

MODULE = __name__
CALLS: dict[str, int] = {}


def _called(name: str) -> None:
    CALLS[name] = CALLS.get(name, 0) + 1


@contextlib.contextmanager
def traced_registrations():
    """Every ``V2AuthenticationReadSession._register`` call, in order."""

    log: list[tuple[str, str, str, str]] = []
    original = aio.V2AuthenticationReadSession._register

    def register(self, identity, digest, grammar, label):
        log.append((identity, digest, grammar, label))
        return original(self, identity, digest, grammar, label)

    with mock.patch.object(aio.V2AuthenticationReadSession, "_register", register):
        yield log


def mapped(rows) -> list[tuple[str, str, str, str]]:
    """Session-less rows as the registrations a consumer session would make."""

    return [(row.identity, row.sha256, aio.forced_grammar(row.identity, row.caller_grammar), row.label)
            for row in rows]


def outcome(fn):
    try:
        return ("ok", fn())
    except Exception as exc:  # noqa: BLE001 - the outcome is compared, not handled
        return ("raise", type(exc).__name__, str(exc))


def make_tree(parent: Path, name: str = "bundle", **files: bytes) -> Path:
    root = parent / name
    root.mkdir(parents=True)
    contents = files or {"metadata.json": b'{"a": 1}', "data.txt": b"payload", "sub/inner.json": b'{"b": 2}'}
    for relative, raw in contents.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return root


# ------------------------------------------------------------- synthetic leaves


def capability_leaf(path, factor):
    """Reads like the reducer: through the capability path and paths derived from it."""

    _called("capability_leaf")
    base = aio.v2_authentication_path(path)
    metadata = json.loads((base / "metadata.json").read_bytes())  # json.loads accepts duplicate keys
    data = (base / "sub").parent.resolve() / "data.txt"
    return {"metadata": metadata, "data": hashlib.sha256(data.read_bytes()).hexdigest(), "factor": factor}


def querying_leaf(path, factor):
    """Branches on session presence at a site the store does not represent."""

    _called("querying_leaf")
    raw = (aio.v2_authentication_path(path) / "data.txt").read_bytes()
    return [len(raw), aio.active_v2_authentication_session() is None, factor]


def nested_session_leaf(path, factor):
    """Enters its own session (inside a consumer's session this raises)."""

    _called("nested_session_leaf")
    with aio.V2AuthenticationReadSession():
        raw = aio.read_authentication_input(Path(path) / "data.txt", grammar="raw", label="nested read")
    return [len(raw), factor]


def path_value_leaf(path, factor):
    """Returns a capability-derived path (a session's run would return a registering one)."""

    _called("path_value_leaf")
    target = aio.v2_authentication_path(path) / "data.txt"
    target.read_bytes()
    return {"target": target, "factor": factor}


def outer_leaf(path, factor):
    _called("outer_leaf")
    return [vdl.call("T_query", querying_leaf, path, factor), factor]


def _spec(leaf_id, fn):
    return vdl.LeafSpec(leaf_id, (f"{MODULE}:{fn.__qualname__}",), (("path", vdl.TREE), ("factor", vdl.SCALAR)))


SPECS = (_spec("T_cap", capability_leaf), _spec("T_query", querying_leaf), _spec("T_nested", nested_session_leaf),
         _spec("T_path_value", path_value_leaf), _spec("T_outer", outer_leaf))


class FakeDeadline:
    def __init__(self):
        self.firings = 0


@contextlib.contextmanager
def run(mode=vdl.ON, physics=None):
    with arc.analysis_run_caches({} if physics is None else physics, vdl_mode=mode) as caches:
        caches.deadline = FakeDeadline()
        yield caches


@contextlib.contextmanager
def session(physics=None):
    """A V2 session; with ``physics``, its calibration physics cache is that shared dict."""

    with aio.V2AuthenticationReadSession() as active:
        if physics is not None:
            active.instrument_calibration_physics_cache = physics
        yield active


class _Tmp(unittest.TestCase):
    def setUp(self):
        CALLS.clear()
        self.tmp = Path(tempfile.mkdtemp(prefix="authio2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        registration = vdl._registered(*SPECS)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)
        self.tree = make_tree(self.tmp)


# ------------------------------------------------------------ the recorder itself


class CapabilityRecording(_Tmp):
    def test_the_capability_flag_is_declared_and_scopes_carry_unrepresented(self):
        self.assertIs(aio.RECORDS_CAPABILITY_READS, True)
        self.assertTrue(vdl._AUTH.capability_complete())
        with aio.recording_authentication_reads() as rows:
            self.assertIsInstance(rows, list)
            self.assertEqual(rows.unrepresented, [])

    def test_v2_capability_path_records_sessionless_reads_like_its_recorded_twin(self):
        target = self.tree / "metadata.json"
        capability = aio.V2AuthenticationPath(target)
        self.assertEqual(capability.read_bytes(), target.read_bytes())  # no recorder: plain Path
        with aio.recording_authentication_reads() as rows:
            raw = capability.read_bytes()
            text = capability.read_text()
            with capability.open("rb") as handle:
                opened = handle.read()
        self.assertEqual((raw, text, opened), (target.read_bytes(), target.read_text(), target.read_bytes()))
        identity = str(target.resolve())
        self.assertEqual([(row.api, row.identity, row.label) for row in rows], [
            ("v2_path.read_bytes", identity, f"v2 path capability {capability}"),
            ("v2_path.read_text", identity, f"v2 path capability {capability}"),
            ("v2_path.open", identity, f"v2 path capability {capability}")])
        self.assertTrue(all(row.sha256 == hashlib.sha256(raw).hexdigest() and row.grammar == "json"
                            and row.caller_grammar == "raw" and not row.in_session for row in rows))
        self.assertEqual(rows.unrepresented, [])

    def test_sessionless_rows_equal_the_session_registrations(self):
        def reads():
            base = aio.v2_authentication_path(self.tree)
            values = [(base / "metadata.json").read_bytes(), (base / "sub" / "inner.json").read_text(),
                      (base / "sub").parent.resolve().joinpath("data.txt").open("rb").read(),
                      aio.read_authentication_input(self.tree / "data.txt", grammar="raw", label="api read"),
                      aio.read_authentication_input_nofollow(self.tree, "sub/inner.json", grammar="json",
                                                             label="nofollow read"),
                      aio.sha256_authentication_input(self.tree / "metadata.json", label="digest read"),
                      aio.read_authentication_text(self.tree / "data.txt", grammar="raw", label="text read")]
            with aio.open_authentication_input(self.tree / "data.txt", "r", grammar="raw", label="open") as handle:
                values.append(handle.read())
            return values

        with traced_registrations() as registered, aio.V2AuthenticationReadSession():
            in_session = reads()
        with aio.recording_authentication_reads() as rows:
            sessionless = reads()
        self.assertEqual(sessionless, in_session)
        self.assertEqual(mapped(rows), registered)
        self.assertEqual(len(registered), 8)
        self.assertEqual(rows.unrepresented, [])

    def test_every_divergence_marks_the_scope_without_changing_the_read(self):
        crlf = make_tree(self.tmp, "crlf", **{"notes.txt": b"a\r\nb\r\n", "bad.txt": b"\xff\xfe"})
        notes = aio.V2AuthenticationPath(crlf / "notes.txt")  # session-less: reads as its recorded twin
        twin = aio._RecordedAuthenticationPath(crlf / "notes.txt")

        def nested_session():
            with aio.V2AuthenticationReadSession():
                pass

        cases = {
            "v2 session entered while recording": nested_session,
            "session presence queried while recording": aio.active_v2_authentication_session,
            "text read differs from the session decode": lambda: aio.read_authentication_text(
                crlf / "notes.txt", grammar="raw", label="crlf"),
            "capability read_text newline argument": lambda: twin.read_text(newline=""),
            "capability path repr": lambda: repr(twin),
            "capability read-write open": lambda: notes.open("r+").close(),
            "capability open buffering argument": lambda: notes.open("rb", buffering=0).close(),
            "text read failed to decode": lambda: aio.read_authentication_text(
                crlf / "bad.txt", grammar="raw", label="bad", encoding="utf-8"),
        }
        for reason, fn in cases.items():
            with self.subTest(reason=reason):
                with aio.recording_authentication_reads() as outer:
                    with aio.recording_authentication_reads() as inner:
                        recorded = outcome(fn)
                plain = outcome(fn)
                self.assertEqual(recorded, plain)  # recording never changes a read's outcome
                self.assertIn(reason, inner.unrepresented)
                self.assertEqual(inner.unrepresented, outer.unrepresented)
        with aio.recording_authentication_reads() as rows:
            recorded = notes.read_text()  # universal newlines: differs from the session's bytes.decode
        self.assertEqual(recorded, (crlf / "notes.txt").read_text())
        self.assertEqual(rows.unrepresented, ["text read differs from the session decode"])

    def test_open_divergence_compares_codec_and_error_handler(self):
        class Handle:
            def __init__(self, encoding, errors):
                self.encoding, self.errors = encoding, errors

        for handle, encoding, errors, marked in ((Handle("UTF-8", "strict"), None, None, False),
                                                 (Handle("utf_8", "strict"), "utf-8", "strict", False),
                                                 (Handle("latin-1", "strict"), None, None, True),
                                                 (Handle("UTF-8", "replace"), None, None, True)):
            with self.subTest(encoding=handle.encoding, errors=handle.errors):
                with aio.recording_authentication_reads() as rows:
                    aio._note_open_divergence(handle, encoding, errors)
                self.assertEqual(bool(rows.unrepresented), marked)

    def test_represented_query_sites_are_exactly_the_store_and_strict_problems(self):
        from joulewise import cli

        self.assertTrue(aio._query_site_represented(cli._strict_problems.__code__))
        self.assertTrue(aio._query_site_represented(vdl._AuthAdapter.session.__code__))
        self.assertFalse(aio._query_site_represented(querying_leaf.__code__))
        self.assertFalse(aio._query_site_represented(cli.validate_bundle.__code__))
        with aio.recording_authentication_reads() as rows:
            vdl._AUTH.session()
        self.assertEqual(rows.unrepresented, [])
        with aio.V2AuthenticationReadSession(), aio.recording_authentication_reads() as rows:
            aio.active_v2_authentication_session()  # a session is active: nothing to represent
        self.assertEqual(rows.unrepresented, [])

    def test_markers_without_a_recorder_are_inert(self):
        aio._note_unrepresented("anything")
        self.assertIsNone(aio.active_v2_authentication_session())
        self.assertFalse(aio.authentication_read_recording_active())


# ------------------------------------------------------------ bridging in the store


class Bridging(_Tmp):
    def serial(self, tree, *, allow=None):
        with aio.V2AuthenticationReadSession() as session:
            if allow is not None:
                session.allow_governed_extraction_spec(allow)
            value = outcome(lambda: capability_leaf(tree, 1))
        return value, dict(session.records), list(session.records)

    def test_a_bridged_hit_reruns_the_grammar_check_under_the_consumers_grammar(self):
        expected, records, order = self.serial(self.tree)
        CALLS.clear()
        verdicts = []
        original = aio.V2AuthenticationReadSession.ensure_grammar_verdict

        def spy(session, identity, raw, **kwargs):
            grammar = original(session, identity, raw, **kwargs)
            verdicts.append((identity, kwargs["caller_grammar"], grammar))
            return grammar

        with run() as caches, mock.patch.object(aio.V2AuthenticationReadSession, "ensure_grammar_verdict", spy):
            self.assertEqual(vdl.call("T_cap", capability_leaf, self.tree, 1), expected[1])  # session-less fill
            with aio.V2AuthenticationReadSession() as consumer:
                value = vdl.call("T_cap", capability_leaf, self.tree, 1)
            memo = dict(arc.memo(vdl.GRAMMAR_VERDICT_MEMO))
            counters = caches.vdl.restricted_counters()
        self.assertEqual(value, expected[1])
        self.assertEqual(CALLS["capability_leaf"], 1)
        self.assertEqual(counters["T_cap:hit"], 1)
        self.assertEqual(dict(consumer.records), records)
        self.assertEqual(list(consumer.records), order)
        metadata = str((self.tree / "metadata.json").resolve())
        # The session-less read asked for "raw"; the consumer's own grammar for the identity is json.
        self.assertEqual(verdicts, [(metadata, "raw", "json")])
        digest = hashlib.sha256((self.tree / "metadata.json").read_bytes()).hexdigest()
        self.assertIs(memo.get((digest, "json", False)), True)
        self.assertEqual(records[metadata].grammar, "json")

    def test_duplicate_key_json_read_through_a_capability_refuses_in_the_session(self):
        bad = make_tree(self.tmp, "bad", **{"metadata.json": b'{"a": 1, "a": 2}', "data.txt": b"x",
                                            "sub/inner.json": b"{}"})
        expected, records, _ = self.serial(bad)
        self.assertEqual(expected[:2], ("raise", "V2AuthenticationInputError"))
        CALLS.clear()
        with run() as caches:
            self.assertEqual(vdl.call("T_cap", capability_leaf, bad, 1)["metadata"], {"a": 2})  # stored
            with aio.V2AuthenticationReadSession() as consumer:
                refused = outcome(lambda: vdl.call("T_cap", capability_leaf, bad, 1))
            counters = caches.vdl.restricted_counters()
        self.assertEqual(refused, expected)
        self.assertEqual(dict(consumer.records), records)
        self.assertEqual(CALLS["capability_leaf"], 2)
        self.assertEqual(counters["T_cap:hit_discarded"], 1)

    def test_the_consumers_vocabulary_flag_decides_the_verdict(self):
        governed = make_tree(self.tmp, "governed", **{
            "metadata.json": b'{"estimator_registration": {"x": 1}}', "data.txt": b"x", "sub/inner.json": b"{}"})
        spec_path = governed / "metadata.json"
        refused, refused_records, _ = self.serial(governed)
        allowed, allowed_records, allowed_order = self.serial(governed, allow=spec_path)
        self.assertEqual(refused[:2], ("raise", "V2AuthenticationInputError"))
        self.assertEqual(allowed[0], "ok")
        CALLS.clear()
        with run():
            vdl.call("T_cap", capability_leaf, governed, 1)
            with aio.V2AuthenticationReadSession() as plain:
                plain_outcome = outcome(lambda: vdl.call("T_cap", capability_leaf, governed, 1))
            with aio.V2AuthenticationReadSession() as consumer:
                consumer.allow_governed_extraction_spec(spec_path)
                consumer_outcome = outcome(lambda: vdl.call("T_cap", capability_leaf, governed, 1))
        self.assertEqual(plain_outcome, refused)
        self.assertEqual(dict(plain.records), refused_records)
        self.assertEqual(consumer_outcome, allowed)
        self.assertEqual(dict(consumer.records), allowed_records)
        self.assertEqual(list(consumer.records), allowed_order)
        # The session-less fill, the refused consumer's recompute; the governed consumer was served.
        self.assertEqual(CALLS["capability_leaf"], 2)

    def assert_never_serves_a_session(self, leaf_id, fn):
        with aio.V2AuthenticationReadSession() as serial:
            expected = outcome(lambda: fn(self.tree, 1))
        CALLS.clear()
        with run() as caches:
            first = vdl.call(leaf_id, fn, self.tree, 1)
            self.assertEqual(vdl.call(leaf_id, fn, self.tree, 1), first)  # session-less consumers are served
            entries = [entry for entry in caches.vdl._entries.values() if entry.leaf_id == leaf_id]
            with aio.V2AuthenticationReadSession() as consumer:
                computed = outcome(lambda: vdl.call(leaf_id, fn, self.tree, 1))
        self.assertEqual(computed[:2], expected[:2])
        self.assertEqual(dict(consumer.records), dict(serial.records))
        self.assertEqual(len(entries), 1)
        self.assertIsNone(entries[0].rows)
        return computed

    def test_an_unrepresented_session_query_never_serves_a_session(self):
        computed = self.assert_never_serves_a_session("T_query", querying_leaf)
        self.assertEqual(computed[1][1], False)  # the in-session branch, computed in the session
        self.assertEqual(CALLS["querying_leaf"], 2)

    def test_a_fill_that_entered_its_own_session_never_serves_a_session(self):
        computed = self.assert_never_serves_a_session("T_nested", nested_session_leaf)
        self.assertEqual(computed[:2], ("raise", "RuntimeError"))

    def test_a_capability_path_in_the_value_never_serves_a_session(self):
        computed = self.assert_never_serves_a_session("T_path_value", path_value_leaf)
        self.assertIsInstance(computed[1]["target"], aio.V2AuthenticationPath)

    def test_a_rowless_inner_hit_makes_the_outer_fill_rowless(self):
        with run() as caches:
            vdl.call("T_query", querying_leaf, self.tree, 1)  # rowless (unrepresented) inner entry
            vdl.call("T_outer", outer_leaf, self.tree, 1)  # the inner call is a hit inside this fill
            self.assertEqual(CALLS["querying_leaf"], 1)
            outer = [entry for entry in caches.vdl._entries.values() if entry.leaf_id == "T_outer"]
            with aio.V2AuthenticationReadSession():
                value = vdl.call("T_outer", outer_leaf, self.tree, 1)
        self.assertEqual(len(outer), 1)
        self.assertIsNone(outer[0].rows)
        self.assertEqual(CALLS["outer_leaf"], 2)
        self.assertEqual(value[0][1], False)

    def test_the_recorded_twin_is_a_capability_tree_kind_in_the_key(self):
        spec = vdl._LEAVES_BY_ID["T_cap"]
        with run() as caches:
            def key(path):
                return caches.vdl._prepare(spec, capability_leaf, (path, 1), {}).key

            with aio.recording_authentication_reads():
                twin = aio.v2_authentication_path(self.tree)
            self.assertIsInstance(twin, aio._RecordedAuthenticationPath)
            self.assertEqual(key(twin), key(aio.V2AuthenticationPath(self.tree)))
            self.assertNotEqual(key(twin), key(Path(self.tree)))


# ------------------------------------------------------- tracers on synthetic S10 data


def _extract_members(destination: Path, names) -> Path:
    from tests.b5_analysis.test_parallel_steps import RUNS
    from tests.b5_analysis.test_shared_physics_cache import ARCHIVE

    prefixes = tuple(RUNS + name + "/" for name in names)
    with tarfile.open(ARCHIVE) as blob:
        blob.extractall(destination, members=[m for m in blob.getmembers() if m.name.startswith(prefixes)],
                        filter="data")
    return destination / RUNS


class RealLeafTracer(unittest.TestCase):
    """Each real leaf on committed synthetic S10 members: session registrations == session-less rows."""

    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis.test_parallel_steps import GOOD, REFUSED

        cls.tmp = Path(tempfile.mkdtemp(prefix="authio2-leaves-"))
        cls.good, cls.refused = GOOD, REFUSED
        cls.runs = _extract_members(cls.tmp, (*GOOD, REFUSED))
        # Calibration physics fits are shared across the class (a fit costs seconds); a warm and
        # a cold fit register the same reads for these leaves, and both arms of every comparison
        # below run against the same warm caches.
        cls.physics, cls.session_physics = {}, {}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @staticmethod
    def leaves(member: Path):
        from joulewise import cli, environment_admission, whole_window

        metadata = json.loads((member / "metadata.json").read_bytes())
        calibration = metadata.get("instrument_calibration") or {}
        bound = calibration.get("b_fiducial_s")
        leaves = {
            "L1": (cli.validate_bundle, (member, True), {}),
            "L3": (vdl.reduce_bundle_dict, (member,), {}),
            "L6": (vdl.verify_instrument_calibration_at, (member, metadata, calibration), {}),
            "L5": (environment_admission.current_environment_refusals, (metadata,),
                   {"bundle_path": member, "measured_window_start_s": metadata.get("measured_window_start_s"),
                    "measured_window_end_s": metadata.get("measured_window_end_s")}),
        }
        if isinstance(bound, (int, float)):
            leaves["L2"] = (whole_window._member_operative_summary,
                            (whole_window._rederive_summary_for_authenticated_fiducial_bound, member,
                             float(bound) * 2 + 1e-3, metadata), {})
        return leaves

    def test_every_session_registration_is_a_recorded_row(self):
        capability_reads = 0
        for member in sorted(self.runs.iterdir()):
            for name, (fn, args, kwargs) in self.leaves(member).items():
                with self.subTest(member=member.name, leaf=name):
                    with arc.analysis_run_caches(self.physics):
                        outcome(lambda: fn(*args, **kwargs))  # warm the shared physics
                    with arc.analysis_run_caches(self.physics), traced_registrations() as registered:
                        with session(self.session_physics):
                            in_session = outcome(lambda: fn(*args, **kwargs))
                    with arc.analysis_run_caches(self.physics), aio.recording_authentication_reads() as rows:
                        sessionless = outcome(lambda: fn(*args, **kwargs))
                    self.assertEqual(rows.unrepresented, [])
                    recorded = mapped(rows)
                    self.assertEqual(recorded[:len(registered)], registered)
                    if in_session[0] == "ok":
                        self.assertEqual(recorded, registered)
                        self.assertEqual(sessionless[0], "ok")
                    else:
                        # The session refused at a strict parse: the next recorded read is the one a
                        # bridged hit re-verifies, and it refuses identically.
                        self.assertEqual(in_session[1], "V2AuthenticationInputError")
                        identity, digest, grammar, label = recorded[len(registered)]
                        raw = Path(identity).read_bytes()
                        verdict = outcome(lambda: aio.ensure_grammar_verdict(raw, digest, grammar, False, label))
                        self.assertEqual(verdict, in_session)
                    capability_reads += sum(1 for row in registered if row[3].startswith("v2 path capability"))
        self.assertGreater(capability_reads, 0)

    def test_real_leaf_bridged_hits_end_with_the_serial_session_records(self):
        member = self.runs / self.good[0]
        for name, (fn, args, kwargs) in self.leaves(member).items():
            leaf_id = {spec.leaf_id[:2]: spec.leaf_id for spec in vdl.LEAVES}[name]
            with self.subTest(leaf=leaf_id):
                with arc.analysis_run_caches(self.physics), session(self.session_physics) as serial:
                    expected = fn(*args, **kwargs)
                with run(physics=self.physics) as caches:
                    self.assertEqual(vdl.call(leaf_id, fn, *args, **kwargs), expected)
                    with session(self.session_physics) as consumer:
                        value = vdl.call(leaf_id, fn, *args, **kwargs)
                    counters = caches.vdl.restricted_counters()
                self.assertEqual(value, expected)
                self.assertEqual(counters.get(f"{leaf_id}:hit"), 1, counters)
                self.assertEqual(dict(consumer.records), dict(serial.records))
                self.assertEqual(list(consumer.records), list(serial.records))


class ExtractionReplayTracer(unittest.TestCase):
    """A floor-extraction replay (no seams) over two cells of S10 members, in and out of a session."""

    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis.test_parallel_steps import GOOD
        from tests.test_floor_extraction import install_synthetic_recovered_manifest

        cls.tmp = Path(tempfile.mkdtemp(prefix="authio2-extraction-"))
        runs = _extract_members(cls.tmp, GOOD)
        cls.runs_root = cls.tmp / "extraction"
        for name in GOOD:
            shutil.copytree(runs / name, cls.runs_root / name)
        install_synthetic_recovered_manifest(cls.runs_root, list(GOOD))
        cell = lambda cell_id, members: {  # noqa: E731
            "cell_id": cell_id, "kind": "absolute", "metric": "gross_energy_j", "window_class": "request",
            "members": [{"slot": m, "bundle_id": m} for m in members]}
        from joulewise import floor_extraction

        cls.spec = {"schema_version": floor_extraction.EXTRACTION_SPEC_SCHEMA_VERSION,
                    "cells": [cell("W-A", (GOOD[0], GOOD[1])), cell("W-B", (GOOD[0], GOOD[1], GOOD[2]))]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_session_registration_of_the_replay_is_a_recorded_row(self):
        from joulewise import floor_extraction

        def replay():
            return outcome(lambda: floor_extraction.extract_cells(self.runs_root, self.spec))

        with arc.analysis_run_caches({}), traced_registrations() as registered:
            with aio.V2AuthenticationReadSession():
                in_session = replay()
        with arc.analysis_run_caches({}), aio.recording_authentication_reads() as rows:
            sessionless = replay()
        self.assertEqual(in_session[0], "ok")
        self.assertEqual(sessionless[0], "ok")
        self.assertEqual(rows.unrepresented, [])
        self.assertEqual(mapped(rows), registered)
        capability = [row for row in rows if row.api.startswith("v2_path.")]
        self.assertTrue(capability)
        self.assertEqual(len(capability),
                         sum(1 for row in registered if row[3].startswith("v2 path capability")))


if __name__ == "__main__":
    unittest.main()
