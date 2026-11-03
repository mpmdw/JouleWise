"""D-188 VDL-FIX round 2: Sol hunt-2 counterexamples (HB, HC1) and the reduce-leaf keying (RL).

HB (P1): an L6 fill made while another member's bound sat in the shared local
dict (a warm fill) must never serve a cold consumer, whose serial refit
returns its own, lower bound. Fixed by the #639 physics-kinds plan; the
admission rule is now also stated in ``_verify`` (a cold consumer is served
only by a fill that started cold for the key, or never consulted it).

HC1 (P1): an attempted open that failed, or found a directory, left no
dependency, so a same-named entry changing type (directory to file, file to
directory) or a failed no-follow read becoming readable kept serving a stale
L5 hit, also a shipped one into a V2 session (bypassing the consumer
grammar). Listings now bind each entry's own type, an opened directory binds
that it is one (with its mode), and a no-follow component opened more often
than successful rows account for makes the fill unstorable.

RL: step 1's L1 fill calls L3 with ``reader.path`` (a capability path) while
the step-2 ``reduce`` verb probes with a plain path; ``reduce_bundle_dict``
uses its path only as ``Path(path)``, so both are keyed as a plain path. The
pins below hold the argument (``reduce_bundle``'s only use of the argument).

Synthetic data only: the committed S10 ALPHA fixture and temporary trees.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import dataclasses
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import textwrap
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import whole_window as ww

MODULE = __name__


class Deadline:
    firings = 0


@contextlib.contextmanager
def run(mode=vdl.ON, physics=None, entries=None):
    with arc.analysis_run_caches({} if physics is None else physics, vdl_mode=mode,
                                 vdl_entries=entries) as caches:
        caches.deadline = Deadline()
        yield caches


def _extract_member(parent: Path) -> Path:
    from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER

    with tarfile.open(ARCHIVE) as blob:
        blob.extractall(parent / "source", members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)],
                        filter="data")
    return parent / "source" / MEMBER


def _outcome(fn):
    from joulewise.authentication_io import V2AuthenticationInputError

    try:
        return ("value", tuple(fn()))
    except V2AuthenticationInputError as exc:
        return ("raised", type(exc).__name__, exc.reason)


class _Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="vdl-sol-hunt2-"))
        cls.member = _extract_member(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def scratch(self, prefix: str) -> Path:
        root = Path(tempfile.mkdtemp(prefix=prefix, dir=self.tmp))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root


# ---------------------------------------------------------------- HB (L6)


class HBWarmFillNeverServesAColdConsumer(_Fixture):
    """Sol HB: /private/tmp/jwsol-hb/repros/repro_l6_warm_to_cold.py, asserting serial equivalence."""

    def test_l6_warm_to_cold_transplant(self):
        from joulewise.authentication_io import V2AuthenticationReadSession
        from joulewise.bundle_read import BundleReader

        root = self.scratch("l6-warm-to-cold-")
        low_path = root / "low" / self.member.name
        shutil.copytree(self.member, low_path)
        high_path = root / "high" / self.member.name
        shutil.copytree(self.member, high_path)
        low = json.loads((low_path / "metadata.json").read_bytes())
        high = copy.deepcopy(low)
        low_bound = low["instrument_calibration"]["b_fiducial_s"]
        high_bound = low_bound + 5e-13
        self.assertTrue(0 < high_bound - low_bound <= 1e-12)
        high["instrument_calibration"]["b_fiducial_s"] = high_bound
        high["instrument_calibration"]["verified_effective_b_fiducial_s"] = high_bound
        (high_path / "metadata.json").write_text(json.dumps(high), encoding="utf-8")
        key = low["instrument_calibration"]["artifact_sha256"]

        def routed(path, metadata, local):
            return ww._verified_instrument_calibration(
                path, metadata, metadata["instrument_calibration"],
                physics_cache=ww.physics_cache_for(local, metadata), local=local)

        physics: dict = {}
        shared_local: dict = {}
        with ww.shared_instrument_calibration_physics_cache(physics), run(physics=physics) as caches:
            with V2AuthenticationReadSession():
                self.assertEqual(routed(high_path, high, shared_local), (high_bound, None))
                # The warm fill: the higher member's bound is already in front.
                self.assertEqual(routed(low_path, low, shared_local), (high_bound, None))
            self.assertNotIn(low_bound.hex(), physics)
            before = copy.deepcopy(physics)
            cold_local: dict = {}
            with V2AuthenticationReadSession():
                served = routed(low_path, low, cold_local)
            counters = caches.vdl.restricted_counters()
        serial_physics = copy.deepcopy(before)
        serial_local: dict = {}
        with ww.shared_instrument_calibration_physics_cache(serial_physics), V2AuthenticationReadSession():
            serial = ww._verify_instrument_calibration(
                BundleReader(low_path), low, low["instrument_calibration"],
                strict_physics=True, physics_cache=ww.physics_cache_for(serial_local, low))
        self.assertEqual(serial, (low_bound, None))
        self.assertEqual(served, serial)
        self.assertEqual(cold_local, serial_local)
        self.assertEqual(physics, serial_physics)
        self.assertEqual(physics[low_bound.hex()][key].hex(), low_bound.hex())
        self.assertNotIn("L6_verify_instrument_calibration:hit", counters)


def reducer_like(path, cache):
    bound = cache.get("cal")
    if bound is None:
        bound = float((Path(path) / "fit.txt").read_text())
        cache["cal"] = bound
    return bound


class HBAdmissionRule(unittest.TestCase):
    """The rule in ``_verify`` itself: a cold consumer only from a cold (or non-consulting) fill."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-hb-rule-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "fit.txt").write_text("2.5")
        spec = vdl.LeafSpec("W_hb", (f"{MODULE}:reducer_like",), (("path", vdl.TREE), ("cache", vdl.PHYSICS)),
                            physics_probe=lambda arguments: [(arguments["cache"], "cal")])
        registration = vdl._registered(spec)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)

    def _verified(self, kind):
        with run() as caches:
            self.assertEqual(vdl.call("W_hb", reducer_like, self.tmp, {}), 2.5)
            (key, entry), = caches.vdl._entries.items()
            self.assertEqual(dict(entry.physics_kinds), {"cal": "set"})
            caches.vdl._entries[key] = dataclasses.replace(entry, physics_kinds=(("cal", kind),))
            prepared = caches.vdl._prepare(vdl._LEAVES_BY_ID["W_hb"], reducer_like, (self.tmp, {}), {})
            with mock.patch.object(vdl.VerifiedStore, "_physics_plan", return_value=[]):
                return caches.vdl._verify(caches.vdl._entries[key], prepared)

    def test_cold_consumer_needs_a_cold_or_non_consulting_fill(self):
        for kind, admitted in (("set", True), ("absent", True), ("noconsult", True),
                               ("promote", False), ("opaque", False)):
            with self.subTest(kind=kind):
                self.assertEqual(self._verified(kind) is not None, admitted)

    def test_reducer_never_tests_membership_without_promoting(self):
        """``noconsult`` rests on the reducer consulting only through the promoting ``get``."""

        from joulewise import reduce

        source = inspect.getsource(reduce._verify_instrument_calibration)
        self.assertEqual(source.count("physics_cache.get("), 1)
        self.assertNotIn("in physics_cache", source)
        self.assertNotIn("__contains__", source)


