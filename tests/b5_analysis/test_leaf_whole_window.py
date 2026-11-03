"""D-188 LEAF-WW: the whole_window verified-derivation leaves (L2, L3, L5, L6) and the clock guard.

Synthetic only: the two committed S10 ALPHA claim members (neg8-window-end-r1
and d117fq31p7-df-cmp-abba-ph-decode-b01-a2, one shared calibration artifact)
are extracted from the committed archive into a temporary directory. One cold
calibration refit (about 15 s on the analysis laptop, an estimate) runs once
per module, under a clock tracer; every test then starts from a copy of the
resulting physics store, so a leaf computation takes well under a second.

The gate is D-188 result equivalence: on a hit, every decision a caller makes
(refusal reasons and their positions, summaries, provenance, the V2 session's
registrations) equals the decision with no store.
"""
from __future__ import annotations

import ast
import contextlib
import datetime
import inspect
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import time
import types
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import whole_window as ww
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from joulewise.bundle_read import BundleReader

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "tests/fixtures/b5_analysis/s10/alpha/archive.tar.xz"
RUNS = "archive/sources/night-custody/runs_claim/"
NAMES = ("neg8-window-end-r1", "d117fq31p7-df-cmp-abba-ph-decode-b01-a2")
MONITORING = hasattr(sys, "monitoring")
needs_monitoring = unittest.skipUnless(
    MONITORING, "the store stores nothing without sys.monitoring (no V2 raise observer)")

CLOCKS = frozenset({
    time.time, time.time_ns, time.monotonic, time.monotonic_ns, time.perf_counter,
    time.perf_counter_ns, time.process_time, time.process_time_ns, time.thread_time,
    time.thread_time_ns, time.localtime, time.gmtime, time.ctime, time.strftime, time.asctime,
    time.clock_gettime, time.clock_gettime_ns, datetime.datetime.now, datetime.datetime.utcnow,
    datetime.datetime.today, datetime.date.today,
})
# The only wall-clock consultation on the leaf paths: the frozen 120 s projection
# host-safety deadline (powermetrics_fiducial._ProjectionWorkBudget, its
# dataclass default_factory included). The run's deadline observer counts its
# firings, and a fill during which the firing count changes is never stored; a
# budget that does not fire leaves the result deterministic (the cell budget is
# checked first).
OBSERVED_CLOCK_CALLERS = frozenset({
    ("joulewise/powermetrics_fiducial.py", "_ProjectionWorkBudget.consume_cell"),
    ("<string>", "__create_fn__.<locals>.__init__"),
})

_STATE: dict = {}


@contextlib.contextmanager
def clock_tracer():
    """Record (file, qualname) of every Python frame that calls a clock function."""

    seen: dict[tuple[str, str], int] = {}
    if not MONITORING:
        yield seen
        return
    monitoring = sys.monitoring
    tool = next((n for n in range(6) if monitoring.get_tool(n) is None), None)
    if tool is None:
        yield seen
        return
    monitoring.use_tool_id(tool, "leaf-ww-clock-tracer")

    def called(code, _offset, function, _arg0):
        try:
            if function in CLOCKS:
                filename = code.co_filename
                if "/joulewise/" in filename:
                    filename = "joulewise/" + filename.split("/joulewise/", 1)[1]
                key = (filename, code.co_qualname)
                seen[key] = seen.get(key, 0) + 1
        except TypeError:
            pass

    monitoring.register_callback(tool, monitoring.events.CALL, called)
    monitoring.set_events(tool, monitoring.events.CALL)
    try:
        yield seen
    finally:
        monitoring.set_events(tool, 0)
        monitoring.register_callback(tool, monitoring.events.CALL, None)
        monitoring.free_tool_id(tool)


