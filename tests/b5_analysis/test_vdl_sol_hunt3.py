"""D-188 VDL-FIX round 3: Sol vf3 counterexamples (V1 tree spellings, V2 shadow decisions).

V1: a tree argument was keyed by ``os.path.abspath`` of its spelling, which
collapses ``missing/..`` lexically and makes a relative spelling equal to its
absolute one. The serial path resolves the spelling as given: the kernel
traverses ``missing`` (so ``missing/..`` fails while ``missing`` is absent),
and a relative spelling's failure text quotes it as given. So (a) an L3 entry
filled through an absolute spelling served a relative call with the absolute
spelling in its failure message, (b) L2, L5 and L6 served the canonical
bundle's success to a ``missing/..`` spelling that serial refuses, and (c) an
L6 refusal filled through ``passage/..`` (an existence-only probe:
``reader.path.resolve(strict=True)``) kept serving after ``passage`` appeared,
also exported, pickled and merged into a V2 session (zero registrations where
serial makes seven). Now a tree spelling is served or stored only when it is
absolute and lexically normal; its exact spelling is in the key and its
realpath is recomputed on every call.

V2: shadow mode recorded each of these as ``shadow_incomparable`` (the
recompute was not storable) with no defect. A recompute that cannot be stored
is now compared by its decision (value vs refusal, which refusal); a different
decision is a defect, an audit-only difference is only counted. Round 5 (lead
ruling K1): the same decision with any other difference (a number, a bound, a
reason) is a ``shadow_value_mismatch`` defect too; the only audit-only field is
L2's failure_message on a non-succeeded summary (``vdl._AUDIT_ONLY_TEXT``).

Synthetic data only: the committed S10 ALPHA fixture member, extracted into a
temporary directory.
"""
from __future__ import annotations

import contextlib
import dataclasses
import json
import os
from pathlib import Path
import pickle
import shutil
import tarfile
import tempfile
import unittest

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import environment_admission as ea
from joulewise import whole_window as ww
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.bundle_read import BundleReader

SHADOW = vdl.Mode("shadow", 1000)
MODES = (vdl.ON, SHADOW)
L2 = "L2_operative_summary"
L3 = "L3_reduce_dict"
L5 = "L5_environment_refusals"
L6 = "L6_verify_instrument_calibration"


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


def _brief(value):
    if isinstance(value, dict):
        return {key: value.get(key) for key in ("status", "failure_reason", "failure_message")}
    return value


class _Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-sol-hunt3-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.path = _extract(self.tmp)
        self.metadata = json.loads((self.path / "metadata.json").read_bytes())
        self.calibration = self.metadata["instrument_calibration"]
        self.key = self.calibration["artifact_sha256"]
        self.bound = self.calibration["b_fiducial_s"]

    def l6(self, path):
        return (vdl.verify_instrument_calibration_at, (path, self.metadata, self.calibration),
                {"physics_cache": {self.key: self.bound}})


# ------------------------------------------------------------------- V1 (a)


class V1RelativeSpelling(_Fixture):
    """Sol vf3 repro_relative_l3.py: the failure text is the caller's own spelling."""

    def test_relative_call_is_not_served_the_absolute_failure_message(self):
        (self.path / "config.json").unlink()
        (self.path / "config.json").mkdir()
        relative = Path(os.path.relpath(self.path))
        serial = vdl.reduce_bundle_dict(relative)
        self.assertIn(str(relative), serial["failure_message"])
        for mode in MODES:
            with self.subTest(mode=mode.name), run(mode) as caches:
                first = vdl.call(L3, vdl.reduce_bundle_dict, self.path)
                second = vdl.call(L3, vdl.reduce_bundle_dict, relative)
                counters = caches.vdl.restricted_counters()
                self.assertIn(str(self.path), first["failure_message"])
                self.assertEqual(second, serial)
                self.assertNotIn(f"{L3}:hit", counters)
                self.assertFalse(caches.vdl.defect_pending())


# ------------------------------------------------------------------- V1 (b)


