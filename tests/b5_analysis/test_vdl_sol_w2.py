"""D-188 VDL-FIX: the two Sol wave-2 counterexamples, and the hit side-effect audit.

Sol #1 (P1): an L1/L3 hit returned the right value but skipped the run view's
partition-to-local promotion (``whole_window._RunPhysicsCacheView.get``), so a
later validation sharing the caller's local dict accepted a member the serial
path rejects. Sol #2 (P2): external reads and listings were bound only to
their resolved targets, so retargeting a symlink on the original pathname
served a stale L5 hit, also inside a V2 session through the bridge.

The audit: every caller-visible physics layer a served hit leaves behind must
equal the serial call's, for every fill state and every hit state (the store
core that L1, L2, L3 and L6 share); the leaf registry, the physics-cache
operations and the run memos are pinned so a new side effect needs review.
Synthetic data only (the committed S10 ALPHA fixture and temporary trees).
"""
from __future__ import annotations

import contextlib
import hashlib
import itertools
import json
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import whole_window as ww

ROOT = Path(__file__).resolve().parents[2]
MODULE = __name__
KEY = "cal"
FRESH = 2.5  # what the synthetic leaves fit from their tree
OTHER = 3.0  # a value some other partition's fit left in a shared local dict
CALLS: dict[str, int] = {}


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


# ----------------------------------------------------------- synthetic leaves


def _fit(path) -> float:
    return float((Path(path) / "fit.txt").read_text())


def reducer_like(path, cache):
    """The reducer's physics pattern: ``get``; on nothing, fit and insert."""

    CALLS["reducer_like"] = CALLS.get("reducer_like", 0) + 1
    bound = cache.get(KEY)
    if bound is None:
        bound = _fit(path)
        cache[KEY] = bound
    return {"bound": bound}


def never_consults(path, cache):
    """A leaf that returns before the reducer would consult the cache."""

    CALLS["never_consults"] = CALLS.get("never_consults", 0) + 1
    return {"bound": None, "fit": _fit(path)}


PARTITION = "p"


def own_view_leaf(path, factor):
    """L1 with no explicit cache (or L2): the leaf builds its own view over a fresh local dict."""

    CALLS["own_view_leaf"] = CALLS.get("own_view_leaf", 0) + 1
    return reducer_like(path, ww._RunPhysicsCacheView({}, arc.run_physics_store(), PARTITION))


def _own_view_probe(arguments):
    return [(ww._RunPhysicsCacheView(vdl._PrivateLocal(), arc.run_physics_store(), PARTITION), KEY)]


def _spec(leaf_id, fn, *, own_view=False):
    if own_view:
        return vdl.LeafSpec(leaf_id, (f"{MODULE}:{fn.__qualname__}",),
                            (("path", vdl.TREE), ("factor", vdl.SCALAR)), physics_probe=_own_view_probe)
    return vdl.LeafSpec(leaf_id, (f"{MODULE}:{fn.__qualname__}",), (("path", vdl.TREE), ("cache", vdl.PHYSICS)),
                        physics_probe=lambda arguments: [(arguments["cache"], KEY)])


SPECS = (
    _spec("W_reduce", reducer_like),
    _spec("W_never", never_consults),
    _spec("W_own", own_view_leaf, own_view=True),
)

# A layer state: None (no such layer), "A" (key absent), or a float.
VALUES = ("A", FRESH, OTHER)


def _layer(mapping, value):
    if value is not None and value != "A":
        mapping[KEY] = value


def _read(mapping):
    return mapping.get(KEY, "A")


class _Synthetic(unittest.TestCase):
    def setUp(self):
        CALLS.clear()
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-sol-w2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        registration = vdl._registered(*SPECS)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)
        self.tree = self.tmp / "bundle"
        self.tree.mkdir()
        (self.tree / "fit.txt").write_text(repr(FRESH))


