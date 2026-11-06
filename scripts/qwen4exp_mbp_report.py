#!/usr/bin/env python3
"""Fill the Saturday results template from immutable probe JSON files.

Missing evidence remains PENDING. This report never closes GOAL items.
"""
import argparse
import json
import re
import statistics
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qwen4exp_mbp_live as live

TEMPLATE = live.ROOT / "docs/align/qwen4_exp_port/mbp_live_results_template.md"
FILES = ("download.json", "convert.json", "memory.json", "quality.json", "benchmark.json",
         "bf16-benchmark.json", "hosted.json", "performance-512.json", "performance-2048.json", "paging.json")
TARGETS = {512: (400, 30), 2048: (550, 30)}


def iostat_cumulative_mb(text, device):
    """Parse macOS ``iostat -Id diskN`` cumulative MB.

    Real output is a device-name line, a ``KB/t xfrs MB`` units line per
    device, then one numeric row with three columns per device (the values
    row carries no device name)::

                  disk4
        KB/t xfrs   MB
       96.67 5200 4909.01
    """
    number = re.compile(r"[-+]?\d+(?:\.\d+)?")
    lines = [line.split() for line in text.splitlines() if line.strip()]
    for i, fields in enumerate(lines):
        if device in fields and all(not number.fullmatch(x) for x in fields):
            column = fields.index(device)
            for values in lines[i + 1:]:
                if values and all(number.fullmatch(x) for x in values):
                    if len(values) >= 3 * (column + 1):
                        return float(values[3 * column + 2])
                    break
            break
    raise ValueError(f"iostat cumulative MB missing for {device}")


def load_iostat(path):
    item = json.loads(Path(path).read_text())
    return item["time"], iostat_cumulative_mb(item["iostat_raw"], item["device"])


def receipt_timing(receipt):
    return {k: receipt.get(k, "PENDING") for k in
            ("started_utc", "finished_utc", "elapsed_seconds", "total_bytes", "mean_MBps")}


def allocation_breakdown(artifact):
    """Actual tensor payload bytes by role; an allocation proxy, not RSS."""
    root, totals = Path(artifact), {"experts": 0, "non-expert bf16": 0, "lm_head": 0}
    index = json.loads((root / "model.safetensors.index.json").read_text())
    seen = set()
    for filename in sorted(set(index["weight_map"].values())):
        with (root / filename).open("rb") as stream:
            size = int.from_bytes(stream.read(8), "little")
            header = json.loads(stream.read(size))
        for name, info in header.items():
            if name == "__metadata__" or name in seen:
                continue
            seen.add(name)
            amount = info["data_offsets"][1] - info["data_offsets"][0]
            role = "lm_head" if "lm_head" in name else ("experts" if "switch_mlp" in name else "non-expert bf16")
            totals[role] += amount
    return totals


def predicted_components(config, context):
    c = config.get("text_config", config)
    layers = int(c.get("num_hidden_layers", 0)); heads = int(c.get("num_key_value_heads", c.get("num_attention_heads", 0)))
    dim = int(c.get("head_dim", int(c.get("hidden_size", 0)) // max(1, int(c.get("num_attention_heads", 1)))))
    kv = 2 * layers * heads * dim * context * 4
    qsa = sum(int(v.get("rows", 0)) * int(v.get("dim", 0)) * 2
              for v in config.get("ngram_tables", {}).get("layers", {}).values() if isinstance(v, dict))
    return kv, qsa


def table(headers, rows):
    def cell(x):
        return str(x).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(cell(c) for c in row) + " |" for row in rows)])


