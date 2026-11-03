"""D-188 LEAF-CLI: strict validation (L1) and the reduce leaf (L3) at the cli sites.

Every test drives the genuine entry points (``cli.validate_bundle``,
``cli._strict_problems`` through it, ``cli.main(['reduce', ...])``) inside an
in-process analysis run whose activation created a verified store, and compares
each value, problem text, exception and session record with the serial
(store-free) computation of the same call. Bytes: the committed synthetic S10
ALPHA member (no custody data), copied per test where a test mutates it.
"""
from __future__ import annotations

import contextlib
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import authentication_io as aio
from joulewise import cli
from joulewise import environment_admission as ea
from joulewise.schemas import SchemaError
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER

L1 = "L1_strict_validation"
L3 = "L3_reduce_dict"


class FakeDeadline:
    """The run's wall-deadline observer: present, never fired (a fill is storable)."""

    def __init__(self):
        self.firings = 0


@contextlib.contextmanager
def run(mode=vdl.ON):
    with arc.analysis_run_caches({}, vdl_mode=mode) as caches:
        caches.deadline = FakeDeadline()
        yield caches


def outcome(fn, *args, **kwargs):
    """A call's value, or its exception's type and text (what a caller can observe)."""

    try:
        return ("value", fn(*args, **kwargs))
    except Exception as exc:  # noqa: BLE001 - compared, never swallowed
        return ("raised", type(exc).__name__, str(exc))


def records(session):
    return {identity: (record.sha256, record.grammar, record.read_count)
            for identity, record in session.records.items()}


class _Member(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="leaf-cli-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        source = cls.tmp / "source"
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(source, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)],
                            filter="data")
        cls.pristine = source / MEMBER

    def copy(self, label: str) -> Path:
        """A copy of the member under its own parent (same final name, same bytes)."""

        target = self.tmp / label / self.pristine.name
        shutil.copytree(self.pristine, target)
        self.addCleanup(shutil.rmtree, target.parent, ignore_errors=True)
        return target

    def counted_strict(self):
        return mock.patch.object(cli, "_strict_problems", wraps=cli._strict_problems)


class Wiring(unittest.TestCase):
    def test_validate_bundle_is_the_registered_genuine_leaf(self):
        spec = {s.leaf_id: s for s in vdl.LEAVES}[L1]
        self.assertEqual(spec.qualnames, ("joulewise.cli:validate_bundle",))
        self.assertIs(vdl._resolve_reference(spec.qualnames[0]), cli.validate_bundle)
        self.assertEqual(set(spec.roles()), set(inspect.signature(cli.validate_bundle).parameters))
        l3 = {s.leaf_id: s for s in vdl.LEAVES}[L3]
        self.assertEqual(set(l3.roles()), set(inspect.signature(vdl.reduce_bundle_dict).parameters))

    def test_no_store_means_no_store_call(self):
        boom = mock.patch.object(vdl.VerifiedStore, "call", side_effect=AssertionError("store used"))
        probe = mock.patch.object(vdl.VerifiedStore, "probe", side_effect=AssertionError("store used"))
        with boom, probe, mock.patch.object(cli, "_strict_problems", return_value=["x"]) as strict, \
                mock.patch("joulewise.cli.BundleReader") as reader:
            reader.return_value.problems.side_effect = lambda: []
            self.assertEqual(cli.validate_bundle(Path("/nonexistent"), True), ["x"])
            with arc.analysis_run_caches({}):  # a run without a store
                self.assertEqual(cli.validate_bundle(Path("/nonexistent"), True), ["x"])
            self.assertEqual(strict.call_count, 2)

    def test_non_strict_calls_never_reach_the_store(self):
        with run() as caches, mock.patch("joulewise.cli.BundleReader") as reader, \
                mock.patch.object(caches.vdl, "call", side_effect=AssertionError("store used")):
            reader.return_value.problems.return_value = ["structural"]
            self.assertEqual(cli.validate_bundle(Path("/nonexistent")), ["structural"])


