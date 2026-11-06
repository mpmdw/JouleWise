"""Synthetic custody tests; no Apple hardware is opened."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple.thermal_gates import (ThermalSession, WindowReferenceRefused,
    load_window_reference, validate_gate_policy)
from tests.align.test_thermal_gate import Transport, policy
from joulewise.align.apple.smc_reader import Reader
from joulewise.clock import FakeClock
from joulewise.bundle import RunBundleWriter
from joulewise.schemas import BenchmarkConfig
from scripts import align_v4_kit as kit


class WindowReferenceCustodyTests(unittest.TestCase):
    def context(self, root, run_id):
        bundle = Path(root)/run_id
        outputs = bundle/'outputs'
        outputs.mkdir(parents=True)
        (bundle/'config.json').write_text('{}\n')
        return SimpleNamespace(run_id=run_id, bundle_path=bundle, outputs_dir=outputs)

    def test_capture_is_canonical_create_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = self.context(tmp, 'source')
            clock = FakeClock()
            obj = ThermalSession(policy(), clock, context, reader=Reader(Transport(clock)))
            obj.start()
            for _ in range(60):
                clock.sleep(1); obj.sample()
            obj.capture_reference('source')
            path = context.outputs_dir/'align_window_reference.json'
            record = json.loads(path.read_bytes())
            digest = record.pop('record_sha256')
            canonical = json.dumps(record, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=True, allow_nan=False).encode()
            self.assertEqual(hashlib.sha256(canonical).hexdigest(), digest)
            self.assertEqual(record['schema'], 'joulewise.align_window_reference.v1')
            obj.reference = None
            with self.assertRaisesRegex(WindowReferenceRefused, 'write_failed'):
                obj.capture_reference('source')
            obj.close()

    def test_policy_requires_role_forms(self):
        base = policy()
        for bad in ({}, {'role': 'capture', 'source_run_id': 'x'},
                    {'role': 'consume'}, {'fast_c': 40, 'slow_c': 40}):
            candidate = {**base, 'window_reference': bad}
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_gate_policy(candidate)

    def test_missing_and_path_refusals_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = self.context(tmp, 'consumer')
            digest = hashlib.sha256((Path(tmp)/'source'/'config.json').read_bytes()).hexdigest() \
                if (Path(tmp)/'source'/'config.json').exists() else 'a'*64
            consume = policy(window_reference={'role': 'consume', 'source_run_id': 'source',
                                                'source_config_sha256': digest})
            with self.assertRaisesRegex(WindowReferenceRefused, 'missing'):
                load_window_reference(validate_gate_policy(consume), context)
            for source in ('../x', 'consumer'):
                consume['window_reference']['source_run_id'] = source
                with self.assertRaisesRegex(WindowReferenceRefused, 'path_refused'):
                    load_window_reference(validate_gate_policy(consume), context)

    def test_kit_capture_bundle_bytes_bind_consumer_and_refuse_tampering(self):
        """Exercise the frozen-kit digest through the production bundle writer."""
        files = kit.build_files()
        plan = json.loads(files[kit.KIT/'collection_plan.json'])
        capture = plan['members'][4]
        consumer = plan['members'][5]
        config = BenchmarkConfig.from_mapping(json.loads(files[Path(capture['config_path'])]))
        with tempfile.TemporaryDirectory() as tmp:
            clock = FakeClock()
            # Launch-lineage admission is tested separately; this test needs
            # the real writer's config serialization and immutable layout.
            with patch('joulewise.bundle._writer_launch_lineage', return_value=None):
                writer = RunBundleWriter.create(Path(tmp), config, clock)
            source_context = SimpleNamespace(run_id=writer.run_id, bundle_path=writer.path,
                                             outputs_dir=writer.path/'outputs')
            capture_policy = policy(window_reference={'role': 'capture'})
            obj = ThermalSession(capture_policy, clock, source_context,
                                 reader=Reader(Transport(clock)))
            obj.start()
            for _ in range(60):
                clock.sleep(1); obj.sample()
            obj.capture_reference(writer.run_id)
            obj.close()

            consumer_path = Path(tmp)/consumer['run_id']
            (consumer_path/'outputs').mkdir(parents=True)
            context = SimpleNamespace(run_id=consumer['run_id'], bundle_path=consumer_path,
                                      outputs_dir=consumer_path/'outputs')
            policy_value = validate_gate_policy(policy(
                window_reference=consumer['spec']['thermal']['window_reference']))
            reference, _ = load_window_reference(policy_value, context)
            self.assertIsNotNone(reference)

            writer.path.joinpath('config.json').write_bytes(b'{}\n')
            with self.assertRaisesRegex(WindowReferenceRefused, 'binding_mismatch'):
                load_window_reference(policy_value, context)


if __name__ == '__main__':
    unittest.main()
