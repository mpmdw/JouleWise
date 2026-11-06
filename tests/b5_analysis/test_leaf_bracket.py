"""D-188 LEAF-BRACKET: leaf L4 in bracket.evaluate_window_bracket, entirely synthetic.

The leaf is the frozen calibration_bracket_for_bundles, served from the
verified derivation store (joulewise/analysis_verified_store.py). Every test
compares the store's outcome with the serial outcome (no store) on the same
bytes: the bracket's fields or its refusal code, and the archive census.

Sol's detail critique rated this leaf unsafe as planned (#4 relocation, #5
negative and timed custody probes, #6 the claim runs root). The custody-probe
tests run the real calibration_ledger.probe_custody (its daemon thread, its
exists/is_dir probe and its two-second timeout) in front of the S2 fixture's
synthetic capture decoder. Today the store never stores a fill that started a
thread, so those fills are unstorable; the tests that relax that rule (as a
later store revision might) show that a refusal resting on a negative or
timed-out probe is still never served. Under that relaxed rule such a refusal
IS stored and exported (only never served): the store has no per-leaf value
predicate yet (review of PR #634, finding 1, deferred to AUTH-IO-2). The
tolerance must not land without one; ``test_tolerated_probe_thread_needs_a_value_predicate``
shows why and flips once the L4 spec carries ``storable_value``.
"""
from __future__ import annotations

import contextlib
import dataclasses
import inspect
import io
import json
import os
from pathlib import Path
import pickle
import re
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import authentication_io as aio
from joulewise import calibration_bracketing as calibration
from joulewise import calibration_ledger as cl
from joulewise.b5_analysis import bracket as br
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s2 as fx

L4 = br.L4
PROBE_THREAD = "custody-locator-probe"
_TEMPORARY = re.compile(r"l9-bracket-(?:members-)?[^/]+")


class _Deadline:
    def __init__(self):
        self.firings = 0


@contextlib.contextmanager
def run(mode=vdl.ON):
    with arc.analysis_run_caches({}, vdl_mode=mode) as caches:
        caches.deadline = _Deadline()
        yield caches


def thaw(value):
    if isinstance(value, dict) or hasattr(value, "items"):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [thaw(item) for item in value]
    return value


def outcome(built):
    """The evaluation as plain data (bracket fields or refusal code) and the archive census."""
    handle = fx.handle(built)
    try:
        result = br.evaluate_window_bracket(handle, repo_root=fx.s0.ROOT)
    except AnalysisRefusal as exc:
        value = ("refused", str(exc))
    else:
        value = ("bracket", result.window.pack, result.trigger_scope,
                 json.dumps(thaw(result.evaluation), sort_keys=True), result.b_fiducial_s.hex(),
                 result.terminal_sequence, result.ledger_copy_sha256, result.compared_with_harvest,
                 result.sources_sha256sums_sha256)
    return value, tuple((row.path, row.sha256, row.check) for row in handle.census())


def frozen_calls():
    """Counts the frozen leaf's executions (its discovery runs once per call)."""
    return mock.patch.object(calibration, "discover_calibration_candidates",
                             wraps=calibration.discover_calibration_candidates)


def counters(caches):
    return {key.removeprefix(L4 + ":"): value for key, value in caches.vdl.restricted_counters().items()
            if key.startswith(L4 + ":")}


def probing_loader(path, *, runs_root, mode="issuing", **_):
    """The real custody probe in front of the S2 fixture's synthetic capture decoder."""
    return cl.probe_custody(Path(path), lambda mapped: fx._decode_capture(mapped, runs_root=runs_root, mode=mode),
                            lambda: None, mode=mode)


def probing():
    return mock.patch.object(calibration, "load_calibration_candidate", side_effect=probing_loader)


def threads_tolerated():
    """Test-only: a store that does not mark fills that start a thread (not today's rule)."""
    return mock.patch.object(vdl, "_THREAD_EVENTS", frozenset())


