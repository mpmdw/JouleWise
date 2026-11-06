"""Synthetic custody tests; no Apple hardware is opened."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from joulewise.align.apple.thermal_gates import (ThermalSession, WindowReferenceRefused,
    load_window_reference, validate_gate_policy)
from tests.align.test_thermal_gate import Transport, policy
from joulewise.align.apple.smc_reader import Reader
from joulewise.clock import FakeClock


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


if __name__ == '__main__':
    unittest.main()