def setUpModule():
    tmp = Path(tempfile.mkdtemp(prefix="leaf-ww-"))
    _STATE["tmp"] = tmp
    with tarfile.open(ARCHIVE) as blob:
        blob.extractall(tmp, members=[m for m in blob.getmembers()
                                      if m.name.startswith(tuple(RUNS + n + "/" for n in NAMES))],
                        filter="data")
    root = tmp / RUNS
    _STATE["root"] = root
    metadata = json.loads((root / NAMES[0] / "metadata.json").read_bytes())
    physics: dict = {}
    with clock_tracer() as seen, ww.shared_instrument_calibration_physics_cache(physics), \
            arc.analysis_run_caches(physics):
        verdict = ww._verify_instrument_calibration(
            BundleReader(root / NAMES[0]), dict(metadata), dict(metadata["instrument_calibration"]),
            strict_physics=True, physics_cache=arc.physics_cache_for_call({}, metadata))
    assert verdict[1] is None, verdict
    _STATE["physics"] = physics
    _STATE["cold_clock_callers"] = dict(seen)


def tearDownModule():
    shutil.rmtree(_STATE["tmp"], ignore_errors=True)


def physics_copy() -> dict:
    return {partition: dict(values) for partition, values in _STATE["physics"].items()}


@contextlib.contextmanager
def run(mode=vdl.ON, physics=None):
    """A driver-shaped run: shared physics store, run caches, a firing-free deadline observer."""

    store = physics_copy() if physics is None else physics
    with ww.shared_instrument_calibration_physics_cache(store), \
            arc.analysis_run_caches(store, vdl_mode=mode) as caches:
        caches.deadline = DeadlineObserver()
        yield caches


def records(session):
    return [(r.normalized_path, r.sha256, r.grammar, r.read_count, r.strict_parse_succeeded)
            for r in session.records.values()]


class Snapshot:
    refusal_reasons = ()
    ledger_schema = "synthetic"
    head_sequence = 1
    head_digest = "synthetic"


def prepare(root: Path, bound: float, *, clamp: bool = True):
    """One session preparation over both members, with the bracket assessment fixed at ``bound``."""

    session = ww.AuthenticatedConsumptionSession(
        root, set(NAMES), calibration_ledger_snapshot=Snapshot(), analysis_clamp=clamp)
    with mock.patch.object(ww, "calibration_bracket_for_bundles", return_value=({"b_fiducial_s": bound}, ())):
        session._prepare(bundle_paths={name: root / name for name in NAMES},
                         policy=types.SimpleNamespace(calibration_bracketing=None))
    return session


def outcome(session, v2):
    return {
        "refusal_reasons": session.refusal_reasons,
        "path_refusal_reasons": session.path_refusal_reasons,
        "ready": session.ready,
        "operative_fiducial_bound_s": session.operative_fiducial_bound_s,
        "summaries": {key: json.dumps(value, sort_keys=True) for key, value in session._summaries.items()},
        "provenance": {key: json.dumps(value, sort_keys=True) for key, value in session._provenance.items()},
        "records": records(v2),
    }


def member_metadata(path: Path) -> dict:
    return json.loads((Path(path) / "metadata.json").read_bytes())


def minted_bound() -> float:
    return member_metadata(_STATE["root"] / NAMES[0])["instrument_calibration"]["verified_effective_b_fiducial_s"]


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="leaf-ww-case-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = _STATE["root"]

    def copy_root(self, name: str = "runs") -> Path:
        target = self.tmp / name
        target.mkdir()
        for member in NAMES:
            shutil.copytree(self.root / member, target / member)
        return target

    def serial(self, root: Path, bound: float, **kwargs):
        """The decision with no store at all (the R2 path)."""

        with run(mode=None), V2AuthenticationReadSession() as v2:
            session = prepare(root, bound, **kwargs)
        return outcome(session, v2)


# ------------------------------------------------------------------------- L2 + L6