def bound_captures(built):
    """The bound session's capture directories (the ones discovery must find)."""
    binding = json.loads((built.archive / "derived/bracket-binding.json").read_bytes())
    root = built.claim / "instrument_validation"
    return [root / f"{binding['session_id']}-{slot}" for slot in ("pre", "post")]


def contained_loader(path, *, runs_root, mode="issuing", **_):
    """probing_loader plus the frozen loader's containment step (calibration_bracketing.py:1678-1682)."""
    def inspect(mapped):
        try:
            directory = Path(mapped).resolve(strict=True)
            directory.relative_to(Path(runs_root).resolve())
        except (OSError, ValueError):
            return None
        return fx._decode_capture(directory, runs_root=runs_root, mode=mode)
    return cl.probe_custody(Path(path), inspect, lambda: None, mode=mode)


@contextlib.contextmanager
def timed_out(slow: Path):
    """The real probe of ``slow`` outlives a shortened custody-probe timeout."""
    real_paths = cl._custody_probe_paths

    class SlowPath(type(slow)):
        def exists(self, *args, **kwargs):
            time.sleep(0.5)
            return super().exists(*args, **kwargs)

    def paths(path, *, mode="issuing"):
        found = real_paths(path, mode=mode)
        return tuple(SlowPath(item) if Path(item) == slow else item for item in found)

    stderr = io.StringIO()
    with mock.patch.object(cl, "_custody_probe_paths", paths), \
            mock.patch.object(cl, "CUSTODY_PROBE_TIMEOUT_S", 0.05), contextlib.redirect_stderr(stderr):
        yield stderr


def stored_l4(payload):
    return [pickle.loads(entry.value) for entry in payload["entries"].values() if entry.leaf_id == L4]


@contextlib.contextmanager
def relocated_behind_symlink(directory: Path):
    """Move ``directory`` out of its runs root and leave a symlink to it (bytes and inodes unchanged)."""
    elsewhere = directory.parents[2] / ("relocated-" + directory.name)
    directory.rename(elsewhere)
    directory.symlink_to(elsewhere, target_is_directory=True)
    try:
        yield
    finally:
        directory.unlink()
        elsewhere.rename(directory)


@contextlib.contextmanager
def moved_aside(directory: Path):
    aside = directory.with_name(directory.name + "-aside")
    directory.rename(aside)
    try:
        yield
    finally:
        aside.rename(directory)


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gamma = fx.build_named("GAMMA_STD")
        cls.alpha = fx.build_named("ALPHA_STD")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="leaf-bracket-")
        self.addCleanup(self.tmp.cleanup)
        adapter = fx.capture_adapter()
        adapter.__enter__()
        self.addCleanup(adapter.__exit__, None, None, None)

    def serial(self, built):
        """The outcome with no store, even inside an activated run."""
        with frozen_calls() as calls, mock.patch.object(vdl, "active_store", return_value=None):
            result = outcome(built)
        self.assertEqual(calls.call_count, 1)
        return result