class StrictLeaf(_Member):
    def test_fill_hit_and_path_free_copy_under_another_parent(self):
        first, second = self.copy("parent-one"), self.copy("parent-two")
        serial = cli.validate_bundle(first, True)
        self.assertEqual(serial, [])
        with run() as caches, self.counted_strict() as strict:
            self.assertEqual(cli.validate_bundle(first, True), serial)
            self.assertEqual(strict.call_count, 1)
            self.assertEqual(cli.validate_bundle(first, True), serial)
            # Another parent, the same final name and bytes: the path-free entry serves it.
            self.assertEqual(cli.validate_bundle(second, True), serial)
            self.assertEqual(strict.call_count, 1)
            counters = caches.vdl.restricted_counters()
            self.assertEqual((counters[f"{L1}:fill"], counters[f"{L1}:hit"]), (1, 2))
            # The nested L3 deposit is keyed on the resolved bundle (not path-free).
            self.assertEqual(counters[f"{L3}:fill"], 1)
            keys = {entry.leaf_id: entry.trees for entry in caches.vdl._entries.values()}
            self.assertEqual(keys[L1][0][0], first.name)
            self.assertEqual(keys[L3][0][0], str(first.resolve()))
            # Equal tree content: the reduce dicts of the two copies are identical.
            physics = arc.physics_cache_for_call(None, json.loads((second / "metadata.json").read_bytes()))
            served = vdl.call(L3, vdl.reduce_bundle_dict, first, reducer_version=None, physics_cache=physics)
            fresh = vdl.call(L3, vdl.reduce_bundle_dict, second, reducer_version=None, physics_cache=physics)
            self.assertEqual(served, fresh)
        self.assertFalse(caches.vdl.defect_pending())

    def test_problem_lists_are_identical_and_never_stored(self):
        broken = self.copy("broken")
        summary = json.loads((broken / "summary_metrics.json").read_bytes())
        summary["status"] = "not-a-status"
        (broken / "summary_metrics.json").write_text(json.dumps(summary), encoding="utf-8")
        serial = cli.validate_bundle(broken, True)
        self.assertTrue(serial)
        with run() as caches, self.counted_strict() as strict:
            self.assertEqual(cli.validate_bundle(broken, True), serial)
            self.assertEqual(cli.validate_bundle(broken, True), serial)
            self.assertEqual(strict.call_count, 2, "a problem list is computed at every position")
            counters = caches.vdl.restricted_counters()
            self.assertEqual(counters[f"{L1}:unstorable"], 2)
            self.assertNotIn(f"{L1}:fill", counters)
            self.assertFalse([e for e in caches.vdl._entries.values() if e.leaf_id == L1])

    def test_a_raising_validation_is_never_stored_and_raises_in_place(self):
        bundle = self.copy("raising")
        with run() as caches, mock.patch.object(cli, "_strict_problems",
                                                side_effect=RuntimeError("strict raised")) as strict:
            for expected_calls in (1, 2):
                with self.assertRaisesRegex(RuntimeError, "strict raised"):
                    cli.validate_bundle(bundle, True)
                self.assertEqual(strict.call_count, expected_calls)
            self.assertFalse([e for e in caches.vdl._entries.values() if e.leaf_id == L1])

    def test_policy_files_beside_the_repo_are_bound_in_the_entry(self):
        """Sol #7: the registered campaign policies an L1 fill reads are verified extras."""

        bundle = self.copy("policy")
        policies = self.tmp / "policies"
        policies.mkdir()
        self.addCleanup(shutil.rmtree, policies, ignore_errors=True)
        expected = json.loads((bundle / "metadata.json").read_bytes())["campaign_policy"]["sha256"]
        matching = [p for p in sorted(ea.REGISTERED_POLICY_DIR.glob("*.json"))
                    if hashlib.sha256(p.read_bytes()).hexdigest() == expected]
        self.assertEqual(len(matching), 1)
        shutil.copy(matching[0], policies / "m_policy.json")
        decoy = policies / "a_decoy.json"  # sorted first: read (and rejected) before the match
        decoy.write_text('{"decoy": 1}\n', encoding="utf-8")
        with mock.patch.object(ea, "REGISTERED_POLICY_DIR", policies):
            serial = cli.validate_bundle(bundle, True)
            with run() as caches, self.counted_strict() as strict:
                self.assertEqual(cli.validate_bundle(bundle, True), serial)
                self.assertEqual(cli.validate_bundle(bundle, True), serial)
                self.assertEqual(strict.call_count, 1)
                (entry,) = [e for e in caches.vdl._entries.values() if e.leaf_id == L1]
                self.assertIn(str(decoy.resolve()), dict(entry.extras))
                self.assertIn(str((policies / "m_policy.json").resolve()), dict(entry.extras))
                self.assertIn(str(policies.resolve()), dict(entry.listings))
                decoy.write_text('{"decoy": 2}\n', encoding="utf-8")
                self.assertEqual(cli.validate_bundle(bundle, True), serial)
                self.assertEqual(strict.call_count, 2, "a changed policy file read beside the bundle misses")
                decoy.write_text('{"decoy": 1}\n', encoding="utf-8")
                self.assertEqual(cli.validate_bundle(bundle, True), serial)
                self.assertEqual(strict.call_count, 2, "the original bytes verify again")
                (policies / "z_new.json").write_text("{}\n", encoding="utf-8")
                self.assertEqual(cli.validate_bundle(bundle, True), serial)
                self.assertEqual(strict.call_count, 3, "a changed policy listing misses")
                (policies / "z_new.json").unlink()
                self.assertEqual(cli.validate_bundle(bundle, True), serial)
                self.assertEqual(strict.call_count, 3)