class V1MissingComponentBeforeDotDot(_Fixture):
    """Sol vf3 repro_tree_spelling.py: L5, L6 and L2 on ``not-a-directory/..``."""

    def test_untraversable_spelling_gets_the_serial_outcome(self):
        from joulewise.reduce import _rederive_summary_for_authenticated_fiducial_bound as rederive

        bad = self.path.parent / "not-a-directory" / ".." / self.path.name
        window = BundleReader(self.path).measured_window()
        for mode in MODES:
            with run(mode) as caches:
                cases = (
                    (L5, ea.current_environment_refusals, (self.metadata,),
                     dict(bundle_path=self.path, measured_window_start_s=window.start_s,
                          measured_window_end_s=window.end_s), None),
                    (L6, vdl.verify_instrument_calibration_at, (self.path, self.metadata, self.calibration),
                     dict(physics_cache={self.key: self.bound}), 0),
                    (L2, ww._member_operative_summary, (rederive, self.path, self.bound, self.metadata), {}, 1),
                )
                for leaf, fn, args, kwargs, index in cases:
                    with self.subTest(mode=mode.name, leaf=leaf):
                        if leaf == L2:
                            # Synthetic fixture physics only (no fresh fit).
                            caches.physics_store[ww._effective_bound_partition(self.metadata)] = {
                                self.key: self.bound}
                        bad_args, bad_kwargs = list(args), dict(kwargs)
                        if index is None:
                            bad_kwargs["bundle_path"] = bad
                        else:
                            bad_args[index] = bad
                        vdl.call(leaf, fn, *args, **kwargs)
                        serial = fn(*bad_args, **bad_kwargs)
                        served = vdl.call(leaf, fn, *bad_args, **bad_kwargs)
                        self.assertEqual(_brief(served), _brief(serial))
                        self.assertEqual(served, serial)
                        self.assertNotIn(f"{leaf}:hit", caches.vdl.restricted_counters())
                self.assertFalse(caches.vdl.defect_pending())


# ------------------------------------------------------------------- V1 (c)


class V1DotDotRefusalBecomingTraversable(_Fixture):
    """Sol vf3 repro_l6_negative_traversal.py, asserting serial equivalence."""

    def test_refusal_through_dotdot_is_not_kept_or_shipped(self):
        passage = self.path.parent / "passage"
        spelled = passage / ".." / self.path.name
        fn, args, kwargs = self.l6(spelled)
        for mode in MODES:
            with self.subTest(mode=mode.name):
                with run(mode) as caches:
                    first = vdl.call(L6, fn, *args, **kwargs)
                    self.assertEqual(first, (None, "instrument_calibration_invalid"))
                    payload = pickle.loads(pickle.dumps(caches.vdl.export_entries()))
                    passage.mkdir()
                    self.addCleanup(lambda: passage.is_dir() and passage.rmdir())
                    serial = fn(*args, **kwargs)
                    self.assertIsNone(serial[1])
                    self.assertEqual(vdl.call(L6, fn, *args, **kwargs), serial)
                    self.assertFalse(caches.vdl.defect_pending())
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
                self.assertEqual(payload["entries"], {}, "a non-normal spelling is never stored")
                passage.rmdir()


# ------------------------------------------------------- V1: what still hits