class LeafBracketTests(_Base):
    def test_fill_then_hit_equals_serial_with_fresh_copy_roots(self):
        for built in (self.gamma, self.alpha):
            with self.subTest(pack=built.entry_data["pack"]):
                expected = self.serial(built)
                self.assertEqual(expected[0][0], "bracket")
                roots = []
                real = br._calibration_assessment

                def spy(runs_root, paths, policy, **kwargs):
                    roots.append(Path(paths[0]).parent)
                    return real(runs_root, paths, policy, **kwargs)

                with run() as caches, frozen_calls() as calls, mock.patch.object(br, "_calibration_assessment", spy):
                    first = outcome(built)
                    second = outcome(built)
                    third = outcome(built)
                self.assertEqual((first, second, third), (expected, expected, expected))
                self.assertEqual(calls.call_count, 1, "the frozen leaf ran once, at the first touch")
                self.assertEqual((counters(caches)["fill"], counters(caches)["hit"]), (1, 2))
                # Sol #4: every evaluation copies into a fresh temporary root.
                self.assertEqual(len(set(roots)), 3)

    def test_in_session_hit_registers_the_serial_reads_relocated(self):
        """Sol #4: a path-free hit's V2 rows land on this evaluation's own copies."""
        def records(session):
            return sorted((_TEMPORARY.sub("<tmp>", identity), record.sha256, record.grammar, record.read_count)
                          for identity, record in session.records.items())

        with aio.V2AuthenticationReadSession() as serial:
            expected = self.serial(self.gamma)
        with run() as caches, frozen_calls() as calls:
            with aio.V2AuthenticationReadSession() as filler:
                filled = outcome(self.gamma)
            with aio.V2AuthenticationReadSession() as consumer:
                served = outcome(self.gamma)
        self.assertEqual((filled, served), (expected, expected))
        self.assertEqual(calls.call_count, 1)
        self.assertEqual(counters(caches)["hit"], 1)
        self.assertEqual(records(filler), records(serial))
        self.assertEqual(records(consumer), records(serial))
        def copy_roots(session):
            return {re.search(r".*/l9-bracket-members-[^/]+", identity).group(0)
                    for identity in session.records if "l9-bracket-members-" in identity}

        # The consumer's rows name its own copies, never the filler's.
        self.assertEqual(len(copy_roots(filler)), 1)
        self.assertEqual(len(copy_roots(consumer)), 1)
        self.assertNotEqual(copy_roots(consumer), copy_roots(filler))

    def test_copies_are_seeded_from_authenticated_digests_not_rehashed(self):
        hashed = []
        real = vdl._hash_file_nofollow

        def counted(path):
            hashed.append(path)
            return real(path)

        with run(), mock.patch.object(vdl, "_hash_file_nofollow", counted):
            outcome(self.gamma)
        self.assertEqual([path for path in hashed if "l9-bracket-members-" in path], [])

    def test_runs_root_is_keyed_and_a_relative_one_bypasses(self):
        """Sol #6: the claim runs root is a real scalar of the leaf (only copy roots are path-free)."""
        observed = {}
        real = br._calibration_assessment
        fn = calibration.calibration_bracket_for_bundles

        def twice(runs_root, paths, policy, **kwargs):
            other = Path(runs_root).parent / "other-claim-runs"
            observed["frozen_other"] = fn(other, paths, policy, **kwargs)
            with frozen_calls() as calls:
                observed["given"] = real(runs_root, paths, policy, **kwargs)
                observed["other"] = real(other, paths, policy, **kwargs)
                observed["again"] = real(runs_root, paths, policy, **kwargs)
                observed["calls"] = calls.call_count
            store = vdl.active_store()
            before = store.restricted_counters()
            with frozen_calls() as calls:
                relative = Path(os.path.relpath(runs_root))
                observed["relative"] = real(relative, paths, policy, **kwargs)
                observed["frozen_relative"] = fn(relative, paths, policy, **kwargs)
                observed["relative_calls"] = calls.call_count
            observed["relative_counters_unchanged"] = store.restricted_counters() == before
            return observed["given"]

        with run(), mock.patch.object(br, "_calibration_assessment", twice):
            outcome(self.gamma)
        self.assertEqual(observed["calls"], 2, "given: fill; other runs root: miss; given again: hit")
        self.assertEqual(observed["other"], observed["frozen_other"])
        self.assertNotEqual(observed["other"], observed["given"], "the runs root decides this binding")
        self.assertEqual(observed["again"], observed["given"])
        self.assertEqual(observed["relative"], observed["frozen_relative"])
        self.assertEqual(observed["relative_calls"], 2)
        self.assertTrue(observed["relative_counters_unchanged"], "a relative runs root never reaches the store")

    def test_snapshot_ledger_path_is_never_read(self):
        """Key projection never changes the snapshot a bypass receives."""
        self.assertNotIn("ledger_path", inspect.getsource(calibration))
        self.assertEqual(inspect.getsource(cl.CalibrationLedgerSnapshot).count("ledger_path"), 1)
        seen = []
        real = calibration.calibration_bracket_for_bundles

        def capture(*args, **kwargs):
            seen.append(kwargs["ledger_snapshot"].ledger_path)
            return real(*args, **kwargs)

        expected = self.serial(self.gamma)
        # The stand-in is not the registered leaf, so the store is bypassed.
        with run(), mock.patch.object(calibration, "calibration_bracket_for_bundles", capture):
            self.assertEqual(outcome(self.gamma), expected)
        self.assertEqual(len(seen), 1)
        self.assertTrue(seen[0].is_absolute())
        self.assertEqual(seen[0].name, "ledger.jsonl")

    def test_changed_candidate_byte_recomputes_with_the_serial_outcome(self):
        with run() as caches, frozen_calls() as calls:
            self.assertEqual(outcome(self.gamma), self.serial(self.gamma))
            target = bound_captures(self.gamma)[1] / "instrument_evidence.json"
            original = target.read_bytes()
            try:
                target.write_bytes(original + b" ")
                changed = outcome(self.gamma)
                self.assertEqual(calls.call_count, 3, "fill, serial, and a full recompute on the changed byte")
                with mock.patch.object(vdl, "active_store", return_value=None):
                    self.assertEqual(changed, self.serial(self.gamma))
            finally:
                target.write_bytes(original)
            self.assertEqual(counters(caches).get("hit", 0), 0)

    def test_harvest_difference_refusal_is_unchanged_on_a_hit(self):
        built = fx.fork(self.gamma, Path(self.tmp.name) / "fork")
        target = built.archive / "withheld/bracket-evaluation.json"
        row = json.loads(target.read_bytes())
        row["assessment"]["b_fiducial_s"] = "counterfactual"
        fx.s0.put(target, row)
        fx.refresh(built)
        expected = self.serial(built)
        self.assertEqual(expected[0], ("refused", "window_bracket_differs_from_harvest"))
        with run() as caches, frozen_calls() as calls:
            outcome(self.gamma)
            self.assertEqual(outcome(built), expected)
        self.assertEqual(calls.call_count, 1)
        self.assertEqual(counters(caches)["hit"], 1, "the leaf was served; the post-check refused")

    def test_a_fired_deadline_makes_the_fill_unstorable(self):
        with run() as caches, frozen_calls() as calls:
            real = calibration.load_calibration_candidate.side_effect

            def firing(*args, **kwargs):
                caches.deadline.firings += 1
                return real(*args, **kwargs)

            with mock.patch.object(calibration.load_calibration_candidate, "side_effect", firing):
                first = outcome(self.gamma)
            second = outcome(self.gamma)
        self.assertEqual(first, second)
        self.assertEqual(calls.call_count, 2)
        self.assertNotIn("hit", counters(caches))

    def test_store_absent_is_exactly_the_frozen_call(self):
        sentinel = (({"status": "x"}), ())
        with mock.patch.object(calibration, "calibration_bracket_for_bundles", return_value=sentinel) as frozen:
            # The caller's keywords (the r1 call at this site), each an opaque stand-in.
            given = dict(mode="issuing", ledger_snapshot=object(), bracket_binding=object(),
                         bracket_window_id=object(), bracket_plan_id=object(), bracket_plan_sha256=object(),
                         bracket_evidence_root_id=object(), trigger_scope=object())
            self.assertIs(br._calibration_assessment("/abs", ["p"], "policy", **given), sentinel)
        frozen.assert_called_once_with("/abs", ["p"], "policy", **given)

    def test_servable_is_exactly_what_the_caller_accepts(self):
        good = {"status": "passed", "b_fiducial_s": 0.03}
        self.assertTrue(br._servable(good, ()))
        for assessment, reasons in ((good, ("x",)), ({**good, "status": "failed"}, ()),
                                    ({**good, "b_fiducial_s": float("nan")}, ()),
                                    ({**good, "b_fiducial_s": -1.0}, ()), ({**good, "b_fiducial_s": True}, ()),
                                    ({**good, "b_fiducial_s": None}, ()), (None, ()), (good, ["x"])):
            with self.subTest(assessment=assessment, reasons=reasons):
                self.assertFalse(br._servable(assessment, reasons))