@needs_monitoring
class OperativePreparation(_Base):
    """L2 and L6 at their real positions in AuthenticatedConsumptionSession._prepare."""

    def counted_rederivations(self):
        original = ww._rederive_summary_for_authenticated_fiducial_bound
        calls = []

        def counted(*args, **kwargs):
            calls.append(args[0])
            return original(*args, **kwargs)

        return calls, mock.patch.object(ww, "_rederive_summary_for_authenticated_fiducial_bound", counted)

    def test_hits_reproduce_every_decision_and_registration(self):
        bound = 2 * minted_bound()
        expected = self.serial(self.root, bound)
        self.assertEqual(expected["refusal_reasons"], ())
        self.assertTrue(expected["ready"])
        calls, patch = self.counted_rederivations()
        with patch, run() as caches:
            for _ in range(3):
                with V2AuthenticationReadSession() as v2:
                    session = prepare(self.root, bound)
                self.assertEqual(outcome(session, v2), expected)
            counters = caches.vdl.restricted_counters()
        # Both dominated members are re-derived once (the fills), then served.
        self.assertEqual(len(calls), 2)
        self.assertEqual(counters.get("L2_operative_summary:fill"), 2)
        self.assertEqual(counters.get("L2_operative_summary:hit"), 4)
        self.assertGreaterEqual(counters.get("L6_verify_instrument_calibration:hit", 0), 2)
        self.assertFalse(caches.vdl.defect_pending())

    def test_shadow_recomputes_hits_without_a_defect(self):
        bound = 2 * minted_bound()
        expected = self.serial(self.root, bound)
        with run(vdl.Mode("shadow", 1000)) as caches:
            for _ in range(2):
                with V2AuthenticationReadSession() as v2:
                    session = prepare(self.root, bound)
                self.assertEqual(outcome(session, v2), expected)
            counters = caches.vdl.restricted_counters()
        self.assertGreaterEqual(counters.get("L2_operative_summary:shadow", 0), 2)
        self.assertNotIn("L2_operative_summary:shadow_mismatch", counters)
        self.assertFalse(caches.vdl.defect_pending())

    def test_unclamped_selection_is_a_distinct_key(self):
        bound = 2 * minted_bound()
        expected = self.serial(self.root, bound, clamp=False)
        with run() as caches:
            with V2AuthenticationReadSession():
                prepare(self.root, bound, clamp=True)
            with V2AuthenticationReadSession() as v2:
                session = prepare(self.root, bound, clamp=False)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(outcome(session, v2), expected)
        self.assertEqual(counters.get("L2_operative_summary:fill"), 4)
        self.assertNotIn("L2_operative_summary:hit", counters)

    def test_widened_bound_is_a_distinct_key_and_calibration_is_reused(self):
        bound, wider = 2 * minted_bound(), 3 * minted_bound()
        expected = self.serial(self.root, wider)
        with run() as caches:
            with V2AuthenticationReadSession():
                prepare(self.root, bound)
            before = caches.vdl.restricted_counters()
            with V2AuthenticationReadSession() as v2:
                session = prepare(self.root, wider)
            after = caches.vdl.restricted_counters()
        self.assertEqual(outcome(session, v2), expected)
        self.assertEqual(after.get("L2_operative_summary:fill", 0) - before.get("L2_operative_summary:fill", 0), 2)
        self.assertEqual(after.get("L2_operative_summary:hit", 0), before.get("L2_operative_summary:hit", 0))
        # L6 holds no bound: the second preparation's routed verification is served.
        self.assertGreater(after.get("L6_verify_instrument_calibration:hit", 0),
                           before.get("L6_verify_instrument_calibration:hit", 0))

    def test_a_tampered_member_byte_is_a_miss_with_the_serial_reasons(self):
        root = self.copy_root()
        bound = 2 * minted_bound()
        with run() as caches:
            with V2AuthenticationReadSession():
                prepare(root, bound)
            target = root / NAMES[1] / "power_trace.csv"
            raw = bytearray(target.read_bytes())
            index = raw.index(b"1")
            raw[index:index + 1] = b"2"  # same size, one digit
            time.sleep(0.05)
            target.write_bytes(bytes(raw))
            before = caches.vdl.restricted_counters()
            with V2AuthenticationReadSession() as v2:
                session = prepare(root, bound)
            after = caches.vdl.restricted_counters()
            tampered = outcome(session, v2)
        expected = self.serial(root, bound)
        self.assertEqual(tampered, expected)
        # The tampered member (first in bundle order) is computed again, never
        # served; the untouched member is served.
        delta = {name: after.get(name, 0) - before.get(name, 0)
                 for name in ("L2_operative_summary:hit", "L2_operative_summary:miss")}
        self.assertEqual(delta, {"L2_operative_summary:hit": 1, "L2_operative_summary:miss": 1})

    def test_a_raising_member_is_recomputed_at_its_position_and_never_stored(self):
        bound = 2 * minted_bound()
        original = ww._rederive_summary_for_authenticated_fiducial_bound
        raising = set()

        def sometimes(path, *args, **kwargs):
            if Path(path).name in raising:
                raise ValueError("synthetic member failure")
            return original(path, *args, **kwargs)

        raising.add(NAMES[1])
        with mock.patch.object(ww, "_rederive_summary_for_authenticated_fiducial_bound", sometimes):
            expected = self.serial(self.root, bound)
            self.assertEqual(expected["refusal_reasons"], ("instrument_calibration_invalid",))
            with run() as caches:
                with V2AuthenticationReadSession() as v2:
                    session = prepare(self.root, bound)
                self.assertEqual(outcome(session, v2), expected)
                raising.clear()
                with V2AuthenticationReadSession() as v2:
                    session = prepare(self.root, bound)
                counters = caches.vdl.restricted_counters()
        self.assertEqual(outcome(session, v2), self.serial(self.root, bound))
        # The raise stored nothing: the member is filled only on its clean call.
        self.assertEqual(counters.get("L2_operative_summary:fill"), 2)
        self.assertEqual(counters.get("L2_operative_summary:hit"), 1)

    def test_a_partition_disagreement_runs_the_direct_call(self):
        """A local entry that the run partition does not hold identically is never routed."""

        bound = 2 * minted_bound()
        with run() as caches, V2AuthenticationReadSession():
            metadata = member_metadata(self.root / NAMES[0])
            key = metadata["instrument_calibration"]["artifact_sha256"]
            local = {key: 0.5}
            view = ww.physics_cache_for(local, metadata)
            self.assertFalse(ww._l2_local_exact(view, local, key, metadata))
            local[key] = _STATE["physics"][next(iter(_STATE["physics"]))][key]
            self.assertTrue(ww._l2_local_exact(ww.physics_cache_for(local, metadata), local, key, metadata))
            self.assertFalse(ww._l2_local_exact(ww.physics_cache_for({}, metadata), {}, key, metadata))
            self.assertIsNotNone(caches.vdl)


