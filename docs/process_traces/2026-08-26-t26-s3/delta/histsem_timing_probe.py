"""Measure the current PACK_AUTH historical re-derivation increment."""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness


PACK = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v3"


def elapsed(*, suppress_rederivation: bool) -> float:
    started = time.perf_counter()
    if suppress_rederivation:
        with mock.patch.object(
            readiness, "_histsem_rederive_pack_authentication", return_value=None
        ):
            readiness._gate_receipt_histsem(PACK)
    else:
        readiness._gate_receipt_histsem(PACK)
    return time.perf_counter() - started


def main() -> None:
    real = [elapsed(suppress_rederivation=False) for _ in range(3)]
    without = [elapsed(suppress_rederivation=True) for _ in range(3)]
    added = statistics.median(real) - statistics.median(without)
    print(
        json.dumps(
            {
                "boundary_callers": ["pre-arm", "predecessor-freeze"],
                "median_added_seconds_per_gate": round(added, 3),
                "median_real_seconds": round(statistics.median(real), 3),
                "median_without_rederivation_seconds": round(
                    statistics.median(without), 3
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
