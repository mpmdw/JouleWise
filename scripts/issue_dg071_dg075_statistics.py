#!/usr/bin/env python3
"""Issue the ratified DG-071 and DG-075 sampling-record statistics.

The governing convention is the ``Addendum 2026-09-02`` at the end of
``docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md``.

A sampler record is one contiguous group of CSV rows — consecutive rows in
file order — that share one `timestamp_s` literal. A literal is the character
string exactly as written in the file, before any numeric conversion; two
literals are equal only when their characters are identical. Every group must
contain exactly one row for each of `ane_power`, `cpu_power` and `gpu_power`,
and the three rows' `interval_start_s` and `interval_end_s` literals must be
identical; a timestamp literal that reappears after another group has begun is
refused. DG-071 uses one interval width, `interval_end_s − interval_start_s`,
per sampler record.

The timestamp and endpoint literals are parsed directly as exact decimals.
Widths, spacings, quantiles and IQR never pass through binary floating point.

For the n values sorted ascending, the quantile at probability p uses the
exact 0-based position h = (n−1)·p and exact linear interpolation between the
two neighbouring order statistics — the sorted values at positions ⌊h⌋ and
⌊h⌋+1 (Hyndman–Fan type 7; numpy `linear` and R type 7 are cross-references).
The median is the p = 0.5 quantile, which is the mean of the two middle values
for even n. IQR is Q3 − Q1, computed exactly before rendering.

The exact seconds in the second table are the values of record: the
authoritative numbers, which nothing downstream re-derives. The millisecond
columns are renderings of them — value × 1000, rounded to four decimal places
with round-half-even, meaning a value exactly halfway between two four-decimal
neighbours goes to the one whose last digit is even — and are never re-used as
inputs. Because rounding is applied after subtraction, a rendered IQR can
differ from the difference of the rendered quartiles by one unit in the last
place.

A float64 replication (numpy `linear`, R type 7) is guaranteed to agree only
to three decimals because a float64 at 1.78e9 s has spacing 2.4e-7 s, coarser
than the file's 1e-7 s literals; the digits characterise the retained bytes,
not the sampler's physical timing resolution. Worked example: median 120.9186
ms exact vs 120.9185 ms float64.

Tiling. The records tile when each record's interval ends exactly at its own
timestamp (`interval_end_s` literal identical to `timestamp_s` literal) and
begins where the previous record ended (`interval_start_s` of record k within
0.000001 s of `timestamp_s` of record k−1); the producer refuses otherwise.
The tiling gap at a boundary is |interval_start_s(k) − timestamp_s(k−1)| in
exact decimal seconds; the header reports the largest gap and the number of
boundaries whose gap is not zero. The writer formatted the interval endpoints
and the timestamp from two separately rounded binary floats, so the seventh
decimal can differ. This is the endpoint convention referred to next.

DG-075 is the DG-071 distribution minus the first record: its consecutive
timestamp differences equal the widths of records 2–n up to the endpoint
convention above, i.e. to within the largest tiling gap.

Usage::

    /Users/edr/code/JouleWise/.venv/bin/python \
        scripts/issue_dg071_dg075_statistics.py \
        --out /path/to/dg071-dg075-statistics.json

The companion Markdown rendering is written beside the JSON with a ``.md``
suffix.  Both files are byte-deterministic for a fixed input and a fixed
producer: the ``git_commit`` they record is the last commit that changed this
script (``git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py``),
not the checkout's HEAD, so re-running the producer from any checkout in which
the script is unchanged since that commit reproduces both files byte for byte.
The script's SHA-256 is recorded beside it and must equal the SHA-256 of the
script as committed there (``git show <producer commit>:<script path>``); an
uncommitted edit to the producer shows as the two hashes differing.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


PINNED_BUNDLE_PATH = Path(
    "/Users/edr/code/JouleWise/runs_window_a10_20260725/"
    "p2015-df-ph-decode-abs-r03/power_trace.csv"
)
PINNED_BUNDLE_REPOSITORY_PATH = (
    "runs_window_a10_20260725/"
    "p2015-df-ph-decode-abs-r03/power_trace.csv"
)
PINNED_BUNDLE_SHA256 = (
    "6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9"
)
EXPECTED_RECORD_SCHEMA = (
    "timestamp_s",
    "power_w",
    "source",
    "rail",
    "interval_start_s",
    "interval_end_s",
)
REQUIRED_STATISTIC_FIELDS = (
    "timestamp_s",
    "interval_start_s",
    "interval_end_s",
)
EXPECTED_RAILS = frozenset(("cpu_power", "gpu_power", "ane_power"))
REGISTRY_ROW_IDS = ("DG-071", "DG-075")
SCHEMA_VERSION = "joulewise.paper.dg071-dg075-statistics.v2"
SCRIPT_REPOSITORY_PATH = "scripts/issue_dg071_dg075_statistics.py"
PROVENANCE_DISCLOSURE = (
    "Provenance. The producer commit is the last commit in the repository's "
    "history that changed the producer script (`git log -1 --format=%H -- "
    f"{SCRIPT_REPOSITORY_PATH}`), not the commit the issuer happened to have "
    "checked out. A committed artifact cannot name the commit that contains "
    "it, so recording the checkout would make byte-exact replay impossible at "
    "exactly the commit a reader checks out; recording the script's last "
    "commit means re-running the producer from any checkout in which the "
    "script is unchanged since that commit reproduces both files byte for "
    "byte. The producer SHA-256 is recorded beside it and must equal the "
    "SHA-256 of the script as committed there (`git show <producer commit>:"
    f"{SCRIPT_REPOSITORY_PATH}`); an uncommitted edit to the producer shows "
    "as the two hashes differing."
)
MS_RENDER_QUANTUM = Decimal("0.0001")
TILING_TOLERANCE_S = Decimal("0.000001")
REFUSAL_EXIT_CODE = 2


class IssuanceRefused(RuntimeError):
    """A stable refusal reason and a human-readable explanation."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason


@dataclass(frozen=True)
class _ParsedRow:
    timestamp_literal: str
    timestamp_s: Decimal
    rail: str
    interval_start_literal: str
    interval_start_s: Decimal
    interval_end_literal: str
    interval_end_s: Decimal


@dataclass(frozen=True)
class SamplerRecord:
    """One validated three-rail sampler record."""

    timestamp_literal: str
    timestamp_s: Decimal
    interval_start_s: Decimal
    interval_end_literal: str
    interval_end_s: Decimal


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _absolute_without_symlink_resolution(path: Path) -> Path:
    """Normalize ``.``/``..`` without allowing a symlink to evade the path pin."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _decimal_string(value: Decimal) -> str:
    """Render an exact Decimal without exponent notation."""

    return format(value, "f")


def _quantile(ordered: list[Decimal], fraction: Decimal) -> Decimal:
    """Hyndman-Fan type-7 quantile of an already-sorted exact sample."""

    if not ordered:
        raise ValueError("empty sample")
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * fraction
    lower_index = int(position)
    if position == Decimal(lower_index):
        return ordered[lower_index]
    upper_index = lower_index + 1
    weight = position - Decimal(lower_index)
    return ordered[lower_index] + weight * (
        ordered[upper_index] - ordered[lower_index]
    )


def _describe(values: list[Decimal]) -> dict[str, Any]:
    """Return exact seconds of record and four-place millisecond renderings."""

    ordered = sorted(values)
    q1_s = _quantile(ordered, Decimal("0.25"))
    median_s = _quantile(ordered, Decimal("0.5"))
    q3_s = _quantile(ordered, Decimal("0.75"))
    iqr_s = q3_s - q1_s

    def render_ms(value: Decimal) -> str:
        rendered = (value * Decimal(1000)).quantize(
            MS_RENDER_QUANTUM, rounding=ROUND_HALF_EVEN
        )
        return _decimal_string(rendered)

    return {
        "sample_count": len(ordered),
        "q1_s": _decimal_string(q1_s),
        "median_s": _decimal_string(median_s),
        "q3_s": _decimal_string(q3_s),
        "iqr_s": _decimal_string(iqr_s),
        "q1_ms": render_ms(q1_s),
        "median_ms": render_ms(median_s),
        "q3_ms": render_ms(q3_s),
        "iqr_ms": render_ms(iqr_s),
    }


def _parse_decimal_literal(
    row: dict[str | None, str | list[str] | None],
    field: str,
    row_number: int,
) -> tuple[str, Decimal]:
    value = row.get(field)
    if not isinstance(value, str) or value.strip() == "":
        raise IssuanceRefused(
            "record_field_missing", f"row {row_number} is missing {field}"
        )
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise IssuanceRefused(
            "record_field_invalid",
            f"row {row_number} field {field} is not a decimal: {value!r}",
        ) from exc
    if not parsed.is_finite():
        raise IssuanceRefused(
            "record_field_invalid",
            f"row {row_number} field {field} is not finite: {value!r}",
        )
    return value, parsed


def _record_from_group(group: list[_ParsedRow]) -> SamplerRecord:
    first = group[0]
    rails = [row.rail for row in group]
    starts = {row.interval_start_literal for row in group}
    ends = {row.interval_end_literal for row in group}
    if (
        len(group) != len(EXPECTED_RAILS)
        or set(rails) != EXPECTED_RAILS
        or len(starts) != 1
        or len(ends) != 1
    ):
        raise IssuanceRefused(
            "record_rail_set_mismatch",
            "timestamp_s literal "
            f"{first.timestamp_literal!r} has rails {rails!r}, "
            f"interval_start_s literals {sorted(starts)!r}, and "
            f"interval_end_s literals {sorted(ends)!r}; expected one row "
            f"per rail {sorted(EXPECTED_RAILS)!r} with identical intervals",
        )
    return SamplerRecord(
        timestamp_literal=first.timestamp_literal,
        timestamp_s=first.timestamp_s,
        interval_start_s=first.interval_start_s,
        interval_end_literal=first.interval_end_literal,
        interval_end_s=first.interval_end_s,
    )


def _read_records(raw: bytes) -> tuple[list[SamplerRecord], int]:
    """Parse rows into contiguous, exact-decimal three-rail records."""

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IssuanceRefused(
            "record_schema_mismatch", f"power_trace.csv is not UTF-8: {exc}"
        ) from exc

    reader = csv.DictReader(text.splitlines())
    if tuple(reader.fieldnames or ()) != EXPECTED_RECORD_SCHEMA:
        raise IssuanceRefused(
            "record_schema_mismatch",
            "expected CSV header "
            f"{EXPECTED_RECORD_SCHEMA!r}, found {tuple(reader.fieldnames or ())!r}",
        )

    groups: list[list[_ParsedRow]] = []
    current_group: list[_ParsedRow] = []
    completed_timestamp_literals: set[str] = set()
    previous_timestamp: Decimal | None = None
    previous_timestamp_literal: str | None = None
    rail_row_count = 0

    for row_number, row in enumerate(reader, start=2):
        if None in row:
            raise IssuanceRefused(
                "record_schema_mismatch",
                f"row {row_number} has fields beyond the pinned schema",
            )

        parsed = {
            field: _parse_decimal_literal(row, field, row_number)
            for field in REQUIRED_STATISTIC_FIELDS
        }
        timestamp_literal, timestamp_s = parsed["timestamp_s"]
        start_literal, interval_start_s = parsed["interval_start_s"]
        end_literal, interval_end_s = parsed["interval_end_s"]

        if (
            current_group
            and timestamp_literal != current_group[0].timestamp_literal
        ):
            completed_literal = current_group[0].timestamp_literal
            completed_timestamp_literals.add(completed_literal)
            groups.append(current_group)
            current_group = []
            if timestamp_literal in completed_timestamp_literals:
                raise IssuanceRefused(
                    "records_not_contiguous",
                    f"row {row_number} returns to timestamp_s literal "
                    f"{timestamp_literal!r} after another record began",
                )

        if previous_timestamp is not None and timestamp_s < previous_timestamp:
            raise IssuanceRefused(
                "timestamps_non_monotone",
                f"row {row_number} timestamp_s {timestamp_literal!r} follows "
                f"{previous_timestamp_literal!r}",
            )
        previous_timestamp = timestamp_s
        previous_timestamp_literal = timestamp_literal

        width = interval_end_s - interval_start_s
        if width <= Decimal(0):
            raise IssuanceRefused(
                "record_interval_not_positive",
                f"row {row_number} has interval width {_decimal_string(width)}",
            )

        rail = row.get("rail")
        current_group.append(
            _ParsedRow(
                timestamp_literal=timestamp_literal,
                timestamp_s=timestamp_s,
                rail=rail if isinstance(rail, str) else "",
                interval_start_literal=start_literal,
                interval_start_s=interval_start_s,
                interval_end_literal=end_literal,
                interval_end_s=interval_end_s,
            )
        )
        rail_row_count += 1

    if current_group:
        groups.append(current_group)
    if not groups:
        raise IssuanceRefused(
            "record_set_empty", "power_trace.csv has no sampler records"
        )
    return [_record_from_group(group) for group in groups], rail_row_count


def _verify_tiling(records: list[SamplerRecord]) -> tuple[Decimal, int]:
    """Verify the exact-end and bounded-start conditions for DG-075."""

    end_mismatches = [
        record.timestamp_literal
        for record in records
        if record.interval_end_literal != record.timestamp_literal
    ]
    gaps = [
        abs(record.interval_start_s - previous.timestamp_s)
        for previous, record in zip(records, records[1:])
    ]
    max_gap = max(gaps, default=Decimal(0))
    if end_mismatches or max_gap > TILING_TOLERANCE_S:
        raise IssuanceRefused(
            "records_do_not_tile",
            f"end/timestamp literal mismatches={len(end_mismatches)}, "
            f"max boundary gap={_decimal_string(max_gap)} s, "
            f"allowed={_decimal_string(TILING_TOLERANCE_S)} s",
        )
    return max_gap, sum(gap != Decimal(0) for gap in gaps)


def _git_commit(repository_root: Path) -> str:
    """Return the last commit that changed the producer script, not HEAD.

    A committed artifact cannot contain the hash of the commit that contains
    it, so recording HEAD would make byte-exact replay impossible at the very
    commit a reader checks out. The last commit touching the script is stable
    across every later commit that leaves the script unchanged.
    """

    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", SCRIPT_REPOSITORY_PATH],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IssuanceRefused(
            "git_commit_unavailable",
            f"could not read the producer's last commit: {exc}",
        ) from exc
    commit = completed.stdout.strip()
    if commit == "":
        raise IssuanceRefused(
            "git_commit_invalid",
            f"{SCRIPT_REPOSITORY_PATH} has no commit in this repository "
            "(the producer script is uncommitted)",
        )
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise IssuanceRefused(
            "git_commit_invalid", f"git log returned {commit!r}"
        )
    return commit


def _method_disclosure(
    *, max_tiling_gap_s: str, nonzero_tiling_boundaries: int, record_count: int
) -> dict[str, str]:
    return {
        "population": (
            "A sampler record is one contiguous group of CSV rows — "
            "consecutive rows in file order — that share one `timestamp_s` "
            "literal. A literal is the character string exactly as written "
            "in the file, before any numeric conversion; two literals are "
            "equal only when their characters are identical. Every group "
            "must contain exactly one row for each of `ane_power`, "
            "`cpu_power` and `gpu_power`, and the three rows' `interval_start_s` "
            "and `interval_end_s` literals must be identical; a timestamp "
            "literal that reappears after another group has begun is refused. "
            "DG-071 uses one interval width, `interval_end_s − "
            "interval_start_s`, per sampler record."
        ),
        "arithmetic": (
            "The timestamp and endpoint literals are parsed directly as exact "
            "decimals. Widths, spacings, quantiles and IQR never pass through "
            "binary floating point."
        ),
        "quantile": (
            "For the n values sorted ascending, the quantile at probability p "
            "uses the exact 0-based position h = (n−1)·p and exact linear "
            "interpolation between the two neighbouring order statistics — "
            "the sorted values at positions ⌊h⌋ and ⌊h⌋+1 (Hyndman–Fan type 7; "
            "numpy `linear` and R type 7 are cross-references)."
        ),
        "median": (
            "The median is the p = 0.5 quantile, which is the mean of the two "
            "middle values for even n."
        ),
        "iqr": (
            "IQR is Q3 − Q1, computed exactly before rendering. Because "
            "rounding is applied after subtraction, a rendered IQR can differ "
            "from the difference of the rendered quartiles by one unit in the "
            "last place."
        ),
        "millisecond_rendering": (
            "The exact seconds in the second table are the values of record: "
            "the authoritative numbers, which nothing downstream re-derives. "
            "The millisecond columns are renderings of them — value × 1000, "
            "rounded to four decimal places with round-half-even, meaning a "
            "value exactly halfway between two four-decimal neighbours goes "
            "to the one whose last digit is even — and are never re-used as "
            "inputs."
        ),
        "float64_replication": (
            "A float64 replication (numpy `linear`, R type 7) is guaranteed "
            "to agree only to three decimals because a float64 at 1.78e9 s "
            "has spacing 2.4e-7 s, coarser than the file's 1e-7 s literals; "
            "the digits characterise the retained bytes, not the sampler's "
            "physical timing resolution. Worked example: median 120.9186 ms "
            "exact vs 120.9185 ms float64."
        ),
        "tiling": (
            "Tiling. The records tile when each record's interval ends exactly "
            "at its own timestamp (`interval_end_s` literal identical to "
            "`timestamp_s` literal) and begins where the previous record ended "
            "(`interval_start_s` of record k within 0.000001 s of `timestamp_s` "
            "of record k−1); the producer refuses otherwise. The tiling gap at "
            "a boundary is |interval_start_s(k) − timestamp_s(k−1)| in exact "
            "decimal seconds; the header reports the largest gap and the "
            "number of boundaries whose gap is not zero. In this bundle "
            f"{nonzero_tiling_boundaries} of {record_count - 1} boundaries have "
            f"a nonzero gap, the largest {max_tiling_gap_s} s: the writer "
            "formatted the interval endpoints and the timestamp from two "
            "separately rounded binary floats, so the seventh decimal can "
            "differ. This is the endpoint convention referred to next."
        ),
        "dg075_dependence": (
            "DG-075 is the DG-071 distribution minus the first record: its "
            "consecutive timestamp differences equal the widths of records "
            "2–n up to the endpoint convention above, i.e. to within the "
            "largest tiling gap."
        ),
        "provenance": PROVENANCE_DISCLOSURE,
    }


def build_payload(
    bundle_path: Path,
    *,
    expected_bundle_path: Path,
    expected_bundle_sha256: str,
    repository_root: Path,
    script_path: Path,
) -> dict[str, Any]:
    """Validate the pinned input and build the deterministic issued payload."""

    actual_path = _absolute_without_symlink_resolution(bundle_path)
    expected_path = _absolute_without_symlink_resolution(expected_bundle_path)
    if actual_path != expected_path:
        raise IssuanceRefused(
            "bundle_path_mismatch",
            f"expected {expected_path}, received {actual_path}",
        )
    if not actual_path.is_file():
        raise IssuanceRefused(
            "bundle_path_unavailable", f"pinned bundle is not a file: {actual_path}"
        )

    raw = actual_path.read_bytes()
    observed_sha256 = _sha256(raw)
    if observed_sha256 != expected_bundle_sha256:
        raise IssuanceRefused(
            "bundle_sha256_mismatch",
            f"expected {expected_bundle_sha256}, observed {observed_sha256}",
        )

    records, rail_row_count = _read_records(raw)
    max_tiling_gap_s, nonzero_tiling_boundaries = _verify_tiling(records)
    if len(records) < 2:
        raise IssuanceRefused(
            "insufficient_unique_timestamps",
            "at least two distinct timestamp_s literals are required",
        )
    widths = [
        record.interval_end_s - record.interval_start_s for record in records
    ]
    ordered_timestamps = sorted(record.timestamp_s for record in records)
    spacings = [
        later - earlier
        for earlier, later in zip(ordered_timestamps, ordered_timestamps[1:])
    ]

    script_raw = script_path.read_bytes()
    max_tiling_gap_text = _decimal_string(max_tiling_gap_s)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "registry_row_ids": list(REGISTRY_ROW_IDS),
        "input_bundle": {
            # The absolute paths above are an execution-time refusal pin only.
            # Custody artifacts use a checkout-independent repository locator.
            "path": PINNED_BUNDLE_REPOSITORY_PATH,
            "sha256": observed_sha256,
            "record_schema": list(EXPECTED_RECORD_SCHEMA),
        },
        "sampler_record_count": len(records),
        "rail_row_count": rail_row_count,
        "rails": sorted(EXPECTED_RAILS),
        "max_tiling_gap_s": max_tiling_gap_text,
        "tiling_gap_nonzero_boundaries": nonzero_tiling_boundaries,
        "statistics": {
            "DG-071": {
                "statistic": "interval_end_s - interval_start_s per sampler record",
                **_describe(widths),
            },
            "DG-075": {
                "statistic": (
                    "consecutive differences of sorted distinct timestamp_s literals"
                ),
                **_describe(spacings),
            },
        },
        "producer": {
            "script_path": SCRIPT_REPOSITORY_PATH,
            "script_sha256": _sha256(script_raw),
            "git_commit": _git_commit(repository_root),
        },
    }
    payload["method"] = _method_disclosure(
        max_tiling_gap_s=payload["max_tiling_gap_s"],
        nonzero_tiling_boundaries=payload["tiling_gap_nonzero_boundaries"],
        record_count=payload["sampler_record_count"],
    )
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    """Render the issued payload without introducing any new calculations."""

    source = payload["input_bundle"]
    producer = payload["producer"]
    dg071 = payload["statistics"]["DG-071"]
    dg075 = payload["statistics"]["DG-075"]
    lines = [
        "# DG-071 / DG-075 issued statistics",
        "",
        f"- Input: `{source['path']}`",
        f"- Input SHA-256: `{source['sha256']}`",
        f"- Sampler records: {payload['sampler_record_count']}",
        f"- Rail rows: {payload['rail_row_count']}",
        f"- Rails: {', '.join(payload['rails'])}",
        f"- Largest tiling gap (s; defined under Method): "
        f"{payload['max_tiling_gap_s']}",
        "- Boundaries with a nonzero tiling gap (see Method): "
        f"{payload['tiling_gap_nonzero_boundaries']}",
        f"- Producer: `{producer['script_path']}`",
        f"- Producer SHA-256: `{producer['script_sha256']}`",
        "- Producer commit (last commit that changed the producer; defined "
        f"under Method): `{producer['git_commit']}`",
        "",
        "## Method",
        "",
        "A sampler record is one contiguous group of CSV rows — consecutive "
        "rows in file order — that share one `timestamp_s` literal. A literal "
        "is the character string exactly as written in the file, before any "
        "numeric conversion; two literals are equal only when their characters "
        "are identical. Every group must contain exactly one row for each of "
        "`ane_power`, `cpu_power` and `gpu_power`, and the three rows' "
        "`interval_start_s` and `interval_end_s` literals must be identical; "
        "a timestamp literal that reappears after another group has begun is "
        "refused. DG-071 uses one interval width, `interval_end_s − "
        "interval_start_s`, per sampler record.",
        "",
        "The timestamp and endpoint literals are parsed directly as exact "
        "decimals. Widths, spacings, quantiles and IQR never pass through "
        "binary floating point.",
        "",
        "For the n values sorted ascending, the quantile at probability p uses "
        "the exact 0-based position h = (n−1)·p and exact linear interpolation "
        "between the two neighbouring order statistics — the sorted values at "
        "positions ⌊h⌋ and ⌊h⌋+1 (Hyndman–Fan type 7; numpy `linear` and R "
        "type 7 are cross-references). The median is the p = 0.5 quantile, "
        "which is the mean of the two middle values for even n. IQR is Q3 − "
        "Q1, computed exactly before rendering.",
        "",
        "The exact seconds in the second table are the values of record: the "
        "authoritative numbers, which nothing downstream re-derives. The "
        "millisecond columns are renderings of them — value × 1000, rounded to "
        "four decimal places with round-half-even, meaning a value exactly "
        "halfway between two four-decimal neighbours goes to the one whose last "
        "digit is even — and are never re-used as inputs. Because rounding is "
        "applied after subtraction, a rendered IQR can differ from the "
        "difference of the rendered quartiles by one unit in the last place.",
        "",
        "A float64 replication (numpy `linear`, R type 7) is guaranteed to "
        "agree only to three decimals because a float64 at 1.78e9 s has spacing "
        "2.4e-7 s, coarser than the file's 1e-7 s literals; the digits "
        "characterise the retained bytes, not the sampler's physical timing "
        "resolution. Worked example: median 120.9186 ms exact vs 120.9185 ms "
        "float64.",
        "",
        "Tiling. The records tile when each record's interval ends exactly at "
        "its own timestamp (`interval_end_s` literal identical to `timestamp_s` "
        "literal) and begins where the previous record ended (`interval_start_s` "
        "of record k within 0.000001 s of `timestamp_s` of record k−1); the "
        "producer refuses otherwise. The tiling gap at a boundary is "
        "|interval_start_s(k) − timestamp_s(k−1)| in exact decimal seconds; the "
        "header reports the largest gap and the number of boundaries whose gap "
        "is not zero. In this bundle "
        f"{payload['tiling_gap_nonzero_boundaries']} of "
        f"{payload['sampler_record_count'] - 1} boundaries have a nonzero gap, "
        f"the largest {payload['max_tiling_gap_s']} s: the writer formatted the "
        "interval endpoints and the timestamp from two separately rounded "
        "binary floats, so the seventh decimal can differ. This is the endpoint "
        "convention referred to next.",
        "",
        "DG-075 is the DG-071 distribution minus the first record: its "
        "consecutive timestamp differences equal the widths of records 2–n "
        "up to the endpoint convention above, i.e. to within the largest tiling "
        "gap.",
        "",
        PROVENANCE_DISCLOSURE,
        "",
        "| Registry row | Sample count | Q1 (ms) | Median (ms) | "
        "Q3 (ms) | IQR (ms) |",
        "|---|---:|---:|---:|---:|---:|",
        f"| DG-071 | {dg071['sample_count']} | {dg071['q1_ms']} | "
        f"{dg071['median_ms']} | {dg071['q3_ms']} | {dg071['iqr_ms']} |",
        f"| DG-075 | {dg075['sample_count']} | {dg075['q1_ms']} | "
        f"{dg075['median_ms']} | {dg075['q3_ms']} | {dg075['iqr_ms']} |",
        "",
        "| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |",
        "|---|---:|---:|---:|---:|",
        f"| DG-071 | {dg071['q1_s']} | {dg071['median_s']} | "
        f"{dg071['q3_s']} | {dg071['iqr_s']} |",
        f"| DG-075 | {dg075['q1_s']} | {dg075['median_s']} | "
        f"{dg075['q3_s']} | {dg075['iqr_s']} |",
        "",
    ]
    return "\n".join(lines)


def issue_artifacts(
    bundle_path: Path,
    out_path: Path,
    *,
    expected_bundle_path: Path,
    expected_bundle_sha256: str,
    repository_root: Path,
    script_path: Path,
) -> dict[str, Any]:
    """Build and write the JSON/Markdown pair after all refusals have passed."""

    if out_path.suffix != ".json":
        raise IssuanceRefused(
            "output_path_invalid", "--out must end in .json for a distinct .md companion"
        )
    payload = build_payload(
        bundle_path,
        expected_bundle_path=expected_bundle_path,
        expected_bundle_sha256=expected_bundle_sha256,
        repository_root=repository_root,
        script_path=script_path,
    )
    json_text = json.dumps(
        payload, indent=2, sort_keys=True, allow_nan=False
    ) + "\n"
    markdown_text = render_markdown(payload)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json_text, encoding="utf-8")
    out_path.with_suffix(".md").write_text(markdown_text, encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle",
        type=Path,
        default=PINNED_BUNDLE_PATH,
        help="exact retained R03P path (defaults to the ratified path pin)",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="checkout used to record the producer git commit",
    )
    parser.add_argument("--out", type=Path, required=True, help="JSON output path")
    args = parser.parse_args(argv)

    try:
        payload = issue_artifacts(
            args.bundle,
            args.out,
            expected_bundle_path=PINNED_BUNDLE_PATH,
            expected_bundle_sha256=PINNED_BUNDLE_SHA256,
            repository_root=args.repository_root,
            script_path=Path(__file__).resolve(),
        )
    except IssuanceRefused as exc:
        print(f"REFUSED {exc.reason}: {exc}", file=sys.stderr)
        print("no output written", file=sys.stderr)
        return REFUSAL_EXIT_CODE

    print(f"wrote {args.out}")
    print(f"wrote {args.out.with_suffix('.md')}")
    for row_id in REGISTRY_ROW_IDS:
        row = payload["statistics"][row_id]
        print(
            f"{row_id} median_ms={row['median_ms']} "
            f"iqr_ms={row['iqr_ms']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