class PhysicsLocalExactness(unittest.TestCase):
    """The routing guards on synthetic views (no bundle needed)."""

    def metadata(self, bound):
        return {"instrument_calibration": {"artifact_sha256": "a" * 64, "b_fiducial_s": bound}}

    def test_l6_guard(self):
        key = "a" * 64
        partition = (0.5).hex()
        store = {partition: {key: 0.75}}
        with ww.shared_instrument_calibration_physics_cache(store):
            local: dict = {}
            view = ww.physics_cache_for(local, self.metadata(0.5))
            self.assertIsInstance(view, ww._RunPhysicsCacheView)
            # A partition entry not yet copied into local: the direct call runs.
            self.assertFalse(ww._l6_local_exact(view, local, key))
            local[key] = 0.75
            self.assertTrue(ww._l6_local_exact(view, local, key))
            fresh: dict = {}
            self.assertTrue(ww._l6_local_exact(ww.physics_cache_for(fresh, self.metadata(0.25)), fresh, key))
            self.assertFalse(ww._l6_local_exact(ww.physics_cache_for({}, self.metadata(0.5)), local, key))
        plain: dict = {}
        self.assertTrue(ww._l6_local_exact(ww.physics_cache_for(plain, self.metadata(0.5)), plain, key))
        self.assertTrue(ww._l6_local_exact(None, plain, key))
        self.assertTrue(ww._l6_local_exact(ww.physics_cache_for(plain, self.metadata(0.5)), plain, None))

    def test_l2_guard(self):
        key = "a" * 64
        partition = (0.5).hex()
        store = {partition: {key: 0.75}}
        metadata = self.metadata(0.5)
        with ww.shared_instrument_calibration_physics_cache(store):
            # A view over another dict than the caller's local.
            self.assertFalse(ww._l2_local_exact(ww.physics_cache_for({key: 0.75}, metadata), {key: 0.75}, key,
                                                metadata))
            local = {key: 0.75}
            self.assertTrue(ww._l2_local_exact(ww.physics_cache_for(local, metadata), local, key, metadata))
            local[key] = 0.5  # leaked from another partition
            self.assertFalse(ww._l2_local_exact(ww.physics_cache_for(local, metadata), local, key, metadata))
            self.assertFalse(ww._l2_local_exact(ww.physics_cache_for({}, metadata), {}, key, metadata))
            self.assertFalse(ww._l2_local_exact(ww.physics_cache_for(local, metadata), local, None, metadata))
        # No run store at all: the leaf's own view would be a fresh dict.
        local = {key: 0.75}
        self.assertFalse(ww._l2_local_exact(ww.physics_cache_for(local, metadata), local, key, metadata))


