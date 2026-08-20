#!/usr/bin/env python3
"""Assemble the science-neutral D-079 r5 capture-flip reissue.

This follows the r3/r4 issuance builders.  It authenticates r4, updates only
the generation identity, governed estimator pins, and reissue provenance, and
refuses any scientific or corpus delta.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: build_r5.py REPOSITORY_ROOT")
REPO = Path(sys.argv[1]).resolve(strict=True)
sys.path.insert(0, str(REPO))
sys.dont_write_bytecode = True

from joulewise.calibration_bracketing import (  # noqa: E402
    ESTIMATOR_CODE_PATHS,
    _canonical_sha256,
    _current_estimator_code_sha256,
)

PREDECESSOR_ID = "d079_calibration_acceptance_v2_n17_r4"
PREDECESSOR_REL = "configs/calibration/calibration_acceptance_d079_v2_n17_r4.json"
ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r5"
OUTPUT_REL = "configs/calibration/calibration_acceptance_d079_v2_n17_r5.json"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    predecessor_raw = (REPO / PREDECESSOR_REL).read_bytes()
    predecessor_sha = sha256(predecessor_raw)
    predecessor = json.loads(predecessor_raw)
    if predecessor.get("acceptance_id") != PREDECESSOR_ID:
        print("REFUSE predecessor acceptance_id mismatch")
        return 2
    if _canonical_sha256(
        {key: value for key, value in predecessor.items() if key != "derivation_sha256"}
    ) != predecessor.get("derivation_sha256"):
        print("REFUSE predecessor derivation_sha256 does not self-authenticate")
        return 2

    estimator_pins = _current_estimator_code_sha256()
    if estimator_pins is None or set(estimator_pins) != set(ESTIMATOR_CODE_PATHS):
        print("REFUSE estimator pin set is not derivable at this head")
        return 2
    old_pins = predecessor["prospective_rederivation"]["estimator_code_sha256"]
    changed = {
        path: {"predecessor": old_pins[path], "reissued": estimator_pins[path]}
        for path in ESTIMATOR_CODE_PATHS
        if old_pins[path] != estimator_pins[path]
    }
    if not changed:
        print("REFUSE no estimator pin moved; r5 would duplicate r4")
        return 2

    artifact = json.loads(predecessor_raw)
    artifact["acceptance_id"] = ACCEPTANCE_ID
    artifact["prospective_rederivation"]["estimator_code_sha256"] = dict(estimator_pins)
    artifact["derivation_notes"]["generation"] = (
        "SCIENCE-NEUTRAL reissue of d079_calibration_acceptance_v2_n17_r4 at the "
        "anchor-v3 production-capture flip head. The capture adapter, strict "
        "verification, stored-method dispatch, and fiducial labelling were made "
        "era-faithful; governed estimator bytes therefore rotated. The full "
        "19-member corpus replay reproduced every anchor bound, disposition, "
        "projection cell count, and b_fiducial value exactly."
    )
    artifact["derivation_notes"]["predecessor"] = {
        "acceptance_id": PREDECESSOR_ID,
        "relative_path": PREDECESSOR_REL,
        "file_sha256": predecessor_sha,
        "derivation_sha256": predecessor["derivation_sha256"],
        "relationship": (
            "retained byte-identical forever as the intermediate anchor-v3 "
            "generation; r5 supersedes r4 only as the LIVE generation and "
            "differs from it in governed estimator pins alone"
        ),
    }
    artifact["derivation_notes"]["reissue_delta"] = {
        "kind": "estimator_pin_rotation_only",
        "changed_estimator_pins": changed,
        "science_neutrality_evidence": (
            "the full 19-member corpus was replayed through "
            "rederive_detection_from_artifacts at the capture-flip head; every "
            "b_fiducial, anchor bound, refusal disposition and projection cell "
            "count reproduced the r4 derivation record exactly"
        ),
    }
    artifact.pop("derivation_sha256", None)
    artifact["derivation_sha256"] = _canonical_sha256(artifact)

    for key in predecessor:
        if key in {
            "acceptance_id",
            "derivation_sha256",
            "prospective_rederivation",
            "derivation_notes",
        }:
            continue
        if artifact[key] != predecessor[key]:
            print(f"REFUSE unexpected delta in top-level key {key}")
            return 2
    predecessor_rederive = dict(predecessor["prospective_rederivation"])
    artifact_rederive = dict(artifact["prospective_rederivation"])
    predecessor_rederive.pop("estimator_code_sha256")
    artifact_rederive.pop("estimator_code_sha256")
    if predecessor_rederive != artifact_rederive:
        print("REFUSE unexpected delta inside prospective_rederivation")
        return 2
    predecessor_notes = dict(predecessor["derivation_notes"])
    artifact_notes = dict(artifact["derivation_notes"])
    for key in ("generation", "predecessor", "reissue_delta"):
        predecessor_notes.pop(key, None)
        artifact_notes.pop(key, None)
    if predecessor_notes != artifact_notes:
        print("REFUSE unexpected delta inside derivation_notes")
        return 2

    payload = (
        json.dumps(artifact, indent=2, ensure_ascii=False, allow_nan=False, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")
    output = REPO / OUTPUT_REL
    output.write_bytes(payload)
    print("ACCEPTANCE_ID", ACCEPTANCE_ID)
    print("PATH", output)
    print("FILE_SHA256", sha256(payload))
    print("DERIVATION_SHA256", artifact["derivation_sha256"])
    for path, change in sorted(changed.items()):
        print("PIN_MOVED", path, change["predecessor"], "->", change["reissued"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
