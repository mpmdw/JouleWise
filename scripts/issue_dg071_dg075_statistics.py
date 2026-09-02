#!/usr/bin/env python3
"""Issue the ratified DG-071 and DG-075 sampling-record statistics.

The 2026-08-31 magistrate ratification defines the two statistics as follows:

"DG-071 (record interval width): median with IQR of
`interval_end_s − interval_start_s` over every retained record of the cited
`p2015-df-ph-decode-abs-r03` bundle, with the exact file path and SHA-256
recorded by the fill's ratification artifact."

"DG-075 (record spacing): median with IQR of differences between
consecutive unique `timestamp_s` values over the same bundle."

Ruling R-167-1 fixes the previously open conventions: ``statistics.median``;
linear-interpolated Q1 and Q3; IQR = Q3 - Q1; unrounded seconds as the issued
values of record; six-decimal millisecond renderings; distinct timestamps
sorted ascending before differencing; duplicates collapsed; and every CSV row
included without filtering.  The command refuses before writing either output
if the exact retained file path, SHA-256, schema, or record ordering differs
from its pins.

Usage::

    /Users/edr/code/JouleWise/.venv/bin/python \
        scripts/issue_dg071_dg075_statistics.py \
        --out /path/to/dg071-dg075-statistics.json

The companion Markdown rendering is written beside the JSON with a ``.md``
suffix.  Both files are byte-deterministic for a fixed checkout and input.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any


PINNED_BUNDLE_PATH = Path(
    "/Users/edr/code/JouleWise/runs_window_a10_20260725/"
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
REGISTRY_ROW_IDS = ("DG-071", "DG-075")
SCHEMA_VERSION = "joulewise.paper.dg071-dg075-statistics.v1"
SCRIPT_REPOSITORY_PATH = "scripts/issue_dg071_dg075_statistics.py"
MS_DECIMALS = 6
REFUSAL_EXIT_CODE = 2


class IssuanceRefused(RuntimeError):
    """A stable refusal reason and a human-readable explanation."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _absolute_without_symlink_resolution(path: Path) -> Path:
    """Normalize ``.``/``..`` without allowing a symlink to evade the path pin."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


# Copied verbatim from scripts/paper_excursion_decomposition.py:246-259 under
# Ruling R-167-1; paper producers remain standalone rather than importing it.
def _quantile(ordered: list[float], fraction: float) -> float:
    """Linear-interpolated quantile of an already-sorted sample."""

    if not ordered:
        raise ValueError("empty sample")
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight


def _describe(values: list[float]) -> dict[str, Any]:
    """Return the ruled median/IQR statistic in seconds and rendered ms."""

    ordered = sorted(values)
    if not ordered:
        raise IssuanceRefused("statistic_sample_empty", "no values to summarize")
    median_s = statistics.median(ordered)
    q1_s = _quantile(ordered, 0.25)
    q3_s = _quantile(ordered, 0.75)
    iqr_s = q3_s - q1_s
    return {
        "sample_count": len(ordered),
        "q1_s": q1_s,
        "median_s": median_s,
        "q3_s": q3_s,
        "iqr_s": iqr_s,
        "q1_ms": round(q1_s * 1000.0, MS_DECIMALS),
        "median_ms": round(median_s * 1000.0, MS_DECIMALS),
        "q3_ms": round(q3_s * 1000.0, MS_DECIMALS),
        "iqr_ms": round(iqr_s * 1000.0, MS_DECIMALS),
    }


def _read_records(raw: bytes) -> tuple[list[float], list[float]]:
    """Parse all retained rows, enforcing the pinned schema and file ordering."""

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

    widths: list[float] = []
    timestamps: list[float] = []
    previous_timestamp: float | None = None
    for row_number, row in enumerate(reader, start=2):
        if None in row:
            raise IssuanceRefused(
                "record_schema_mismatch",
                f"row {row_number} has fields beyond the pinned schema",
            )

        parsed: dict[str, float] = {}
        for field in REQUIRED_STATISTIC_FIELDS:
            value = row.get(field)
            if value is None or value.strip() == "":
                raise IssuanceRefused(
                    "record_field_missing", f"row {row_number} is missing {field}"
                )
            try:
                parsed[field] = float(value)
            except ValueError as exc:
                raise IssuanceRefused(
                    "record_field_invalid",
                    f"row {row_number} field {field} is not a float: {value!r}",
                ) from exc
            if not math.isfinite(parsed[field]):
                raise IssuanceRefused(
                    "record_field_invalid",
                    f"row {row_number} field {field} is not finite: {value!r}",
                )

        timestamp = parsed["timestamp_s"]
        if previous_timestamp is not None and timestamp < previous_timestamp:
            raise IssuanceRefused(
                "timestamps_non_monotone",
                f"row {row_number} timestamp_s {timestamp!r} follows "
                f"{previous_timestamp!r}",
            )
        previous_timestamp = timestamp

        width = parsed["interval_end_s"] - parsed["interval_start_s"]
        if width <= 0.0:
            raise IssuanceRefused(
                "record_interval_not_positive",
                f"row {row_number} has interval width {width!r}",
            )
        widths.append(width)
        timestamps.append(timestamp)

    if not widths:
        raise IssuanceRefused("record_set_empty", "power_trace.csv has no records")
    return widths, timestamps


def _git_commit(repository_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IssuanceRefused(
            "git_commit_unavailable", f"could not read repository HEAD: {exc}"
        ) from exc
    commit = completed.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise IssuanceRefused(
            "git_commit_invalid", f"git rev-parse returned {commit!r}"
        )
    return commit


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

    widths, timestamps = _read_records(raw)
    unique_timestamps = sorted(set(timestamps))
    if len(unique_timestamps) < 2:
        raise IssuanceRefused(
            "insufficient_unique_timestamps",
            "at least two distinct timestamp_s values are required",
        )
    spacings = [
        later - earlier
        for earlier, later in zip(unique_timestamps, unique_timestamps[1:])
    ]

    script_raw = script_path.read_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_row_ids": list(REGISTRY_ROW_IDS),
        "input_bundle": {
            "path": str(actual_path),
            "sha256": observed_sha256,
            "record_schema": list(EXPECTED_RECORD_SCHEMA),
        },
        "record_count": len(widths),
        "distinct_timestamp_count": len(unique_timestamps),
        "duplicate_timestamp_count": len(timestamps) - len(unique_timestamps),
        "statistics": {
            "DG-071": {
                "statistic": "interval_end_s - interval_start_s",
                **_describe(widths),
            },
            "DG-075": {
                "statistic": "consecutive unique timestamp_s difference",
                **_describe(spacings),
            },
        },
        "producer": {
            "script_path": SCRIPT_REPOSITORY_PATH,
            "script_sha256": _sha256(script_raw),
            "git_commit": _git_commit(repository_root),
        },
    }


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
        f"- Retained record count: {payload['record_count']}",
        f"- Distinct timestamp count: {payload['distinct_timestamp_count']}",
        f"- Duplicate timestamps dropped: {payload['duplicate_timestamp_count']}",
        f"- Producer: `{producer['script_path']}`",
        f"- Producer SHA-256: `{producer['script_sha256']}`",
        f"- Git commit: `{producer['git_commit']}`",
        "",
        "Milliseconds are renderings rounded to six decimals. The unrounded ",
        "seconds below are the issued values of record.",
        "",
        "| Registry row | Sample count | Median (ms) | IQR (ms) |",
        "|---|---:|---:|---:|",
        f"| DG-071 | {dg071['sample_count']} | {dg071['median_ms']:.6f} | "
        f"{dg071['iqr_ms']:.6f} |",
        f"| DG-075 | {dg075['sample_count']} | {dg075['median_ms']:.6f} | "
        f"{dg075['iqr_ms']:.6f} |",
        "",
        "| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |",
        "|---|---:|---:|---:|---:|",
        f"| DG-071 | {dg071['q1_s']!r} | {dg071['median_s']!r} | "
        f"{dg071['q3_s']!r} | {dg071['iqr_s']!r} |",
        f"| DG-075 | {dg075['q1_s']!r} | {dg075['median_s']!r} | "
        f"{dg075['q3_s']!r} | {dg075['iqr_s']!r} |",
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
            f"{row_id} median_ms={row['median_ms']:.6f} "
            f"iqr_ms={row['iqr_ms']:.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
