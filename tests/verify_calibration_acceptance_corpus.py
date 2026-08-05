#!/usr/bin/env python3
"""Re-verify the D-079 v2 member table against primary evidence bytes."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_ledger import content_id_from_artifact_hashes


EXPECTED = {
    "n": 19,
    "minimum_s": Decimal("0.022741007370546462"),
    "minimum_member_id": "20260722T215127-eeef661a",
    "maximum_s": Decimal("0.03355875667989999"),
    "maximum_member_id": "20260722T222332-901c5c13",
    "range_s": Decimal("0.010817749309353528"),
    "mean_s": Decimal("0.026950033977532761"),
    "sample_sd_s": Decimal("0.002970761365307205"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(repo_root: Path, artifact_path: Path) -> None:
    repo_root = repo_root.resolve(strict=True)
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    values: list[tuple[str, Decimal]] = []
    prior = {
        row["content_id"]: row
        for row in artifact["prior_observation_set"]["observations"]
    }
    for member in artifact["derivation_corpus"]["members"]:
        directory = (repo_root / member["source_directory"]).resolve(strict=True)
        directory.relative_to(repo_root)
        manifest_path = directory / "manifest.json"
        evidence_path = directory / "instrument_evidence.json"
        evidence = json.loads(
            evidence_path.read_text(encoding="utf-8"),
            parse_float=str,
            parse_int=str,
        )
        if evidence["b_fiducial_s"] != member["b_fiducial_s"]:
            raise ValueError(f"{member['member_id']}: b_fiducial_s mismatch")
        if sha256(manifest_path) != member["manifest_sha256"]:
            raise ValueError(f"{member['member_id']}: manifest sha256 mismatch")
        if sha256(evidence_path) != member["instrument_evidence_sha256"]:
            raise ValueError(
                f"{member['member_id']}: instrument evidence sha256 mismatch"
            )
        content_id = content_id_from_artifact_hashes(
            {
                "manifest.json": member["manifest_sha256"],
                "instrument_evidence.json": member[
                    "instrument_evidence_sha256"
                ],
            }
        )
        if (
            content_id not in prior
            or prior[content_id].get("attempt_id") != member["member_id"]
            or prior[content_id].get("disposition") != "valid"
        ):
            raise ValueError(
                f"{member['member_id']}: prior_observation_set mismatch"
            )
        values.append((member["member_id"], Decimal(member["b_fiducial_s"])))

    minimum = min(values, key=lambda row: row[1])
    maximum = max(values, key=lambda row: row[1])
    with localcontext() as context:
        context.prec = 80
        mean = sum((value for _, value in values), Decimal(0)) / Decimal(
            len(values)
        )
        sample_sd = (
            sum((value - mean) ** 2 for _, value in values)
            / Decimal(len(values) - 1)
        ).sqrt()
        quantum = Decimal("0.000000000000000001")
        observed = {
            "n": len(values),
            "minimum_s": minimum[1],
            "minimum_member_id": minimum[0],
            "maximum_s": maximum[1],
            "maximum_member_id": maximum[0],
            "range_s": maximum[1] - minimum[1],
            "mean_s": mean.quantize(quantum, rounding=ROUND_HALF_EVEN),
            "sample_sd_s": sample_sd.quantize(
                quantum, rounding=ROUND_HALF_EVEN
            ),
        }
    if observed != EXPECTED:
        raise ValueError(f"banked reconstruction mismatch: {observed!r}")
    print(f"n={observed['n']} min={minimum[1]} ({minimum[0]})")
    print(f"max={maximum[1]} ({maximum[0]}) range={observed['range_s']}")
    print(f"mean={observed['mean_s']} sample_sd={observed['sample_sd_s']}")
    print("PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    verify(args.repo_root, args.artifact)


if __name__ == "__main__":
    main()
