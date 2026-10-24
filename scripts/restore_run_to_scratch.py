"""Run a reader against one restored bundle, removing the scratch copy afterward.

Example: python scripts/restore_run_to_scratch.py --run-dir ARCHIVE/sources/claim-runs/RUN \
    --scratch-dir SCRATCH --compression-records ARCHIVE.desk/compression.jsonl \
    -- python reader.py {run}

The archive and compression journal are read-only. Compressed files require a
matching journal entry; decompressed sizes and SHA-256 digests must match before
the reader starts. No run or outcome values are printed by this tool.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.desk_restore import (MIN_RESERVE_GIB, readable_run, restored_run,
                                    _inventory, _records, shutil)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--scratch-dir", required=True, type=Path)
    parser.add_argument("--compression-records", type=Path)
    parser.add_argument("--reserve-gib", type=float, default=MIN_RESERVE_GIB,
                        help=f"free space remaining after restore (at least {MIN_RESERVE_GIB} GiB)")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="reader command; each {run} is replaced by the restored bundle path")
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or not any("{run}" in arg for arg in command):
        parser.error("a reader command containing {run} is required")
    try:
        with restored_run(args.run_dir, args.scratch_dir,
                          compression_records=args.compression_records,
                          reserve_gib=args.reserve_gib) as restored:
            return subprocess.run([arg.replace("{run}", str(restored)) for arg in command],
                                  check=False).returncode
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"restore-to-scratch: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
