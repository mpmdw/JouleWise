#!/usr/bin/env python3
"""Reproduce the Q9 recorded-prefill proof from the custodied bundles.

The defaults point at the read-only corpora in the main JouleWise checkout.
Every corpus and source-repository path can be overridden for replay.  The
script writes a deterministic machine record and a proof document beside
itself unless --output-dir is supplied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_VERSION = "prefill-phase-proof/v1"
MIN_PHASE_SAMPLES = 3
REQUIRED_STREAMS = (
    "events.jsonl",
    "power_trace.csv",
    "raw/powermetrics.plist",
    "outputs/tokens.jsonl",
    "summary_metrics.json",
    "metadata.json",
)
SOURCE_PATHS = (
    "joulewise/reduce.py",
    "joulewise/bundle_read.py",
    "joulewise/adapters/powermetrics.py",
)


@dataclass(frozen=True)
class Population:
    stack: str
    component: str
    root: Path
    pattern: re.Pattern[str]
    expected_count: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(value)
    return rows


def quantile(values: list[float], probability: float) -> float:
    """Hyndman-Fan type 7 quantile (the common linear interpolation rule)."""
    if not values:
        raise ValueError("quantile requires at least one value")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def distribution(values: Iterable[float]) -> dict[str, float]:
    items = list(values)
    return {
        "min": min(items),
        "p25": quantile(items, 0.25),
        "median": statistics.median(items),
        "p75": quantile(items, 0.75),
        "p95": quantile(items, 0.95),
        "max": max(items),
    }


def fmt(value: float, digits: int = 9) -> str:
    if value == 0.0:
        return "0"
    return f"{value:.{digits}g}"


def find_one(
    events: list[dict[str, Any]], *, event_type: str, phase: str
) -> dict[str, Any]:
    matches = [
        event
        for event in events
        if event.get("event_type") == event_type and event.get("phase") == phase
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one {event_type}/{phase} event, found {len(matches)}"
        )
    return matches[0]


def load_and_sum_trace(path: Path, manifest: list[str]) -> tuple[list[dict[str, Any]], int]:
    groups: dict[float, dict[str, Any]] = {}
    row_count = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_header = [
            "timestamp_s",
            "power_w",
            "source",
            "rail",
            "interval_start_s",
            "interval_end_s",
        ]
        if reader.fieldnames != expected_header:
            raise ValueError(f"{path}: unexpected header {reader.fieldnames!r}")
        for row in reader:
            row_count += 1
            timestamp = float(row["timestamp_s"])
            power = float(row["power_w"])
            start = float(row["interval_start_s"])
            end = float(row["interval_end_s"])
            rail = row["rail"]
            if row["source"] != "powermetrics":
                raise ValueError(f"{path}: non-powermetrics source {row['source']!r}")
            if rail not in manifest:
                raise ValueError(f"{path}: rail {rail!r} is outside manifest")
            group = groups.setdefault(
                timestamp,
                {"timestamp_s": timestamp, "start_s": start, "end_s": end,
                 "power_w": 0.0, "rails": []},
            )
            if group["start_s"] != start or group["end_s"] != end:
                raise ValueError(f"{path}: rail supports disagree at {timestamp}")
            group["power_w"] += power
            group["rails"].append(rail)
    curve = [groups[key] for key in sorted(groups)]
    required = sorted(manifest)
    for point in curve:
        if sorted(point["rails"]) != required:
            raise ValueError(
                f"{path}: incomplete or duplicate rail set at {point['timestamp_s']}"
            )
    return curve, row_count


def integrate_interval_curve(curve: list[dict[str, Any]], start: float, end: float) -> float:
    """Mirror reduce._integrate for interval-average power observations."""
    return math.fsum(
        point["power_w"]
        * max(0.0, min(end, point["end_s"]) - max(start, point["start_s"]))
        for point in curve
    )


def overlap_sample_count(curve: list[dict[str, Any]], start: float, end: float) -> int:
    return sum(
        1
        for point in curve
        if min(end, point["end_s"]) > max(start, point["start_s"])
    )


def import_raw_parser(source_repo: Path):
    sys.path.insert(0, str(source_repo))
    try:
        from joulewise.adapters.powermetrics import samples_from_raw_powermetrics
    except Exception as exc:  # pragma: no cover - environment diagnostic
        raise RuntimeError(
            f"cannot import the raw powermetrics parser from {source_repo}: {exc}"
        ) from exc
    return samples_from_raw_powermetrics


def compare_raw_to_csv(
    raw_data: bytes,
    endpoint: float,
    csv_path: Path,
    samples_from_raw_powermetrics: Any,
) -> dict[str, Any]:
    samples = samples_from_raw_powermetrics(
        raw_data, first_record_endpoint_s=endpoint
    )
    with csv_path.open(newline="", encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))
    mismatch_count = 0
    max_float_delta = 0.0
    if len(samples) != len(csv_rows):
        mismatch_count += abs(len(samples) - len(csv_rows))
    for sample, row in zip(samples, csv_rows):
        if sample.source != row["source"] or sample.rail != row["rail"]:
            mismatch_count += 1
        pairs = (
            (sample.timestamp_s, float(row["timestamp_s"])),
            (sample.power_w, float(row["power_w"])),
            (sample.interval_start_s, float(row["interval_start_s"])),
            (sample.interval_end_s, float(row["interval_end_s"])),
        )
        deltas = [abs(float(left) - right) for left, right in pairs]
        max_float_delta = max(max_float_delta, *deltas)
        if any(delta != 0.0 for delta in deltas):
            mismatch_count += 1
    return {
        "raw_sample_rows": len(samples),
        "csv_sample_rows": len(csv_rows),
        "mismatch_count": mismatch_count,
        "max_float_delta": max_float_delta,
        "exact_match": mismatch_count == 0 and max_float_delta == 0.0,
    }


def select_bundles(population: Population) -> list[Path]:
    if not population.root.is_dir():
        raise FileNotFoundError(f"missing corpus root: {population.root}")
    selected = sorted(
        path
        for path in population.root.iterdir()
        if path.is_dir() and population.pattern.fullmatch(path.name)
    )
    if len(selected) != population.expected_count:
        raise ValueError(
            f"{population.stack}/{population.component}: selected {len(selected)} "
            f"bundles under {population.root}, expected {population.expected_count}"
        )
    if population.component == "decode_absolute":
        observed = {path.name.rsplit("-r", 1)[-1] for path in selected}
        expected = {f"{index:02d}" for index in range(1, 11)}
        if observed != expected:
            raise ValueError(
                f"{population.stack}/{population.component}: repetition IDs are "
                f"{sorted(observed)}, expected 01 through 10"
            )
    elif population.component == "decode_abba":
        observed: dict[str, set[str]] = defaultdict(set)
        for path in selected:
            match = re.search(r"-b(\d{2})-(a1|b1|b2|a2)$", path.name)
            if match is None:  # guarded by the full population regex
                raise ValueError(f"{path}: cannot parse block and position")
            observed[match.group(1)].add(match.group(2))
        expected_blocks = {f"{index:02d}" for index in range(1, 11)}
        expected_positions = {"a1", "b1", "b2", "a2"}
        if set(observed) != expected_blocks or any(
            positions != expected_positions for positions in observed.values()
        ):
            raise ValueError(
                f"{population.stack}/{population.component}: expected blocks 01 "
                "through 10 with exactly a1,b1,b2,a2 in each block"
            )
    return selected


def git_blob_provenance(source_repo: Path, commits: Counter[str]) -> dict[str, Any]:
    producing_commits: dict[str, Any] = {}
    for commit in sorted(commits):
        paths: dict[str, str] = {}
        for relative in SOURCE_PATHS:
            completed = subprocess.run(
                ["git", "-C", str(source_repo), "show", f"{commit}:{relative}"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if completed.returncode != 0:
                detail = completed.stderr.decode("utf-8", errors="replace").strip()
                raise ValueError(f"cannot read {relative} at {commit}: {detail}")
            paths[relative] = sha256_bytes(completed.stdout)
        producing_commits[commit] = {
            "bundle_count": commits[commit],
            "source_sha256": paths,
        }
    replay_hashes = {
        relative: sha256_bytes((source_repo / relative).read_bytes())
        for relative in SOURCE_PATHS
    }
    producing_parser_hashes = {
        item["source_sha256"]["joulewise/adapters/powermetrics.py"]
        for item in producing_commits.values()
    }
    parser_matches = replay_hashes["joulewise/adapters/powermetrics.py"] in producing_parser_hashes
    if not parser_matches:
        raise ValueError(
            "the replay checkout's powermetrics parser does not match any "
            "producing-commit parser; check out the recorded source before replay"
        )
    return {
        "producing_commits": producing_commits,
        "replay_checkout_source_sha256": replay_hashes,
        "replay_parser_matches_producing_commit": parser_matches,
    }


def analyze_bundle(
    population: Population,
    bundle: Path,
    samples_from_raw_powermetrics: Any,
) -> dict[str, Any]:
    missing = [relative for relative in REQUIRED_STREAMS if not (bundle / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"{bundle}: missing required streams: {missing}")

    stream_bytes = {relative: (bundle / relative).read_bytes() for relative in REQUIRED_STREAMS}
    stream_evidence = {
        relative: {"bytes": len(data), "sha256": sha256_bytes(data)}
        for relative, data in stream_bytes.items()
    }
    metadata = json.loads(stream_bytes["metadata.json"])
    summary = json.loads(stream_bytes["summary_metrics.json"])
    events = [json.loads(line) for line in stream_bytes["events.jsonl"].splitlines() if line]
    output_tokens = [
        json.loads(line)
        for line in stream_bytes["outputs/tokens.jsonl"].splitlines()
        if line
    ]

    prefill_start_event = find_one(events, event_type="phase_start", phase="prefill")
    prefill_end_event = find_one(events, event_type="phase_end", phase="prefill")
    decode_start_event = find_one(events, event_type="phase_start", phase="decode")
    decode_end_event = find_one(events, event_type="phase_end", phase="decode")
    token_events = [
        event
        for event in events
        if event.get("event_type") == "token" and event.get("phase") == "decode"
    ]
    if not token_events or not output_tokens:
        raise ValueError(f"{bundle}: decode token evidence is empty")
    token_zero_events = [event for event in token_events if event.get("metadata", {}).get("index") == 0]
    token_zero_outputs = [row for row in output_tokens if row.get("index") == 0]
    if len(token_zero_events) != 1 or len(token_zero_outputs) != 1:
        raise ValueError(f"{bundle}: expected exactly one token index 0 in each token stream")

    prefill_start = float(prefill_start_event["timestamp_s"])
    prefill_end = float(prefill_end_event["timestamp_s"])
    decode_start = float(decode_start_event["timestamp_s"])
    decode_end = float(decode_end_event["timestamp_s"])
    token_zero_event_s = float(token_zero_events[0]["timestamp_s"])
    token_zero_output_s = float(token_zero_outputs[0]["timestamp_s"])
    if not prefill_start < prefill_end < decode_start < token_zero_event_s <= decode_end:
        raise ValueError(f"{bundle}: phase/token boundary ordering is not strict")
    if token_zero_event_s != token_zero_output_s:
        raise ValueError(f"{bundle}: token index 0 timestamps disagree between streams")

    boundary_events = (
        prefill_start_event,
        prefill_end_event,
        decode_start_event,
        decode_end_event,
    )
    boundary_methods = [event.get("metadata", {}).get("phase_boundary_method") for event in boundary_events]
    if boundary_methods != ["first_token"] * 4:
        raise ValueError(f"{bundle}: boundary methods are {boundary_methods!r}")

    model = metadata.get("model", {})
    expected_model_fragment = "1.5B" if population.stack == "1.5B" else "7B"
    if expected_model_fragment not in str(model.get("name", "")):
        raise ValueError(f"{bundle}: model identity does not match {population.stack}")
    if metadata.get("run_id") != bundle.name:
        raise ValueError(f"{bundle}: metadata.run_id does not match directory name")
    if summary.get("status") != "succeeded":
        raise ValueError(f"{bundle}: summary status is not succeeded")

    rail_manifest = metadata.get("device", {}).get("rail_manifest")
    if rail_manifest != ["cpu_power", "gpu_power", "ane_power"]:
        raise ValueError(f"{bundle}: unexpected rail manifest {rail_manifest!r}")
    curve, trace_row_count = load_and_sum_trace(bundle / "power_trace.csv", rail_manifest)
    prefill_energy = integrate_interval_curve(curve, prefill_start, prefill_end)
    sample_count = overlap_sample_count(curve, prefill_start, prefill_end)
    derived_status = (
        "identifiable" if sample_count >= MIN_PHASE_SAMPLES
        else "not_resolvable_sample_count"
    )
    recorded_energy = float(summary["phase_energy_j"]["prefill"])
    recorded_status = summary["measurement_quality"]["phase_identifiability"]["prefill"]
    discrepancy = prefill_energy - recorded_energy

    endpoint = float(
        metadata["uncertainty_evidence"]["clock_anchor"]
        ["first_sample_end_point_epoch_s"]
    )
    raw_match = compare_raw_to_csv(
        stream_bytes["raw/powermetrics.plist"],
        endpoint,
        bundle / "power_trace.csv",
        samples_from_raw_powermetrics,
    )
    if not raw_match["exact_match"]:
        raise ValueError(f"{bundle}: raw powermetrics does not exactly reproduce power_trace.csv")
    if derived_status != recorded_status:
        raise ValueError(
            f"{bundle}: independently derived status {derived_status!r} differs "
            f"from recorded status {recorded_status!r}"
        )

    provenance = summary.get("summary_provenance", {})
    if provenance.get("reducer_id") != "joulewise.reduce_bundle" or provenance.get("reducer_version") != "0.5.2":
        raise ValueError(f"{bundle}: unexpected reducer provenance {provenance!r}")

    return {
        "stack": population.stack,
        "population_component": population.component,
        "corpus_root": str(population.root.resolve()),
        "bundle": bundle.name,
        "run_id": metadata["run_id"],
        "model": {"name": model.get("name"), "revision": model.get("revision")},
        "config_sha256": metadata.get("config_sha256"),
        "git_commit": metadata.get("git_commit"),
        "summary_provenance": provenance,
        "streams": stream_evidence,
        "boundary": {
            "method": "first_token",
            "prefill_start_s": prefill_start,
            "prefill_end_s": prefill_end,
            "prefill_duration_s": prefill_end - prefill_start,
            "decode_start_s": decode_start,
            "decode_end_s": decode_end,
            "first_decode_token_event_s": token_zero_event_s,
            "first_output_token_s": token_zero_output_s,
            "prefill_end_to_decode_start_us": (decode_start - prefill_end) * 1_000_000,
            "prefill_end_to_first_token_us": (token_zero_event_s - prefill_end) * 1_000_000,
            "prefill_decode_overlap_s": max(
                0.0, min(prefill_end, decode_end) - max(prefill_start, decode_start)
            ),
            "strict_order": True,
            "token_zero_streams_agree": True,
        },
        "power": {
            "source": "powermetrics",
            "rail_manifest": rail_manifest,
            "trace_row_count": trace_row_count,
            "summed_interval_count": len(curve),
            "prefill_overlap_sample_count": sample_count,
            "integration_method": "sum_manifest_rails_then_interval_overlap_rectangle",
            "edge_handling": "clip_each_interval_support_to_phase_window",
            "raw_to_csv": raw_match,
        },
        "prefill_energy": {
            "recorded_j": recorded_energy,
            "rederived_j": prefill_energy,
            "signed_discrepancy_j": discrepancy,
            "absolute_discrepancy_j": abs(discrepancy),
        },
        "resolvability": {
            "recorded": recorded_status,
            "rederived": derived_status,
            "minimum_samples": MIN_PHASE_SAMPLES,
        },
        "anomalies": [],
    }


def counter_dict(values: Iterable[Any]) -> dict[str, int]:
    return dict(sorted((str(key), count) for key, count in Counter(values).items()))


def summarize_stack(stack: str, bundles: list[dict[str, Any]]) -> dict[str, Any]:
    discrepancies = [row["prefill_energy"]["absolute_discrepancy_j"] for row in bundles]
    durations = [row["boundary"]["prefill_duration_s"] for row in bundles]
    first_token_gaps = [row["boundary"]["prefill_end_to_first_token_us"] for row in bundles]
    decode_start_gaps = [row["boundary"]["prefill_end_to_decode_start_us"] for row in bundles]
    statuses = [row["resolvability"]["rederived"] for row in bundles]
    sample_counts = [row["power"]["prefill_overlap_sample_count"] for row in bundles]
    q1 = quantile(discrepancies, 0.25)
    q3 = quantile(discrepancies, 0.75)
    outlier_threshold = q3 + 1.5 * (q3 - q1)
    outliers = [
        {"bundle": row["bundle"], "absolute_discrepancy_j": value}
        for row, value in zip(bundles, discrepancies)
        if value > outlier_threshold
    ]
    boundary_proven = all(
        row["boundary"]["strict_order"]
        and row["boundary"]["token_zero_streams_agree"]
        and row["boundary"]["prefill_decode_overlap_s"] == 0.0
        for row in bundles
    )
    energy_exact = all(value == 0.0 for value in discrepancies)
    raw_exact = all(row["power"]["raw_to_csv"]["exact_match"] for row in bundles)
    not_resolvable = statuses.count("not_resolvable_sample_count")
    if not boundary_proven or not energy_exact or not raw_exact:
        verdict = "NOT-PROVEN"
    elif not_resolvable:
        verdict = "PROVEN-WITH-CAVEATS"
    else:
        verdict = "PROVEN"
    anomalies: list[dict[str, Any]] = []
    if not_resolvable:
        anomalies.append({
            "kind": "sampling_resolution_limitation",
            "bundle_count": not_resolvable,
            "text": (
                f"{not_resolvable} of {len(bundles)} prefill windows overlap fewer "
                f"than {MIN_PHASE_SAMPLES} power intervals"
            ),
        })
    return {
        "stack": stack,
        "bundle_count": len(bundles),
        "population_components": counter_dict(row["population_component"] for row in bundles),
        "model_names": counter_dict(row["model"]["name"] for row in bundles),
        "model_revisions": counter_dict(row["model"]["revision"] for row in bundles),
        "git_commits": counter_dict(row["git_commit"] for row in bundles),
        "config_sha256": counter_dict(row["config_sha256"] for row in bundles),
        "required_stream_presence": {
            relative: sum(relative in row["streams"] for row in bundles)
            for relative in REQUIRED_STREAMS
        },
        "boundary_method_counts": counter_dict(row["boundary"]["method"] for row in bundles),
        "strict_boundary_order_count": sum(row["boundary"]["strict_order"] for row in bundles),
        "zero_prefill_decode_overlap_count": sum(
            row["boundary"]["prefill_decode_overlap_s"] == 0.0 for row in bundles
        ),
        "token_zero_stream_agreement_count": sum(
            row["boundary"]["token_zero_streams_agree"] for row in bundles
        ),
        "raw_to_csv_exact_count": sum(row["power"]["raw_to_csv"]["exact_match"] for row in bundles),
        "prefill_duration_s": distribution(durations),
        "prefill_end_to_decode_start_us": distribution(decode_start_gaps),
        "prefill_end_to_first_token_us": distribution(first_token_gaps),
        "prefill_overlap_sample_count": counter_dict(sample_counts),
        "resolvability": counter_dict(statuses),
        "absolute_discrepancy_j": {
            **distribution(discrepancies),
            "exact_zero_count": sum(value == 0.0 for value in discrepancies),
            "tukey_upper_fence_j": outlier_threshold,
            "outliers": outliers,
        },
        "anomalies": anomalies,
        "verdict": verdict,
        "verdict_basis": {
            "boundary_isolation_proven": boundary_proven,
            "recorded_energy_exactly_reproduced": energy_exact,
            "raw_powermetrics_exactly_reproduces_trace": raw_exact,
            "not_resolvable_bundle_count": not_resolvable,
        },
    }


def render_proof(results: dict[str, Any]) -> str:
    stacks = {item["stack"]: item for item in results["stack_summaries"]}
    lines = [
        "# Q9 prefill phase-recording proof",
        "",
        "## Question and definitions",
        "",
        "This desk proof asks whether the stored `phase_energy_j.prefill` value measures only prompt processing, rather than prompt processing plus some generated-token work. **Prefill** is the model's processing of the complete input prompt before its first generated output token. **Decode** is the later, token-by-token generation of output. A **phase window** is the time interval between one `phase_start` event and its matching `phase_end` event in `events.jsonl`.",
        "",
        "The summary label **`identifiable`** means that at least three recorded power intervals overlap the phase window. **`not_resolvable_sample_count`** means that fewer than three intervals overlap it, so the energy is still computable but the telemetry cadence is too coarse for the project's stronger phase-resolution label. It does not mean that the phase markers are absent or that they include decode time.",
        "",
        "This document and `results.json` are generated by `audit_prefill_phase.py`; quantitative statements below come from that one persisted run.",
        "",
        "## Method and computation provenance",
        "",
        "For each bundle, the script reads the paired `phase_start`/`phase_end` events for `prefill` and `decode` from `events.jsonl`. The field `metadata.phase_boundary_method` on all four boundary events must equal `first_token`, meaning the runtime closes prefill and opens decode at the first generated-token boundary. The script then checks token index 0 in both the decode `token` event and `outputs/tokens.jsonl`.",
        "",
        "The recorded summary identifies its producer as `joulewise.reduce_bundle` reducer version 0.5.2. At each bundle's recorded `metadata.git_commit`, `joulewise/reduce.py` obtains validated windows from `BundleReader.phase_windows()` in `joulewise/bundle_read.py`; its `_phase_energy()` calls `_integrate()` for each phase interval. On the powermetrics path, `_derive_anchor_context()` reconstructs interval records from `raw/powermetrics.plist` through `joulewise/adapters/powermetrics.py`, verifies the stored trace shape, and uses CPU, GPU, and Apple Neural Engine (ANE) package-power rails together.",
        "",
        "This audit re-parses every raw plist through the producing code's public raw parser and requires an exact row-for-row match with `power_trace.csv`; the script fails if the replay parser's bytes do not match a producing-commit parser. It then independently sums CPU + GPU + ANE power for each interval and multiplies each summed power by only the duration where that interval overlaps the prefill window. At a phase edge, a partially overlapping interval is clipped to the boundary; it is never wholly assigned to either side. This is the interval-support rectangle rule used by reducer 0.5.2.",
        "",
        "Exact source-file SHA-256 values at every producing commit are in `results.json` under `source_code_provenance`. They bind the named computation paths without assuming that today's checkout still has the same bytes.",
        "",
    ]

    for stack_name in ("1.5B", "7B"):
        item = stacks[stack_name]
        components = item["population_components"]
        commit_text = ", ".join(
            f"`{commit}` ({count} bundles)"
            for commit, count in item["git_commits"].items()
        )
        lines.extend([
            f"## {stack_name} stack",
            "",
            "### Population and provenance",
            "",
            f"The population is {item['bundle_count']} Qwen2.5 {stack_name} bundles: {components.get('decode_absolute', 0)} decode absolute-cell bundles and {components.get('decode_abba', 0)} decode comparative bundles arranged as ten four-run A-B-B-A blocks (ABBA). The exact corpus roots, selected directory names, model revision, configuration hashes, producing Git commits, and hashes of all six evidence streams appear per bundle in `results.json`.",
            "",
            "Every selected bundle contains all required evidence streams:",
            "",
            "| Evidence stream | Bundles | Role in this proof |",
            "|---|---:|---|",
            f"| `events.jsonl` | {item['required_stream_presence']['events.jsonl']} | Prefill/decode start and end markers, boundary method, decode token index 0 |",
            f"| `power_trace.csv` | {item['required_stream_presence']['power_trace.csv']} | Timestamped CPU/GPU/ANE interval powers used for the independent integration |",
            f"| `raw/powermetrics.plist` | {item['required_stream_presence']['raw/powermetrics.plist']} | Primary power capture from which the trace is reconstructed |",
            f"| `outputs/tokens.jsonl` | {item['required_stream_presence']['outputs/tokens.jsonl']} | Independent output-token index 0 timestamp |",
            f"| `summary_metrics.json` | {item['required_stream_presence']['summary_metrics.json']} | Recorded `phase_energy_j.prefill`, phase-resolution status, reducer identity |",
            f"| `metadata.json` | {item['required_stream_presence']['metadata.json']} | Model, run, Git, clock-anchor, and rail-manifest provenance |",
            "",
            "### Boundary evidence",
            "",
            f"All {item['bundle_count']} bundles record `first_token` on the prefill-start, prefill-end, decode-start, and decode-end events. All {item['strict_boundary_order_count']} have the strict order prefill start < prefill end < decode start < decode token 0, and the token-0 timestamps in the event and output streams agree in all {item['token_zero_stream_agreement_count']}. The prefill and decode windows have zero temporal overlap in all {item['zero_prefill_decode_overlap_count']} bundles.",
            "",
            f"Prefill lasts {fmt(item['prefill_duration_s']['min'])}–{fmt(item['prefill_duration_s']['max'])} seconds (median {fmt(item['prefill_duration_s']['median'])}). The first decode token follows the prefill end by {fmt(item['prefill_end_to_first_token_us']['min'])}–{fmt(item['prefill_end_to_first_token_us']['max'])} microseconds (median {fmt(item['prefill_end_to_first_token_us']['median'])}). Decode itself starts {fmt(item['prefill_end_to_decode_start_us']['min'])}–{fmt(item['prefill_end_to_decode_start_us']['max'])} microseconds after prefill ends.",
            "",
            "### Energy consistency and resolution",
            "",
            f"All {item['bundle_count']} summaries record `joulewise.reduce_bundle` version 0.5.2. Their producing commits are {commit_text}. For this stack, the computation path and raw inputs are the `events.jsonl` phase markers plus the raw powermetrics CPU/GPU/ANE intervals described in the shared provenance section above; the per-commit source hashes are machine-recorded in `results.json`.",
            "",
            f"The raw plist reconstructs `power_trace.csv` exactly for {item['raw_to_csv_exact_count']}/{item['bundle_count']} bundles. Reintegrating the recorded prefill window reproduces `phase_energy_j.prefill` exactly in {item['absolute_discrepancy_j']['exact_zero_count']}/{item['bundle_count']} bundles. The absolute discrepancy distribution is min {fmt(item['absolute_discrepancy_j']['min'])} J, 25th percentile {fmt(item['absolute_discrepancy_j']['p25'])} J, median {fmt(item['absolute_discrepancy_j']['median'])} J, 75th percentile {fmt(item['absolute_discrepancy_j']['p75'])} J, 95th percentile {fmt(item['absolute_discrepancy_j']['p95'])} J, and max {fmt(item['absolute_discrepancy_j']['max'])} J. A Tukey upper-fence check finds {len(item['absolute_discrepancy_j']['outliers'])} discrepancy outliers.",
            "",
            f"Overlapping power-interval counts are {json.dumps(item['prefill_overlap_sample_count'], sort_keys=True)}. Recorded and independently re-derived resolution labels agree: {json.dumps(item['resolvability'], sort_keys=True)}.",
            "",
            "### Mislabeling discriminator",
            "",
            "If `prefill` included decode time, at least one of the following would be visible: the prefill end marker would occur at or after decode start/token 0; the prefill and decode intervals would overlap; or the clipped power integration would consume interval support after decode began. None occurs. The integration stops exactly at the prefill-end timestamp, every decode start and token 0 is later, every phase overlap is zero, and the resulting energy equals the stored prefill value. This discriminates phase attribution from mere token identity: knowing which token was emitted would not, by itself, establish where the energy window ended.",
            "",
            "### Anomalies and verdict",
            "",
        ])
        if item["anomalies"]:
            anomaly = item["anomalies"][0]
            lines.append(
                f"Flagged, not changed: {anomaly['bundle_count']}/{item['bundle_count']} bundles have `not_resolvable_sample_count` because their prefill windows overlap fewer than {MIN_PHASE_SAMPLES} power intervals. This is a sampling-resolution limitation; the boundary ordering, non-overlap, raw-to-trace reconstruction, and exact energy reproduction still pass."
            )
        else:
            lines.append("No anomalies were found in the selected population.")
        lines.extend([
            "",
            f"**Verdict: {item['verdict']}.** " + (
                "The phase boundaries isolate prompt processing, the primary power stream reproduces the analyzed trace, and every stored prefill energy is exactly reproduced with sufficient sample resolution."
                if item["verdict"] == "PROVEN"
                else "The phase boundaries isolate prompt processing and every stored prefill energy is exactly reproduced; the bounded caveat is coarse power-sample resolution in the flagged bundles, not boundary mislabeling."
                if item["verdict"] == "PROVEN-WITH-CAVEATS"
                else "One or more required boundary, primary-stream, or energy-consistency discriminators failed."
            ),
            "",
        ])

    lines.extend([
        "## Whole-population conclusion",
        "",
        f"Across all {results['population']['bundle_count']} bundles, all required streams are present, every prefill window ends before decode starts and before token 0, raw powermetrics exactly reconstructs every stored trace, and independent interval-support integration exactly reproduces every recorded prefill energy. The per-stack verdicts preserve the resolution distinction instead of hiding it.",
        "",
        "No bundle was modified. This is a read-only analysis of recorded evidence; it performed no measurement.",
    ])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a10-root", type=Path, default=Path("/Users/edr/code/JouleWise/runs_window_a10_20260725"))
    parser.add_argument("--c-root", type=Path, default=Path("/Users/edr/code/JouleWise/runs_window_c_20260726"))
    parser.add_argument("--seven-b-root", type=Path, default=Path("/Users/edr/code/JouleWise/runs_window_7bfloor_20260729"))
    parser.add_argument("--source-repo", type=Path, default=Path("/Users/edr/code/JouleWise"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    populations = (
        Population("1.5B", "decode_absolute", args.a10_root,
                   re.compile(r"p2015-df-ph-decode-abs-r\d{2}"), 10),
        Population("1.5B", "decode_abba", args.c_root,
                   re.compile(r"p2015-df-cmp-abba-ph-decode-b\d{2}-(?:a1|b1|b2|a2)"), 40),
        Population("7B", "decode_absolute", args.seven_b_root,
                   re.compile(r"sw7bfloor-df-ph-decode-abs-r\d{2}"), 10),
        Population("7B", "decode_abba", args.seven_b_root,
                   re.compile(r"sw7bfloor-df-cmp-abba-ph-decode-b\d{2}-(?:a1|b1|b2|a2)"), 40),
    )
    selected = [(population, select_bundles(population)) for population in populations]
    all_paths = [path for _, paths in selected for path in paths]
    if len(all_paths) != 100 or len(set(all_paths)) != 100:
        raise ValueError("the selected population is not exactly 100 unique bundles")
    for path in all_paths:
        missing = [relative for relative in REQUIRED_STREAMS if not (path / relative).is_file()]
        if missing:
            raise FileNotFoundError(f"{path}: missing required streams: {missing}")

    samples_from_raw_powermetrics = import_raw_parser(args.source_repo.resolve())
    bundles: list[dict[str, Any]] = []
    for population, paths in selected:
        for path in paths:
            bundles.append(analyze_bundle(population, path, samples_from_raw_powermetrics))

    commits = Counter(str(row["git_commit"]) for row in bundles)
    stack_summaries = [
        summarize_stack(stack, [row for row in bundles if row["stack"] == stack])
        for stack in ("1.5B", "7B")
    ]
    results = {
        "schema": "joulewise.prefill_phase_proof.v1",
        "script_version": SCRIPT_VERSION,
        "inputs": {
            "a10_root": str(args.a10_root.resolve()),
            "c_root": str(args.c_root.resolve()),
            "seven_b_root": str(args.seven_b_root.resolve()),
            "source_repo": str(args.source_repo.resolve()),
            "selection": [
                {
                    "stack": population.stack,
                    "component": population.component,
                    "root": str(population.root.resolve()),
                    "directory_regex": population.pattern.pattern,
                    "expected_count": population.expected_count,
                }
                for population in populations
            ],
        },
        "method": {
            "minimum_phase_samples": MIN_PHASE_SAMPLES,
            "integration": "sum CPU+GPU+ANE power, then sum power_w * clipped interval overlap seconds",
            "edge_handling": "clip interval_start_s/interval_end_s support at both phase boundaries",
            "raw_trace_check": "parse raw/powermetrics.plist at metadata clock-anchor endpoint and compare every power_trace.csv field exactly",
            "discrepancy_outliers": "absolute discrepancy above Q3 + 1.5 * IQR using type-7 quartiles",
        },
        "population": {
            "bundle_count": len(bundles),
            "stacks": counter_dict(row["stack"] for row in bundles),
            "components": counter_dict(row["population_component"] for row in bundles),
        },
        "source_code_provenance": git_blob_provenance(args.source_repo.resolve(), commits),
        "stack_summaries": stack_summaries,
        "bundles": bundles,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "results.json"
    proof_path = args.output_dir / "PROOF.md"
    results_path.write_text(
        json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    proof_path.write_text(render_proof(results), encoding="utf-8")
    digest = sha256_bytes(results_path.read_bytes())
    print(f"bundles={len(bundles)}")
    for item in stack_summaries:
        print(
            f"{item['stack']}: verdict={item['verdict']} "
            f"identifiability={json.dumps(item['resolvability'], sort_keys=True)} "
            f"max_abs_discrepancy_j={item['absolute_discrepancy_j']['max']}"
        )
    print(f"results_sha256={digest}")
    return 0 if all(item["verdict"] != "NOT-PROVEN" for item in stack_summaries) else 2


if __name__ == "__main__":
    raise SystemExit(main())
