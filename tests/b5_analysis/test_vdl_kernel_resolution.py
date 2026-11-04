"""D-188 VDL-FIX round 4 (review of #641): the kernel's resolution of a spelling.

Round 3 served a tree argument only when its spelling was absolute and
lexically normal, on the premise that the kernel then resolves it as
``os.path.realpath`` does. That is false when a symlink on the way holds
``passage/..``: the spelling stays normal, the non-strict realpath drops
``passage`` lexically, and the kernel traverses it. With ``passage`` missing
or a file the kernel fails (ENOENT, ENOTDIR); with ``passage`` a directory the
caller cannot search, even ``realpath(strict=True)`` succeeds while the kernel
fails (EACCES). The tree walk ran at the realpath, so an existence-only probe
on the spelling (L6's ``reader.path.resolve(strict=True)``, L2/L5's stats) was
not decided by the hashed tree: L2, L5 and L6 served the other state's
decision in both directions with no defect in on mode, and an L6 refusal was
exported, pickled and merged into a V2 session (zero registrations where
serial makes seven).

Now the kernel's resolution (``os.stat`` of the spelling) must reach the
realpath root itself (same device and inode as its ``lstat``) on every call,
after a fill and before a deferred hit applies, or the leaf runs unchanged.
An extra read or listing kept under an alias is held to the same rule on its
fill and on every hit.

Synthetic data only: the committed S10 ALPHA fixture member, extracted into a
temporary directory, and small synthetic trees.
"""
from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
import pickle
import shutil
import tarfile
import tempfile
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import cli
from joulewise import environment_admission as ea
from joulewise import whole_window as ww
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.bundle_read import BundleReader

MODULE = __name__
SHADOW = vdl.Mode("shadow", 1000)
MODES = (vdl.ON, SHADOW)
L1 = "L1_strict_validation"
L2 = "L2_operative_summary"
L5 = "L5_environment_refusals"
L6 = "L6_verify_instrument_calibration"
SEARCHABLE = 0o755
LOCKED = 0o600


class Deadline:
    firings = 0


@contextlib.contextmanager
def run(mode=vdl.ON, entries=None):
    with arc.analysis_run_caches({}, vdl_mode=mode, vdl_entries=entries) as caches:
        caches.deadline = Deadline()
        yield caches


def _extract(parent: Path) -> Path:
    from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER

    with tarfile.open(ARCHIVE) as blob:
        blob.extractall(parent, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)],
                        filter="data")
    return parent / MEMBER


class _Passage:
    """A middle component ``passage`` behind a symlink ``... -> passage/../<name>``.

    ``good()`` makes it a searchable directory; ``bad()`` makes it the given
    untraversable kind: missing, a regular file, or a directory the caller
    cannot search.
    """

    def __init__(self, path: Path, kind: str):
        self.path, self.kind = path, kind

    def clear(self) -> None:
        if self.path.is_symlink() or self.path.is_file():
            self.path.unlink()
        elif self.path.is_dir():
            os.chmod(self.path, SEARCHABLE)
            self.path.rmdir()

    def good(self) -> None:
        self.clear()
        self.path.mkdir(mode=SEARCHABLE)

    def bad(self) -> None:
        self.clear()
        if self.kind == "file":
            self.path.write_text("not a directory")
        elif self.kind == "locked":
            self.path.mkdir(mode=SEARCHABLE)
            os.chmod(self.path, LOCKED)


KINDS = ("missing", "file", "locked")


def _searchable_by_kernel_only_when_good(test: unittest.TestCase, passage: _Passage, spelled: str, real: Path):
    """The premise the round-4 fix rests on, checked on this filesystem."""

    passage.good()
    test.assertTrue(os.path.exists(spelled))
    passage.bad()
    test.assertFalse(os.path.exists(spelled), passage.kind)
    test.assertEqual(os.path.realpath(spelled), str(real), passage.kind)
    if passage.kind == "locked":
        test.assertEqual(os.path.realpath(spelled, strict=True), str(real))
        with test.assertRaises(PermissionError):
            os.stat(spelled)