class PhysicsSideEffectMatrix(_Synthetic):
    """Store core audit (L1, L2, L3, L6 share ``_apply``): served == serial in every layer, every state."""

    def _sequence(self, leaf_id, fn, view_kind, fill_state, hit_state, *, store):
        """Fill in ``fill_state``, then call again in ``hit_state``; values and layers after each call."""

        outcomes = []
        physics: dict = {}
        context = run(physics=physics) if store else contextlib.nullcontext()
        with context:
            for local_value, shared_value in (fill_state, hit_state):
                if view_kind == "dict":
                    local = {}
                    _layer(local, local_value)
                    argument = local
                    shared = None
                else:
                    partition = physics.setdefault(PARTITION, {})
                    partition.clear()
                    _layer(partition, shared_value)
                    local = {}
                    _layer(local, local_value)
                    argument = ww._RunPhysicsCacheView(local, physics, PARTITION)
                    shared = partition
                if view_kind == "own":
                    if store:
                        value = vdl.call(leaf_id, fn, self.tree, 1)
                    else:
                        with arc.analysis_run_caches(physics):
                            value = fn(self.tree, 1)
                    outcomes.append((value, _read(physics[PARTITION])))
                    continue
                value = vdl.call(leaf_id, fn, self.tree, argument) if store else fn(self.tree, argument)
                outcomes.append((value, _read(local), None if shared is None else _read(physics[PARTITION])))
        return outcomes

    def _matrix(self, leaf_id, fn, view_kind):
        if view_kind == "dict":
            states = [(value, None) for value in VALUES]
        elif view_kind == "own":
            states = [(None, value) for value in VALUES]
        else:
            states = list(itertools.product(VALUES, VALUES))
        served = 0
        for fill_state, hit_state in itertools.product(states, states):
            with self.subTest(leaf=leaf_id, view=view_kind, fill=fill_state, hit=hit_state):
                before = CALLS.get(fn.__name__, 0)
                serial = self._sequence(leaf_id, fn, view_kind, fill_state, hit_state, store=False)
                middle = CALLS.get(fn.__name__, 0)
                stored = self._sequence(leaf_id, fn, view_kind, fill_state, hit_state, store=True)
                served += (middle - before) - (CALLS.get(fn.__name__, 0) - middle)
                self.assertEqual(stored, serial)
        return served

    def test_run_view_with_a_caller_local_dict(self):
        # L1/L3 with an explicit local dict (bracket selection), L6 through a run view.
        self.assertGreater(self._matrix("W_reduce", reducer_like, "view"), 0)

    def test_plain_dict(self):
        # A caller's own dict outside a run partition (L3, L6 with no run store).
        self.assertGreater(self._matrix("W_reduce", reducer_like, "dict"), 0)

    def test_leaf_that_never_consults(self):
        self.assertGreater(self._matrix("W_never", never_consults, "view"), 0)

    def test_leaf_building_its_own_view(self):
        # L1 with no explicit cache and no session, and L2: only the partition is visible.
        self.assertGreater(self._matrix("W_own", own_view_leaf, "own"), 0)

    def test_the_reported_promotion_is_replayed(self):
        """Sol #1 in miniature: warm partition, empty local dict, a hit."""

        physics = {PARTITION: {KEY: FRESH}}
        with run(physics=physics) as caches:
            vdl.call("W_reduce", reducer_like, self.tree, ww._RunPhysicsCacheView({}, physics, PARTITION))
            local: dict = {}
            vdl.call("W_reduce", reducer_like, self.tree, ww._RunPhysicsCacheView(local, physics, PARTITION))
            self.assertEqual(caches.vdl.restricted_counters().get("W_reduce:hit"), 1)
        self.assertEqual(local, {KEY: FRESH})

    def test_shadow_compares_every_layer(self):
        """A served hit that would omit the promotion is a shadow mismatch (it was invisible before)."""

        import dataclasses

        physics = {PARTITION: {KEY: FRESH}}
        with run(vdl.Mode("shadow", 1000), physics=physics) as caches:
            vdl.call("W_reduce", reducer_like, self.tree, ww._RunPhysicsCacheView({}, physics, PARTITION))
            (key, entry), = caches.vdl._entries.items()
            caches.vdl._entries[key] = dataclasses.replace(entry, physics_kinds=((KEY, "noconsult"),))
            local: dict = {}
            vdl.call("W_reduce", reducer_like, self.tree, ww._RunPhysicsCacheView(local, physics, PARTITION))
            self.assertEqual(local, {KEY: FRESH})  # the caller got the recomputed state
            self.assertTrue(caches.vdl.defect_pending())


