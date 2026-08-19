#!/usr/bin/env python3
"""Prove the r6 presentation reissue did not perturb the r4 D-079 corpus."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

if len(sys.argv) not in {3, 4}:
    raise SystemExit(
        "usage: prove_r6_neutrality.py REPOSITORY_ROOT R4_DERIVATION_RECORD [MEMBER_INDEX|--aggregate]"
    )
REPO = Path(sys.argv[1]).resolve(strict=True)
R4_RECORD = Path(sys.argv[2]).resolve(strict=True)
sys.path.insert(0, str(REPO))
sys.dont_write_bytecode = True

from joulewise.adapters.powermetrics import (  # noqa: E402
    anchor_records_from_powermetrics,
    parse_powermetrics_records,
)
from joulewise.powermetrics_fiducial import rederive_detection_from_artifacts  # noqa: E402
from joulewise.uncertainty_evidence import (  # noqa: E402
    CLOCK_METHOD_V3,
    derive_powermetrics_anchor_v3,
    stamp_from_mapping,
)

CORPUS_ROOT = Path("/Users/edr/code/JouleWise")
RAW_SEARCH_ROOTS = (
    CORPUS_ROOT,
    Path("/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup"),
)
OUT = Path(__file__).with_name("r6-neutrality-proof.json")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def locate_raw(member_id: str, expected_sha: str) -> bytes:
    candidates: list[Path] = []
    for root in RAW_SEARCH_ROOTS:
        if root.is_dir():
            candidates.extend(root.glob(f"*/instrument_validation/{member_id}/raw/powermetrics.plist"))
            candidates.extend(root.glob(f"*/*/instrument_validation/{member_id}/raw/powermetrics.plist"))
    for candidate in candidates:
        if candidate.is_file():
            raw = candidate.read_bytes()
            if sha256(raw) == expected_sha:
                return raw
    raise FileNotFoundError(f"{member_id}: raw/powermetrics.plist hash not found")


def main() -> int:
    expected_rows = json.loads(R4_RECORD.read_text(encoding="utf-8"))
    if len(sys.argv) == 4 and sys.argv[3] == "--aggregate":
        fragments = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(OUT.parent.glob("r6-neutrality-member-*.json"))
        ]
        rows = [row for fragment in fragments for row in fragment["members"]]
        mismatches = [item for fragment in fragments for item in fragment["mismatches"]]
        if len(rows) != len(expected_rows):
            mismatches.append(f"member_count:{len(rows)}!={len(expected_rows)}")
        OUT.write_text(json.dumps({"members": rows, "mismatches": mismatches}, indent=2) + "\n")
        transcript = "\n".join(
            (OUT.parent / f"neutrality-member-{index}.txt").read_text(
                encoding="utf-8"
            ).rstrip()
            for index in range(len(expected_rows))
        )
        (OUT.parent / "neutrality-transcript.txt").write_text(
            transcript + "\n", encoding="utf-8"
        )
        print("MEMBERS", len(rows))
        print("MISMATCHES", len(mismatches))
        print("PROOF", OUT)
        return 0 if not mismatches else 2
    if len(sys.argv) == 4:
        try:
            expected_rows = [expected_rows[int(sys.argv[3])]]
        except (ValueError, IndexError) as exc:
            raise SystemExit(f"invalid member index: {sys.argv[3]}") from exc
    observed_rows: list[dict] = []
    mismatches: list[str] = []
    for expected in expected_rows:
        member_id = expected["member_id"]
        directory = CORPUS_ROOT / expected["source_directory"]
        evidence_raw = (directory / "instrument_evidence.json").read_bytes()
        evidence = json.loads(evidence_raw)
        events_raw = (directory / "events.jsonl").read_bytes()
        anchor_block = evidence["clock_anchor"]
        raw = locate_raw(member_id, evidence["artifact_sha256"]["raw/powermetrics.plist"])
        stamps = {
            name: stamp_from_mapping(value)
            for name, value in anchor_block["clock_stamps"].items()
            if isinstance(value, dict)
        }
        derived_anchor = derive_powermetrics_anchor_v3(
            stamps=stamps,
            records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)),
        )
        bounded = derived_anchor.get("status") == "bounded"
        observed = {
            "member_id": member_id,
            "disposition": "bounded" if bounded else "refused",
            "anchor_bound_s": derived_anchor.get("effective_clock_anchor_bound_s"),
            "anchor_detail": derived_anchor.get("detail"),
            "b_fiducial_s": None,
            "projection_evaluated_cell_count": None,
        }
        if bounded:
            detection = rederive_detection_from_artifacts(
                raw, events_raw, anchor_block, anchor_method=CLOCK_METHOD_V3
            )
            observed["b_fiducial_s"] = detection.b_fiducial_s
            observed["projection_evaluated_cell_count"] = detection.projection_evaluated_cell_count
        expected_anchor = expected["anchor_v3"]
        comparisons = {
            "disposition": (expected["v3_disposition"], observed["disposition"]),
            "anchor_bound_s": (expected_anchor.get("effective_clock_anchor_bound_s"), observed["anchor_bound_s"]),
            "anchor_detail": (expected_anchor.get("detail"), observed["anchor_detail"]),
            "b_fiducial_s": (expected.get("b_fiducial_v3_s"), observed["b_fiducial_s"]),
            "projection_evaluated_cell_count": (expected.get("projection_evaluated_cell_count"), observed["projection_evaluated_cell_count"]),
        }
        for name, pair in comparisons.items():
            if pair[0] != pair[1]:
                mismatches.append(f"{member_id}:{name}:{pair[0]!r}!={pair[1]!r}")
        observed_rows.append(observed)
        print(f"{member_id} {observed['disposition']} exact={not any(item.startswith(member_id + ':') for item in mismatches)}")
    output = OUT
    if len(sys.argv) == 4:
        output = OUT.with_name(f"r6-neutrality-member-{sys.argv[3]}.json")
    output.write_text(json.dumps({"members": observed_rows, "mismatches": mismatches}, indent=2) + "\n")
    print("MEMBERS", len(observed_rows))
    print("MISMATCHES", len(mismatches))
    print("PROOF", output)
    return 0 if not mismatches else 2


if __name__ == "__main__":
    raise SystemExit(main())