class V1NormalSpellingsStillHit(_Fixture):
    def test_absolute_normal_spelling_hits(self):
        fn, args, kwargs = self.l6(self.path)
        with run() as caches:
            first = vdl.call(L6, fn, *args, **kwargs)
            second = vdl.call(L6, fn, *args, **kwargs)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(first, second)
        self.assertEqual(counters.get(f"{L6}:fill"), 1)
        self.assertEqual(counters.get(f"{L6}:hit"), 1)

    def test_symlinked_ancestor_hits_under_its_own_spelling_and_follows_a_retarget(self):
        real = self.path.parent
        alias = self.tmp / "alias"
        os.symlink(real, alias)
        through = alias / self.path.name
        fn, args, kwargs = self.l6(through)
        with run() as caches:
            first = vdl.call(L6, fn, *args, **kwargs)
            self.assertEqual(vdl.call(L6, fn, *args, **kwargs), first)
            self.assertEqual(caches.vdl.restricted_counters().get(f"{L6}:hit"), 1)
            # The canonical spelling is a different key (the value may quote its spelling).
            canonical_fn, canonical_args, canonical_kwargs = self.l6(self.path)
            vdl.call(L6, canonical_fn, *canonical_args, **canonical_kwargs)
            self.assertEqual(caches.vdl.restricted_counters().get(f"{L6}:hit"), 1)
            # Retarget the ancestor link to a copy whose calibration bytes differ.
            other = self.tmp / "other"
            shutil.copytree(real, other, symlinks=True)
            manifest = other / self.path.name / "metadata.json"
            changed = dict(self.metadata, instrument_calibration=dict(self.calibration, b_fiducial_s=0.5))
            manifest.write_text(json.dumps(changed), encoding="utf-8")
            alias.unlink()
            os.symlink(other, alias)
            serial = fn(*args, **kwargs)
            self.assertEqual(vdl.call(L6, fn, *args, **kwargs), serial)
            self.assertEqual(caches.vdl.restricted_counters().get(f"{L6}:hit"), 1)

    def test_only_absolute_normal_spellings_reach_the_store(self):
        base = str(self.path)
        spellings = (base + "/", base.replace("/archive/", "/archive/./"), base.replace("/archive/", "/archive//"),
                     os.path.relpath(base), str(self.path.parent / "x" / ".." / self.path.name))
        for spelling in spellings:
            with self.subTest(spelling=spelling), run() as caches:
                fn, args, kwargs = self.l6(spelling)
                self.assertEqual(vdl.call(L6, fn, *args, **kwargs), fn(*args, **kwargs))
                self.assertEqual(caches.vdl.restricted_counters(), {f"{L6}:bypass": 1})


# ------------------------------------------------------------------------ V2