class SessionLeaf(_Member):
    """V2 sessions: physics partitions, session-less fills, grammar bridging."""

    def test_session_cache_holding_another_value_is_never_served_across(self):
        bundle = self.copy("partition")
        key = json.loads((bundle / "metadata.json").read_bytes())["instrument_calibration"]["artifact_sha256"]
        with aio.V2AuthenticationReadSession() as reference:
            reference.instrument_calibration_physics_cache[key] = 0.5 ** 7
            serial = outcome(cli.validate_bundle, bundle, True)
        with run() as caches, self.counted_strict() as strict:
            with aio.V2AuthenticationReadSession() as filler:
                filled = outcome(cli.validate_bundle, bundle, True)
            self.assertEqual(strict.call_count, 1)
            self.assertIn(key, filler.instrument_calibration_physics_cache)
            self.assertNotEqual(filler.instrument_calibration_physics_cache[key], 0.5 ** 7)
            with aio.V2AuthenticationReadSession() as consumer:
                consumer.instrument_calibration_physics_cache[key] = 0.5 ** 7
                self.assertEqual(outcome(cli.validate_bundle, bundle, True), serial)
            self.assertEqual(strict.call_count, 2, "a cache value other than the fill's post-value is not admitted")
            self.assertEqual(records(consumer), records(reference))
            self.assertEqual(consumer.instrument_calibration_physics_cache,
                             reference.instrument_calibration_physics_cache)
            with aio.V2AuthenticationReadSession() as again:
                self.assertEqual(outcome(cli.validate_bundle, bundle, True), filled)
            self.assertEqual(strict.call_count, 2, "an empty cache admits the in-session entry")
            self.assertEqual(records(again), records(filler))
        self.assertFalse(caches.vdl.defect_pending())

    def test_session_less_fill_serves_a_session_only_through_complete_rows(self):
        bundle = self.copy("bridge")
        with aio.V2AuthenticationReadSession() as reference:
            serial = outcome(cli.validate_bundle, bundle, True)
        complete = bool(getattr(aio, "RECORDS_CAPABILITY_READS", False))
        with run() as caches, self.counted_strict() as strict:
            self.assertEqual(outcome(cli.validate_bundle, bundle, True)[0], "value")
            with aio.V2AuthenticationReadSession() as consumer:
                self.assertEqual(outcome(cli.validate_bundle, bundle, True), serial)
            self.assertEqual(strict.call_count, 1 if complete else 2)
            self.assertEqual(records(consumer), records(reference))
            self.assertEqual(consumer.instrument_calibration_physics_cache,
                             reference.instrument_calibration_physics_cache)
        self.assertFalse(caches.vdl.defect_pending())

    def test_duplicate_key_calibration_json_refuses_as_serially_in_a_session(self):
        """Sol #3: a session-less fill accepted bytes a session's strict parse refuses."""

        bundle = self.copy("duplicate")
        manifest = bundle / "instrument_calibration/manifest.json"
        raw = manifest.read_text(encoding="utf-8")
        manifest.write_text(raw.replace("{", '{\n  "pulse_count": -1,', 1), encoding="utf-8")
        session_less = outcome(cli.validate_bundle, bundle, True)
        with aio.V2AuthenticationReadSession() as reference:
            in_session = outcome(cli.validate_bundle, bundle, True)
        self.assertNotEqual(session_less, in_session, "the fixture must separate the two grammars")
        for complete in (False, True):
            with self.subTest(records_capability_reads=complete), \
                    mock.patch.object(aio, "RECORDS_CAPABILITY_READS", complete, create=True), \
                    run() as caches:
                self.assertEqual(outcome(cli.validate_bundle, bundle, True), session_less)
                with aio.V2AuthenticationReadSession() as consumer:
                    self.assertEqual(outcome(cli.validate_bundle, bundle, True), in_session)
                self.assertEqual(records(consumer), records(reference))
                self.assertEqual(outcome(cli.validate_bundle, bundle, True), session_less)
                self.assertFalse(caches.vdl.defect_pending())

    def test_shadow_recomputes_hits_without_defects(self):
        bundle = self.copy("shadow")
        serial = cli.validate_bundle(bundle, True)
        with run(vdl.Mode("shadow", 1000)) as caches, self.counted_strict() as strict:
            self.assertEqual(cli.validate_bundle(bundle, True), serial)
            self.assertEqual(cli.validate_bundle(bundle, True), serial)
            self.assertEqual(strict.call_count, 2)
            self.assertEqual(caches.vdl.restricted_counters()[f"{L1}:shadow"], 1)
            self.assertFalse(caches.vdl.defect_pending())