class PathnameBinding(_Synthetic):
    """Sol #2 in miniature: an extra read and a listing through a symlinked directory."""

    def test_retargeted_symlink_is_a_miss(self):
        good, bad = self.tmp / "good", self.tmp / "bad"
        good.mkdir()
        bad.mkdir()
        (good / "policy.json").write_text("1")
        (bad / "policy.json").write_text("2")
        alias = self.tmp / "alias"
        alias.symlink_to(good, target_is_directory=True)
        spec = vdl.LeafSpec("W_alias", (f"{MODULE}:{read_through.__qualname__}",),
                            (("path", vdl.TREE), ("directory", vdl.SCALAR)))
        with vdl._registered(spec), run() as caches:
            self.assertEqual(vdl.call("W_alias", read_through, self.tree, str(alias)), ["1"])
            entry, = caches.vdl._entries.values()
            self.assertIn((str(alias / "policy.json"), str((good / "policy.json").resolve())), entry.aliases)
            self.assertEqual(vdl.call("W_alias", read_through, self.tree, str(alias)), ["1"])
            self.assertEqual(caches.vdl.restricted_counters().get("W_alias:hit"), 1)
            alias.unlink()
            alias.symlink_to(bad, target_is_directory=True)
            self.assertEqual(vdl.call("W_alias", read_through, self.tree, str(alias)), ["2"])
            self.assertEqual(caches.vdl.restricted_counters().get("W_alias:hit"), 1)

    def test_tree_read_through_a_foreign_alias_is_unstorable(self):
        alias = self.tmp / "elsewhere"
        alias.symlink_to(self.tree, target_is_directory=True)
        spec = vdl.LeafSpec("W_alias_tree", (f"{MODULE}:{read_tree_through.__qualname__}",),
                            (("path", vdl.TREE), ("directory", vdl.SCALAR)))
        with vdl._registered(spec), run() as caches:
            vdl.call("W_alias_tree", read_tree_through, self.tree, str(alias))
            self.assertEqual(caches.vdl._entries, {})


    # Review of #639 (LOW, latent): a no-follow read opens its directory by the
    # caller's pathname and reads the row relative to it; that directory
    # pathname must be bound too, or retargeting a component serves the old row.
    def _directory_route(self, session):
        from joulewise.authentication_io import V2AuthenticationReadSession

        good, bad = self.tmp / "good", self.tmp / "bad"
        for directory, value in ((good, "1"), (bad, "2")):
            (directory / "sub").mkdir(parents=True)
            (directory / "sub" / "p.json").write_text(value)
        alias = self.tmp / "link"
        alias.symlink_to(good, target_is_directory=True)
        directory = str(alias / "sub")
        spec = vdl.LeafSpec("W_nofollow", (f"{MODULE}:{read_nofollow_through.__qualname__}",),
                            (("path", vdl.TREE), ("directory", vdl.SCALAR)))

        def call(fn):
            with V2AuthenticationReadSession() if session else contextlib.nullcontext():
                return fn()

        with vdl._registered(spec), run() as caches:
            served = lambda: call(lambda: vdl.call("W_nofollow", read_nofollow_through, self.tree, directory))
            self.assertEqual(served(), "1")
            entry, = caches.vdl._entries.values()
            self.assertIn((directory, str((good / "sub").resolve())), entry.aliases)
            self.assertEqual(served(), "1")
            self.assertEqual(caches.vdl.restricted_counters().get("W_nofollow:hit"), 1)
            alias.unlink()
            alias.symlink_to(bad, target_is_directory=True)
            fresh = call(lambda: read_nofollow_through(self.tree, directory))
            self.assertEqual(fresh, "2")
            self.assertEqual(served(), fresh)
            self.assertEqual(caches.vdl.restricted_counters().get("W_nofollow:hit"), 1)

    def test_nofollow_directory_through_a_retargeted_component_is_a_miss(self):
        self._directory_route(session=False)

    def test_nofollow_directory_through_a_retargeted_component_is_a_miss_in_a_session(self):
        self._directory_route(session=True)

    # Review of #639 (LOW, latent): a relative pathname is bound to the cwd of
    # each hit, not to the cwd of the fill.
    def test_relative_read_is_resolved_against_the_cwd_of_the_hit(self):
        import os

        good, bad = self.tmp / "good", self.tmp / "bad"
        for directory, value in ((good, "1"), (bad, "2")):
            directory.mkdir()
            (directory / "p.json").write_text(value)
        self.addCleanup(os.chdir, os.getcwd())
        spec = vdl.LeafSpec("W_relative", (f"{MODULE}:{read_relative.__qualname__}",),
                            (("path", vdl.TREE), ("name", vdl.SCALAR)))
        with vdl._registered(spec), run() as caches:
            os.chdir(good)
            self.assertEqual(vdl.call("W_relative", read_relative, self.tree, "p.json"), "1")
            entry, = caches.vdl._entries.values()
            self.assertIn(("p.json", str((good / "p.json").resolve())), entry.aliases)
            self.assertEqual(vdl.call("W_relative", read_relative, self.tree, "p.json"), "1")
            self.assertEqual(caches.vdl.restricted_counters().get("W_relative:hit"), 1)
            os.chdir(bad)
            fresh = read_relative(self.tree, "p.json")
            self.assertEqual(fresh, "2")
            self.assertEqual(vdl.call("W_relative", read_relative, self.tree, "p.json"), fresh)
            self.assertEqual(caches.vdl.restricted_counters().get("W_relative:hit"), 1)

    def test_relative_read_into_the_tree_is_unstorable(self):
        import os

        self.addCleanup(os.chdir, os.getcwd())
        spec = vdl.LeafSpec("W_relative_tree", (f"{MODULE}:{read_relative.__qualname__}",),
                            (("path", vdl.TREE), ("name", vdl.SCALAR)))
        with vdl._registered(spec), run() as caches:
            os.chdir(self.tree)
            vdl.call("W_relative_tree", read_relative, self.tree, "fit.txt")
            self.assertEqual(caches.vdl._entries, {})


