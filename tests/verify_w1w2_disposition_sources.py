"""Authenticate the twelve set-aside identities from local harvest primary bytes.

Run with python3 -B -m tests.verify_w1w2_disposition_sources. No raw replay,
ledger writes, calibration registration, or archive fetch is performed.
"""

import hashlib
import json
from pathlib import Path

from joulewise.calibration_dispositions import (
    DISPOSITION_DECISIONS, W1W2_SET_ASIDE_DECISION_ID,
)
from joulewise.calibration_ledger import content_id_from_artifact_hashes

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / (
    "docs/process_traces/2026-09-27-activation-77b1bee2/"
    "60-prepare-record/30-run1/candidate_acceptance_25g83.json"
)
CANDIDATE_SHA256 = "dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2"
ARCHIVE_ROOTS = (
    Path("/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root"),
    Path("/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root"),
)


def candidate_members():
    raw = CANDIDATE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CANDIDATE_SHA256
    candidate = json.loads(raw)
    members = candidate["derivation_corpus"]["members"]
    assert len(members) == candidate["derivation_corpus"]["n"] == 12
    assert candidate["candidate_not_issued"] is True
    prior = {row["content_id"]: row for row in candidate["prior_observation_set"]["observations"]}
    result = {}
    for member in members:
        hashes = {
            "manifest.json": member["manifest_sha256"],
            "instrument_evidence.json": member["instrument_evidence_sha256"],
        }
        content_id = content_id_from_artifact_hashes(hashes)
        assert content_id is not None and content_id not in result
        row = prior[content_id]
        assert row["disposition"] == "valid"
        assert row["attempt_id"] == member["member_id"]
        assert row["session_id"] == member["source_directory"].split("/")[0]
        result[content_id] = member
    return result


def main():
    members = candidate_members()
    valid = {}
    for root in ARCHIVE_ROOTS:
        for directory in sorted((root / "runs/instrument_validation").iterdir()):
            evidence_path = directory / "instrument_evidence.json"
            if not evidence_path.is_file():
                continue
            evidence = json.loads(evidence_path.read_bytes())
            if evidence.get("status") != "valid":
                continue
            hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                      for name in ("manifest.json", "instrument_evidence.json")}
            content_id = content_id_from_artifact_hashes(hashes)
            member = members[content_id]
            assert directory.name == member["member_id"]
            assert hashes == {"manifest.json": member["manifest_sha256"],
                              "instrument_evidence.json": member["instrument_evidence_sha256"]}
            assert content_id not in valid
            valid[content_id] = directory
            print(content_id, directory)
    assert set(valid) == set(members) == set(
        DISPOSITION_DECISIONS[W1W2_SET_ASIDE_DECISION_ID]["content_ids"]
    )
    print("W1W2_PRIMARY_IDENTITIES=PASS valid=12 registry=12")


if __name__ == "__main__":
    main()