# --------------------------------------------------------------- HC1 (L5)


def list_files(path, directory):
    """A listing whose answer depends on entry types only (scandir d_type, no open, no stat)."""

    return sorted(entry.name for entry in os.scandir(directory) if entry.is_file(follow_symlinks=False))


def nofollow_first(path, directories):
    """Try each directory's ``p.json`` without following symlinks; the first readable one wins."""

    from joulewise.authentication_io import read_authentication_input_nofollow

    for directory in directories:
        try:
            return read_authentication_input_nofollow(directory, "p.json", grammar="raw", label="x").decode()
        except OSError:
            continue
    return None


def open_first(path, candidates):
    for candidate in candidates:
        try:
            return Path(candidate).read_text()
        except OSError:
            continue
    return None


class HC1FailedOpens(_Fixture):
    """Sol HC1: /private/tmp/jwsol-hc/repro_policy_shipped.py and repro_policy_type.py, asserting equivalence."""

    def _policy(self):
        from joulewise import environment_admission as ea
        from joulewise.bundle_read import BundleReader

        metadata = json.loads((self.member / "metadata.json").read_bytes())
        window = BundleReader(self.member).measured_window()
        expected = metadata["campaign_policy"]["sha256"]
        raw = next(p.read_bytes() for p in sorted(ea.REGISTERED_POLICY_DIR.glob("*.json"))
                   if hashlib.sha256(p.read_bytes()).hexdigest() == expected)

        args = {"bundle_path": self.member, "measured_window_start_s": window.start_s,
                "measured_window_end_s": window.end_s, "post_run_collector_raised_unmeasured": True}

        def call():
            return ww._verified_environment_refusals(metadata, **args)

        def serial():
            return ea.current_environment_refusals(metadata, **args)

        return raw, call, serial

    def test_shipped_hit_after_a_directory_candidate_became_invalid_json(self):
        from joulewise import environment_admission as ea
        from joulewise.authentication_io import V2AuthenticationReadSession

        raw, call, serial_call = self._policy()
        policies = self.scratch("policy-ship-") / "policies"
        policies.mkdir()
        (policies / "100-valid.json").write_bytes(raw)
        candidate = policies / "000-placeholder.json"
        candidate.mkdir()
        with mock.patch.object(ea, "REGISTERED_POLICY_DIR", policies):
            with run(vdl.BLIND_ON) as filler:
                with V2AuthenticationReadSession():
                    first = _outcome(call)
                payload = filler.vdl.export_entries(new_only=True)
            self.assertEqual(first, ("value", ()))
            self.assertEqual(len(payload["entries"]), 1)
            candidate.rmdir()
            candidate.write_text("{broken json")
            with run(vdl.BLIND_ON) as consumer:
                consumer.vdl.merge_entries(payload)
                with V2AuthenticationReadSession():
                    served = _outcome(call)
                counters = consumer.vdl.restricted_counters()
            with V2AuthenticationReadSession():
                serial = _outcome(serial_call)
        self.assertEqual(serial, ("raised", "V2AuthenticationInputError", "v2_authentication_invalid_json"))
        self.assertEqual(served, serial)
        self.assertNotIn("L5_environment_refusals:hit", counters)

    def test_directory_candidate_replaced_by_the_valid_policy(self):
        from joulewise import environment_admission as ea

        raw, call, serial_call = self._policy()
        policies = self.scratch("policy-type-") / "policies"
        policies.mkdir()
        candidate = policies / "policy.json"
        candidate.mkdir()
        with mock.patch.object(ea, "REGISTERED_POLICY_DIR", policies), run() as caches:
            first = call()
            self.assertEqual(len(caches.vdl._entries), 1)
            candidate.rmdir()
            candidate.write_bytes(raw)
            serial = serial_call()
            served = call()
            counters = caches.vdl.restricted_counters()
        self.assertEqual(first, ("environment_admission_missing",))
        self.assertEqual(serial, ())
        self.assertEqual(served, serial)
        self.assertEqual(counters.get("L5_environment_refusals:hit", 0), 0)

    def test_unreadable_or_dangling_candidates_are_unstorable(self):
        """A failed file open (no directory there) leaves nothing to re-verify: never stored."""

        from joulewise import environment_admission as ea

        raw, call, _ = self._policy()
        for label in ("dangling", "unreadable"):
            with self.subTest(candidate=label):
                policies = self.scratch(f"policy-{label}-") / "policies"
                policies.mkdir()
                (policies / "100-valid.json").write_bytes(raw)
                candidate = policies / "000-candidate.json"
                if label == "dangling":
                    candidate.symlink_to(policies / "missing-target.json")
                else:
                    candidate.write_text("{}")
                    candidate.chmod(0)
                    self.addCleanup(candidate.chmod, 0o600)
                    if os.access(candidate, os.R_OK):
                        self.skipTest("running with read access to mode-0 files")
                with mock.patch.object(ea, "REGISTERED_POLICY_DIR", policies), run() as caches:
                    self.assertEqual(call(), ())
                    self.assertEqual(caches.vdl._entries, {})