def render(template, reports, run_id):
    def worker(name):
        return reports.get(name, {}).get("results", {})
    memory, memory_steps = [], []
    monitor = reports.get("memory.json", {})
    for r in worker("memory.json").get("runs", []):
        cap = r.get("effective_metal_cap_bytes", worker("memory.json").get("effective_metal_cap_bytes", live.METAL_CAP))
        peak = r["metal"]["peak_bytes"]
        ple_pages = max((t.get("resident_bytes", 0) for t in r.get("ple_after", {}).values()), default=0) // 16384
        memory.append([r["context"], r["prompt_tokens"], round(r["metal"]["peak_bytes"] / 1e9, 3),
                       round(sum(t["resident_bytes"] for t in r["ple_after"].values()) / 1e9, 3),
                       r.get("prediction", {}).get("relative_error", "n/a")])
        memory_steps.append([r["context"], round(peak/1e9, 3), round(cap/1e9, 3),
                             round((cap-peak)/1e9, 3), round(100*(cap-peak)/cap, 2), ple_pages])
    quality, benchmark = [], []
    for filename, rows in (("quality.json", quality), ("benchmark.json", benchmark)):
        for stage, r in worker(filename).get("e2e", {}).get("stages", {}).items():
            rows.append([stage, r.get("verdict"), r.get("passed", "n/a"), r.get("n", "n/a")])
    speed = []
    for step in (512, 2048):
        source = worker(f"performance-{step}.json")
        groups = {}
        for r in source.get("runs", []):
            if not r.get("warmup"):
                groups.setdefault((r["context"], r["reasoning_effort"]), []).append(r)
        if groups:
            for (context, effort), rows in groups.items():
                p = [x["prefill_tps"] for x in rows]; d = [x["decode_tps"] for x in rows]
                verdict = "MEETS" if statistics.median(p) >= TARGETS[step][0] and statistics.median(d) >= TARGETS[step][1] else "MISSES"
                speed.append([step, context, effort, f"{statistics.median(p):.2f} ({min(p):.2f}-{max(p):.2f})",
                              f"{statistics.median(d):.2f} ({min(d):.2f}-{max(d):.2f})", verdict])
        else:
            for r in source.get("medians", []):
                verdict = "MEETS" if r["prefill_tps"] >= TARGETS[step][0] and r["decode_tps"] >= TARGETS[step][1] else "MISSES"
                speed.append([step, r["context"], r["reasoning_effort"], r["prefill_tps"], r["decode_tps"], verdict])
    paging = []
    for r in worker("paging.json").get("runs", []):
        before, after = r["ple_before"], r["ple_after"]
        lookups = sum(after[k]["lookups"] - before[k]["lookups"] for k in after)
        unique = sum(after[k].get("unique_rows", 0) - before[k].get("unique_rows", 0) for k in after)
        gather = sum(after[k].get("gather_seconds", 0) - before[k].get("gather_seconds", 0) for k in after)
        elapsed = r.get("prefill_seconds", 0) + r.get("decode_seconds", 0)
        disk_mb = disk_seconds = "PENDING"
        try:
            t0, mb0 = load_iostat(r["disk_before"]); t1, mb1 = load_iostat(r["disk_after"])
            disk_mb, disk_seconds = mb1-mb0, t1-t0
        except (OSError, ValueError, KeyError):
            pass
        rate = disk_mb/disk_seconds if isinstance(disk_mb, float) and disk_seconds > 0 else "PENDING"
        paging.append(["cold-unknown" if r["repeat"] == 0 else "warm", disk_mb, disk_seconds, rate,
                       lookups, unique, gather, gather/elapsed if elapsed else "PENDING"])
    evidence = [[name, reports[name].get("verdict", "receipt"), reports[name].get("abort") or ""]
                if name in reports else [name, "PENDING", "missing"] for name in FILES]
    reference = reports.get("bf16-benchmark.json", {})
    ref_summary = {"bf16_report_verdict": reference.get("verdict", "PENDING"),
                   "hosted_identity": reference.get("hosted_identity", "PENDING"),
                   "benchmark_comparison": worker("benchmark.json").get("e2e", {}).get("reference_comparison", "PENDING"),
                   "hosted_logprobs_verdict": worker("hosted.json").get("hosted", {}).get("verdict", "PENDING")}
    summary = {k: monitor.get(k, "PENDING") for k in ("initial_swap_used_bytes", "swapouts_delta", "min_free_percent",
                                                        "pressure_levels", "max_compressor_growth_bytes")}
    summary["load_phase_peak_bytes"] = worker("memory.json").get("load_metal", {}).get("peak_bytes", "PENDING")
    allocation = []
    artifact_path = reports.get("convert.json", {}).get("artifact")
    if artifact_path and Path(artifact_path).is_dir():
        actual = allocation_breakdown(artifact_path)
        config = json.loads((Path(artifact_path) / "config.json").read_text())
        weights = sum(actual.values())
        for r in worker("memory.json").get("runs", []):
            kv, qsa = predicted_components(config, r["context"])
            observed = r["metal"]["peak_bytes"]
            allocation.append([r["context"], actual["experts"], actual["non-expert bf16"], actual["lm_head"],
                               kv, qsa, observed - weights - kv - qsa])
    receipts = {name: receipt_timing(reports.get(name, {})) for name in ("download.json", "convert.json")}
    actions = []
    actions.append("- Memory: inspect or fall back to maxfit5." if monitor.get("verdict") in ("aborted", "fail") else "- Memory: continue staged validation when evidence is complete.")
    actions.append("- Speed: investigate target misses; PR #670 targets are e3 extrapolations." if any(r[-1] == "MISSES" for r in speed) else "- Speed: retain target result and caveat.")
    actions.append("- Evidence: collect all PENDING files before a decision.")
    synthetic = "SYNTHETIC" if any(r.get("synthetic") or r.get("step") == 1 for r in reports.values()) else "LIVE-EVIDENCE"
    values = {"RUN_ID": run_id, "SYNTHETIC": synthetic,
              "SOURCE": json.dumps(reports.get("download.json", {}).get("revision", "PENDING")),
              "ARTIFACT": json.dumps(reports.get("convert.json", {}), indent=2),
              "RECEIPT_TIMINGS": json.dumps(receipts, indent=2),
              "MEMORY_SUMMARY": json.dumps(summary, indent=2),
              "MEMORY_ROWS": table(["Final context", "Prompt tokens", "Metal peak GB", "PLE resident GB", "Prediction relative error"], memory),
              "MEMORY_STEP_ROWS": table(["Context", "Metal GB", "Cap GB", "Margin GB", "Margin %", "Max PLE resident pages"], memory_steps),
              "ALLOCATION_ROWS": table(["Context", "Experts B", "Non-expert bf16 B", "lm_head B", "FP KV B", "QSA cache B", "Observed residual B"], allocation),
              "MEMORY_MONITOR": json.dumps({k: v for k, v in reports.get("memory.json", {}).items()
                                             if k != "results"}, indent=2),
              "QUALITY_ROWS": table(["Stage", "Verdict", "Passed", "n"], quality),
              "BENCHMARK_ROWS": table(["Stage", "Verdict", "Passed", "n"], benchmark),
              "PERFORMANCE_ROWS": table(["Prefill chunk", "Context", "Effort", "Prefill median (min-max)", "Decode median (min-max)", "Target"], speed),
              "PAGING_ROWS": table(["Pass", "Disk MB", "Elapsed s", "MB/s", "PLE lookups", "Unique rows", "Gather s", "Gather share"], paging),
              "REFERENCE": json.dumps(ref_summary, indent=2),
              "EVIDENCE": table(["Evidence", "Status", "Abort/missing reason"], evidence),
              "NEXT_ACTIONS": "\n".join(actions)}
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--run-dir", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--evidence-only", action="store_true")
    args = p.parse_args(argv)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "expected_files": FILES, "missing_evidence": "PENDING"}))
        return 0
    if not args.run_dir or not args.out:
        p.error("--run-dir and --out are required")
    directory, output = live.external(args.run_dir), live.external(args.out)
    reports = {name: json.loads((directory / name).read_text()) for name in FILES if (directory / name).exists()}
    with output.open("x") as f:
        f.write(render(TEMPLATE.read_text(), reports, directory.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