def read_nofollow_through(path, directory):
    from joulewise.authentication_io import read_authentication_input_nofollow

    _fit(path)
    return read_authentication_input_nofollow(directory, "p.json", grammar="raw", label="x").decode()


def read_relative(path, name):
    _fit(path)
    with open(name, "rb") as handle:
        return handle.read().decode()


def read_through(path, directory):
    return [(Path(directory) / name).read_text() for name in sorted(p.name for p in Path(directory).glob("*.json"))]


def read_tree_through(path, directory):
    return (Path(directory) / "fit.txt").read_text()


# ------------------------------------------------------ Sol's reproducers (S10)


class SolWave2Reproducers(unittest.TestCase):
    """The two committed counterexamples, asserting serial equivalence (they asserted the defect)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="vdl-sol-w2-real-"))
        cls.low = _extract_member(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _two_members(self):
        """Sol #1's pair: one calibration artifact, metadata bounds 5e-13 apart (within the 1e-12 tolerance)."""

        from joulewise import cli
        from joulewise.reduce import reduce_bundle

        root = Path(tempfile.mkdtemp(prefix="pair-", dir=self.tmp))
        low = root / "low" / self.low.name
        shutil.copytree(self.low, low)
        high = root / "high" / self.low.name
        shutil.copytree(self.low, high)
        lowmeta = json.loads((low / "metadata.json").read_bytes())
        key = lowmeta["instrument_calibration"]["artifact_sha256"]
        cold: dict = {}
        self.assertEqual(cli.validate_bundle(low, True, physics_cache=cold), [])
        lowvalue = cold[key]
        highmeta = json.loads((high / "metadata.json").read_bytes())
        highmeta["instrument_calibration"]["b_fiducial_s"] += 5e-13
        highvalue = max(highmeta["instrument_calibration"]["b_fiducial_s"], lowvalue)
        highmeta["instrument_calibration"]["verified_effective_b_fiducial_s"] = highvalue
        (high / "metadata.json").write_text(json.dumps(highmeta))
        self.assertGreater(highvalue, lowvalue)
        summary = reduce_bundle(high, _instrument_calibration_physics_cache={key: highvalue}).to_dict()
        (high / "summary_metrics.json").write_text(json.dumps(summary))
        physics = {ww._effective_bound_partition(lowmeta): {key: lowvalue},
                   ww._effective_bound_partition(highmeta): {key: highvalue}}
        return low, high, key, physics

    def test_sol1_l1_and_nested_l3_hits_replay_the_local_promotion(self):
        from joulewise import cli

        low, high, key, physics = self._two_members()

        def sequence():
            local: dict = {}
            first = cli.validate_bundle(high, True, physics_cache=local)
            after_first = dict(local)
            second = cli.validate_bundle(low, True, physics_cache=local)
            return first, key in after_first, second

        def fresh_physics():
            return {partition: dict(values) for partition, values in physics.items()}

        serial_physics = fresh_physics()
        with ww.shared_instrument_calibration_physics_cache(serial_physics), arc.analysis_run_caches(serial_physics):
            serial = sequence()
        self.assertEqual(serial[0], [])
        self.assertTrue(serial[1])
        self.assertTrue(serial[2])  # the serial path rejects the second member

        # L1 route: the high member's validation is served from a warm entry.
        served_physics = fresh_physics()
        with ww.shared_instrument_calibration_physics_cache(served_physics), \
                run(vdl.BLIND_ON, physics=served_physics) as caches:
            self.assertEqual(cli.validate_bundle(high, True, physics_cache={}), [])
            served = sequence()
            counters = caches.vdl.restricted_counters()
            reductions = caches.vdl.export_entries(lambda _key, entry: entry.leaf_id == "L3_reduce_dict")
        self.assertGreaterEqual(counters.get("L1_strict_validation:hit", 0), 1)
        self.assertEqual(served, serial)
        self.assertEqual(served_physics, serial_physics)

        # Nested route: only L3 is seeded, so L1 fills and its inner L3 call is served.
        l3_physics = fresh_physics()
        with ww.shared_instrument_calibration_physics_cache(l3_physics), \
                run(vdl.BLIND_ON, physics=l3_physics, entries=reductions) as caches:
            served_l3 = sequence()
            counters = caches.vdl.restricted_counters()
        self.assertGreaterEqual(counters.get("L3_reduce_dict:hit", 0), 1)
        self.assertEqual(served_l3, serial)
        self.assertEqual(l3_physics, serial_physics)

        # Shadow agrees with serial and records no defect.
        shadow_physics = fresh_physics()
        with ww.shared_instrument_calibration_physics_cache(shadow_physics), \
                run(vdl.Mode("shadow", 1000), physics=shadow_physics) as caches:
            self.assertEqual(cli.validate_bundle(high, True, physics_cache={}), [])
            shadowed = sequence()
            self.assertFalse(caches.vdl.defect_pending())
        self.assertEqual(shadowed, serial)

    def test_sol2_retargeted_policy_directory_is_never_served(self):
        from joulewise import environment_admission as ea
        from joulewise.authentication_io import V2AuthenticationReadSession
        from joulewise.bundle_read import BundleReader

        root = Path(tempfile.mkdtemp(prefix="policy-alias-", dir=self.tmp))
        bundle = self.low
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        window = BundleReader(bundle).measured_window()
        digest = metadata["campaign_policy"]["sha256"]
        policy = next(p for p in ea.REGISTERED_POLICY_DIR.glob("*.json")
                      if hashlib.sha256(p.read_bytes()).hexdigest() == digest)
        good, bad = root / "good", root / "bad"
        good.mkdir()
        bad.mkdir()
        shutil.copy(policy, good / "policy.json")
        (bad / "policy.json").write_text("{}")
        alias = root / "policies"
        alias.symlink_to(good, target_is_directory=True)
        args = {"bundle_path": bundle, "measured_window_start_s": window.start_s,
                "measured_window_end_s": window.end_s, "post_run_collector_raised_unmeasured": False}
        with mock.patch.object(ea, "REGISTERED_POLICY_DIR", alias), run(vdl.BLIND_ON) as caches:
            first = ww._verified_environment_refusals(metadata, **args)
            again = ww._verified_environment_refusals(metadata, **args)
            self.assertEqual(first, again)
            self.assertEqual(caches.vdl.restricted_counters().get("L5_environment_refusals:hit"), 1)
            alias.unlink()
            alias.symlink_to(bad, target_is_directory=True)
            fresh = ea.current_environment_refusals(metadata, **args)
            cached = ww._verified_environment_refusals(metadata, **args)
            with V2AuthenticationReadSession():
                session_cached = ww._verified_environment_refusals(metadata, **args)
            with V2AuthenticationReadSession():
                session_fresh = ea.current_environment_refusals(metadata, **args)
            self.assertEqual(caches.vdl.restricted_counters().get("L5_environment_refusals:hit"), 1)
        self.assertEqual(first, ())
        self.assertEqual(fresh, ("environment_admission_missing",))
        self.assertEqual(cached, fresh)
        self.assertEqual(session_cached, session_fresh)
        self.assertEqual(session_fresh, ("environment_admission_missing",))


