"""Council ruling 7: bundles record the observed AC powermode; the v4 desk
marks instrument_ok false on any member mismatch. Synthetic only."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.align.apple import powermode
from joulewise.align.apple.workload import EpisodeRuntimeAdapter
from joulewise.align.records import Episode, from_json
from joulewise.clock import FakeClock
from scripts import align_pilot_session as pilot, align_v4_kit as kit, align_v4_session as session
from tests.align.test_apple_campaign import as_config, episode_spec

AC2 = "Battery Power:\n powermode 0\nAC Power:\n lowpowermode 0\n powermode 2\n"


def run_episode(reader=None):
    clock = FakeClock()
    adapter = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
    if reader is not None:
        adapter.powermode_reader = reader
    config = as_config(episode_spec(hidden=False), "powermode-record")
    assert adapter.prepare(config).ok
    result = adapter.run_workload(config)
    return from_json(Episode, result.output_artifacts["align_episode.json"])


class BundleRecordTests(unittest.TestCase):
    def test_bound_reader_value_is_recorded_in_the_bundle(self):
        episode = run_episode(lambda: 2)
        self.assertEqual(episode.hardware["ac_powermode"]["value"], 2)
        self.assertEqual(episode.hardware["ac_powermode"]["observed_at"], "episode_start")
        self.assertEqual(episode.hardware["ac_powermode"]["source"], powermode.SOURCE)

    def test_reader_failure_records_an_unobserved_value(self):
        def broken():
            raise ValueError("pmset unavailable")
        record = run_episode(broken).hardware["ac_powermode"]
        self.assertIsNone(record["value"])
        self.assertIn("pmset unavailable", record["error"])

    def test_one_transient_read_failure_is_retried(self):
        # Cold pass LOW 4: one flaky pmset read must not cost the window check.
        calls = []
        def flaky():
            calls.append(1)
            if len(calls) == 1:
                raise ValueError("pmset -g custom failed: exit 1")
            return 2
        self.assertEqual(run_episode(flaky).hardware["ac_powermode"]["value"], 2)
        self.assertEqual(len(calls), 2)

    def test_two_read_failures_record_an_unobserved_value(self):
        calls = []
        def broken():
            calls.append(1)
            raise ValueError("pmset unavailable")
        record = run_episode(broken).hardware["ac_powermode"]
        self.assertIsNone(record["value"])
        self.assertEqual((len(calls), record["attempts"]), (2, 2))

    def test_fake_clock_without_reader_records_nothing(self):
        self.assertNotIn("ac_powermode", run_episode().hardware)

    def test_wp15_registry_binds_the_reader(self):
        from types import SimpleNamespace
        from joulewise.align.apple.thermal_gates import ThermalRegistry
        from tests.align.test_apple_campaign import base_config
        clock = FakeClock()
        runtime = EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
        delegate = SimpleNamespace(resolve_runtime=lambda c, k: (runtime, None),
                                   resolve_telemetry=lambda c, k: (object(), None))
        reader = lambda: 0  # noqa: E731
        registry = ThermalRegistry(delegate, status_factory=lambda t, c: "feed", powermode_reader=reader)
        registry.resolve_runtime(base_config(), clock)
        registry.resolve_telemetry(base_config(), clock)
        self.assertIs(runtime.powermode_reader, reader)

    def test_observation_reads_only_the_ac_block(self):
        calls = []

        def runner(argv):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, AC2, "")
        self.assertEqual(powermode.observe_ac_powermode(runner), 2)
        self.assertEqual(calls, [powermode.QUERY])
        with self.assertRaisesRegex(ValueError, "exit 1"):
            powermode.observe_ac_powermode(lambda argv: subprocess.CompletedProcess(argv, 1, "", ""))


class DeskPowermodeTests(unittest.TestCase):
    def fixture(self, root, observed):
        registration = root / "kit/registration"
        registration.mkdir(parents=True)
        members = [{"run_id": f"m{i}", "ac_powermode": 0} for i in range(3)]
        (registration.parent / "collection_plan.json").write_text(json.dumps({"members": members}))
        runs = root / "runs"
        for member, value in zip(members, observed):
            outputs = runs / member["run_id"] / "outputs"
            outputs.mkdir(parents=True)
            hardware = {} if value == "absent" else {"ac_powermode": {"value": value}}
            (outputs / "align_episode.json").write_text(json.dumps({"hardware": hardware}))
        return {"registration_dir": str(registration), "measurement_root": str(root)}, runs

    def test_desk_check_passes_only_when_every_bundle_matches(self):
        with tempfile.TemporaryDirectory() as td:
            state, runs = self.fixture(Path(td), [0, 0, 0])
            added, report = session.powermode_desk_check(state=state, members=[], runs_root=runs,
                                                         kit_path=kit.KIT)
            # This minimal fixture has no registration artifacts. Keep the
            # existing v4 fail-closed registration check alongside powermode.
            self.assertEqual(added, {"ac_powermode_members": True, "v4_registration_evidence": False})
            self.assertEqual(report["powermode_mismatches"], [])
        for observed in ([0, 2, 0], [0, "absent", 0]):
            with self.subTest(observed=observed), tempfile.TemporaryDirectory() as td:
                state, runs = self.fixture(Path(td), observed)
                added, report = session.powermode_desk_check(state=state, members=[], runs_root=runs,
                                                             kit_path=kit.KIT)
                self.assertEqual(added, {"ac_powermode_members": False, "v4_registration_evidence": False})
                self.assertEqual([m["run_id"] for m in report["powermode_mismatches"]], ["m1"])

    def test_v4_desk_wires_the_powermode_check(self):
        with patch.object(pilot, "desk", return_value={}) as desk:
            session.desk("synthetic-session", harvest=False)
        self.assertIs(desk.call_args.kwargs["extra_checks"], session.powermode_desk_check)
        self.assertEqual(desk.call_args.kwargs["desk_schema"], kit.DESK_SCHEMA)
        with patch.object(pilot, "desk", return_value={"harvest_status": "not_run",
                                                       "pilot_status": "instrument_ok"}) as desk:
            self.assertEqual(session.main(["desk", "--session-root", "s", "--no-harvest"]), 0)
        self.assertIs(desk.call_args.kwargs["extra_checks"], session.powermode_desk_check)


if __name__ == "__main__":
    unittest.main()