# ---------------------------------------------------------------------------- L3, L5, L6


@needs_monitoring
class LeafCalls(_Base):
    def window(self, path):
        return BundleReader(path).measured_window()

    def test_neg8_reference_reduction_hits_and_equals_serial(self):
        member = self.root / NAMES[0]
        with run(mode=None):
            expected = ww._reference_energy_evidence_detail(member)
            expected_without_idle = ww._reference_energy_evidence_detail(member, require_idle_subtracted=False)
        with run() as caches, V2AuthenticationReadSession() as v2:
            first = ww._reference_energy_evidence_detail(member)
            second = ww._reference_energy_evidence_detail(member)
            # require_idle_subtracted is a consumer check, not a key (Sol #9): served.
            third = ww._reference_energy_evidence_detail(member, require_idle_subtracted=False)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(first, expected)
        self.assertEqual(second, expected)
        self.assertEqual(third, expected_without_idle)
        self.assertEqual(counters.get("L3_reduce_dict:fill"), 1)
        self.assertEqual(counters.get("L3_reduce_dict:hit"), 2)
        with run(mode=None), V2AuthenticationReadSession() as serial:
            ww._reference_energy_evidence_detail(member)
            ww._reference_energy_evidence_detail(member)
            ww._reference_energy_evidence_detail(member, require_idle_subtracted=False)
        self.assertEqual(records(v2), records(serial))

    def test_neg8_reduction_failure_keeps_its_refusal(self):
        root = self.copy_root()
        member = root / NAMES[0]
        (member / "power_trace.csv").write_bytes(b"not,a,trace\n")
        with run(mode=None):
            expected = ww._reference_energy_evidence_detail(member)
        with run() as caches:
            self.assertEqual(ww._reference_energy_evidence_detail(member), expected)
            self.assertEqual(ww._reference_energy_evidence_detail(member), expected)
            self.assertFalse(caches.vdl.defect_pending())

    def test_environment_refusals_hit_and_replay_stored_refusals(self):
        root = self.copy_root()
        member = root / NAMES[0]
        metadata = member_metadata(member)
        broken = json.loads(json.dumps(metadata))
        broken["environment_admission"]["attempts"][-1]["end_s"] = None
        window = self.window(member)

        def call(md, start=window.start_s, end=window.end_s, flag=True):
            return ww._verified_environment_refusals(
                md, bundle_path=member, measured_window_start_s=start, measured_window_end_s=end,
                post_run_collector_raised_unmeasured=flag)

        with run(mode=None):
            clean = call(metadata)
            refused = call(broken)
        self.assertNotEqual(refused, ())
        with run() as caches:
            self.assertEqual(call(metadata), clean)
            self.assertEqual(call(metadata), clean)
            self.assertEqual(call(broken), refused)
            self.assertEqual(call(broken), refused)  # a stored refusal-carrying return replays its reasons
            hits = caches.vdl.restricted_counters().get("L5_environment_refusals:hit")
            # Every scalar is in the key: each mutation is a miss.
            call(metadata, start=window.start_s + 1.0)
            call(metadata, end=window.end_s + 1.0)
            call(metadata, flag=False)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(hits, 2)
        self.assertEqual(counters.get("L5_environment_refusals:hit"), hits)
        self.assertEqual(counters.get("L5_environment_refusals:fill"), 5)

    def test_calibration_verification_hits_and_mutations_miss(self):
        member = self.root / NAMES[0]
        metadata = member_metadata(member)
        calibration = metadata["instrument_calibration"]
        wrong = dict(calibration, b_fiducial_s=calibration["b_fiducial_s"] * 2)
        local: dict = {}

        def call(cal, md=metadata):
            # One preparation's call-local cache, shared across its members.
            return ww._verified_instrument_calibration(
                member, dict(md), dict(cal), physics_cache=ww.physics_cache_for(local, md), local=local)

        with run(mode=None):
            good = call(calibration)
            bad = call(wrong)
        self.assertIsNone(good[1])
        self.assertIsNotNone(bad[1])
        local.clear()
        with run() as caches:
            # The run partition already holds the fit and local does not: the
            # direct call runs (it copies the entry into local, as before).
            self.assertEqual(call(calibration), good)
            self.assertIn(calibration["artifact_sha256"], local)
            self.assertEqual(caches.vdl.restricted_counters(), {})
            self.assertEqual(call(calibration), good)
            self.assertEqual(call(calibration), good)
            self.assertEqual(call(wrong), bad)
            self.assertEqual(call(wrong), bad)
            self.assertEqual(call(calibration, dict(metadata, extra=1)), good)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(counters.get("L6_verify_instrument_calibration:hit"), 2)
        self.assertEqual(counters.get("L6_verify_instrument_calibration:fill"), 3)

    def test_l6_fill_is_storable_with_a_fresh_reader(self):
        """Sol #8: the reader is built inside the leaf, so a successful fill is storable."""

        member = self.root / NAMES[0]
        metadata = member_metadata(member)
        key = metadata["instrument_calibration"]["artifact_sha256"]
        spec = next(spec for spec in vdl.LEAVES if spec.leaf_id == "L6_verify_instrument_calibration")
        self.assertEqual(spec.qualnames, ("joulewise.analysis_verified_store:verify_instrument_calibration_at",))
        with run() as caches:
            local = {key: _STATE["physics"][next(iter(_STATE["physics"]))][key]}
            ww._verified_instrument_calibration(
                member, dict(metadata), dict(metadata["instrument_calibration"]),
                physics_cache=ww.physics_cache_for(local, metadata), local=local)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(counters.get("L6_verify_instrument_calibration:fill"), 1)
        self.assertNotIn("L6_verify_instrument_calibration:unstorable", counters)

    def test_ambient_environment_is_in_the_key(self):
        member = self.root / NAMES[0]
        metadata = member_metadata(member)
        window = self.window(member)

        def call():
            return ww._verified_environment_refusals(
                metadata, bundle_path=member, measured_window_start_s=window.start_s,
                measured_window_end_s=window.end_s, post_run_collector_raised_unmeasured=True)

        with run() as caches:
            call()
            with mock.patch.dict(os.environ, {"JOULEWISE_LEAF_WW_TEST": "1"}):
                call()
            counters = caches.vdl.restricted_counters()
        self.assertEqual(counters.get("L5_environment_refusals:fill"), 2)
        self.assertNotIn("L5_environment_refusals:hit", counters)