class StorableValueTests(unittest.TestCase):
    def test_storable_value_is_exactly_the_servable_pair(self):
        good = {"status": "passed", "b_fiducial_s": 0}
        self.assertTrue(br._storable_value((good, ())))
        for value in ((good, ("x",)), [good, ()], (good,), ({**good, "status": "failed"}, ()), None):
            with self.subTest(value=value):
                self.assertFalse(br._storable_value(value))

    def test_located_as_recorded(self):
        with tempfile.TemporaryDirectory(prefix="leaf-located-") as raw:
            root = Path(os.path.realpath(raw))
            (root / "inside").mkdir()
            (root / "inside" / "a").write_bytes(b"a")
            entry = vdl.Entry(L4, b"", (), ((str(root / "inside" / "a"), "d"),), ((str(root / "inside"), "n"),), (), (), None)
            self.assertTrue(br._located_as_recorded(entry))
            (root / "inside").rename(root / "moved")
            (root / "inside").symlink_to(root / "moved", target_is_directory=True)
            self.assertFalse(br._located_as_recorded(entry))
            self.assertFalse(br._located_as_recorded(object()))


class CustodyProbeTests(_Base):
    """Sol #5: candidate custody probes (real probe_custody) and their timeout."""

    def test_probe_thread_makes_every_fill_unstorable_today(self):
        with probing():
            expected = self.serial(self.gamma)
            self.assertEqual(expected[0][0], "bracket")
            with run() as caches, frozen_calls() as calls:
                self.assertEqual(outcome(self.gamma), expected)
                self.assertEqual(outcome(self.gamma), expected)
        self.assertEqual(calls.call_count, 2)
        self.assertEqual(counters(caches).get("unstorable"), 2)
        self.assertNotIn("hit", counters(caches))

    def test_negative_probe_refusal_is_never_served(self):
        missing = bound_captures(self.gamma)[1]
        with probing(), threads_tolerated():
            with moved_aside(missing):
                refused = self.serial(self.gamma)
            self.assertEqual(refused[0], ("refused", "window_bracket_not_passed"))
            restored = self.serial(self.gamma)
            self.assertEqual(restored[0][0], "bracket")
            for guard in (True, False):
                with self.subTest(guard=guard), run() as caches, frozen_calls() as calls, \
                        contextlib.ExitStack() as stack:
                    if not guard:
                        stack.enter_context(mock.patch.object(br, "_servable", return_value=True))
                    with moved_aside(missing):
                        self.assertEqual(outcome(self.gamma), refused)
                    # Stored and exportable, only never served: no store value
                    # predicate yet (finding 1, deferred to AUTH-IO-2).
                    self.assertEqual(counters(caches)["fill"], 1, "a stored fill on a negative probe")
                    if guard:
                        self.assertEqual(outcome(self.gamma), restored)
                        self.assertEqual(calls.call_count, 2)
                    else:
                        # Mutation check: without the guard the stale refusal
                        # is served after the capture is back.
                        self.assertEqual(outcome(self.gamma), refused)

    def test_timed_out_probe_is_never_served(self):
        with probing(), threads_tolerated():
            expected = self.serial(self.gamma)
            with run() as caches, frozen_calls() as calls:
                with timed_out(bound_captures(self.gamma)[0]) as stderr:
                    timed = outcome(self.gamma)
                self.assertIn("custody_locator_unreachable reason=timeout", stderr.getvalue())
                self.assertEqual(timed[0], ("refused", "window_bracket_not_passed"))
                # Stored and exportable, only never served: no store value
                # predicate yet (finding 1, deferred to AUTH-IO-2).
                self.assertEqual(counters(caches)["fill"], 1)
                self.assertEqual(outcome(self.gamma), expected)
        self.assertEqual(calls.call_count, 2, "the timed-out outcome was recomputed, not served")

    def test_timeout_dependent_fill_is_never_stored_or_merged(self):
        """Review finding 1 tripwire, today's store rule (the real probe thread, not tolerated).

        A refusal resting on a timed-out probe is not stored, so no export
        carries it into a store that has served the pass. This fails if the
        probe thread becomes tolerated without a value predicate.
        """
        with probing():
            expected = self.serial(self.gamma)
            with run() as filler:
                with timed_out(bound_captures(self.gamma)[0]) as stderr:
                    timed = outcome(self.gamma)
                self.assertIn("custody_locator_unreachable reason=timeout", stderr.getvalue())
                self.assertEqual(timed[0], ("refused", "window_bracket_not_passed"))
                exported = filler.vdl.export_entries()
            self.assertEqual(stored_l4(exported), [])
            with run() as consumer:
                self.assertEqual(outcome(self.gamma), expected)
                self.assertEqual(outcome(self.gamma), expected)
                consumer.vdl.merge_entries(exported)
                self.assertFalse(consumer.vdl.defect_pending())
                consumer.vdl.check_defects()

    def test_tolerated_probe_thread_needs_a_value_predicate(self):
        """Review finding 1: why the thread tolerance must land with a store value predicate.

        Simulated tolerance: one process's timed-out refusal is merged into a
        store that has served the pass under the same key. Without a value
        predicate on the L4 spec (today) the refusal is exported and poisons a
        served key: a host timing event becomes a store defect. Once
        AUTH-IO-2 gives LeafSpec ``storable_value`` (bracket._storable_value
        for L4), nothing is exported and nothing is poisoned.
        """
        predicate = getattr(vdl._LEAVES_BY_ID[L4], "storable_value", None)
        with probing(), threads_tolerated():
            expected = self.serial(self.gamma)
            with run() as filler:
                with timed_out(bound_captures(self.gamma)[0]):
                    self.assertEqual(outcome(self.gamma)[0], ("refused", "window_bracket_not_passed"))
                exported = filler.vdl.export_entries()
            with run() as consumer:
                self.assertEqual(outcome(self.gamma), expected)
                self.assertEqual(outcome(self.gamma), expected)
                self.assertEqual(counters(consumer)["hit"], 1)
                consumer.vdl.merge_entries(exported)
                poisoned = consumer.vdl.defect_pending()
        stored = stored_l4(exported)
        if predicate is None:
            self.assertEqual(len(stored), 1)
            self.assertFalse(br._storable_value(stored[0]))
            self.assertTrue(poisoned, "the hazard the predicate removes")
        else:
            self.assertEqual(stored, [])
            self.assertFalse(poisoned)

    def test_relocated_candidate_behind_a_symlink_is_never_served(self):
        """Review finding 2: same bytes and inodes, moved out of the runs root behind a symlink."""
        captured = bound_captures(self.gamma)[0]
        with mock.patch.object(calibration, "load_calibration_candidate", side_effect=contained_loader), \
                threads_tolerated():
            expected = self.serial(self.gamma)
            self.assertEqual(expected[0][0], "bracket")
            with relocated_behind_symlink(captured):
                relocated = self.serial(self.gamma)
            self.assertEqual(relocated[0], ("refused", "window_bracket_not_passed"))
            for guard in (True, False):
                with self.subTest(guard=guard), run() as caches, frozen_calls() as calls, \
                        contextlib.ExitStack() as stack:
                    if not guard:
                        stack.enter_context(mock.patch.object(br, "_located_as_recorded", return_value=True))
                    self.assertEqual(outcome(self.gamma), expected)
                    self.assertEqual(counters(caches)["fill"], 1)
                    with relocated_behind_symlink(captured):
                        if guard:
                            self.assertEqual(outcome(self.gamma), relocated)
                            self.assertEqual(calls.call_count, 2, "recomputed live, not served")
                        else:
                            # Mutation check: the store alone verifies the
                            # moved bytes and serves the stale pass.
                            self.assertEqual(outcome(self.gamma), expected)
                            self.assertEqual(counters(caches)["hit"], 1)

    def test_positive_probe_reads_bind_the_served_pass(self):
        captured = bound_captures(self.gamma)[0]
        with probing(), threads_tolerated():
            expected = self.serial(self.gamma)
            with moved_aside(captured):
                refused = self.serial(self.gamma)
            with run() as caches, frozen_calls() as calls:
                self.assertEqual(outcome(self.gamma), expected)
                self.assertEqual(outcome(self.gamma), expected)
                self.assertEqual((calls.call_count, counters(caches)["hit"]), (1, 1))
                with moved_aside(captured):
                    self.assertEqual(outcome(self.gamma), refused)
                self.assertEqual(calls.call_count, 2)

    def test_tracer_every_opened_or_probed_path_is_bound(self):
        """Inside the fill: every open and stat is under a copy, a recorded extra, or code."""
        opened, probed = set(), set()
        lock = threading.Lock()

        def inside() -> bool:
            return vdl.fill_active() or threading.current_thread().name == PROBE_THREAD

        def hook(event, args):
            if event == "open" and inside() and isinstance(args[0], (str, bytes)):
                with lock:
                    opened.add(os.path.abspath(os.fsdecode(args[0])))

        tracing = [True]
        sys.addaudithook(lambda event, args: hook(event, args) if tracing[0] else None)
        self.addCleanup(tracing.__setitem__, 0, False)
        real_stat, real_lstat = os.stat, os.lstat

        def traced(real):
            def call(path, *args, **kwargs):
                if inside() and isinstance(path, (str, bytes, os.PathLike)):
                    with lock:
                        probed.add(os.path.abspath(os.fsdecode(os.fspath(path))))
                return real(path, *args, **kwargs)
            return call

        roots = []
        real_assessment = br._calibration_assessment

        def spy(runs_root, paths, policy, **kwargs):
            roots.append(os.path.realpath(Path(paths[0]).parent))
            return real_assessment(runs_root, paths, policy, **kwargs)

        with probing(), threads_tolerated(), run() as caches, \
                mock.patch.object(br, "_calibration_assessment", spy), \
                mock.patch("os.stat", traced(real_stat)), mock.patch("os.lstat", traced(real_lstat)):
            self.assertEqual(outcome(self.gamma)[0][0], "bracket")
        tracing[0] = False
        entries = list(caches.vdl._entries.values())
        self.assertEqual(len(entries), 1)
        extras = {path for path, _ in entries[0].extras}
        code = tuple(os.path.realpath(root) + os.sep for root in
                     {sys.prefix, sys.base_prefix, str(Path(vdl.__file__).resolve().parent),
                      str(Path(__file__).resolve().parent)})

        def bound(path: str, *, probe: bool) -> bool:
            real = os.path.realpath(path)
            if (real + os.sep).startswith(code) or any(real == root or real.startswith(root + os.sep) for root in roots):
                return True
            if real in extras:
                return True
            # A probe (exists/is_dir, or resolve's lstat of a parent) of a
            # directory is bound only through the reads recorded beneath it.
            # Resolving a copy lstats each of its ancestors.
            prefix = real.rstrip(os.sep) + os.sep
            return probe and (any(extra.startswith(prefix) for extra in extras)
                              or any(root.startswith(prefix) for root in roots))

        probed_captures = {os.path.realpath(path) for path in probed} & {
            os.path.realpath(path) for path in bound_captures(self.gamma)}
        self.assertEqual(len(probed_captures), 2, "the tracer saw the custody probes")
        self.assertEqual(sorted(path for path in opened if not bound(path, probe=False)), [])
        self.assertEqual(sorted(path for path in probed if not bound(path, probe=True)), [])
        self.assertTrue({os.path.realpath(path / "instrument_evidence.json")
                         for path in bound_captures(self.gamma)} <= extras)


if __name__ == "__main__":
    unittest.main()