class _Fixture(unittest.TestCase):
    def setUp(self):
        if os.geteuid() == 0:
            self.skipTest("a mode-600 directory is searchable by root")
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-kernel-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.path = _extract(self.tmp)
        self.metadata = json.loads((self.path / "metadata.json").read_bytes())
        self.calibration = self.metadata["instrument_calibration"]
        self.key = self.calibration["artifact_sha256"]
        self.bound = self.calibration["b_fiducial_s"]
        self.link = self.path.parent / "linked-bundle"
        os.symlink(f"passage/../{self.path.name}", self.link)
        self.spelled = str(self.link)
        self.assertTrue(os.path.isabs(self.spelled) and os.path.normpath(self.spelled) == self.spelled)

    def passage(self, kind: str) -> _Passage:
        passage = _Passage(self.path.parent / "passage", kind)
        self.addCleanup(passage.clear)
        return passage

    def l6(self, path):
        return (vdl.verify_instrument_calibration_at, (path, self.metadata, self.calibration),
                {"physics_cache": {self.key: self.bound}})

    def cases(self, caches):
        from joulewise.reduce import _rederive_summary_for_authenticated_fiducial_bound as rederive

        # Synthetic fixture physics only (no fresh fit), for L2.
        caches.physics_store[ww._effective_bound_partition(self.metadata)] = {self.key: self.bound}
        window = BundleReader(self.path).measured_window()
        return (
            (L5, ea.current_environment_refusals, (self.metadata,),
             dict(bundle_path=self.spelled, measured_window_start_s=window.start_s,
                  measured_window_end_s=window.end_s)),
            (L6,) + self.l6(self.spelled),
            (L2, ww._member_operative_summary, (rederive, self.spelled, self.bound, self.metadata), {}),
        )


def _brief(value):
    if isinstance(value, dict):
        return {key: value.get(key) for key in ("status", "failure_reason")}
    return value


def outcome(fn, *args, **kwargs):
    """The caller-visible outcome: a value, or the exception's type and text."""

    try:
        return ("value", fn(*args, **kwargs))
    except Exception as exc:  # noqa: BLE001 - an exception is an outcome to compare
        return ("raise", type(exc).__name__, str(exc))


def _brief_outcome(result):
    return (result[0], _brief(result[1])) if result[0] == "value" else result


