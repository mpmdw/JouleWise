import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from joulewise import cli
from joulewise.align.apple.thermal_gates import ThermalRegistry
from joulewise.schemas import RunStatus
from tests.align.test_apple_campaign import base_config, episode_spec


class CliRegistrySelectionTests(unittest.TestCase):
    def invoke(self, config):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp)/'config.json'
            cfg.write_text(json.dumps(config.to_dict()))
            summary = SimpleNamespace(status=RunStatus.SUCCEEDED, run_id=config.run_id or 'run',
                                      failure_reason=None)
            with patch('joulewise.cli.run_benchmark', return_value=(Path(tmp)/'bundle', summary)) as run:
                cli.main(['run', str(cfg), '--runs-dir', str(Path(tmp)/'runs')])
            return run.call_args.kwargs

    def test_anchor_none_and_gate_registry_preserve_other_kwargs(self):
        base = base_config()
        anchor = self.invoke(base)
        gate = {'sensors': {'s_fast': 'Tfak', 's_slow': 'Tslw', 'fan_keys': [], 'r0_sha256': 'a'*64},
                'delta_fast_c': 1, 'delta_slow_c': 1, 'turn_cap_s': 30, 'per_turn': True,
                'heavy': False, 'chunk_tokens': 256, 'window_reference': {'role': 'capture'}}
        spec = replace(episode_spec(hidden=False), thermal=gate, warmup_condition='benign')
        gated_config = replace(base, workload_profile=replace(base.workload_profile,
                               name='align_episode', prompt_text=spec.to_text(), prompt_tokens=None))
        gated = self.invoke(gated_config)
        self.assertIsNone(anchor.pop('registry'))
        self.assertIsInstance(gated.pop('registry'), ThermalRegistry)
        self.assertEqual(anchor, gated)

    def test_gate_repetitions_two_refuses_before_bundle(self):
        base = base_config()
        gate = {'sensors': {'s_fast': 'Tfak', 's_slow': 'Tslw'}}
        spec = replace(episode_spec(hidden=False), thermal=gate)
        config = replace(base, workload_profile=replace(base.workload_profile, name='align_episode',
                         repetitions=2, prompt_text=spec.to_text(), prompt_tokens=None))
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp)/'config.json'; cfg.write_text(json.dumps(config.to_dict()))
            self.assertEqual(cli.main(['run', str(cfg), '--runs-dir', str(Path(tmp)/'runs')]), 2)
            self.assertFalse((Path(tmp)/'runs').exists())


if __name__ == '__main__':
    unittest.main()
