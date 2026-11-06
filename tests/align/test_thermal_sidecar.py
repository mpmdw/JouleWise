"""In-process thermometry; all sensors/clocks are synthetic."""
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from joulewise.align.apple import thermal, thermal_gates
from joulewise.align.apple.workload import EpisodeSpec, EpisodeRuntimeAdapter
from joulewise.hazards import base
from joulewise.clock import FakeClock, SystemClock
from joulewise.interfaces import AdapterResult, AdapterFailure
from tests.hazards.fakes import FakeClocks
from tests.hazards.test_temperature import FakeSensors, POLICY
from tests.align.test_apple_campaign import base_config, episode_spec

ROOT = Path(__file__).resolve().parents[2]
PINNED = {'joulewise/hazards/smc.py': 'c1896f0c4fd8510ab4a2273927d4d71d8cc7a1a6940928117ba50d8441f70351', 'joulewise/hazards/monitor.py': '9ed83410fc2fe7bdbf8e8acffcf913af5bd4442bb23adc14ed61430e0a3c957b', 'joulewise/schemas.py': '344b12ce178b8acb212059097a4ade507812a4be1673a6552ec221a83055e1d1', 'joulewise/b5/driver.py': 'e1b3df745c82f4a4cec812ade3e4e7c1b460c6c4bec1f6970a3ef13736ab2e89', 'joulewise/b5/harvest.py': '2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744'}

