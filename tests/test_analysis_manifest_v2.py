from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_manifest as v1
from joulewise import analysis_manifest_v2 as v2
from joulewise.detection_floor_registry import DetectionFloorRegistryError


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_REGISTRY = ROOT / "configs" / "analysis_registry" / "slice_2m_ap2.v1.json"
V1_MODULE = ROOT / "joulewise" / "analysis_manifest.py"
V1_MODULE_SHA256 = (
    "5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9"
)


class AnalysisManifestV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(ANALYSIS_REGISTRY.read_text(encoding="utf-8"))

    def _registry_metric_rows(self) -> list[dict[str, object]]:
        closed_sets = v2.default_detection_floor_closed_sets()
        return [
            {
                "metric_tag": name.replace(".", "_"),
                "name": name,
                "window_class": window_class,
                "unit": "J",
                "ratio_estimand": None,
            }
            for name, window_class in closed_sets.metric_window_classes.items()
        ]

    def test_frozen_v1_rows_retain_v1_semantics_and_bytes(self) -> None:
        self.assertEqual(
            hashlib.sha256(V1_MODULE.read_bytes()).hexdigest(),
            V1_MODULE_SHA256,
        )
        self.assertEqual(
            v2.validate_analysis_registry(self.registry),
            v1.validate_analysis_registry(self.registry),
        )

    def test_authenticated_detection_floor_metric_rows_are_accepted(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["metrics"] = self._registry_metric_rows()
        self.assertEqual(v2.validate_analysis_registry(registry), [])
        self.assertIn(
            "registry.metrics: must contain the four frozen AP-2 metric rows",
            v1.validate_analysis_registry(registry),
        )

    def test_unregistered_metric_is_refused(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["metrics"] = self._registry_metric_rows()
        registry["metrics"].append(
            {
                "metric_tag": "unregistered",
                "name": "phase_energy_j.unregistered",
                "window_class": "phase",
                "unit": "J",
                "ratio_estimand": None,
            }
        )
        self.assertIn(
            "registry.metrics[9].name: not declared by the authenticated detection-floor registry",
            v2.validate_analysis_registry(registry),
        )

    def test_successor_rows_fail_closed_when_registry_authentication_fails(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["metrics"].append(
            {
                "metric_tag": "idle_subtracted_request",
                "name": "idle_subtracted_energy_j",
                "window_class": "request",
                "unit": "J",
                "ratio_estimand": None,
            }
        )
        with mock.patch.object(
            v2,
            "default_detection_floor_closed_sets",
            side_effect=DetectionFloorRegistryError("synthetic authentication failure"),
        ):
            with self.assertRaisesRegex(
                DetectionFloorRegistryError,
                "synthetic authentication failure",
            ):
                v2.validate_analysis_registry(registry)


if __name__ == "__main__":
    unittest.main()
