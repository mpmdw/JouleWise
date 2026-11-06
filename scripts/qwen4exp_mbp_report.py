#!/usr/bin/env python3
"""Fill the Saturday results template from immutable probe JSON files.

Missing evidence remains PENDING. This report never closes GOAL items.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qwen4exp_mbp_live as live

TEMPLATE = live.ROOT / "docs/align/qwen4_exp_port/mbp_live_results_template.md"
FILES = ("download.json", "convert.json", "memory.json", "quality.json", "benchmark.json",
         "bf16-benchmark.json", "hosted.json", "performance-512.json", "performance-2048.json", "paging.json")


def table(headers, rows):
    def cell(x):
        return str(x).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(cell(c) for c in row) + " |" for row in rows)])


def render(template, reports, run_id):
    def worker(name):
        return reports.get(name, {}).get("results", {})
    def stamp(name):
        report = reports.get(name, {})
        return "SYNTHETIC" if report.get("synthetic") is True or worker(name).get("synthetic") is True else "REAL"
    memory = []
    for r in worker("memory.json").get("runs", []):
        memory.append([stamp("memory.json"), r["context"], r["prompt_tokens"], round(r["metal"]["peak_bytes"] / 1e9, 3),
                       round(sum(t["resident_bytes"] for t in r["ple_after"].values()) / 1e9, 3),
                       r.get("prediction", {}).get("relative_error", "n/a")])
    quality, benchmark = [], []
    for filename, rows in (("quality.json", quality), ("benchmark.json", benchmark)):
        for stage, r in worker(filename).get("e2e", {}).get("stages", {}).items():
            rows.append([stamp(filename), stage, r.get("verdict"), r.get("passed", "n/a"), r.get("n", "n/a")])
    speed = []
    for step in (512, 2048):
        for r in worker(f"performance-{step}.json").get("medians", []):
            speed.append([stamp(f"performance-{step}.json"), step, r["context"], r["reasoning_effort"],
                          round(r["prefill_tps"], 2), round(r["decode_tps"], 2)])
    paging = []
    for r in worker("paging.json").get("runs", []):
        before, after = r["ple_before"], r["ple_after"]
        paging.append([stamp("paging.json"), r["repeat"], r["major_faults"], r["minor_faults"], r["input_blocks"],
                       sum(after[k]["lookups"] - before[k]["lookups"] for k in after),
                       round(sum(t["resident_bytes"] for t in after.values()) / 1e9, 3)])
    evidence = [[stamp(name), name, reports[name].get("verdict", "receipt"), reports[name].get("abort") or ""]
                if name in reports else ["PENDING", name, "PENDING", "missing"] for name in FILES]
    reference = reports.get("bf16-benchmark.json", {})
    ref_summary = {"bf16_report_verdict": reference.get("verdict", "PENDING"),
                   "hosted_identity": reference.get("hosted_identity", "PENDING"),
                   "benchmark_comparison": worker("benchmark.json").get("e2e", {}).get("reference_comparison", "PENDING"),
                   "hosted_logprobs_verdict": worker("hosted.json").get("hosted", {}).get("verdict", "PENDING")}
    values = {"RUN_ID": run_id, "SOURCE": json.dumps(reports.get("download.json", {}).get("revision", "PENDING")),
              "ARTIFACT": json.dumps(reports.get("convert.json", {}), indent=2),
              "MEMORY_ROWS": table(["Artifact", "Final context", "Prompt tokens", "Metal peak GB", "PLE resident GB", "Prediction relative error"], memory),
              "MEMORY_MONITOR": json.dumps({k: v for k, v in reports.get("memory.json", {}).items()
                                             if k != "results"}, indent=2),
              "QUALITY_ROWS": table(["Artifact", "Stage", "Verdict", "Passed", "n"], quality),
              "BENCHMARK_ROWS": table(["Artifact", "Stage", "Verdict", "Passed", "n"], benchmark),
              "PERFORMANCE_ROWS": table(["Artifact", "Prefill chunk", "Context", "Effort", "Prefill tok/s", "Decode tok/s"], speed),
              "PAGING_ROWS": table(["Artifact", "Pass", "Major faults", "Minor faults", "Input blocks", "PLE lookups", "Resident GB"], paging),
              "REFERENCE": json.dumps(ref_summary, indent=2),
              "EVIDENCE": table(["Artifact", "Evidence", "Status", "Abort/missing reason"], evidence)}
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--run-dir", type=Path)
    p.add_argument("--out", type=Path)
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
