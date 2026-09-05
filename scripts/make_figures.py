#!/usr/bin/env python3
"""RPT-001 vertical-slice analysis pipeline (spec: docs/specs/c027/rpt-001_report_vertical_slice.md).

Authenticates the six pinned strict-valid legacy bundles, but does not extract
or reproduce their measurements.  The pre-repair time-anchor defect voided
every energy result from this corpus, so the v2 route emits explicit void
placeholders instead:

- ``analysis/rpt001-v2/dataset.csv``            (void placeholder)
- ``analysis/rpt001-v2/aggregates.json``        (void placeholder)
- ``figures/rpt001-v2/F1_legacy_l1_instrument_results.svg``
- ``analysis/rpt001-v2/tables/T1_legacy_l1_results.{csv,md}``
- ``analysis/rpt001-v2/tables/S1_legacy_stack_identity.{csv,md}``
- ``analysis/rpt001-v2/claims_index.jsonl``     (retained row, status voided)
- ``analysis/rpt001-v2/artifact_manifest.json``

Deterministic: sorted keys, fixed precision, no timestamps, no absolute
paths in outputs. Read-only over ``runs/``.

Usage:
    python3 scripts/make_figures.py --runs-root /Users/edr/code/JouleWise/runs \
        --input-manifest analysis/rpt001-v2/input_manifest.json
    python3 scripts/make_figures.py --runs-root /Users/edr/code/JouleWise/runs \
        --bootstrap-input-manifest
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from joulewise.aggregate import aggregate_experiment  # noqa: E402
from joulewise.bundle_read import BundleReader  # noqa: E402
from joulewise.cli import validate_bundle  # noqa: E402
from joulewise.publication_privacy import (  # noqa: E402
    TREE_IDENTITY_ALGORITHM,
    TREE_IDENTITY_VERSION,
    tree_identity_descriptor,
    tree_sha256,
)

SCHEMA_INPUT = "joulewise.report_analysis_input.v1"
ARTIFACT_VERSION = "rpt001-v2"
EVIDENCE_CLASS = "legacy_l1_manual_review_pre_2m"
VOID_STATUS = "voided"
VOID_LABEL = "VOIDED historical evidence — permanently ineligible for claim use"
LEGACY_LABEL = VOID_LABEL
VOID_DISPOSITION = (
    "Pre-repair time attribution is invalid; no measurement from this corpus "
    "is eligible for claim use or reproduced by the rpt001-v2 route."
)
VOID_REASON_CODES = ["pre_repair_time_anchor_invalid"]
VOID_CLAIM_TEXT = (
    "The retained RPT-001 legacy L1 history row is voided because its pre-repair "
    "time anchor invalidates physical energy attribution; it is permanently "
    "ineligible for claim use and carries no energy result."
)
BOUNDARY_LABEL = "Apple SoC CPU + GPU + ANE package power"

EXPERIMENTS = ["example-mac-mlx-local", "example-mac-mlx-qwen35-122b-512t"]
STACK_IDS = {
    "example-mac-mlx-local": "LEGACY-M3MAX-QWEN25-1P5B-MLX",
    "example-mac-mlx-qwen35-122b-512t": "LEGACY-M3MAX-QWEN35-122B-A10B-MLX",
}

ANALYSIS_DIR = Path("analysis") / ARTIFACT_VERSION
FIGURES_DIR = Path("figures") / ARTIFACT_VERSION
FIGURE_NAME = "F1_legacy_l1_instrument_results.svg"

DATASET_COLUMNS = [
    "run_id", "experiment_id", "repetition", "bundle_tree_sha256",
    "config_sha256", "strict_validation", "evidence_class", "stack_id",
    "hardware_target_id", "hardware_model", "model_name", "model_family",
    "model_revision", "quantization_name", "quantization_bits",
    "quantization_group_size", "workload_name", "prompt_text_sha256",
    "runtime_output_tokens", "token_count_source", "runtime_stop_reason",
    "output_policy", "gross_energy_j", "energy_request_j",
    "energy_output_token_j", "ttft_s", "throughput_tokens_s",
    "cooldown_cap_hit", "boundary_label", "telemetry_backend", "bundle_path",
]

UNKNOWN = "unknown"
LEGACY_V1_TREE_IDENTITY_ALGORITHM = "sha256"
LEGACY_V1_TREE_IDENTITY_VERSION = "rpt001.bundle-tree.tab-v1"
VOID_CSV_COLUMNS = ["artifact_version", "artifact_id", "status", "disposition"]


def fail(msg: str) -> None:
    print(f"make_figures: ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bundle_tree_entries(bundle_dir: Path) -> list[dict[str, object]]:
    """Inventory a bundle tree using the publication packer's entry shape."""

    entries: list[dict[str, object]] = []
    for path in sorted(bundle_dir.rglob("*")):
        rel = path.relative_to(bundle_dir).as_posix()
        if path.is_symlink():
            fail(f"bundle tree contains a symlink: {bundle_dir}/{rel}")
        if path.is_dir():
            continue
        if not path.is_file():
            fail(f"bundle tree contains a non-file artifact: {bundle_dir}/{rel}")
        entries.append({
            "path": rel,
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })
    return entries


