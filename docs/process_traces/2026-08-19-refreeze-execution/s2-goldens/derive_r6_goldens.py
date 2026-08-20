#!/usr/bin/env python3
"""One-time r6 review derivation for the generalized-mint fixture goldens.

This is deliberately throwaway review evidence, not a tracked regeneration
tool.  It builds only the test fixture and canonicalizes its pinset projection
with that fixture's independent JSON oracle.  It does not call a generalized
mint builder or any mint implementation hash helper.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# The script is stored outside the checkout; import the checked-out fixture
# rather than a globally installed test package.
sys.path.insert(0, str(Path.cwd()))
from tests import test_mint_floor_artifact_generalized as fixture


EXPECTED_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"
EXPECTED_ACCEPTANCE_SHA256 = (
    "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"
)


def main() -> None:
    pinset, inputs, _snapshot = fixture.synthetic_v2_fixture()
    acceptance = next(iter(inputs.values())).calibration_acceptance
    if acceptance["acceptance_id"] != EXPECTED_ACCEPTANCE_ID:
        raise SystemExit(f"wrong live fixture acceptance: {acceptance['acceptance_id']!r}")
    if fixture.file_sha256(fixture.DEFAULT_ACCEPTANCE_BOUND_PATH) != EXPECTED_ACCEPTANCE_SHA256:
        raise SystemExit("r6 file SHA-256 is not the reviewed acceptance pin")

    # Component artifact bytes contain no acceptance projection.  Retain their
    # reviewed component pins, then independently re-derive the acceptance-
    # bearing producer pins and their aggregate from the fixture JSON.
    for producer, entry, component_sha256 in zip(
        pinset["producer_plans"],
        pinset["aggregate"]["component_artifacts"],
        fixture.SYNTHETIC_COMPONENT_SHA256S,
        strict=True,
    ):
        producer["component_artifact"]["sha256"] = component_sha256
        entry["sha256"] = component_sha256
        entry["producer_pin_sha256"] = fixture._fixture_canonical_sha256(producer)

    producer_pins = tuple(
        entry["producer_pin_sha256"]
        for entry in pinset["aggregate"]["component_artifacts"]
    )
    producer_set = fixture._fixture_canonical_sha256(pinset["producer_plans"])
    transcript = {
        "acceptance_id": acceptance["acceptance_id"],
        "acceptance_file_sha256": fixture.file_sha256(
            fixture.DEFAULT_ACCEPTANCE_BOUND_PATH
        ),
        "synthetic_component_sha256s": fixture.SYNTHETIC_COMPONENT_SHA256S,
        "synthetic_producer_pin_sha256s": producer_pins,
        "synthetic_producer_set_sha256": producer_set,
        "cli_component_sha256s": fixture.CLI_COMPONENT_SHA256S,
        "oracle": "tests.test_mint_floor_artifact_generalized._fixture_canonical_sha256",
        "mint_implementation_called": False,
    }
    print(json.dumps(transcript, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
