#!/usr/bin/env python3
"""Offline re-gate of one saved decoder-layer directory under gate amendment A1.

For case directories written before A1, which lack the ``*.input`` norm traces.
The norm inputs are recovered from traces that already were the exact tensors
each norm consumed: ``attn.norm`` <- the case ``input.npy`` cast to the compute
dtype (both workers read the same snapshot), ``mlp.norm`` <- each side's own
``attn.streams``. ``attention.gated_norm`` consumed untraced tensors; it is
reported as not A1-evaluable, with its stored plain-gate result. Every other
trace keeps its stored metric. No worker runs and nothing is downloaded. Norm
weights are read from a local checkpoint view (e.g. the byte-exact restaged
subset under work/staging/views/<unit>); pass --manifest to verify those view
files against the streaming manifest's recorded hashes first.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.qwen4_gold.core import (IndexedCheckpoint, TraceFile, compare_norm, norm_specs,  # noqa: E402
                                             round_bf16, sha256)


def case_input(case, dtype):
    import numpy as np
    value = np.load(case / "input.npy", allow_pickle=False).astype(np.float32)
    return round_bf16(value) if dtype == "bf16" else value


def regate(layer_dir, checkpoint, unit):
    specs = norm_specs(checkpoint.config, unit)
    results = {}
    for case in sorted(p for p in layer_dir.iterdir() if p.is_dir() and ".attempt-" not in p.name):
        report = json.loads((case / "report.json").read_text())
        dtype = "bf16" if "-bf16-" in case.name else "fp32"
        rows = {}
        for name, metric in sorted(report["metrics"].items()):
            if name not in specs:
                rows[name] = {"pass": metric["pass"], "source": "stored"}
                continue
            if name == "attn.norm":
                x_ref = x_mlx = case_input(case, dtype)
            elif name == "mlp.norm":
                x_ref, x_mlx = (TraceFile(case / side / "attn.streams.npy") for side in ("reference", "mlx"))
            else:
                rows[name] = {"pass": metric["pass"], "source": "stored plain gate; A1 not evaluable (inputs untraced)",
                              "max_abs": metric.get("max_abs")}
                continue
            weight = checkpoint.read(checkpoint.prefix + specs[name]["weight"], framework="numpy", dtype="fp32")
            a1 = compare_norm(TraceFile(case / "reference" / f"{name}.npy"), TraceFile(case / "mlx" / f"{name}.npy"),
                              x_ref, x_mlx, weight, specs[name], dtype)
            rows[name] = {"pass": a1["pass"], "source": "A1 recomputed", "stored_plain_pass": metric["pass"], **a1}
        results[case.name] = {"stored_status": report["status"],
                              "a1_status": "PASS" if all(r["pass"] for r in rows.values()) else "FAIL",
                              "traces": rows}
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer-dir", required=True, help="e.g. work/parity/layer-000")
    parser.add_argument("--checkpoint", required=True, help="local checkpoint (view) holding the unit's norm weights")
    parser.add_argument("--unit", required=True)
    parser.add_argument("--manifest", help="streaming manifest.json; verifies the checkpoint view's derived-shard hashes")
    parser.add_argument("--output", help="write full JSON here")
    args = parser.parse_args(argv)
    root = Path(args.checkpoint).resolve()
    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text())
        work = Path(args.manifest).resolve().parent
        for key, row in manifest["derived_shards"].items():
            if (work / key).parent == root and sha256(work / key) != row["sha256"]:
                raise SystemExit(f"checkpoint view changed since the run: {key}")
    checkpoint = IndexedCheckpoint(root)
    results = regate(Path(args.layer_dir), checkpoint, args.unit)
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    for case, row in results.items():
        print(f"{case}: stored={row['stored_status']} A1={row['a1_status']}")
        for name, trace in row["traces"].items():
            if trace["source"] != "stored" or not trace["pass"]:
                detail = ""
                if trace["source"] == "A1 recomputed":
                    detail = (f" plain={trace['stored_plain_pass']} chained_max_abs={trace['max_abs']:.3g}"
                              f" max_allowance={trace['propagation']['max_allowance']:.3g}"
                              f" input_max_abs={trace['propagation']['input_max_abs']:.3g}"
                              f" mlx_op_max_rel={trace['mlx_op']['max_relative']:.3g}"
                              f" ref_op_max_rel={trace['reference_op']['max_relative']:.3g}"
                              f" cosine={trace['cosine']:.15f}")
                print(f"  {name}: pass={trace['pass']} [{trace['source']}]{detail}")
    return 0 if all(r["a1_status"] == "PASS" for r in results.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
