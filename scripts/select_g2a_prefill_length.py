#!/usr/bin/env python3
"""Materialize the ratified D-166 G2-a prefill-length decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence


SCHEMA_VERSION = "joulewise.g2a_prefill_selection.v1"
LADDER = (512, 1024, 2048, 4096)
MIN_SMALL_MEMBERS = 5
MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5
REDUCER_MIN_PHASE_SAMPLES = 3


class SummaryError(ValueError):
    """The G2-a summary cannot authorize a selection decision."""


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise SummaryError("duplicate_key")
        value[key] = item
    return value


def _rule() -> dict[str, Any]:
    return {
        "all_small_count_ge_5_required": True,
        "ladder_prefill_tokens": list(LADDER),
        "minimum_overlapping_power_interval_count": (
            MIN_OVERLAPPING_POWER_INTERVAL_COUNT
        ),
        "minimum_small_members_per_rung": MIN_SMALL_MEMBERS,
        "reducer_min_phase_samples": REDUCER_MIN_PHASE_SAMPLES,
        "selection": "shortest_qualifying_rung",
    }


def _normalized_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(LADDER):
        raise SummaryError("expected_four_row_array")
    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise SummaryError("row_not_object")
        length = item.get("length")
        small_members = item.get("small_members")
        all_small = item.get("all_small_count_ge_5")
        if isinstance(length, bool) or not isinstance(length, int):
            raise SummaryError("length_not_integer")
        if isinstance(small_members, bool) or not isinstance(small_members, int):
            raise SummaryError("small_members_not_integer")
        if not isinstance(all_small, bool):
            raise SummaryError("all_small_count_ge_5_not_boolean")
        rows.append(
            {
                "all_small_count_ge_5": all_small,
                "length": length,
                "small_members": small_members,
            }
        )
    rows.sort(key=lambda row: row["length"])
    if tuple(row["length"] for row in rows) != LADDER:
        raise SummaryError("ladder_mismatch_or_duplicate")
    return rows


def select(summary: Any, *, summary_sha256: str) -> dict[str, Any]:
    rows = _normalized_rows(summary)
    qualifying = [
        row["length"]
        for row in rows
        if row["small_members"] >= MIN_SMALL_MEMBERS
        and row["all_small_count_ge_5"]
    ]
    selected = qualifying[0] if qualifying else None
    record: dict[str, Any] = {
        "collection_prefill_tokens": selected if selected is not None else 4096,
        "qualifying_prefill_tokens": qualifying,
        "refusal": None,
        "rule": _rule(),
        "schema_version": SCHEMA_VERSION,
        "selected_prefill_tokens": selected,
        "status": "selected" if selected is not None else "refused",
        "summary_sha256": summary_sha256,
    }
    if selected is None:
        record["refusal"] = {
            "code": "no_g2a_prefill_rung_qualifies",
            "fallback_action": "collect_at_4096",
            "fallback_label": "collect-at-4096",
            "result_reporting": {
                "count_below_reducer_minimum": {
                    "count_range": "<3",
                    "refusal": "not_resolvable_sample_count",
                },
                "count_below_pre_registered_floor": {
                    "count_range": "3-4",
                    "disclose_reducer_resolvable_result": True,
                    "refusal": "below the pre-registered count floor of 5",
                },
            },
        }
    return record


def _malformed_record(*, summary_sha256: str | None, reason: str) -> dict[str, Any]:
    return {
        "collection_prefill_tokens": None,
        "qualifying_prefill_tokens": [],
        "refusal": {
            "code": "malformed_g2a_prefill_summary",
            "reason": reason,
        },
        "rule": _rule(),
        "schema_version": SCHEMA_VERSION,
        "selected_prefill_tokens": None,
        "status": "refused",
        "summary_sha256": summary_sha256,
    }


def _write_record(path: Path, record: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw: bytes | None = None
    reason: str | None = None
    try:
        raw = args.summary.read_bytes()
    except OSError:
        reason = "input_unreadable"
    summary_sha256 = hashlib.sha256(raw).hexdigest() if raw is not None else None
    record: dict[str, Any]
    if raw is None:
        record = _malformed_record(summary_sha256=None, reason=str(reason))
    else:
        try:
            summary = json.loads(raw, object_pairs_hook=_strict_object_pairs)
            record = select(summary, summary_sha256=summary_sha256)
        except (UnicodeDecodeError, json.JSONDecodeError):
            reason = "invalid_json"
            record = _malformed_record(
                summary_sha256=summary_sha256, reason=reason
            )
        except SummaryError as exc:
            reason = str(exc)
            record = _malformed_record(
                summary_sha256=summary_sha256, reason=reason
            )
    try:
        _write_record(args.output, record)
    except OSError as exc:
        print(f"selection output unwritable: {exc}", file=sys.stderr)
        return 2
    return 2 if reason is not None else 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
