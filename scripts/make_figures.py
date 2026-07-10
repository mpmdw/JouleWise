#!/usr/bin/env python3
"""RPT-001 vertical-slice analysis pipeline (spec: docs/specs/c027/rpt-001_report_vertical_slice.md).

Reads the six pinned strict-valid legacy bundles through the existing shared
read layer (``joulewise.bundle_read.BundleReader`` +
``joulewise.aggregate.aggregate_experiment``) and emits:

- ``analysis/rpt001-v1/dataset.csv``            (one row per bundle)
- ``analysis/rpt001-v1/aggregates.json``        (aggregate_experiment output)
- ``figures/rpt001-v1/F1_legacy_l1_instrument_results.svg``
- ``analysis/rpt001-v1/tables/T1_legacy_l1_results.{csv,md}``
- ``analysis/rpt001-v1/tables/S1_legacy_stack_identity.{csv,md}``
- ``analysis/rpt001-v1/claims_index.jsonl``     (one canonical claims row)
- ``analysis/rpt001-v1/artifact_manifest.json``

Deterministic: sorted keys, fixed precision, no timestamps, no absolute
paths in outputs. Read-only over ``runs/``.

Usage:
    python3 scripts/make_figures.py --runs-root /Users/edr/code/JouleWise/runs \
        --input-manifest analysis/rpt001-v1/input_manifest.json
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

SCHEMA_INPUT = "joulewise.report_analysis_input.v1"
ARTIFACT_VERSION = "rpt001-v1"
EVIDENCE_CLASS = "legacy_l1_manual_review_pre_2m"
LEGACY_LABEL = "legacy L1 (manual review; pre-2M)"
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


def fail(msg: str) -> None:
    print(f"make_figures: ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bundle_tree_sha256(bundle_dir: Path) -> str:
    """SHA-256 of the canonical sorted list of relpath, byte sha256, size."""
    lines = []
    for p in sorted(bundle_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(bundle_dir).as_posix()
            lines.append(f"{rel}\t{sha256_file(p)}\t{p.stat().st_size}\n")
    return hashlib.sha256("".join(sorted(lines)).encode("utf-8")).hexdigest()


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


def extract_rows(runs_root: Path, manifests: dict, tree: dict) -> list[dict]:
    rows = []
    for exp_id in sorted(manifests):
        manifest = manifests[exp_id]
        cap_members = cooldown_cap_members(manifest)
        for member in manifest["members"]:
            reader = BundleReader(runs_root / member)
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
                "runtime_output_tokens": workload.get("output_tokens", UNKNOWN),
                "token_count_source": quality.get("token_count_source", UNKNOWN),
                "runtime_stop_reason": UNKNOWN,
                "output_policy": UNKNOWN,
                "gross_energy_j": num(summary.get("gross_energy_j")),
                "energy_request_j": num(summary.get("energy_request_j")),
                "energy_output_token_j": num(summary.get("energy_output_token_j")),
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
        for metric in ("gross_energy_j", "energy_request_j", "energy_output_token_j",
                       "ttft_s", "throughput_tokens_s"):
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
    """Two-panel deterministic SVG per spec §4.2/§4.3 (stdlib, no matplotlib)."""
    W, H = 940, 560
    # Panel A (request energy) >= 60% of plot width.
    ax0, ax1, ay0, ay1 = 70.0, 590.0, 70.0, 400.0
    bx0, bx1 = 660.0, 910.0
    stack_ids = sorted(stacks)
    offsets = [-8.0, 0.0, 8.0]

    a_max = max(s["metrics"]["gross_energy_j"]["max"] for s in stacks.values()) * 1.1
    b_max = max(s["metrics"]["energy_output_token_j"]["max"] for s in stacks.values()) * 1000.0 * 1.1

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

    axis(ax0, ax1, "Panel A: request energy (primary)", a_max, "J per request")
    axis(bx0, bx1, "Panel B: per-token companion", b_max, "mJ per runtime-observed output token")

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

    for panel, (x0, x1, axis_max) in {"A": (ax0, ax1, a_max), "B": (bx0, bx1, b_max)}.items():
        span = x1 - x0
        for i, stack_id in enumerate(stack_ids):
            m = stacks[stack_id]["metrics"]
            xc = x0 + span * (i + 0.5) / len(stack_ids)
            label_y = ay1 + 16
            # Panel B is narrow; use the unambiguous suffix (full IDs in Panel A, footer, S1).
            label = stack_id if panel == "A" else stack_id.replace("LEGACY-M3MAX-", "")
            e.append(f'<text x="{_fmt(xc)}" y="{_fmt(label_y)}" text-anchor="middle" font-size="11">{label}</text>')
            e.append(f'<text x="{_fmt(xc)}" y="{_fmt(label_y + 14)}" text-anchor="middle" font-size="10" fill="#444">n=3</text>')
            if panel == "A":
                s_idle = m["energy_request_j"]
                s_gross = m["gross_energy_j"]
                series(xc - 25, s_idle["points"], s_idle["mean"], s_idle["min"], s_idle["max"], axis_max, True)
                series(xc + 25, s_gross["points"], s_gross["mean"], s_gross["min"], s_gross["max"], axis_max, False)
            else:
                s_tok = m["energy_output_token_j"]
                pts = [v * 1000.0 for v in s_tok["points"]]
                series(xc, pts, s_tok["mean"] * 1000.0, s_tok["min"] * 1000.0, s_tok["max"] * 1000.0, axis_max, True)

    # Legend (Panel A bases named).
    e.append(f'<circle cx="{_fmt(ax0 + 10)}" cy="450" r="4" fill="#1f6f8b" stroke="#1f6f8b"/>')
    e.append(f'<text x="{_fmt(ax0 + 20)}" y="454">idle-subtracted energy_request_j (primary basis)</text>')
    e.append(f'<circle cx="{_fmt(ax0 + 330)}" cy="450" r="4" fill="white" stroke="#1f6f8b"/>')
    e.append(f'<text x="{_fmt(ax0 + 340)}" y="454">gross gross_energy_j (context basis)</text>')
    e.append(f'<text x="{_fmt(bx0)}" y="454" font-size="11" fill="#444">idle-subtracted basis; mJ/runtime-observed output token</text>')

    # Mandatory footers (D-058 / spec §4.3).
    e.append(f'<text x="{_fmt(ax0)}" y="490" font-size="11">{LEGACY_LABEL} · n=3 per exact stack · Apple SoC CPU+GPU+ANE package-power boundary ·</text>')
    e.append(f'<text x="{_fmt(ax0)}" y="506" font-size="11">descriptive stack-specific observations; no cross-stack efficiency or scaling claim · full identities: Table S1</text>')
    e.append(f'<text x="{_fmt(ax0)}" y="530" font-size="11" fill="#444">Output-token values use runtime-observed counts. Tokenizer identity was not captured in these</text>')
    e.append(f'<text x="{_fmt(ax0)}" y="544" font-size="11" fill="#444">legacy bundles; values are tokenizer-scoped descriptors, not comparable work units.</text>')
    e.append("</svg>")
    return "\n".join(e) + "\n"


# ---------------------------------------------------------------- tables ----

T1_COLUMNS = [
    "stack_id", "model_display_name", "n",
    "gross_j_request_mean", "gross_j_request_sd", "gross_j_request_min_max",
    "idlesub_j_request_mean", "idlesub_j_request_sd", "idlesub_j_request_min_max",
    "idlesub_mj_output_token_mean", "idlesub_mj_output_token_sd", "idlesub_mj_output_token_min_max",
    "throughput_tokens_s_mean", "ttft_ms_mean",
    "token_denominator_scope", "boundary", "evidence_label", "quality_waiver",
]


def t1_rows(stacks: dict, waivers: dict) -> list[dict]:
    rows = []
    for stack_id in sorted(stacks):
        m = stacks[stack_id]["metrics"]
        g, i, t = m["gross_energy_j"], m["energy_request_j"], m["energy_output_token_j"]
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
            "idlesub_mj_output_token_mean": f"{t['mean'] * 1000:.1f}",
            "idlesub_mj_output_token_sd": f"{t['sd'] * 1000:.1f}",
            "idlesub_mj_output_token_min_max": f"{t['min'] * 1000:.1f}–{t['max'] * 1000:.1f}",
            "throughput_tokens_s_mean": f"{m['throughput_tokens_s']['mean']:.1f}",
            "ttft_ms_mean": f"{m['ttft_s']['mean'] * 1000:.1f}",
            "token_denominator_scope": "runtime-observed output tokens; tokenizer identity unknown (legacy bundle)",
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

def claims_row(stacks: dict, mean_by_stack: dict) -> dict:
    small, large = sorted(stacks)
    return {
        "schema": "joulewise.claims_index.v1",
        "claim_id": "CLM-RPT001-LEGACY-L1-001",
        "claim_text": (
            "Across three strict-valid legacy runs per exact stack, mean "
            f"idle-subtracted request energy was {mean_by_stack[small]!r} J for stack "
            f"{small} and {mean_by_stack[large]!r} J for stack {large}; these are "
            "separate stack-specific L1 observations, not a cross-stack comparison, "
            "efficiency ranking, or scaling claim."
        ),
        "claim_level": "L1",
        "claim_role": "secondary",
        "status": "supported",
        "evidence_class": EVIDENCE_CLASS,
        "legacy_label": LEGACY_LABEL,
        "figure_ids": ["F1_legacy_l1_instrument_results"],
        "table_ids": ["T1_legacy_l1_results", "S1_legacy_stack_identity"],
        "analysis_function": "make_f1_legacy_l1_instrument_results",
        "dataset_filter": "artifact_version == rpt001-v1",
        "bundle_ids": [f"{e}__r{i}" for e in EXPERIMENTS for i in (1, 2, 3)],
        "manifest_ids": EXPERIMENTS,
        "stack_ids": sorted(STACK_IDS.values()),
        "boundary_labels": [BOUNDARY_LABEL],
        "metrics": [
            {"metric": "gross_energy_j", "basis": "gross request",
             "unit": "J/request", "denominator_provenance": "request"},
            {"metric": "energy_request_j", "basis": "idle-subtracted request",
             "unit": "J/request", "denominator_provenance": "request"},
            {"metric": "energy_output_token_j",
             "basis": "idle-subtracted output-token companion",
             "unit": "J/runtime-observed output token",
             "denominator_provenance": "runtime_observed",
             "tokenizer_identity": UNKNOWN_LEGACY},
        ],
        "strict_validation": {"result": "passed", "mode": "strict", "legacy_allowlist": True},
        "quality_waivers": [
            {"scope": "example-mac-mlx-local__r2",
             "reason": "cooldown cap hit was recorded; the point is retained and visibly reported under the legacy manual-review carve-out"},
            {"scope": "token-normalized companion metrics",
             "reason": "legacy bundles predate captured tokenizer identity, sampler/output policy, and stop-reason provenance; values remain explicitly tokenizer-unknown L1 descriptors and support no ranking"},
        ],
        "floor_ref": {"status": "not_applicable_legacy_l1", "artifact": None, "row_id": None},
        "analysis_manifest_ref": None,
        "verdict_ref": {
            "schema": "joulewise.claim_verdict.v1",
            "status": "not_applicable_l1",
            "artifact": None, "sha256": None, "row_id": None,
            "contrast_id": None, "reason_codes": [],
        },
        "claim_ceiling_reason_codes": [
            "legacy_pre_2m", "n3_below_l2_protocol",
            "no_interleaved_cross_condition_design", "no_detection_floor_artifact",
            "no_contrast_verdict", "tokenizer_identity_unavailable",
        ],
        "artifact_manifest": "analysis/rpt001-v1/artifact_manifest.json",
    }


# ---------------------------------------------------------------- main ------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-root", default="runs", type=Path)
    ap.add_argument("--input-manifest",
                    default=Path("analysis/rpt001-v1/input_manifest.json"), type=Path)
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
    manifests = gate_inputs(runs_root, input_manifest)
    tree = input_manifest["bundle_tree_sha256"]

    rows = extract_rows(runs_root, manifests, tree)
    write_dataset(rows, analysis_dir / "dataset.csv")

    aggregates = {
        exp_id: aggregate_experiment(runs_root, manifests[exp_id])
        for exp_id in sorted(manifests)
    }
    (analysis_dir / "aggregates.json").write_text(dump_json({
        "schema": "joulewise.report_analysis_aggregates.v1",
        "artifact_version": ARTIFACT_VERSION,
        "evidence_class": EVIDENCE_CLASS,
        "note": "aggregate_experiment() output preserved verbatim; the RPT-001 "
                "figure deliberately renders raw points + mean + min-max, not "
                "the Student-t interval (spec §4.2).",
        "experiments": aggregates,
    }), encoding="utf-8", newline="\n")

    stacks = per_stack_metrics(rows)

    # Cross-check: figure/table stats must agree with aggregate_experiment().
    for exp_id, stack_id in STACK_IDS.items():
        agg_mean = aggregates[exp_id]["metrics"]["energy_request_j"]["mean"]
        local_mean = stacks[stack_id]["metrics"]["energy_request_j"]["mean"]
        if abs(agg_mean - local_mean) > 1e-12:
            fail(f"aggregate/table mean mismatch for {stack_id}")

    figures_path = figures_dir / FIGURE_NAME
    figures_path.write_text(render_figure(stacks), encoding="utf-8", newline="\n")

    waivers = {
        STACK_IDS["example-mac-mlx-local"]:
            "cooldown cap hit recorded before r2; point retained and reported (legacy manual-review carve-out)",
    }
    t1 = t1_rows(stacks, waivers)
    (tables_dir / "T1_legacy_l1_results.csv").write_text(csv_table(T1_COLUMNS, t1), encoding="utf-8", newline="\n")
    (tables_dir / "T1_legacy_l1_results.md").write_text(
        f"Table T1: per-stack instrument results — {LEGACY_LABEL}. Values are mean, "
        "sample SD, and observed min–max over n=3 sequential repetitions per exact stack. "
        "No cross-stack comparison is made.\n\n"
        "Output-token columns use runtime-observed counts; tokenizer identity is unknown (legacy bundle).\n\n"
        + markdown_table(T1_COLUMNS, t1), encoding="utf-8", newline="\n")

    s1 = s1_rows(stacks)
    s1_columns = ["stack_id"] + S1_FIELDS
    (tables_dir / "S1_legacy_stack_identity.csv").write_text(csv_table(s1_columns, s1), encoding="utf-8", newline="\n")
    (tables_dir / "S1_legacy_stack_identity.md").write_text(
        f"Table S1: full D-058 stack identity for both legacy stacks — {LEGACY_LABEL}. "
        "Every cell is a concrete recorded value or an explicit unknown.\n\n"
        + markdown_table(s1_columns, s1), encoding="utf-8", newline="\n")

    mean_by_stack = {sid: stacks[sid]["metrics"]["energy_request_j"]["mean"] for sid in stacks}
    row = claims_row(stacks, mean_by_stack)
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
        "build_mode": "real-bundles",
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
    print("make_figures: OK — dataset, aggregates, figure, T1, S1, claims row, artifact manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