class Routing(_Base):
    def test_no_store_and_off_are_the_direct_calls(self):
        member = self.root / NAMES[0]
        metadata = member_metadata(member)
        sentinel = (1.0, None)
        with mock.patch.object(ww, "_verify_instrument_calibration", return_value=sentinel) as direct:
            for mode in (None, vdl.OFF):
                with run(mode=mode) as caches:
                    self.assertIsNone(caches.vdl)
                    self.assertEqual(ww._verified_instrument_calibration(
                        member, metadata, metadata["instrument_calibration"], physics_cache=None, local={}), sentinel)
            # A replaced verifier (as tests install) is called directly even with a store.
            with run():
                self.assertEqual(ww._verified_instrument_calibration(
                    member, metadata, metadata["instrument_calibration"], physics_cache=None, local={}), sentinel)
        self.assertEqual(direct.call_count, 3)
        self.assertIsInstance(direct.call_args.args[0], BundleReader)
        self.assertEqual(direct.call_args.kwargs, {"strict_physics": True, "physics_cache": None})

    def test_bundle_copies_are_never_routed(self):
        copies = self.tmp / "l9-bracket-members-synthetic"
        copies.mkdir()
        member = copies / NAMES[0]
        shutil.copytree(self.root / NAMES[0], member)
        with run() as caches:
            self.assertIsNone(ww._verified_store_for(member))
            self.assertIsNotNone(ww._verified_store_for(self.root / NAMES[0]))
            ww._reference_energy_evidence_detail(member)
            ww._reference_energy_evidence_detail(member)
            counters = caches.vdl.restricted_counters()
        self.assertFalse([name for name in counters if name.startswith("L3_")])

    def test_leaf_specs_match_the_called_functions(self):
        """Key schema: every parameter of each called leaf has exactly one role."""

        from joulewise import analysis_verified_store as store_module, environment_admission

        functions = {
            "L2_operative_summary": ww._member_operative_summary,
            "L3_reduce_dict": store_module.reduce_bundle_dict,
            "L5_environment_refusals": environment_admission.current_environment_refusals,
            "L6_verify_instrument_calibration": store_module.verify_instrument_calibration_at,
        }
        self.assertIs(ww.current_environment_refusals, environment_admission.current_environment_refusals)
        for spec in vdl.LEAVES:
            if spec.leaf_id not in functions:
                continue
            function = functions[spec.leaf_id]
            with self.subTest(leaf=spec.leaf_id):
                self.assertEqual(set(spec.roles()), set(inspect.signature(function).parameters))
                self.assertIn(f"{function.__module__}:{function.__qualname__}", spec.qualnames)
                # Not path-free: every key carries the resolved bundle root, so a
                # copy elsewhere can never be served another tree's entry.
                self.assertFalse(spec.path_free)
                source = inspect.getsource(ww)
                self.assertIn(f'"{spec.leaf_id}"', source)

    def test_leaf_sites_keep_their_exception_mapping(self):
        """The rewired sites sit inside the same except clauses as before."""

        tree = ast.parse(inspect.getsource(ww))
        expected = {
            "_verified_instrument_calibration": {("BundleReadError", "OSError", "TypeError", "ValueError")},
            "_verified_operative_rederivation": None,  # inside consume(); its except is below
            "_verified_reduce_dict": {("Exception",)},
        }
        seen: dict[str, set] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                types_ = set()
                for handler in node.handlers:
                    kind = handler.type
                    names = tuple(getattr(e, "id", None) for e in (kind.elts if isinstance(kind, ast.Tuple) else [kind]))
                    types_.add(names)
                for inner in ast.walk(ast.Module(body=node.body, type_ignores=[])):
                    if isinstance(inner, ast.Call) and getattr(inner.func, "id", None) in expected:
                        seen.setdefault(inner.func.id, set()).update(types_)
        self.assertEqual(seen["_verified_instrument_calibration"], expected["_verified_instrument_calibration"])
        self.assertEqual(seen["_verified_reduce_dict"], expected["_verified_reduce_dict"])
        self.assertIn(("BundleReadError", "OSError", "OverflowError", "TypeError", "ValueError"),
                      seen["_verified_operative_rederivation"])


