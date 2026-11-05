"""Save value-free metadata from this lane's fresh synthetic acceptance run."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(directory):
    directory = directory.resolve()
    assert directory.is_relative_to(ROOT / ".scratch-d190/r2/.scratch-s10f/tmp")
    driver = json.loads((directory / "driver-summary.json").read_bytes())
    result = json.loads((directory / "comparison-initial.json").read_bytes())
    progress = [json.loads(line) for line in (directory / "progress.jsonl").read_text().splitlines()]
    rows, cover = result["comparisons"], result["coverage"]
    recompute = json.loads((directory / "recompute.json").read_bytes())
    assert result["recompute_program_sha256"] == recompute["program_sha256"] == sha(
        ROOT / "scripts/independent_recompute_b5.py")
    totals = dict(comparisons=len(rows), numeric_agreements=sum(
        r["verdict"] == "AGREE" and "difference" in r for r in rows),
        categorical_agreements=sum(r["verdict"] == "AGREE" and "difference" not in r
                                  and not r.get("status", "").startswith("agree_null:") for r in rows),
        agree_null=result["null_agreements"], disagreements=sum(r["verdict"] != "AGREE" for r in rows))
    assert totals["comparisons"] == sum(totals[k] for k in
        ("numeric_agreements", "categorical_agreements", "disagreements")) + totals["agree_null"]["total"]
    leaves = cover["leaves"]
    summary = dict(case=directory.name, synthetic_only=True,
        r2_commit=driver["r2_commit"], record_sha256=driver["record_sha256"],
        exits={"driver": driver["driver_rc"], **{event["event"].removesuffix("_done"): event["rc"]
               for event in progress if event["event"] in ("recompute_done", "comparison_done")}},
        completed_without_tooling_refusal=driver["completed_without_tooling_refusal"],
        steps=driver["steps"], driver_wall_s=driver["driver_wall_s"], totals=totals,
        coverage=dict(normalized_paths=len(leaves),
            compared=sum(not value.startswith("uncovered") for value in leaves.values()),
            uncovered=sum(value.startswith("uncovered") for value in leaves.values()),
            uncovered_numeric=len(cover["uncovered_numeric"]), unmapped=len(cover["unmapped"]),
            unbound=len(cover["unbound"]), nonfinite=len(cover["nonfinite"]), absent_sources=cover["absent_sources"]),
        bar_set=result["bar_set"], comparison_stopped=recompute["comparison_stopped"],
        counts=result["counts"], structure_flags=result["structure_flags"],
        disagreements=[{k: row[k] for k in ("family", "key", "reason", "status") if k in row}
                       for row in rows if row["verdict"] != "AGREE"],
        commands={name: json.loads((directory / name).read_bytes()) for name in
                  ("recompute-command.json", "comparator-command.json")},
        sha256={relative: sha(ROOT / relative) for relative in
                ("scripts/independent_recompute_b5.py", "scripts/compare_b5_recompute.py",
                 "configs/analysis/b5/recompute_bars.json")},
        artifact_sha256={name: sha(directory / name) for name in
                         ("recompute.json", "comparison-initial.json", "index.json")},
        recompute_flags=dict(Counter(f["code"] for f in recompute["flags"])))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = summarize(args.directory)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("case", "exits", "totals", "coverage")}))
