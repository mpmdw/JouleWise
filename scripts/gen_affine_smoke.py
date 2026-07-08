#!/usr/bin/env python3
"""Generate the affine smoke suite manifest and scorer sidecar."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.workloads import DEFAULT_SMOKE_SUITE_SEED, write_affine_smoke_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="configs/suite_manifests/affine_smoke_v1.json",
        help="manifest output path",
    )
    parser.add_argument(
        "--sidecar",
        default=None,
        help="annotation sidecar output path",
    )
    parser.add_argument(
        "--suite-seed",
        default=DEFAULT_SMOKE_SUITE_SEED,
        help="deterministic suite seed",
    )
    args = parser.parse_args(argv)
    manifest_path, sidecar_path, digest = write_affine_smoke_files(
        args.manifest,
        args.sidecar,
        suite_seed=args.suite_seed,
    )
    print(f"wrote {manifest_path}")
    print(f"wrote {sidecar_path}")
    print(f"suite_manifest_sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
