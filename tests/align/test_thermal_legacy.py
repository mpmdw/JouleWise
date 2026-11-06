"""Frozen legacy config bytes and spec serialization (no model/data access)."""
import hashlib
import json
from pathlib import Path
import unittest

from joulewise.align.apple.workload import EpisodeSpec

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COUNT = 84
EXPECTED_SHA = '7bd1609ea1f292c0b398597019097e703356e426065ed38e86bb3e249191862a'


class LegacyTests(unittest.TestCase):
    def test_all_legacy_stage_bytes_and_episode_specs_are_unchanged(self):
        paths = sorted(p for v in range(4) for p in (ROOT/'configs/campaigns'/f'align_pilot_v{v}'/'stages').rglob('*.json'))
        lines = [f'{p.relative_to(ROOT)}\0{hashlib.sha256(p.read_bytes()).hexdigest()}\n' for p in paths]
        # Verified equal to pilot-10 kit 83e2dac59 (was c9a0a3943) before freezing, including all anchors,
        # legacy cells, and order manifests across v0-v3; no absolute data paths followed.
        self.assertEqual(len(paths), EXPECTED_COUNT)
        self.assertEqual(hashlib.sha256(''.join(lines).encode()).hexdigest(), EXPECTED_SHA)
        for path in paths:
            value = json.loads(path.read_text())
            profile = value.get('workload_profile', {}) if isinstance(value, dict) else {}
            if profile.get('name') == 'align_episode':
                text = profile['prompt_text']
                spec = EpisodeSpec.from_text(text)
                self.assertEqual(spec.to_text(), text, str(path.relative_to(ROOT)))
                self.assertIsNone(spec.thermal)
                self.assertIsNone(spec.warmup_condition)


if __name__ == '__main__':
    unittest.main()