def bundle_tree_sha256(bundle_dir: Path) -> str:
    """Canonical NUL-delimited bundle identity used by publication packs."""

    return tree_sha256(bundle_tree_entries(bundle_dir))


def legacy_v1_bundle_tree_sha256(bundle_dir: Path) -> str:
    """Sealed rpt001-v1 tab-delimited path/hash/size identity algorithm."""

    lines = []
    for p in sorted(bundle_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(bundle_dir).as_posix()
            lines.append(f"{rel}\t{sha256_file(p)}\t{p.stat().st_size}\n")
    return hashlib.sha256("".join(sorted(lines)).encode("utf-8")).hexdigest()


def validate_bundle_tree_identity_descriptor(value: object) -> None:
    if value != tree_identity_descriptor():
        fail(
            "bundle_tree_identity must identify the canonical publication fold "
            f"({TREE_IDENTITY_ALGORITHM}, {TREE_IDENTITY_VERSION}), got {value!r}"
        )


def dump_json(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def num(value) -> str:
    """Full-precision deterministic formatter for CSV numerics."""
    if value is None:
        return ""
    return repr(float(value))


def build_input_manifest(runs_root: Path) -> dict:
    experiments = []
    tree = {}
    for exp_id in EXPERIMENTS:
        mpath = runs_root / "experiments" / f"{exp_id}.json"
        if not mpath.is_file():
            fail(f"experiment manifest missing: {mpath}")
        manifest = json.loads(mpath.read_text())
        members = manifest["members"]
        experiments.append({
            "experiment_id": exp_id,
            "manifest_path": f"runs/experiments/{exp_id}.json",
            "manifest_sha256": sha256_file(mpath),
            "members": members,
        })
        for member in members:
            tree[member] = bundle_tree_sha256(runs_root / member)
    return {
        "schema": SCHEMA_INPUT,
        "artifact_version": ARTIFACT_VERSION,
        "bundle_tree_identity": tree_identity_descriptor(),
        "evidence_class": EVIDENCE_CLASS,
        "runs_root": "runs",
        "experiments": experiments,
        "bundle_tree_sha256": tree,
        "analysis_manifest_ref": None,
        "claim_verdict_ref": {
            "schema": "joulewise.claim_verdict.v1",
            "path": None,
            "sha256": None,
        },
    }


def gate_inputs(runs_root: Path, input_manifest: dict) -> dict:
    """Spec §3.2 input gate. Returns {experiment_id: manifest_dict}."""
    if input_manifest.get("schema") != SCHEMA_INPUT:
        fail(f"unknown input manifest schema: {input_manifest.get('schema')!r}")
    if input_manifest.get("artifact_version") != ARTIFACT_VERSION:
        fail(
            "input manifest artifact_version must be "
            f"{ARTIFACT_VERSION!r}, got {input_manifest.get('artifact_version')!r}"
        )
    validate_bundle_tree_identity_descriptor(input_manifest.get("bundle_tree_identity"))
    exps = input_manifest.get("experiments", [])
    if len(exps) != 2:
        fail("input manifest must pin exactly two experiments")
    all_members: list[str] = []
    manifests: dict[str, dict] = {}
    for entry in exps:
        exp_id = entry["experiment_id"]
        mpath = runs_root / "experiments" / f"{exp_id}.json"
        actual = sha256_file(mpath)
        if actual != entry["manifest_sha256"]:
            fail(f"experiment manifest hash mismatch for {exp_id}")
        manifest = json.loads(mpath.read_text())
        if manifest["members"] != entry["members"]:
            fail(f"membership/order mismatch for {exp_id}")
        manifests[exp_id] = manifest
        all_members.extend(entry["members"])
    if len(all_members) != 6 or len(set(all_members)) != 6:
        fail("input manifest must pin six unique member bundles")
    pinned_tree = input_manifest["bundle_tree_sha256"]
    if sorted(pinned_tree) != sorted(all_members):
        fail("bundle_tree_sha256 keys do not match pinned members")
    for member in all_members:
        bundle_dir = runs_root / member
        actual = bundle_tree_sha256(bundle_dir)
        if actual != pinned_tree[member]:
            fail(f"bundle tree hash mismatch for {member}")
        problems = validate_bundle(bundle_dir, strict=True)
        if problems:
            fail(f"strict validation failed for {member}: {problems}")
        summary = BundleReader(bundle_dir).raw_summary()
        if not isinstance(summary, dict) or summary.get("status") != "succeeded":
            fail(f"bundle {member} is not status=succeeded")
    return manifests


def cooldown_cap_members(manifest: dict) -> set[str]:
    """Members whose preceding cooldown hit the cap (from experiment manifest)."""
    members = manifest["members"]
    flagged: set[str] = set()
    for entry in manifest.get("cooldown", []):
        if entry.get("result") == "cap_hit":
            after = entry.get("after_member")
            if after in members:
                idx = members.index(after)
                if idx + 1 < len(members):
                    flagged.add(members[idx + 1])
    return flagged


def realized_output_tokens(bundle_dir: Path, reader: BundleReader) -> tuple[int, str]:
    """Count emitted output tokens from the immutable token artifact.

    The configured output budget is deliberately not read here. The token
    records are authoritative for the realized count; metadata and the
    explicit decode-completion event are independent consistency checks when
    present. Equality with a configured cap never supplies a stop reason.
    """
    token_path = bundle_dir / "outputs" / "tokens.jsonl"
    try:
        lines = token_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        fail(f"realized token artifact unavailable for {bundle_dir.name}: {exc}")
    records = []
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid outputs/tokens.jsonl line {line_no} for {bundle_dir.name}: {exc}")
        if not isinstance(record, dict) or record.get("index") != len(records):
            fail(
                f"non-contiguous outputs/tokens.jsonl index at line {line_no} "
                f"for {bundle_dir.name}"
            )
        records.append(record)
    if not records:
        fail(f"realized token artifact is empty for {bundle_dir.name}")

    count = len(records)
    metadata = reader.raw_metadata() or {}
    observed = (metadata.get("workload_observed") or {}).get("output_token_count")
    if observed is not None and observed != count:
        fail(
            f"realized token count mismatch for {bundle_dir.name}: "
            f"outputs/tokens.jsonl={count}, metadata={observed!r}"
        )
    decode_counts = [
        event.get("metadata", {}).get("emitted_tokens")
        for event in reader.events()
        if event.get("event_type") == "phase_end"
        and event.get("phase") == "decode"
        and event.get("metadata", {}).get("emitted_tokens") is not None
    ]
    if decode_counts and (len(decode_counts) != 1 or decode_counts[0] != count):
        fail(
            f"realized token count mismatch for {bundle_dir.name}: "
            f"outputs/tokens.jsonl={count}, decode events={decode_counts!r}"
        )
    return count, "outputs/tokens.jsonl"


def extract_rows(runs_root: Path, manifests: dict, tree: dict) -> list[dict]:
    rows = []
    for exp_id in sorted(manifests):
        manifest = manifests[exp_id]
        cap_members = cooldown_cap_members(manifest)
        for member in manifest["members"]:
            bundle_dir = runs_root / member
            reader = BundleReader(bundle_dir)
            config = reader.raw_config() or {}
            metadata = reader.raw_metadata() or {}
            summary = reader.raw_summary() or {}
            model = config.get("model", {})
            quant = config.get("quantization", {})
            workload = config.get("workload_profile", {}) or {}
            quality = summary.get("measurement_quality", {}) or {}
            device = metadata.get("device", {}) or {}
            prompt = workload.get("prompt_text")
            rep = member.rsplit("__r", 1)[-1]
            output_tokens, output_tokens_source = realized_output_tokens(bundle_dir, reader)
            rows.append({
                "run_id": member,
                "experiment_id": exp_id,
                "repetition": rep,
                "bundle_tree_sha256": tree[member],
                "config_sha256": metadata.get("config_sha256", UNKNOWN),
                "strict_validation": "passed (strict; legacy allowlist)",
                "evidence_class": EVIDENCE_CLASS,
                "stack_id": STACK_IDS[exp_id],
                "hardware_target_id": config.get("hardware_target", {}).get("id", UNKNOWN),
                "hardware_model": device.get("hw_model", UNKNOWN),
                "model_name": model.get("name", UNKNOWN),
                "model_family": model.get("family", UNKNOWN),
                "model_revision": model.get("revision", UNKNOWN),
                "quantization_name": quant.get("name") or UNKNOWN,
                "quantization_bits": quant.get("bits") if quant.get("bits") is not None else UNKNOWN,
                "quantization_group_size": quant.get("group_size") if quant.get("group_size") is not None else UNKNOWN,
                "workload_name": workload.get("name", UNKNOWN),
                "prompt_text_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest() if isinstance(prompt, str) else UNKNOWN,
                "runtime_output_tokens": output_tokens,
                "token_count_source": output_tokens_source,
                "runtime_stop_reason": UNKNOWN,
                "output_policy": UNKNOWN,
                "gross_energy_j": num(summary.get("gross_energy_j")),
                "energy_request_j": num(summary.get("energy_request_j")),
                # Legacy bundles lack complete stop-reason/output-policy
                # provenance, so v2 omits rather than overstates this companion.
                "energy_output_token_j": "",
                "ttft_s": num(summary.get("ttft_s")),
                "throughput_tokens_s": num(summary.get("throughput_tokens_s")),
                "cooldown_cap_hit": "true" if member in cap_members else "false",
                "boundary_label": device.get("boundary", BOUNDARY_LABEL),
                "telemetry_backend": quality.get("telemetry_source", UNKNOWN),
                "bundle_path": f"runs/{member}",
            })
    rows.sort(key=lambda r: (r["experiment_id"], int(r["repetition"])))
    return rows


def write_dataset(rows: list[dict], out: Path) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=DATASET_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    out.write_text(buf.getvalue(), encoding="utf-8")


def stats3(values: list[float]) -> dict:
    import statistics
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "sd": statistics.stdev(values) if len(values) >= 2 else None,
        "min": min(values),
        "max": max(values),
    }


def per_stack_metrics(rows: list[dict]) -> dict:
    """{stack_id: {metric: stats3 + points}} in lexical stack order."""
    out: dict[str, dict] = {}
    for stack_id in sorted(STACK_IDS.values()):
        stack_rows = [r for r in rows if r["stack_id"] == stack_id]
        metrics = {}
        for metric in ("gross_energy_j", "energy_request_j", "ttft_s",
                       "throughput_tokens_s"):
            pts = [float(r[metric]) for r in stack_rows]
            metrics[metric] = {**stats3(pts), "points": pts}
        out[stack_id] = {
            "metrics": metrics,
            "model_name": stack_rows[0]["model_name"],
            "rows": stack_rows,
        }
    return out


# ---------------------------------------------------------------- figure ----

def _ymap(v: float, vmax: float, y0: float, y1: float) -> float:
    return y1 - (v / vmax) * (y1 - y0)


def _fmt(v: float) -> str:
    return f"{v:.2f}"


def render_figure(stacks: dict) -> str:
    """Request-energy-only deterministic SVG (stdlib, no matplotlib)."""
    W, H = 940, 560
    ax0, ax1, ay0, ay1 = 70.0, 910.0, 70.0, 400.0
    stack_ids = sorted(stacks)
    offsets = [-8.0, 0.0, 8.0]

    a_max = max(s["metrics"]["gross_energy_j"]["max"] for s in stacks.values()) * 1.1

    e = []
    e.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="sans-serif" font-size="12">')
    e.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')
    e.append(f'<text x="{ax0}" y="30" font-size="16" font-weight="bold">'
             f'Per-request energy by exact stack — {LEGACY_LABEL}</text>')
    e.append(f'<text x="{ax0}" y="48" font-size="12" fill="#444">'
             'Points: three retained sequential repetitions; marker: arithmetic mean; '
             'whisker: observed min–max range (not a confidence interval).</text>')

    def axis(x0, x1, title, vmax, unit, nticks=5):
        e.append(f'<line x1="{_fmt(x0)}" y1="{_fmt(ay1)}" x2="{_fmt(x1)}" y2="{_fmt(ay1)}" stroke="black"/>')
        e.append(f'<line x1="{_fmt(x0)}" y1="{_fmt(ay0)}" x2="{_fmt(x0)}" y2="{_fmt(ay1)}" stroke="black"/>')
        for i in range(nticks + 1):
            v = vmax * i / nticks
            y = _ymap(v, vmax, ay0, ay1)
            e.append(f'<line x1="{_fmt(x0 - 4)}" y1="{_fmt(y)}" x2="{_fmt(x0)}" y2="{_fmt(y)}" stroke="black"/>')
            e.append(f'<text x="{_fmt(x0 - 8)}" y="{_fmt(y + 4)}" text-anchor="end">{v:.0f}</text>')
        e.append(f'<text x="{_fmt((x0 + x1) / 2)}" y="{_fmt(ay0 - 8)}" text-anchor="middle" font-weight="bold">{title}</text>')
        e.append(f'<text x="{_fmt(x0 - 44)}" y="{_fmt((ay0 + ay1) / 2)}" text-anchor="middle" '
                 f'transform="rotate(-90 {_fmt(x0 - 44)} {_fmt((ay0 + ay1) / 2)})">{unit}</text>')

    axis(ax0, ax1, "Request energy (primary)", a_max, "J per request")

    def series(cx, values, mean, vmin, vmax_v, axis_max, filled):
        ymin = _ymap(vmin, axis_max, ay0, ay1)
        ymax = _ymap(vmax_v, axis_max, ay0, ay1)
        ymean = _ymap(mean, axis_max, ay0, ay1)
        e.append(f'<line x1="{_fmt(cx)}" y1="{_fmt(ymin)}" x2="{_fmt(cx)}" y2="{_fmt(ymax)}" stroke="#555" stroke-width="1.5"/>')
        e.append(f'<line x1="{_fmt(cx - 12)}" y1="{_fmt(ymean)}" x2="{_fmt(cx + 12)}" y2="{_fmt(ymean)}" stroke="black" stroke-width="2.5"/>')
        for off, v in zip(offsets, values):
            y = _ymap(v, axis_max, ay0, ay1)
            fill = "#1f6f8b" if filled else "white"
            e.append(f'<circle cx="{_fmt(cx + off)}" cy="{_fmt(y)}" r="4" fill="{fill}" stroke="#1f6f8b" stroke-width="1.5"/>')

    span = ax1 - ax0
    for i, stack_id in enumerate(stack_ids):
        m = stacks[stack_id]["metrics"]
        xc = ax0 + span * (i + 0.5) / len(stack_ids)
        label_y = ay1 + 16
        e.append(f'<text x="{_fmt(xc)}" y="{_fmt(label_y)}" text-anchor="middle" font-size="11">{stack_id}</text>')
        e.append(f'<text x="{_fmt(xc)}" y="{_fmt(label_y + 14)}" text-anchor="middle" font-size="10" fill="#444">n=3</text>')
        s_idle = m["energy_request_j"]
        s_gross = m["gross_energy_j"]
        series(xc - 25, s_idle["points"], s_idle["mean"], s_idle["min"], s_idle["max"], a_max, True)
        series(xc + 25, s_gross["points"], s_gross["mean"], s_gross["min"], s_gross["max"], a_max, False)

    # Legend (Panel A bases named).
    e.append(f'<circle cx="{_fmt(ax0 + 10)}" cy="450" r="4" fill="#1f6f8b" stroke="#1f6f8b"/>')
    e.append(f'<text x="{_fmt(ax0 + 20)}" y="454">idle-subtracted energy_request_j (primary basis)</text>')
    e.append(f'<circle cx="{_fmt(ax0 + 330)}" cy="450" r="4" fill="white" stroke="#1f6f8b"/>')
    e.append(f'<text x="{_fmt(ax0 + 340)}" y="454">gross gross_energy_j (context basis)</text>')

    # Mandatory footers (D-058 / spec §4.3).
    e.append(f'<text x="{_fmt(ax0)}" y="490" font-size="11">{LEGACY_LABEL} · n=3 per exact stack · Apple SoC CPU+GPU+ANE package-power boundary ·</text>')
    e.append(f'<text x="{_fmt(ax0)}" y="506" font-size="11">descriptive stack-specific observations; no cross-stack efficiency or scaling claim · full identities: Table S1</text>')
    e.append(f'<text x="{_fmt(ax0)}" y="530" font-size="11" fill="#444">Per-output-token companion omitted: legacy bundles lack complete runtime stop-reason and</text>')
    e.append(f'<text x="{_fmt(ax0)}" y="544" font-size="11" fill="#444">output-policy provenance; no stop reason is inferred from equality with the configured cap.</text>')
    e.append("</svg>")
    return "\n".join(e) + "\n"


# ---------------------------------------------------------------- tables ----

T1_COLUMNS = [
    "stack_id", "model_display_name", "n",
    "gross_j_request_mean", "gross_j_request_sd", "gross_j_request_min_max",
    "idlesub_j_request_mean", "idlesub_j_request_sd", "idlesub_j_request_min_max",
    "throughput_tokens_s_mean", "ttft_ms_mean",
    "token_companion_status", "boundary", "evidence_label", "quality_waiver",
]


def t1_rows(stacks: dict, waivers: dict) -> list[dict]:
    rows = []
    for stack_id in sorted(stacks):
        m = stacks[stack_id]["metrics"]
        g, i = m["gross_energy_j"], m["energy_request_j"]
        rows.append({
            "stack_id": stack_id,
            "model_display_name": stacks[stack_id]["model_name"],
            "n": 3,
            "gross_j_request_mean": f"{g['mean']:.1f}",
            "gross_j_request_sd": f"{g['sd']:.1f}",
            "gross_j_request_min_max": f"{g['min']:.1f}–{g['max']:.1f}",
            "idlesub_j_request_mean": f"{i['mean']:.1f}",
            "idlesub_j_request_sd": f"{i['sd']:.1f}",
            "idlesub_j_request_min_max": f"{i['min']:.1f}–{i['max']:.1f}",
            "throughput_tokens_s_mean": f"{m['throughput_tokens_s']['mean']:.1f}",
            "ttft_ms_mean": f"{m['ttft_s']['mean'] * 1000:.1f}",
            "token_companion_status": "omitted: runtime stop reason and output policy unavailable",
            "boundary": BOUNDARY_LABEL,
            "evidence_label": LEGACY_LABEL,
            "quality_waiver": waivers.get(stack_id, "none"),
        })
    return rows


def markdown_table(columns: list[str], rows: list[dict]) -> str:
    lines = ["| " + " | ".join(columns) + " |",
             "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[c]) for c in columns) + " |")
    return "\n".join(lines) + "\n"


def csv_table(columns: list[str], rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


S1_FIELDS = [
    "hardware_unit", "os_version", "runtime_version", "kernel_library",
    "model_artifact_hash", "quantization", "tokenizer_identity",
    "sampler_output_policy", "batching_concurrency_policy",
    "measurement_boundary", "telemetry_backend",
]

UNKNOWN_LEGACY = "unknown (legacy bundle)"
NOT_CAPTURED = "unavailable (not captured)"


def s1_rows(stacks: dict) -> list[dict]:
    rows = []
    for stack_id in sorted(stacks):
        r0 = stacks[stack_id]["rows"][0]
        q = f"{r0['quantization_name']} (bits={r0['quantization_bits']}, group_size="
        q += (str(r0["quantization_group_size"]) if r0["quantization_group_size"] != UNKNOWN
              else UNKNOWN_LEGACY) + ")"
        rows.append({
            "stack_id": stack_id,
            "hardware_unit": f"{r0['hardware_target_id']} ({r0['hardware_model']}); physical unit id: {UNKNOWN_LEGACY}",
            "os_version": "macOS (kern.osversion 24G720 recorded in bundle metadata)",
            "runtime_version": "MLX 0.31.2 / mlx-lm 0.31.3 (from adapter prepare metadata)",
            "kernel_library": UNKNOWN_LEGACY,
            "model_artifact_hash": f"{NOT_CAPTURED}; repo revision {r0['model_revision']} (revision, not a byte hash)",
            "quantization": q,
            "tokenizer_identity": f"{UNKNOWN_LEGACY}; prompt source/BOS handling: {NOT_CAPTURED}",
            "sampler_output_policy": UNKNOWN_LEGACY,
            "batching_concurrency_policy": UNKNOWN_LEGACY,
            "measurement_boundary": BOUNDARY_LABEL,
            "telemetry_backend": r0["telemetry_backend"],
        })
    return rows


# ------------------------------------------------------------ claims row ----

def voided_claim_row() -> dict:
    """Retain the historical index identity without reproducing voided results."""

    return {
        "schema": "joulewise.claims_index.v1",
        "claim_id": "CLM-RPT001-LEGACY-L1-001",
        "claim_text": VOID_CLAIM_TEXT,
        "claim_level": "L1",
        "claim_role": "secondary",
        "status": VOID_STATUS,
        "evidence_class": EVIDENCE_CLASS,
        "legacy_label": VOID_LABEL,
        "figure_ids": ["F1_legacy_l1_instrument_results"],
        "table_ids": ["T1_legacy_l1_results", "S1_legacy_stack_identity"],
        "analysis_function": "emit_rpt001_void_placeholders",
        "dataset_filter": "none (legacy corpus voided)",
        "bundle_ids": [f"{e}__r{i}" for e in EXPERIMENTS for i in (1, 2, 3)],
        "manifest_ids": EXPERIMENTS,
        "stack_ids": sorted(STACK_IDS.values()),
        "boundary_labels": [BOUNDARY_LABEL],
        "metrics": [],
        "strict_validation": {
            "result": "not_applicable_voided",
            "mode": "none",
            "legacy_allowlist": False,
        },
        "quality_waivers": [],
        "floor_ref": {"status": VOID_STATUS, "artifact": None, "row_id": None},
        "analysis_manifest_ref": None,
        "verdict_ref": {
            "schema": "joulewise.claim_verdict.v1",
            "status": VOID_STATUS,
            "artifact": None, "sha256": None, "row_id": None,
            "contrast_id": None, "reason_codes": VOID_REASON_CODES,
        },
        "claim_ceiling_reason_codes": [
            *VOID_REASON_CODES,
            "legacy_pre_2m",
        ],
        "artifact_manifest": "analysis/rpt001-v1/artifact_manifest.json",
    }


def render_void_csv(artifact_id: str) -> str:
    return csv_table(VOID_CSV_COLUMNS, [{
        "artifact_version": ARTIFACT_VERSION,
        "artifact_id": artifact_id,
        "status": VOID_STATUS,
        "disposition": VOID_DISPOSITION,
    }])


def render_void_markdown(title: str, artifact_id: str) -> str:
    return (
        f"{title}\n\n"
        f"Status: **{VOID_LABEL}**.\n\n"
        f"{VOID_DISPOSITION}\n\n"
        + markdown_table(VOID_CSV_COLUMNS, [{
            "artifact_version": ARTIFACT_VERSION,
            "artifact_id": artifact_id,
            "status": VOID_STATUS,
            "disposition": VOID_DISPOSITION,
        }])
    )


def render_void_figure() -> str:
    """Deterministic SVG placeholder with no measurement geometry or values."""

    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 260" '
        'font-family="sans-serif" font-size="16">',
        '<rect x="0" y="0" width="940" height="260" fill="white"/>',
        '<rect x="32" y="32" width="876" height="196" rx="12" fill="#fff4f2" '
        'stroke="#a33" stroke-width="2"/>',
        '<text x="64" y="88" font-size="24" font-weight="bold">VOIDED historical evidence</text>',
        '<text x="64" y="126">Permanently ineligible for claim use.</text>',
        '<text x="64" y="160">Pre-repair time attribution is invalid.</text>',
        '<text x="64" y="194">No measurement values are rendered.</text>',
        '</svg>',
        '',
    ])


def voided_aggregates() -> dict:
    return {
        "schema": "joulewise.report_analysis_aggregates.v1",
        "artifact_version": ARTIFACT_VERSION,
        "evidence_class": EVIDENCE_CLASS,
        "status": VOID_STATUS,
        "disposition": VOID_DISPOSITION,
        "void_reason_codes": VOID_REASON_CODES,
        "experiments": {},
    }


# ---------------------------------------------------------------- main ------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-root", default="runs", type=Path)
    ap.add_argument("--input-manifest",
                    default=Path("analysis/rpt001-v2/input_manifest.json"), type=Path)
    ap.add_argument("--bootstrap-input-manifest", action="store_true",
                    help="DANGEROUS bootstrap: re-baseline evidence hashes in the pinned input manifest.")
    ap.add_argument("--offline", action="store_true",
                    help="Explicitly prohibit network-dependent steps (this pipeline is fully offline).")
    ap.add_argument("--out-root", default=Path("."), type=Path,
                    help="Repository root to write analysis/figures outputs under.")
    args = ap.parse_args()

    runs_root = args.runs_root
    out_root = args.out_root
    if args.bootstrap_input_manifest:
        print("WARNING: --bootstrap-input-manifest RE-BASELINES EVIDENCE; review every changed hash.",
              file=sys.stderr)
        manifest = build_input_manifest(runs_root)
        target = out_root / args.input_manifest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dump_json(manifest), encoding="utf-8", newline="\n")
        print(f"make_figures: wrote {args.input_manifest}")

    # Build the complete publication in a sibling staging tree. No destination
    # artifact is touched until every input gate, render, and hash succeeds.
    stage_base = out_root.resolve()
    stage_base.mkdir(parents=True, exist_ok=True)
    stage_tmp = Path(tempfile.mkdtemp(prefix=".rpt001-stage-", dir=stage_base))
    analysis_dir = stage_tmp / ANALYSIS_DIR
    tables_dir = analysis_dir / "tables"
    figures_dir = stage_tmp / FIGURES_DIR
    for d in (analysis_dir, tables_dir, figures_dir):
        d.mkdir(parents=True, exist_ok=True)

    input_manifest = json.loads((out_root / args.input_manifest).read_text())
    gate_inputs(runs_root, input_manifest)
    tree = input_manifest["bundle_tree_sha256"]

    # The corpus is authenticated above, but its measurements are never read
    # into a regenerated publication artifact.  Every v2 surface carries the
    # same explicit void disposition.
    (analysis_dir / "dataset.csv").write_text(
        render_void_csv("dataset"), encoding="utf-8", newline="\n")
    (analysis_dir / "aggregates.json").write_text(
        dump_json(voided_aggregates()), encoding="utf-8", newline="\n")
    (figures_dir / FIGURE_NAME).write_text(
        render_void_figure(), encoding="utf-8", newline="\n")

    for stem, title in (
        ("T1_legacy_l1_results", "Table T1: voided legacy result placeholder"),
        ("S1_legacy_stack_identity", "Table S1: voided legacy identity placeholder"),
    ):
        (tables_dir / f"{stem}.csv").write_text(
            render_void_csv(stem), encoding="utf-8", newline="\n")
        (tables_dir / f"{stem}.md").write_text(
            render_void_markdown(title, stem), encoding="utf-8", newline="\n")

    row = voided_claim_row()
    (analysis_dir / "claims_index.jsonl").write_text(
        json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    outputs = [
        ANALYSIS_DIR / "dataset.csv",
        ANALYSIS_DIR / "aggregates.json",
        ANALYSIS_DIR / "claims_index.jsonl",
        ANALYSIS_DIR / "tables" / "T1_legacy_l1_results.csv",
        ANALYSIS_DIR / "tables" / "T1_legacy_l1_results.md",
        ANALYSIS_DIR / "tables" / "S1_legacy_stack_identity.csv",
        ANALYSIS_DIR / "tables" / "S1_legacy_stack_identity.md",
        FIGURES_DIR / FIGURE_NAME,
    ]
    manifest_out = {
        "schema": "joulewise.report_artifact_manifest.v1",
        "artifact_version": ARTIFACT_VERSION,
        "build_mode": "voided-placeholder",
        "status": VOID_STATUS,
        "void_reason_codes": VOID_REASON_CODES,
        "bundle_tree_identity": tree_identity_descriptor(),
        "input_manifest_sha256": hashlib.sha256((out_root / args.input_manifest).read_bytes()).hexdigest(),
        "experiment_manifest_sha256": {
            e["experiment_id"]: e["manifest_sha256"]
            for e in input_manifest["experiments"]
        },
        "bundle_tree_sha256": tree,
        "generator_sha256": {
            "scripts/make_figures.py": sha256_file(Path(__file__)),
        },
        "outputs": {str(p): sha256_file(stage_tmp / p) for p in sorted(outputs, key=str)},
    }
    (analysis_dir / "artifact_manifest.json").write_text(dump_json(manifest_out), encoding="utf-8", newline="\n")
    try:
        for rel in outputs + [ANALYSIS_DIR / "artifact_manifest.json"]:
            source = stage_tmp / rel
            target = out_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, target)
    finally:
        shutil.rmtree(stage_tmp, ignore_errors=True)
    print("make_figures: OK — authenticated inputs; emitted void placeholders and voided claim row")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
