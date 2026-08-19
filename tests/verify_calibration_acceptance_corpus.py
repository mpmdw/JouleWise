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


# Banked per GENERATION.  `stored_lexeme_is_member_value` records the
# generation's value semantics: the n=19 generations copy the lexeme stored in
# each bundle's instrument_evidence.json, while the anchor-v3 generation
# SUPERSEDES those scalars with values re-derived from primary bytes under the
# rate-aware set-membership estimator, so equality with the stored lexeme would
# be a defect rather than a proof.
EXPECTED_BY_ACCEPTANCE_ID = {
    "d079_calibration_acceptance_v2_n19": {
        "stored_lexeme_is_member_value": True,
        "n": 19,
        "minimum_s": Decimal("0.022741007370546462"),
        "minimum_member_id": "20260722T215127-eeef661a",
        "maximum_s": Decimal("0.03355875667989999"),
        "maximum_member_id": "20260722T222332-901c5c13",
        "range_s": Decimal("0.010817749309353528"),
        "mean_s": Decimal("0.026950033977532761"),
        "sample_sd_s": Decimal("0.002970761365307205"),
    },
    "d079_calibration_acceptance_v2_n17_r3": {
        "stored_lexeme_is_member_value": False,
        "n": 17,
        "minimum_s": Decimal("0.02317490442656863"),
        "minimum_member_id": "20260722T215127-eeef661a",
        "maximum_s": Decimal("0.03289849371536248"),
        "maximum_member_id": "20260722T214220-1acdbbc0",
        "range_s": Decimal("0.00972358928879385"),
        "mean_s": Decimal("0.026848579671140323"),
        "sample_sd_s": Decimal("0.002460856207694636"),
    },
}
EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n19_r2"] = (
    EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n19"]
)
# r4 is a science-neutral estimator-pin reissue of r3: identical corpus,
# identical member table, therefore identical expected statistics AND the same
# anchor-v3 value semantics (the stored v2 lexeme is SUPERSEDED, never copied).
EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n17_r4"] = (
    EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n17_r3"]
)
EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n17_r5"] = (
    EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n17_r3"]
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(repo_root: Path, artifact_path: Path) -> None:
    repo_root = repo_root.resolve(strict=True)
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    banked = EXPECTED_BY_ACCEPTANCE_ID.get(artifact["acceptance_id"])
    if banked is None:
        raise ValueError(f"no banked reconstruction for {artifact['acceptance_id']}")
    expected = {key: item for key, item in banked.items()
                if key != "stored_lexeme_is_member_value"}
    stored_is_member = banked["stored_lexeme_is_member_value"]
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
        stored_matches = evidence["b_fiducial_s"] == member["b_fiducial_s"]
        if stored_is_member and not stored_matches:
            raise ValueError(f"{member['member_id']}: b_fiducial_s mismatch")
        if not stored_is_member and stored_matches:
            raise ValueError(
                f"{member['member_id']}: a re-derived generation must not copy "
                "the superseded stored scalar"
            )
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
    if observed != expected:
        raise ValueError(f"banked reconstruction mismatch: {observed!r}")
    print(f"n={observed['n']} min={minimum[1]} ({minimum[0]})")
    print(f"max={maximum[1]} ({maximum[0]}) range={observed['range_s']}")
    print(f"mean={observed['mean_s']} sample_sd={observed['sample_sd_s']}")
    print(
        f"acceptance_id={artifact['acceptance_id']} "
        f"stored_lexeme_is_member_value={stored_is_member}"
    )
    print("PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    verify(args.repo_root, args.artifact)


if __name__ == "__main__":
    main()