class ReduceLeaf(_Member):
    """Step 2: ``joulewise reduce`` serves a step-1 deposit, byte-identically."""

    def reduce(self, bundle, output):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["reduce", str(bundle), "--output", str(output)])
        return code, out.getvalue().replace(str(output), "<out>"), err.getvalue()

    def test_step_two_reduce_is_served_byte_identically(self):
        bundle = self.copy("step2")
        outputs = self.tmp / "step2-out"
        outputs.mkdir()
        self.addCleanup(shutil.rmtree, outputs, ignore_errors=True)
        serial = self.reduce(bundle, outputs / "serial.json")
        with run() as caches:
            self.assertEqual(cli.validate_bundle(bundle, True), [])  # step 1 deposits L3
            with mock.patch.object(cli, "reduce_bundle", side_effect=AssertionError("recomputed")):
                served = self.reduce(bundle, outputs / "served.json")
            counters = caches.vdl.restricted_counters()
        self.assertEqual(served, serial)
        self.assertEqual((outputs / "served.json").read_bytes(), (outputs / "serial.json").read_bytes())
        self.assertGreaterEqual(counters[f"{L3}:hit"], 1)
        self.assertNotIn(f"{L3}:hit_discarded", counters)

    def test_miss_keeps_the_two_failure_stages_apart(self):
        """Sol #9: a raising reduction escapes ``_cmd_reduce`` (``main`` maps it to exit 2);
        a SchemaError in to_dict is ``_cmd_reduce``'s own diagnostic and exit 3."""

        bundle = self.copy("stages")
        outputs = self.tmp / "stages-out"
        outputs.mkdir()
        self.addCleanup(shutil.rmtree, outputs, ignore_errors=True)
        unserializable = mock.Mock()
        unserializable.to_dict.side_effect = SchemaError("summary is not admissible here")
        for label, patch, expect in (
            ("serialize", {"return_value": unserializable}, "exit3"),
            ("reduce", {"side_effect": SchemaError("reduction raised")}, "raises"),
        ):
            results = []
            for active in (False, True):
                context = run() if active else contextlib.nullcontext()
                with context, mock.patch.object(cli, "reduce_bundle", **patch):
                    results.append(outcome(self.reduce, bundle, outputs / f"{label}-{active}.json"))
            with self.subTest(stage=label):
                self.assertEqual(results[0], results[1])
                if expect == "exit3":
                    self.assertEqual(results[1][1][0], 3)
                    self.assertIn("reduced summary is not admissible: summary is not admissible here",
                                  results[1][1][2])
                else:
                    self.assertEqual(results[1], ("value", (2, "", "error: reduction raised\n")))

    def test_reduce_never_fills_the_store(self):
        bundle = self.copy("nofill")
        outputs = self.tmp / "nofill-out"
        outputs.mkdir()
        self.addCleanup(shutil.rmtree, outputs, ignore_errors=True)
        with run() as caches:
            code, _, _ = self.reduce(bundle, outputs / "first.json")
            counters = caches.vdl.restricted_counters()
            self.assertFalse(caches.vdl._entries)
        self.assertNotIn(f"{L3}:fill", counters)
        self.assertEqual(counters[f"{L3}:miss"], 1)
        self.assertIn(code, (0, 3))


class CensusRegistration(unittest.TestCase):
    def test_store_is_classified_for_the_scanned_cli_module(self):
        document = json.loads((Path(__file__).resolve().parents[2]
                               / "configs/gates/hazard_refusals.json").read_bytes())
        self.assertIn("joulewise/cli.py", document["scan"]["modules"])
        self.assertEqual(document["scan"]["not_scanned"].get("joulewise/analysis_verified_store.py"),
                         "analysis")

    def test_cli_raise_sites_and_guards_unchanged(self):
        from tests.hazards import refusal_census

        document = refusal_census.load_allowlist()
        listed = {(e["function"], e["kind"], e["detail"]): (e["count"], e["guard"]) for e in document["sites"]
                  if e["file"] == "joulewise/cli.py"}
        sites = refusal_census.scan(["joulewise/cli.py"])
        guards = refusal_census.site_guards(sites)
        observed = {key[1:4]: (count, guards[key]) for key, count in refusal_census.site_counts(sites).items()}
        self.assertEqual(observed, listed)
        self.assertEqual(listed[("_cmd_reduce", "return_code", "3")][0], 1)


if __name__ == "__main__":
    unittest.main()
