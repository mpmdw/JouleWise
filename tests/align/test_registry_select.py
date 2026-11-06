import unittest
from dataclasses import replace

from joulewise.align.apple.registry_select import registry_for_config
from joulewise.align.apple.thermal_gates import ThermalRegistry
from tests.align.test_apple_campaign import base_config, episode_spec


class RegistrySelectTests(unittest.TestCase):
    def test_none_paths_and_gate_map(self):
        base = base_config()
        self.assertIsNone(registry_for_config(base))
        malformed = replace(base, workload_profile=replace(base.workload_profile,
                            name='align_episode', prompt_text='{'))
        self.assertIsNone(registry_for_config(malformed))
        spec = replace(episode_spec(hidden=False), thermal={'sample_interval_s': 1,
                       'sensors': ['TC0P']})
        sensor_only = replace(base, workload_profile=replace(base.workload_profile,
                              name='align_episode', prompt_text=spec.to_text()))
        self.assertIsNone(registry_for_config(sensor_only))
        gate = {'sensors': {'s_fast': 'Tfak', 's_slow': 'Tslw', 'fan_keys': [], 'r0_sha256': 'a'*64}}
        gated = replace(base, workload_profile=replace(base.workload_profile,
                        name='align_episode', prompt_text=replace(spec, thermal=gate).to_text()))
        self.assertIsInstance(registry_for_config(gated), ThermalRegistry)


if __name__ == '__main__':
    unittest.main()