# ------------------------------------------------------------- registry audit


class LeafSideEffectAudit(unittest.TestCase):
    """Pins every caller-visible side effect the six leaves can have, so a new one needs review.

    * Physics caches (L1, L2, L3, L6): replayed exactly (``PhysicsSideEffectMatrix``).
    * V2 session records: rows, bridged and registered (test_vdl_core, test_auth_capability_bridge).
    * Mutable scalar arguments (L4's ``diagnostics``, ``ledger_snapshot``): a fill
      that changes any scalar's canonical form is never stored (test_vdl_core T_mutate).
    * Run memos: written by leaf bodies and skipped by a hit; each is a
      content-keyed, success-only memo whose presence changes no decision
      (their own tests: test_auth_recorder_and_verdict_memo,
      test_environment_admission_memo_first, test_leaf_cli).
    * ``analysis_run_cache.note`` counters: read only by ``stats()``, which no decision reads.
    """

    PHYSICS_LEAVES = {"L1_strict_validation", "L2_operative_summary", "L3_reduce_dict",
                      "L6_verify_instrument_calibration"}
    DECISION_INVARIANT_MEMOS = {"GRAMMAR_VERDICT_MEMO", "_STRICT_CLOCK_EVIDENCE_MEMO",
                                "_IDLE_PARSE_SUCCESS_MEMO", "_THERMAL_SCAN_MEMO"}

    def _sources(self):
        return {path: path.read_text() for path in sorted((ROOT / "joulewise").rglob("*.py"))}

    def test_six_leaves_and_their_physics(self):
        self.assertEqual([spec.leaf_id for spec in vdl.LEAVES],
                         ["L1_strict_validation", "L2_operative_summary", "L3_reduce_dict",
                          "L4_calibration_bracket", "L5_environment_refusals",
                          "L6_verify_instrument_calibration"])
        for spec in vdl.LEAVES:
            with self.subTest(leaf=spec.leaf_id):
                has_physics = spec.physics_probe is not None or vdl.PHYSICS in spec.roles().values()
                self.assertEqual(has_physics, spec.leaf_id in self.PHYSICS_LEAVES)

    def test_reducer_is_the_only_physics_cache_operator(self):
        """The kinds model rests on ``get`` then ``cache[key] = bound`` being the only operations."""

        pattern = re.compile(r"physics_cache(\.\w+\(|\[)")
        found = {}
        for path, text in self._sources().items():
            if path.name == "analysis_verified_store.py":
                continue
            for line in text.splitlines():
                for match in pattern.finditer(line):
                    found.setdefault(path.relative_to(ROOT).as_posix(), set()).add(match.group(1))
        self.assertEqual(found, {"joulewise/reduce.py": {".get(", "["}})

    def test_physics_view_operations_are_get_and_setitem(self):
        methods = {name for name in vars(ww._RunPhysicsCacheView) if not name.startswith("__") or name in
                   ("__contains__", "__getitem__", "__setitem__")}
        self.assertEqual(methods, {"get", "__contains__", "__getitem__", "__setitem__"})

    def test_probes_mark_leaf_built_views_private(self):
        metadata = {"instrument_calibration": {"artifact_sha256": "a" * 64, "b_fiducial_s": 0.5}}
        with run():
            with mock.patch.object(vdl, "_bundle_metadata", return_value=metadata):
                (view, _), = vdl._probe_strict({"path": "/x", "physics_cache": None})
                self.assertIsInstance(view._local, vdl._PrivateLocal)
                (explicit, _), = vdl._probe_strict({"path": "/x", "physics_cache": {}})
                self.assertNotIsInstance(explicit._local, vdl._PrivateLocal)
            (operative, _), = vdl._probe_operative({"metadata": metadata})
            self.assertIsInstance(operative._local, vdl._PrivateLocal)

    def test_run_memos_are_the_reviewed_decision_invariant_set(self):
        names = set()
        for path, text in self._sources().items():
            if path.name == "analysis_run_cache.py":
                continue
            names.update(re.findall(r"\bmemo\((\w+)\)", text))
        self.assertEqual(names, self.DECISION_INVARIANT_MEMOS)

    def test_run_counters_feed_no_decision(self):
        readers = [path for path, text in self._sources().items()
                   if path.name != "analysis_run_cache.py" and re.search(r"\.stats\(\)|\.hits\b|\.misses\b", text)]
        self.assertEqual(readers, [])


if __name__ == "__main__":
    unittest.main()
