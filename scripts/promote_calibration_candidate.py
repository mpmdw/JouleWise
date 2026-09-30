#!/usr/bin/env python3
"""Promote the reviewed 25G83 candidate using lead-authored issuance text."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.issue_calibration_acceptance_generation import (  # noqa: E402
    derivation_input_sha256, derivation_sha256,
)

CANDIDATE = ROOT / "docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json"
CANDIDATE_SHA256 = "dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2"
INPUT_SHA256 = "e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011"
ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n12_25g83_r1"
RULING_IDS = (
    "SCI-25G83-CANDIDATE-01", "SCI-25G83-CANDIDATE-01-A1",
    "SCI-25G83-CANDIDATE-01-A2", "SCI-25G83-CANDIDATE-01-A3",
)
CLAIM_ELIGIBLE_MEANING = (
    "these bytes are an authentic issued calibration, and its numbers may "
    "serve as the timing-uncertainty basis of a reported result. It is a "
    "property of the file. It is not permission to start a window. Permission "
    "to start a claim-bearing window is separate; H1 withholds it, and H5 "
    "to H7 condition it."
)
PROTECTED = (
    "schema_version", "acceptance_id", "decision_ids", "ledger_cutoff",
    "identity_epoch", "prospective_rederivation", "derivation_corpus",
    "prior_observation_set", "decimal_derivation", "registered_generation_row",
    "derivation_input_sha256",
)


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw, object_pairs_hook=_unique_pairs,
                       parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _repository_bytes(relative_path: Any) -> bytes:
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("cited path missing")
    path = (ROOT / relative_path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("cited path outside repository")
    try:
        return path.read_bytes()
    except OSError as error:
        raise ValueError(f"cited file missing: {relative_path}") from error


def _verify_cited_files(value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            _verify_cited_files(item)
    elif isinstance(value, dict):
        if "relative_path" in value and "file_sha256" in value:
            digest = value["file_sha256"]
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("cited file digest malformed")
            if hashlib.sha256(_repository_bytes(value["relative_path"])).hexdigest() != digest:
                raise ValueError(f"cited file digest mismatch: {value['relative_path']}")
        for item in value.values():
            _verify_cited_files(item)


def _validate_text(text: dict[str, Any], candidate: dict[str, Any]) -> None:
    if set(text) != {"reason", "required_verification", "network_time_provenance", "issuance_record"}:
        raise ValueError("issuance text fields incomplete")
    if not isinstance(text["reason"], str) or not text["reason"]:
        raise ValueError("issuance reason missing")
    if not isinstance(text["required_verification"], str) or not text["required_verification"].startswith("complete: "):
        raise ValueError("required_verification must begin 'complete: '")
    record = text["issuance_record"]
    if not isinstance(record, dict):
        raise ValueError("issuance record missing")
    def complete_citation(value: Any, digest_field: str = "file_sha256") -> bool:
        return (isinstance(value, dict)
                and isinstance(value.get("relative_path"), str)
                and bool(value["relative_path"])
                and isinstance(value.get(digest_field), str)
                and bool(value[digest_field]))

    source = record.get("source_candidate")
    if not complete_citation(source) or source.get("file_sha256") != CANDIDATE_SHA256 or source.get("derivation_sha256") != candidate["derivation_sha256"]:
        raise ValueError("issuance record source candidate mismatch")
    disclosures = record.get("disclosures")
    if not isinstance(disclosures, list) or len(disclosures) < 8 or [item.get("id") for item in disclosures if isinstance(item, dict)] != [f"D{n}" for n in range(1, len(disclosures) + 1)] or any(not isinstance(item.get("text"), str) or not item["text"] for item in disclosures if isinstance(item, dict)):
        raise ValueError("issuance disclosures D1..D8 missing or unordered")
    holds = record.get("holds")
    if (not isinstance(holds, list) or
            not {"H1", "H5", "H6", "H7"} <= {
                item.get("id") for item in holds
                if isinstance(item, dict) and isinstance(item.get("text"), str) and item["text"]
            }):
        raise ValueError("H1 H5 H6 H7 holds or text missing")
    rulings = record.get("rulings")
    if not isinstance(rulings, list) or [item.get("id") for item in rulings if isinstance(item, dict)] != list(RULING_IDS) or any(
        not complete_citation(item)
        or re.fullmatch(r"[0-9a-f]{64}", item.get("file_sha256", "")) is None
        for item in rulings
    ):
        raise ValueError("ruling digests missing")
    provenance = text["network_time_provenance"]
    if not isinstance(provenance, dict) or provenance.get("disclosure_id") != "D8":
        raise ValueError("network time provenance missing D8")
    source_rulings = provenance.get("source_rulings")
    if (not isinstance(source_rulings, list) or not source_rulings
            or any(not complete_citation(item) for item in source_rulings)
            or not complete_citation(provenance.get("preserved_log"), "plain_text_sha256")):
        raise ValueError("network time citations incomplete")
    _verify_cited_files(text)
    preserved_log = provenance.get("preserved_log")
    if not isinstance(preserved_log, dict):
        raise ValueError("preserved log missing")
    try:
        log_digest = hashlib.sha256(gzip.decompress(
            _repository_bytes(preserved_log.get("relative_path"))
        )).hexdigest()
    except (OSError, EOFError) as error:
        raise ValueError("preserved log invalid") from error
    if log_digest != preserved_log.get("plain_text_sha256"):
        raise ValueError("preserved log plain-text digest mismatch")
    d8_text = disclosures[7]["text"]
    if provenance.get("text") != d8_text:
        raise ValueError("network time provenance differs from D8")
    if record.get("claim_eligible_meaning") != CLAIM_ELIGIBLE_MEANING:
        raise ValueError("claim_eligible_meaning mismatch")
    if not isinstance(record.get("hold_enforcement"), str) or not record["hold_enforcement"].strip():
        raise ValueError("hold_enforcement missing")


def promote(candidate_raw: bytes, issuance_raw: bytes) -> bytes:
    if hashlib.sha256(candidate_raw).hexdigest() != CANDIDATE_SHA256:
        raise ValueError("candidate digest mismatch")
    candidate = _parse(candidate_raw)
    if (
        candidate.get("acceptance_id") != ACCEPTANCE_ID
        or candidate.get("artifact_role") != "candidate"
        or candidate.get("candidate_not_issued") is not True
        or candidate.get("derivation_input_sha256") != derivation_input_sha256(candidate)
        or candidate.get("derivation_sha256") != derivation_sha256(candidate)
    ):
        raise ValueError("candidate seal or role mismatch")
    issuance = _parse(issuance_raw)
    _validate_text(issuance, candidate)
    issued: dict[str, Any] = {}
    for key, value in candidate.items():
        if key == "candidate_not_issued":
            continue
        if key == "artifact_role":
            value = "issued"
        elif key == "issuance":
            # The candidate's licence sentence applies only to unissued bytes.
            value = {"status": "issued", "claim_eligible": True,
                     "reason": issuance["reason"]}
        elif key == "backfill_candidate":
            value = dict(value)
            value["status"] = "issued"
            value["production_issuance_blocked"] = False
            value["required_verification"] = issuance["required_verification"]
        elif key == "derivation_notes":
            value = dict(value)
            value["network_time_provenance"] = issuance["network_time_provenance"]
            value["issuance_record"] = issuance["issuance_record"]
        issued[key] = value
    issued["derivation_input_sha256"] = derivation_input_sha256(issued)
    if issued["derivation_input_sha256"] != INPUT_SHA256:
        raise ValueError("STOP: derivation input seal differs from ruled digest")
    issued["derivation_sha256"] = derivation_sha256(issued)
    for key in PROTECTED:
        if issued[key] != candidate[key] or json.dumps(issued[key], ensure_ascii=True) != json.dumps(candidate[key], ensure_ascii=True):
            raise ValueError(f"protected field changed: {key}")
    for key, value in candidate["derivation_notes"].items():
        if issued["derivation_notes"].get(key) != value:
            raise ValueError(f"protected note changed: {key}")
    if issued["backfill_candidate"]["candidate_inventory"] != candidate["backfill_candidate"]["candidate_inventory"]:
        raise ValueError("candidate inventory changed")
    raw = (json.dumps(issued, indent=2, sort_keys=False, ensure_ascii=True) + "\n").encode("utf-8")
    # Not an independent check: both sides derive from the same parsed object.
    # The independent check is test P2 on the written file.
    if _parse(raw) != issued:
        raise ValueError("serialization self-check failed")
    return raw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--issuance-text", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out", type=Path)
    action.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        raw = promote(args.candidate.read_bytes(), args.issuance_text.read_bytes())
        path = args.out or args.check
        if args.check:
            if path.read_bytes() != raw:
                raise ValueError("issued file differs from promotion output")
        else:
            if path.exists() and path.read_bytes() != raw:
                raise ValueError("refusing to overwrite different bytes")
            path.write_bytes(raw)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"promotion refused: {error}\n")
    print(f"issued sha256={hashlib.sha256(raw).hexdigest()}")


if __name__ == "__main__":
    main()