class V2ShadowComparesDecisions(_Fixture):
    """An unstorable shadow recompute is still compared by its decision."""

    def _tampered(self, leaf, fn, args, kwargs, replacement):
        with run() as producer:
            vdl.call(leaf, fn, *args, **kwargs)
            payload = producer.vdl.export_entries()
        (key, entry), = payload["entries"].items()
        payload["entries"] = {key: dataclasses.replace(entry, value=pickle.dumps(replacement(pickle.loads(entry.value))))}
        return payload

    def test_a_different_decision_is_a_defect(self):
        fn, args, kwargs = self.l6(self.path)
        payload = self._tampered(L6, fn, args, kwargs, lambda _: (None, "instrument_calibration_invalid"))
        with run(SHADOW, entries=payload) as consumer:
            consumer.deadline = None  # every recompute is unstorable, so not comparable in full
            served = vdl.call(L6, fn, *args, **kwargs)
            counters = consumer.vdl.restricted_counters()
            self.assertEqual(served, fn(*args, **kwargs))
            self.assertTrue(consumer.vdl.defect_pending())
            self.assertEqual(counters.get(f"{L6}:shadow_mismatch"), 1)
            self.assertNotIn(f"{L6}:shadow_incomparable", counters)
            self.assertEqual(consumer.vdl._entries, {}, "the key is poisoned")
            with self.assertRaises(vdl.VerifiedStoreDefect):
                consumer.vdl.check_defects()

    def test_another_refusal_is_a_defect(self):
        (self.path / "config.json").unlink()
        (self.path / "config.json").mkdir()
        payload = self._tampered(L3, vdl.reduce_bundle_dict, (self.path,), {},
                                 lambda value: dict(value, failure_reason="schema_error"))
        with run(SHADOW, entries=payload) as consumer:
            consumer.deadline = None
            vdl.call(L3, vdl.reduce_bundle_dict, self.path)
            self.assertTrue(consumer.vdl.defect_pending())

    def _assert_value_defect(self, consumer, leaf, counters, key):
        self.assertTrue(consumer.vdl.defect_pending())
        self.assertEqual(consumer.vdl._defects, [f"{leaf}:shadow_value_mismatch"])
        self.assertEqual(counters.get(f"{leaf}:shadow_mismatch"), 1)
        self.assertNotIn(f"{leaf}:shadow_incomparable", counters)
        self.assertNotIn(key, consumer.vdl._entries, "the key is poisoned")
        self.assertIn(key, consumer.vdl._poisoned)
        with self.assertRaises(vdl.VerifiedStoreDefect):
            consumer.vdl.check_defects()

    def l2(self):
        from joulewise.reduce import _rederive_summary_for_authenticated_fiducial_bound as rederive

        return ww._member_operative_summary, (rederive, self.path, self.bound, self.metadata), {}

    def test_same_decision_other_number_is_a_defect(self):
        """Round 5 K1: the cold reviewer's check_shadow_same_kind_number.py, now a defect.

        A stored L6 bound that differs from serial (same decision kind: a bound,
        not a refusal), served against an unstorable recompute (no deadline).
        Before round 5 this counted ``shadow_incomparable_differs`` and the
        entry stayed live.
        """

        fn, args, kwargs = self.l6(self.path)
        payload = self._tampered(L6, fn, args, kwargs, lambda value: (value[0] * 1.5, value[1]))
        (key,) = payload["entries"]
        with run(SHADOW, entries=payload) as consumer:
            consumer.deadline = None  # recompute unstorable -> not comparable in full
            served = vdl.call(L6, fn, *args, **kwargs)
            counters = consumer.vdl.restricted_counters()
            self.assertEqual(served, fn(*args, **kwargs))
            self.assertIsNotNone(served[0])
            self._assert_value_defect(consumer, L6, counters, key)

    def test_a_blind_run_counts_the_value_defect_and_stops_serving(self):
        fn, args, kwargs = self.l6(self.path)
        payload = self._tampered(L6, fn, args, kwargs, lambda value: (value[0] * 1.5, value[1]))
        blind = vdl.Mode("shadow", 1000, blind=True)
        with run(blind, entries=payload) as consumer:
            consumer.deadline = None
            served = vdl.call(L6, fn, *args, **kwargs)
            counters = consumer.vdl.restricted_counters()
            self.assertEqual(served, fn(*args, **kwargs))
            self.assertFalse(consumer.vdl.defect_pending(), "a blind run never raises a defect")
            self.assertEqual(counters.get(f"defect:{L6}:shadow_value_mismatch"), 1)
            self.assertTrue(consumer.vdl._serving_disabled)
            consumer.vdl.check_defects()

    def test_l3_failure_message_is_not_audit_only(self):
        """L3's failure_message can decide L1 (cli AXI strict comparison): a defect."""

        (self.path / "config.json").unlink()
        (self.path / "config.json").mkdir()
        payload = self._tampered(L3, vdl.reduce_bundle_dict, (self.path,), {},
                                 lambda value: dict(value, failure_message="elsewhere"))
        (key,) = payload["entries"]
        with run(SHADOW, entries=payload) as consumer:
            consumer.deadline = None
            served = vdl.call(L3, vdl.reduce_bundle_dict, self.path)
            counters = consumer.vdl.restricted_counters()
            self.assertEqual(served, vdl.reduce_bundle_dict(self.path))
            self._assert_value_defect(consumer, L3, counters, key)

    def test_an_audit_only_difference_is_counted_not_a_defect(self):
        """L2's failure_message on a failed summary is the one enumerated audit-only field."""

        (self.path / "config.json").unlink()
        (self.path / "config.json").mkdir()
        fn, args, kwargs = self.l2()
        payload = self._tampered(L2, fn, args, kwargs, lambda value: dict(value, failure_message="elsewhere"))
        with run(SHADOW, entries=payload) as consumer:
            consumer.deadline = None
            served = vdl.call(L2, fn, *args, **kwargs)
            counters = consumer.vdl.restricted_counters()
        self.assertEqual(served["status"], "failed")
        self.assertEqual(served, fn(*args, **kwargs))
        self.assertFalse(consumer.vdl.defect_pending())
        self.assertEqual(counters.get(f"{L2}:shadow_incomparable"), 1)
        self.assertEqual(counters.get(f"{L2}:shadow_incomparable_differs"), 1)

    def test_l2_other_differences_are_defects(self):
        fn, args, kwargs = self.l2()
        cases = {
            "succeeded, number": (False, lambda value: dict(value, gross_energy_j=value["gross_energy_j"] * 2)),
            "succeeded, message": (False, lambda value: dict(value, failure_message="elsewhere")),
            "failed, message and number": (True, lambda value: dict(value, failure_message="elsewhere",
                                                                    gross_energy_j=1.0)),
            "failed, message None": (True, lambda value: dict(value, failure_message=None)),
        }
        for name, (broken, replacement) in cases.items():
            with self.subTest(case=name):
                if broken and (self.path / "config.json").is_file():
                    (self.path / "config.json").unlink()
                    (self.path / "config.json").mkdir()
                payload = self._tampered(L2, fn, args, kwargs, replacement)
                (key,) = payload["entries"]
                with run(SHADOW, entries=payload) as consumer:
                    consumer.deadline = None
                    served = vdl.call(L2, fn, *args, **kwargs)
                    counters = consumer.vdl.restricted_counters()
                    self.assertEqual(served["status"], "failed" if broken else "succeeded")
                    self._assert_value_defect(consumer, L2, counters, key)

    def test_audit_only_fields(self):
        only = vdl._differs_only_in_audit_text
        failed = {"status": "failed", "failure_reason": "unknown_error", "failure_message": "x", "gross_energy_j": None}
        self.assertEqual(dict(vdl._AUDIT_ONLY_TEXT), {L2: frozenset({"failure_message"})})
        self.assertTrue(only(L2, failed, dict(failed, failure_message="y")))
        for leaf in ("L1_strict_validation", L3, "L4_calibration_bracket", L5, L6, "synthetic"):
            self.assertFalse(only(leaf, failed, dict(failed, failure_message="y")))
        self.assertFalse(only(L2, failed, dict(failed, failure_message=None)))
        self.assertFalse(only(L2, failed, dict(failed, failure_message="y", gross_energy_j=1.0)))
        self.assertFalse(only(L2, failed, dict(failed, failure_message="y", extra=None)))
        self.assertFalse(only(L2, failed, {key: failed[key] for key in reversed(list(failed))}))
        succeeded = dict(failed, status="succeeded", failure_reason=None)
        self.assertFalse(only(L2, succeeded, dict(succeeded, failure_message="y")))
        self.assertFalse(only(L2, (0.25, None), (0.5, None)))

    def test_decision_kinds(self):
        kind = vdl._decision_kind
        self.assertNotEqual(kind(L6, (0.25, None)), kind(L6, (None, "instrument_calibration_invalid")))
        self.assertEqual(kind(L6, (0.25, None)), kind(L6, (0.5, None)))
        self.assertNotEqual(kind(L5, ()), kind(L5, ("environment_admission_missing",)))
        self.assertNotEqual(kind(L5, ("a",)), kind(L5, ("b",)))
        self.assertNotEqual(kind("L1_strict_validation", []), kind("L1_strict_validation", ["problem"]))
        summary = {"status": "failed", "failure_reason": "unknown_error", "failure_message": "x"}
        self.assertEqual(kind(L2, summary), kind(L2, dict(summary, failure_message="y")))
        self.assertNotEqual(kind(L2, summary), kind(L2, dict(summary, status="succeeded", failure_reason=None)))
        self.assertNotEqual(kind("L4_calibration_bracket", ({"status": "passed"}, ())),
                            kind("L4_calibration_bracket", ({"status": "failed"}, ("r",))))


if __name__ == "__main__":
    unittest.main()