# --------------------------------------------------------------------------- clock guard


def clock_leaf(path, factor):
    ww.build_neg8_freshness_observation([{}])
    return factor


def stamped_leaf(path, factor):
    ww.build_neg8_freshness_observation([{}], evaluated_at_s=1.0)
    return factor


class ClockGuard(_Base):
    def test_every_wall_clock_read_in_whole_window_is_noted_first(self):
        tree = ast.parse(inspect.getsource(ww))
        found = 0
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            notes = [node.lineno for node in ast.walk(function)
                     if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_note_clock"]
            for node in ast.walk(function):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name) and node.func.value.id in {"time", "datetime"}):
                    found += 1
                    with self.subTest(function=function.name, line=node.lineno):
                        self.assertTrue(any(line < node.lineno for line in notes))
        self.assertEqual(found, 2)

    @needs_monitoring
    def test_a_clock_consulting_fill_is_never_stored(self):
        tree = self.tmp / "tree"
        tree.mkdir()
        (tree / "data.txt").write_bytes(b"x")
        specs = tuple(vdl.LeafSpec(leaf_id, (f"{__name__}:{fn.__name__}",),
                                   (("path", vdl.TREE), ("factor", vdl.SCALAR)))
                      for leaf_id, fn in (("T_clock", clock_leaf), ("T_stamped", stamped_leaf)))
        with vdl._registered(*specs), run() as caches:
            for _ in range(2):
                vdl.call("T_clock", clock_leaf, tree, 1)
                vdl.call("T_stamped", stamped_leaf, tree, 1)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(counters.get("T_clock:unstorable"), 2)
        self.assertNotIn("T_clock:hit", counters)
        self.assertEqual(counters.get("T_stamped:fill"), 1)
        self.assertEqual(counters.get("T_stamped:hit"), 1)

    @needs_monitoring
    def test_leaf_paths_consult_only_the_observed_projection_deadline(self):
        """Dynamic inventory: every clock call made while the four leaves compute.

        The module's cold refit (the calibration projection) and warm calls of
        L2, L3, L5 and L6 run under a CALL tracer; only the deadline-observed
        projection budget may consult a clock.
        """

        cold = _STATE["cold_clock_callers"]
        self.assertIn(("joulewise/powermetrics_fiducial.py", "_ProjectionWorkBudget.consume_cell"), cold)
        member = self.root / NAMES[0]
        metadata = member_metadata(member)
        window = BundleReader(member).measured_window()
        key = metadata["instrument_calibration"]["artifact_sha256"]
        with run() as caches, clock_tracer() as warm:
            local = {key: _STATE["physics"][next(iter(_STATE["physics"]))][key]}
            ww._verified_instrument_calibration(
                member, dict(metadata), dict(metadata["instrument_calibration"]),
                physics_cache=ww.physics_cache_for(local, metadata), local=local)
            ww._verified_environment_refusals(
                metadata, bundle_path=member, measured_window_start_s=window.start_s,
                measured_window_end_s=window.end_s, post_run_collector_raised_unmeasured=True)
            ww._reference_energy_evidence_detail(member)
            ww._member_operative_summary(ww._rederive_operative_summary, member, 2 * minted_bound(), metadata)
            self.assertIsNotNone(caches.vdl)
        # Excluded: this test module, and the standard library's threading
        # (ThreadPoolExecutor.submit's non-blocking idle-semaphore acquire in
        # the store's own tree hashing, outside every leaf's value).
        stdlib_threading = os.path.join(os.path.dirname(os.__file__), "threading.py")
        callers = {key for key in (set(cold) | set(warm))
                   if not key[0].endswith("test_leaf_whole_window.py") and key[0] != stdlib_threading}
        self.assertLessEqual(callers, OBSERVED_CLOCK_CALLERS, sorted(callers - OBSERVED_CLOCK_CALLERS))


if __name__ == "__main__":
    unittest.main()