class PlacementTests(unittest.TestCase):
    def test_gate_session_reuses_the_sidecar_reader_journal_and_cleanup(self):
        from tests.align.test_thermal_gate import policy
        with tempfile.TemporaryDirectory() as tmp:
            reader = mock.Mock(wraps=FakeSensors())
            config = policy(sensors=POLICY)
            obj = thermal_gates.ThermalSession(config, FakeClock(), mock.Mock(outputs_dir=Path(tmp)), reader=reader)
            self.addCleanup(obj.close)
            obj.start()
            self.assertIs(obj.reader, obj.sidecar.reader)
            snapshot = obj.sidecar.snapshot()
            obj.sample()
            self.assertEqual(len(snapshot), 1)
            self.assertEqual(len(obj.rows), 2)
            reader.read.assert_called_with(thermal.keys(POLICY))
            self.assertEqual(reader.read.call_count, 2)
            obj.close()
            obj.close()
            reader.close.assert_called_once()
            rows = [json.loads(line) for line in (Path(tmp)/'align_thermal.jsonl').read_text().splitlines()]
            self.assertTrue(all(r['schema'] == 'joulewise.align_thermal.v1' for r in rows))
            self.assertEqual([r['kind'] for r in rows], ['session_start', 'reading', 'reading', 'session_end'])

    def test_identity_readiness_opens_no_collector_and_cannot_run_without_one(self):
        from tests.align.test_thermal_gate import policy
        runtime = mock.Mock()
        runtime.prepare.return_value = AdapterResult(ok=True)
        for slot in (POLICY, policy()):
            spec = replace(episode_spec(hidden=False), thermal=slot, warmup_condition='benign',
                           deadman_s=330 if 'sensors' in slot else None)
            config = replace(base_config(), workload_profile=replace(base_config().workload_profile,
                                                                     prompt_text=spec.to_text()))
            with self.subTest(slot=slot), mock.patch.object(thermal, 'Sidecar') as collector:
                adapter = EpisodeRuntimeAdapter(runtime, SystemClock())
                self.assertTrue(adapter.prepare(config).ok)
                collector.assert_not_called()
                with self.assertRaisesRegex(AdapterFailure, 'requires bundle outputs'):
                    adapter.run_workload(config)
                adapter.cleanup(config)

    def test_gate_collector_survives_native_cleanup_and_closes_on_prepare_failure(self):
        from tests.align.test_thermal_gate import policy
        spec = replace(episode_spec(hidden=False), thermal=policy(), warmup_condition='benign',
                       deadman_s=330)
        config = replace(base_config(), workload_profile=replace(base_config().workload_profile,
                                                                 prompt_text=spec.to_text()))
        for prepare_ok in (False, True):
            events = []
            runtime, sidecar = mock.Mock(), mock.Mock()
            runtime.prepare.return_value = AdapterResult(ok=prepare_ok)
            sidecar.tick.return_value = {
                'module': 'temperature', 'kind': 'reading',
                'started': base.Stamp(0, 0, 0).to_json(), 'finished': base.Stamp(0, 0, 0).to_json(),
                'values': {'sensors': {'Tfak': 40., 'Tslw': 40.}, 'errors': {}}}
            def cleanup(*args):
                events.append('runtime.cleanup')
                raise RuntimeError('cleanup fault')
            runtime.cleanup.side_effect = cleanup
            sidecar.stop.side_effect = lambda: events.append('sidecar.stop')
            with self.subTest(prepare_ok=prepare_ok), mock.patch.object(thermal, 'Sidecar', return_value=sidecar):
                adapter = EpisodeRuntimeAdapter(runtime, FakeClock())
                self.assertEqual(adapter.prepare(config, mock.Mock(outputs_dir=Path('unused'))).ok, prepare_ok)
                runtime.prepare.assert_called_once()
                if prepare_ok:
                    with self.assertRaisesRegex(RuntimeError, 'cleanup fault'):
                        adapter.cleanup(config)
                self.assertEqual(events, ['runtime.cleanup', 'sidecar.stop'] if prepare_ok else ['sidecar.stop'])
                sidecar.stop.assert_called_once()

    def test_measurement_core_matches_pre_pr_bytes(self):
        for name, digest in PINNED.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_sidecar_bundle_path_and_phase_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            reader = mock.Mock(wraps=FakeSensors())
            ctx = base.Context(clocks=FakeClocks(read_cost_ns=0))
            sidecar = thermal.Sidecar(Path(tmp) / "outputs", POLICY, reader=reader, ctx=ctx)
            sidecar.start(background=False)
            sidecar.tick()
            sidecar.event("align_thermal_gate", {"state": "release"})
            sidecar.event("align_thermal_hold", {"state": "begin"})
            sidecar.stop()
            reader.close.assert_called_once()
            path = Path(tmp) / "outputs/align_thermal.jsonl"
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([r["kind"] for r in rows], ["session_start", "reading", "align_thermal_gate",
                                                       "align_thermal_hold", "session_end"])
            self.assertEqual(rows[1]["values"]["sensors"]["TG0D"], 50)
            self.assertFalse((Path(tmp) / "hazards").exists())
            for row in rows:
                base.Stamp.from_json(row["started"])
            with self.assertRaises(FileExistsError):
                thermal.Sidecar(Path(tmp) / "outputs", POLICY).start(background=False)

    def test_adapter_starts_before_runtime_prepare_and_stops_even_on_cleanup_fault(self):
        spec = replace(episode_spec(hidden=False), thermal=POLICY)
        config = replace(base_config(), workload_profile=replace(base_config().workload_profile,
                                                                 prompt_text=spec.to_text()))
        events = []
        runtime = mock.Mock(name="runtime")
        runtime.prepare.side_effect = lambda *a: events.append("runtime.prepare") or AdapterResult(ok=True)
        runtime.cleanup.side_effect = RuntimeError("cleanup fault")
        sidecar = mock.Mock()
        sidecar.start.side_effect = lambda: events.append("sidecar.start")
        context = mock.Mock(outputs_dir=Path("unused"))
        adapter = EpisodeRuntimeAdapter(runtime, FakeClock())
        with mock.patch.object(thermal, "Sidecar", return_value=sidecar):
            self.assertTrue(adapter.prepare(config, context).ok)
            self.assertEqual(events, ["sidecar.start", "runtime.prepare"])
            with self.assertRaisesRegex(RuntimeError, "cleanup fault"):
                adapter.cleanup(config, context)
        sidecar.stop.assert_called_once()

    def test_unset_slot_preserves_legacy_spec_bytes_and_no_sidecar(self):
        spec = episode_spec(hidden=False)
        self.assertNotIn("thermal", json.loads(spec.to_text()))
        self.assertIsNone(EpisodeSpec.from_text(spec.to_text()).thermal)

    def test_journal_retains_key_type_raw_bytes_value_and_error(self):
        from joulewise.align.apple.smc_reader import Reader
        from tests.hazards.test_smc_enumeration import IndexedTransport
        with tempfile.TemporaryDirectory() as tmp:
            transport = IndexedTransport()
            config = {**POLICY, "fan_keys": ["F0Ac"]}
            sidecar = thermal.Sidecar(Path(tmp), config, reader=Reader(transport),
                                      ctx=base.Context(clocks=FakeClocks(read_cost_ns=0)))
            sidecar.start(background=False)
            row = sidecar.tick()
            self.assertEqual(row["values"]["readings"]["TH0P"], {
                "data_type": "sp78", "data_size": 2, "raw_hex": "2100", "value": 33, "error": None})
            transport.fail_on.add("TG0D")
            self.assertIsNotNone(sidecar.tick()["values"]["readings"]["TG0D"]["error"])
            sidecar.stop()

    def test_failed_prepare_closes_sidecar(self):
        spec = replace(episode_spec(hidden=False), thermal=POLICY)
        config = replace(base_config(), workload_profile=replace(base_config().workload_profile,
                                                                 prompt_text=spec.to_text()))
        runtime = mock.Mock()
        runtime.prepare.return_value = AdapterResult(ok=False)
        sidecar = mock.Mock()
        with mock.patch.object(thermal, "Sidecar", return_value=sidecar):
            adapter = EpisodeRuntimeAdapter(runtime, FakeClock())
            self.assertFalse(adapter.prepare(config, mock.Mock(outputs_dir=Path("unused"))).ok)
        sidecar.stop.assert_called_once()
