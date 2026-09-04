#!/usr/bin/env python3
"""Issue or byte-check the science-neutral D-079 r7 successor.

The magistrate authorized this exact successor path on 2026-09-04.  This
producer authenticates the retained r6 issuance, permits only the r7 identity,
provenance, and governed estimator-pin rotation, and emits deterministic JSON.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


PREDECESSOR_ID = "d079_calibration_acceptance_v2_n17_r6"
PREDECESSOR_RELATIVE_PATH = (
    "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
)
PREDECESSOR_FILE_SHA256 = (
    "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"
)
ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r7"
OUTPUT_RELATIVE_PATH = (
    "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json"
)
EXPECTED_CHANGED_ESTIMATOR_PINS = frozenset(
    {"joulewise/powermetrics_fiducial.py"}
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_root", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare existing output bytes with the deterministic payload",
    )
    return parser


def _payload(repository: Path) -> tuple[bytes, Mapping[str, Mapping[str, str]], str]:
    sys.path.insert(0, str(repository))
    sys.dont_write_bytecode = True
    from joulewise.calibration_bracketing import (  # noqa: PLC0415
        ESTIMATOR_CODE_PATHS,
        _canonical_sha256,
        _current_estimator_code_sha256,
        load_calibration_acceptance_bound,
    )

    predecessor_path = repository / PREDECESSOR_RELATIVE_PATH
    predecessor_raw = predecessor_path.read_bytes()
    if _sha256(predecessor_raw) != PREDECESSOR_FILE_SHA256:
        raise ValueError("predecessor exact-byte digest mismatch")
    predecessor = load_calibration_acceptance_bound(predecessor_path)
    if predecessor is None or predecessor.get("acceptance_id") != PREDECESSOR_ID:
        raise ValueError("predecessor is not the registered r6 issuance")

    estimator_pins = _current_estimator_code_sha256()
    if estimator_pins is None or set(estimator_pins) != set(ESTIMATOR_CODE_PATHS):
        raise ValueError("current governed estimator pin set is not derivable")
    old_pins = predecessor["prospective_rederivation"]["estimator_code_sha256"]
    changed = {
        path: {"predecessor": old_pins[path], "reissued": estimator_pins[path]}
        for path in ESTIMATOR_CODE_PATHS
        if old_pins[path] != estimator_pins[path]
    }
    if set(changed) != EXPECTED_CHANGED_ESTIMATOR_PINS:
        raise ValueError(
            "changed governed estimator pins must be exactly "
            f"{sorted(EXPECTED_CHANGED_ESTIMATOR_PINS)!r}; observed "
            f"{sorted(changed)!r}"
        )

    artifact: dict[str, Any] = deepcopy(predecessor)
    artifact["acceptance_id"] = ACCEPTANCE_ID
    artifact["prospective_rederivation"]["estimator_code_sha256"] = dict(
        estimator_pins
    )
    notes = artifact["derivation_notes"]
    notes["generation"] = (
        "SCIENCE-NEUTRAL reissue of d079_calibration_acceptance_v2_n17_r6 "
        "at the instrument executable path-and-digest pin head. Only the "
        "governed powermetrics fiducial estimator bytes rotated; the accepted "
        "corpus, member values, thresholds, and operatives are unchanged."
    )
    notes["predecessor"] = {
        "acceptance_id": PREDECESSOR_ID,
        "relative_path": PREDECESSOR_RELATIVE_PATH,
        "file_sha256": PREDECESSOR_FILE_SHA256,
        "derivation_sha256": predecessor["derivation_sha256"],
        "relationship": (
            "retained byte-identical forever as the prior anchor-v3 "
            "generation; r7 supersedes r6 only as the LIVE generation and "
            "differs from it in the governed powermetrics fiducial estimator "
            "pin plus generation identity and provenance"
        ),
    }
    notes["reissue_delta"] = {
        "kind": "estimator_pin_rotation_only",
        "changed_estimator_pins": changed,
        "science_neutrality_evidence": (
            "the r6 accepted corpus, member values, decimal derivation, "
            "thresholds, operatives, ledger cutoff, and identity epoch are "
            "copied without change; only code provenance rotates"
        ),
    }
    artifact.pop("derivation_sha256")
    artifact["derivation_sha256"] = _canonical_sha256(artifact)

    allowed_top_level = {
        "acceptance_id",
        "prospective_rederivation",
        "derivation_notes",
        "derivation_sha256",
    }
    for key in predecessor:
        if key not in allowed_top_level and artifact[key] != predecessor[key]:
            raise ValueError(f"unexpected science-facing delta at {key}")
    old_rederivation = dict(predecessor["prospective_rederivation"])
    new_rederivation = dict(artifact["prospective_rederivation"])
    old_rederivation.pop("estimator_code_sha256")
    new_rederivation.pop("estimator_code_sha256")
    if old_rederivation != new_rederivation:
        raise ValueError("unexpected non-estimator prospective delta")
    old_notes = dict(predecessor["derivation_notes"])
    new_notes = dict(notes)
    for key in ("generation", "predecessor", "reissue_delta"):
        old_notes.pop(key, None)
        new_notes.pop(key, None)
    if old_notes != new_notes:
        raise ValueError("unexpected retained derivation-note delta")

    payload = (
        json.dumps(
            artifact,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")
    return payload, changed, artifact["derivation_sha256"]


def main() -> int:
    args = _parser().parse_args()
    repository = args.repository_root.resolve(strict=True)
    output = repository / OUTPUT_RELATIVE_PATH
    try:
        payload, changed, derivation_sha256 = _payload(repository)
        if args.check:
            if output.read_bytes() != payload:
                raise ValueError("issued bytes differ from deterministic payload")
            action = "CHECKED"
        else:
            with output.open("xb") as handle:
                if handle.write(payload) != len(payload):
                    raise OSError("short artifact write")
            action = "ISSUED"
    except (OSError, ValueError) as exc:
        print(f"REFUSE {exc}")
        return 2

    print(action, ACCEPTANCE_ID)
    print("PATH", OUTPUT_RELATIVE_PATH)
    print("FILE_SHA256", _sha256(payload))
    print("DERIVATION_SHA256", derivation_sha256)
    for path, change in sorted(changed.items()):
        print("PIN_MOVED", path, change["predecessor"], "->", change["reissued"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