class HC1Synthetic(unittest.TestCase):
    """HC1 in miniature: entry kinds in listings, and failed no-follow reads."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-hc1-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.tree = self.tmp / "bundle"
        self.tree.mkdir()
        (self.tree / "fit.txt").write_text("1")

    def test_listing_binds_entry_kinds(self):
        directory = self.tmp / "candidates"
        directory.mkdir()
        (directory / "a.json").mkdir()
        (directory / "b.json").write_text("1")
        spec = vdl.LeafSpec("W_list", (f"{MODULE}:list_files",), (("path", vdl.TREE), ("directory", vdl.SCALAR)))
        with vdl._registered(spec), run() as caches:
            self.assertEqual(vdl.call("W_list", list_files, self.tree, str(directory)), ["b.json"])
            self.assertEqual(vdl.call("W_list", list_files, self.tree, str(directory)), ["b.json"])
            self.assertEqual(caches.vdl.restricted_counters().get("W_list:hit"), 1)
            (directory / "a.json").rmdir()
            (directory / "a.json").write_text("0")
            fresh = list_files(self.tree, str(directory))
            self.assertEqual(fresh, ["a.json", "b.json"])
            self.assertEqual(vdl.call("W_list", list_files, self.tree, str(directory)), fresh)
            self.assertEqual(caches.vdl.restricted_counters().get("W_list:hit"), 1)

    def test_failed_nofollow_read_is_unstorable(self):
        first, second = self.tmp / "first", self.tmp / "second"
        first.mkdir()
        second.mkdir()
        (second / "p.json").write_text("2")
        spec = vdl.LeafSpec("W_nofollow_first", (f"{MODULE}:nofollow_first",),
                            (("path", vdl.TREE), ("directories", vdl.SCALAR)))
        directories = (str(first), str(second))
        with vdl._registered(spec), run() as caches:
            self.assertEqual(vdl.call("W_nofollow_first", nofollow_first, self.tree, directories), "2")
            self.assertEqual(caches.vdl._entries, {})
            (first / "p.json").write_text("1")
            fresh = nofollow_first(self.tree, directories)
            self.assertEqual(fresh, "1")
            self.assertEqual(vdl.call("W_nofollow_first", nofollow_first, self.tree, directories), fresh)
            self.assertNotIn("W_nofollow_first:hit", caches.vdl.restricted_counters())

    def test_successful_nofollow_reads_still_store_and_hit(self):
        second = self.tmp / "second"
        (second / "sub").mkdir(parents=True)
        (second / "sub" / "p.json").write_text("2")
        spec = vdl.LeafSpec("W_nofollow_ok", (f"{MODULE}:nofollow_first",),
                            (("path", vdl.TREE), ("directories", vdl.SCALAR)))
        directories = (str(second / "sub"), str(second / "sub"))
        with vdl._registered(spec), run() as caches:
            self.assertEqual(vdl.call("W_nofollow_ok", nofollow_first, self.tree, directories), "2")
            entry, = caches.vdl._entries.values()
            self.assertIn((str((second / "sub").resolve()), (second / "sub").stat().st_mode & 0o7777),
                          entry.directories)
            self.assertEqual(vdl.call("W_nofollow_ok", nofollow_first, self.tree, directories), "2")
            self.assertEqual(caches.vdl.restricted_counters().get("W_nofollow_ok:hit"), 1)

    def test_opened_directory_must_stay_a_directory_with_its_mode(self):
        candidate = self.tmp / "candidate.json"
        candidate.mkdir()
        fallback = self.tmp / "fallback.json"
        fallback.write_text("fallback")
        spec = vdl.LeafSpec("W_open_first", (f"{MODULE}:open_first",),
                            (("path", vdl.TREE), ("candidates", vdl.SCALAR)))
        candidates = (str(candidate), str(fallback))
        with vdl._registered(spec), run() as caches:
            self.assertEqual(vdl.call("W_open_first", open_first, self.tree, candidates), "fallback")
            self.assertEqual(vdl.call("W_open_first", open_first, self.tree, candidates), "fallback")
            self.assertEqual(caches.vdl.restricted_counters().get("W_open_first:hit"), 1)
            candidate.rmdir()
            candidate.write_text("candidate")
            fresh = open_first(self.tree, candidates)
            self.assertEqual(fresh, "candidate")
            self.assertEqual(vdl.call("W_open_first", open_first, self.tree, candidates), fresh)
            self.assertEqual(caches.vdl.restricted_counters().get("W_open_first:hit"), 1)


# ------------------------------------------------------------------- RL (L3)


class RLReduceLeafKeying(unittest.TestCase):
    """``plain_trees`` is sound only while the L3 body and ``reduce_bundle`` use the path as ``Path(path)``."""

    def test_only_the_reduce_leaf_keys_capability_paths_as_plain(self):
        self.assertEqual([spec.leaf_id for spec in vdl.LEAVES if spec.plain_trees], ["L3_reduce_dict"])

    def test_reduce_leaf_body_normalizes_its_path_first(self):
        tree = ast.parse(textwrap.dedent(inspect.getsource(vdl.reduce_bundle_dict)))
        function = tree.body[0]
        body = [node for node in function.body
                if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))]
        imports, first = body[0], body[1]
        self.assertIsInstance(imports, ast.ImportFrom)
        self.assertEqual(ast.unparse(first), "path = Path(path)")
        uses = [node for node in ast.walk(function) if isinstance(node, ast.Name) and node.id == "path"]
        # The assignment's target and source, then one argument per reduce_bundle call.
        self.assertEqual(len(uses), 4)

    def test_reduce_bundle_uses_its_path_only_as_a_plain_path(self):
        from joulewise import reduce

        function = ast.parse(textwrap.dedent(inspect.getsource(reduce.reduce_bundle))).body[0]
        uses = [node for node in ast.walk(function) if isinstance(node, ast.Name) and node.id == "path"]
        self.assertEqual(len(uses), 1)
        calls = [node for node in ast.walk(function) if isinstance(node, ast.Call)
                 and any(argument is uses[0] for argument in node.args)]
        self.assertEqual([ast.unparse(call) for call in calls], ["Path(path)"])
        self.assertIn("reader = BundleReader(Path(path))", ast.unparse(function))

    def test_capability_and_plain_path_share_one_entry(self):
        from joulewise.authentication_io import _RecordedAuthenticationPath, V2AuthenticationPath

        spec = vdl._LEAVES_BY_ID["L3_reduce_dict"]
        store = vdl.VerifiedStore(vdl.ON)
        tmp = Path(tempfile.mkdtemp(prefix="vdl-rl-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "metadata.json").write_text("{}")
        keys = set()
        with run():
            for kind in (Path, _RecordedAuthenticationPath, V2AuthenticationPath):
                prepared = store._prepare(spec, vdl.reduce_bundle_dict, (kind(tmp),),
                                          {"reducer_version": None, "physics_cache": None})
                keys.add(prepared.key)
        self.assertEqual(len(keys), 1)


if __name__ == "__main__":
    unittest.main()
