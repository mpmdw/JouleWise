from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.detection_floor_registry import (
    DetectionFloorRegistryError,
    load_detection_floor_closed_sets,
)


ROOT = Path(__file__).resolve().parents[1]
DETECTION_REGISTRY = (
    ROOT / "configs" / "analysis_registry" / "detection_floor_closed_sets.v1.json"
)
DETECTION_DIGEST = DETECTION_REGISTRY.with_suffix(".sha256")


class ClosedSetRegistryTests(unittest.TestCase):
    def test_detection_floor_registry_bytes_are_checksum_bound(self) -> None:
        registry = load_detection_floor_closed_sets(repository_root=ROOT)
        observed = hashlib.sha256(DETECTION_REGISTRY.read_bytes()).hexdigest()
        recorded = DETECTION_DIGEST.read_text(encoding="utf-8").split()[0]
        self.assertEqual(registry.sha256, observed)
        self.assertEqual(registry.sha256, recorded)

    def test_changed_detection_floor_declaration_requires_matching_digest(self) -> None:
        value = json.loads(DETECTION_REGISTRY.read_text(encoding="utf-8"))
        value["floor_metrics"].append(
            {
                "name": "phase_energy_j.score",
                "window_class": "phase",
                "authority": "counterfactual test declaration",
            }
        )
        value["calibration_scopes"].append(
            {
                "scope_id": "successor_window",
                "authority": "counterfactual test declaration",
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_path = tmp_path / DETECTION_REGISTRY.name
            digest_path = registry_path.with_suffix(".sha256")
            registry_path.write_text(
                json.dumps(value, indent=2) + "\n",
                encoding="utf-8",
            )
            digest_path.write_bytes(DETECTION_DIGEST.read_bytes())
            with self.assertRaisesRegex(DetectionFloorRegistryError, "sha256 mismatch"):
                load_detection_floor_closed_sets(
                    registry_path=registry_path,
                    digest_path=digest_path,
                )

            digest = hashlib.sha256(registry_path.read_bytes()).hexdigest()
            digest_path.write_text(
                f"{digest}  {registry_path.name}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                DetectionFloorRegistryError,
                "immutable trust anchor mismatch.*new registry identity",
            ):
                load_detection_floor_closed_sets(
                    registry_path=registry_path,
                    digest_path=digest_path,
                )


if __name__ == "__main__":
    unittest.main()
