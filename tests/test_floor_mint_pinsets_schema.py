"""Registry synchronization checks for floor-mint pinset schema v2."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from joulewise.calibration_bracketing import (
    ISSUED_ACCEPTANCE_REGISTRY,
    _D102_GENERATION_DERIVATIONS,
    acceptance_bracket_screen_s,
)


REPOSITORY = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPOSITORY / "scripts/floor_mint_pinsets/schema_v2.json"


def _conditional_screens(schema: dict) -> dict[str, dict[str, str]]:
    definitions = schema["$defs"]
    surfaces = {
        "finalProducer": definitions["finalProducer"]["allOf"],
        "pinRequirements": definitions["pinRequirements"]["allOf"][0][
            "properties"
        ]["producer_plans"]["items"]["allOf"],
    }
    observed: dict[str, dict[str, str]] = {}
    for surface, conditionals in surfaces.items():
        by_definition: dict[str, str] = {}
        for conditional in conditionals:
            acceptance = conditional["if"]["properties"][
                "calibration_acceptance"
            ]
            reference = acceptance["properties"]["acceptance_id"]["$ref"]
            definition_name = reference.rsplit("/", 1)[-1]
            cells = conditional["then"]["properties"]["cells"]["items"]
            if surface == "finalProducer":
                contract = cells["properties"]["postcollection"]["properties"]
            else:
                contract = cells["properties"]["allowance_contract"]["properties"]
            by_definition[definition_name] = contract["bracket_screen_s"]["const"]
        observed[surface] = by_definition
    return observed


class FloorMintPinsetsSchemaTests(unittest.TestCase):
    def test_generation_screen_conditionals_match_python_registries(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        issued_ids = set(ISSUED_ACCEPTANCE_REGISTRY)
        derivation_ids = set(_D102_GENERATION_DERIVATIONS)
        self.assertEqual(issued_ids, derivation_ids)

        conditionals = _conditional_screens(schema)
        self.assertEqual(
            conditionals["finalProducer"], conditionals["pinRequirements"]
        )
        self.assertEqual(
            set(conditionals["finalProducer"]),
            {"n19AcceptanceIds", "n17AcceptanceIds"},
        )

        ids_by_screen: dict[str, set[str]] = {}
        for acceptance_id in issued_ids:
            screen = acceptance_bracket_screen_s(acceptance_id)
            self.assertIsNotNone(screen)
            ids_by_screen.setdefault(screen, set()).add(acceptance_id)

        for definition_name, screen in conditionals["finalProducer"].items():
            with self.subTest(definition=definition_name):
                self.assertEqual(
                    set(schema["$defs"][definition_name]["enum"]),
                    ids_by_screen[screen],
                )


if __name__ == "__main__":
    unittest.main()
