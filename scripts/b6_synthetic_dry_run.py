#!/usr/bin/env python3
"""Ten synthetic archives: nine counting sessions, one excluded, no study I/O."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.independent_recompute.support_b6_production import production_block, b6, sha


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True, help="new synthetic-only output directory")
    parser.add_argument("--workers", type=b6.B5.worker_count, default=1)
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=False)
    archives, attempts, document = production_block(args.out_dir / "archives")
    numbers, public = args.out_dir / "synthetic-numbers.json", args.out_dir / "public.json"
    started = time.monotonic()
    rc = b6.main(["block", *[x for a in archives for x in ("--session", str(a))],
                  "--closed", "--loop-attempts", str(attempts), "--inputs", str(document),
                  "--inputs-sha256", sha(document), "--workers", str(args.workers),
                  "--restricted-out", str(numbers), "--public-out", str(public)])
    receipt = {"synthetic_only": True, "exit_code": rc, "archives": len(archives),
               "science_units_per_cell": 10, "raw_records_per_member": 16,
               "seconds": time.monotonic() - started, "b5_loaded_sha256": b6.B5.loaded_sha256,
               "program_sha256": sha(ROOT / "scripts/independent_recompute_b6.py")}
    if numbers.exists():
        result = json.loads(numbers.read_bytes())
        receipt["option_c"] = result["block"]["option_c"]
        receipt["counting_by_pack"] = json.loads(public.read_bytes())["counting_by_pack"]
        receipt["output_sha256"] = sha(numbers)
        receipt["zstd"] = next(v["zstd"] for v in result["inputs"]["census"].values() if v["zstd"])
    (args.out_dir / "receipt.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print("synthetic_dry_run exit=" + str(rc) + " comparator=" + str(receipt.get("option_c", {}).get("pass", False)))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