class PremiseOnThisFilesystem(_Fixture):
    def test_realpath_disagrees_with_the_kernel(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                _searchable_by_kernel_only_when_good(self, self.passage(kind), self.spelled, self.path)

    def test_helper(self):
        passage = self.passage("missing")
        passage.good()
        self.assertTrue(vdl._kernel_resolves_to(self.spelled, str(self.path)))
        self.assertFalse(vdl._kernel_resolves_to(self.spelled, str(self.path.parent)))
        for kind in KINDS:
            with self.subTest(kind=kind):
                passage.kind = kind
                passage.bad()
                self.assertFalse(vdl._kernel_resolves_to(self.spelled, str(self.path)))
        self.assertFalse(vdl._kernel_resolves_to("bad\0spelling", str(self.path)))
        # The realpath root itself: a symlink at ``root`` is not its target.
        self.assertFalse(vdl._kernel_resolves_to(str(self.path), str(self.link)))


class TraversabilityChangesUnderTheSameSpelling(_Fixture):
    """The reviewer's repro_symlink_dotdot.py (both orders), for each untraversable kind."""

    def test_served_equals_serial(self):
        for kind in KINDS:
            passage = self.passage(kind)
            for order in ("positive-first", "negative-first"):
                for mode in MODES:
                    for index in range(3):
                        with run(mode) as caches:
                            leaf, fn, args, kwargs = self.cases(caches)[index]
                            with self.subTest(kind=kind, order=order, mode=mode.name, leaf=leaf):
                                try:
                                    (passage.good if order == "positive-first" else passage.bad)()
                                    first_serial = outcome(fn, *args, **dict(kwargs))
                                    first = outcome(vdl.call, leaf, fn, *args, **kwargs)
                                    self.assertEqual(first, first_serial)
                                    (passage.bad if order == "positive-first" else passage.good)()
                                    serial = outcome(fn, *args, **dict(kwargs))
                                    self.assertNotEqual(_brief_outcome(serial), _brief_outcome(first),
                                                        "the decision flips")
                                    served = outcome(vdl.call, leaf, fn, *args, **kwargs)
                                    self.assertEqual(_brief_outcome(served), _brief_outcome(serial))
                                    self.assertEqual(served, serial)
                                    self.assertNotIn(f"{leaf}:hit", caches.vdl.restricted_counters())
                                    self.assertFalse(caches.vdl.defect_pending())
                                finally:
                                    passage.clear()

    def test_a_refusal_is_not_shipped_into_a_session(self):
        """The reviewer's repro_l6_symlink_negative.py, asserting serial equivalence."""

        fn, args, kwargs = self.l6(self.spelled)
        for kind in KINDS:
            passage = self.passage(kind)
            for mode in MODES:
                with self.subTest(kind=kind, mode=mode.name):
                    passage.bad()
                    with run(mode) as caches:
                        bad_serial = outcome(fn, *args, **kwargs)
                        first = outcome(vdl.call, L6, fn, *args, **kwargs)
                        self.assertEqual(first, bad_serial)
                        if kind == "locked":  # serial raises EACCES here
                            self.assertEqual(first[:2], ("raise", "PermissionError"))
                        else:
                            self.assertEqual(first, ("value", (None, "instrument_calibration_invalid")))
                        payload = pickle.loads(pickle.dumps(caches.vdl.export_entries()))
                        passage.good()
                        serial = fn(*args, **kwargs)
                        self.assertIsNone(serial[1])
                        self.assertEqual(vdl.call(L6, fn, *args, **kwargs), serial)
                        self.assertFalse(caches.vdl.defect_pending())
                    self.assertEqual(payload["entries"], {}, "an untraversable spelling is never stored")
                    with run(mode, entries=payload) as consumer:
                        with V2AuthenticationReadSession() as session:
                            served = vdl.call(L6, fn, *args, **kwargs)
                            registrations = len(session.records)
                        with V2AuthenticationReadSession() as session:
                            fresh = fn(*args, **kwargs)
                            serial_registrations = len(session.records)
                        self.assertEqual(served, fresh)
                        self.assertEqual(serial_registrations, 7)
                        self.assertEqual(registrations, serial_registrations)
                        self.assertFalse(consumer.vdl.defect_pending())
                    passage.clear()

    def test_a_good_entry_is_not_served_once_the_spelling_breaks(self):
        """A fill made while ``passage`` is searchable is stored; a later untraversable call bypasses."""

        fn, args, kwargs = self.l6(self.spelled)
        for kind in KINDS:
            passage = self.passage(kind)
            with self.subTest(kind=kind), run() as caches:
                passage.good()
                first = vdl.call(L6, fn, *args, **kwargs)
                self.assertEqual(vdl.call(L6, fn, *args, **kwargs), first)
                self.assertEqual(caches.vdl.restricted_counters().get(f"{L6}:hit"), 1)
                passage.bad()
                self.assertEqual(outcome(vdl.call, L6, fn, *args, **kwargs), outcome(fn, *args, **kwargs))
                counters = caches.vdl.restricted_counters()
                self.assertEqual(counters.get(f"{L6}:hit"), 1)
                self.assertEqual(counters.get(f"{L6}:bypass"), 1)
                passage.clear()

    def test_path_free_l1_canonical_fill_is_not_served_through_a_broken_middle_link(self):
        """The reviewer's repro_l1_pathfree_symlink.py: the key holds only the final name."""

        hop = self.tmp / "hop"
        os.symlink(os.path.join("passage", os.pardir, os.path.relpath(self.path.parent, self.tmp)), hop)
        passage = _Passage(self.tmp / "passage", "missing")
        self.addCleanup(passage.clear)
        spelled = str(hop / self.path.name)
        for kind in KINDS:
            passage.kind = kind
            passage.bad()
            for mode in MODES:
                with self.subTest(kind=kind, mode=mode.name), run(mode) as caches:
                    vdl.call(L1, cli.validate_bundle, self.path, True)
                    serial = outcome(cli.validate_bundle, spelled, True)
                    self.assertEqual(outcome(vdl.call, L1, cli.validate_bundle, spelled, True), serial)
                    self.assertNotIn(f"{L1}:hit", caches.vdl.restricted_counters())
                    self.assertFalse(caches.vdl.defect_pending())
            passage.clear()


class DeferredAndPostFillChecks(_Fixture):
    """The same rule in ``_apply`` (a pool-probed hit) and ``_entry`` (after a fill)."""

    def test_deferred_hit_rechecks_the_kernel(self):
        fn, args, kwargs = self.l6(self.spelled)
        passage = self.passage("missing")
        for kind in KINDS:
            passage.kind = kind
            with self.subTest(kind=kind), run():
                passage.good()
                vdl.call(L6, fn, *args, **kwargs)
                hit = vdl.probe(L6, fn, *args, **kwargs)
                self.assertIsNotNone(hit)
                passage.bad()
                with self.assertRaises(vdl._Bypass):
                    hit.apply()
                passage.clear()

    def test_post_fill_check(self):
        fn, args, kwargs = self.l6(self.spelled)
        passage = self.passage("missing")
        seen = []
        real = vdl._kernel_resolves_to

        def flaky(spelling, root):
            # The prepare check sees the spelling good; the post-fill check
            # sees it broken, as if ``passage`` vanished during the fill.
            if spelling != self.spelled:
                return real(spelling, root)
            seen.append(root)
            return len(seen) == 1 and real(spelling, root)

        passage.good()
        with run() as caches, mock.patch.object(vdl, "_kernel_resolves_to", flaky):
            vdl.call(L6, fn, *args, **kwargs)
            self.assertEqual(seen, [str(self.path)] * 2)
            self.assertEqual(caches.vdl._entries, {})
            self.assertEqual(caches.vdl.restricted_counters().get(f"{L6}:fill"), None)


# --------------------------------------------------- extra reads and listings


def read_one(path, file):
    try:
        return Path(file).read_text()
    except OSError as exc:
        return type(exc).__name__


def list_one(path, directory):
    try:
        return sorted(os.listdir(directory))
    except OSError as exc:
        return type(exc).__name__


SPECS = (
    vdl.LeafSpec("K_read", (f"{MODULE}:{read_one.__qualname__}",), (("path", vdl.TREE), ("file", vdl.SCALAR))),
    vdl.LeafSpec("K_list", (f"{MODULE}:{list_one.__qualname__}",),
                 (("path", vdl.TREE), ("directory", vdl.SCALAR))),
)


class AliasedExtraReads(unittest.TestCase):
    """An extra read or listing through ``hop -> passage/../real`` (outside the tree)."""

    def setUp(self):
        if os.geteuid() == 0:
            self.skipTest("a mode-600 directory is searchable by root")
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-kernel-extra-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        registration = vdl._registered(*SPECS)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)
        self.tree = self.tmp / "bundle"
        self.tree.mkdir()
        (self.tree / "fit.txt").write_text("1")
        self.real = self.tmp / "real"
        self.real.mkdir()
        (self.real / "data.txt").write_text("content")
        hop = self.tmp / "hop"
        os.symlink("passage/../real", hop)
        self.passage = _Passage(self.tmp / "passage", "missing")
        self.addCleanup(self.passage.clear)
        self.cases = (("K_read", read_one, str(hop / "data.txt")), ("K_list", list_one, str(hop)))

    def test_served_equals_serial_in_both_orders(self):
        for kind in KINDS:
            self.passage.kind = kind
            for order in ("positive-first", "negative-first"):
                for leaf, fn, spelled in self.cases:
                    with self.subTest(kind=kind, order=order, leaf=leaf), run() as caches:
                        (self.passage.good if order == "positive-first" else self.passage.bad)()
                        first = vdl.call(leaf, fn, self.tree, spelled)
                        self.assertEqual(first, fn(self.tree, spelled))
                        (self.passage.bad if order == "positive-first" else self.passage.good)()
                        serial = fn(self.tree, spelled)
                        self.assertNotEqual(serial, first)
                        self.assertEqual(vdl.call(leaf, fn, self.tree, spelled), serial)
                        self.assertNotIn(f"{leaf}:hit", caches.vdl.restricted_counters())
                        self.passage.clear()

    def test_traversable_alias_still_hits(self):
        self.passage.good()
        for leaf, fn, spelled in self.cases:
            with self.subTest(leaf=leaf), run() as caches:
                first = vdl.call(leaf, fn, self.tree, spelled)
                self.assertEqual(vdl.call(leaf, fn, self.tree, spelled), first)
                self.assertEqual(caches.vdl.restricted_counters().get(f"{leaf}:hit"), 1)


if __name__ == "__main__":
    unittest.main()
