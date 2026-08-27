"""Exercise histsem materialization and cleanup failures at both public boundaries."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness


PACK = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v3"
REAL_RUN = readiness.subprocess.run
REAL_TEMPORARY_DIRECTORY = tempfile.TemporaryDirectory


def boundary_results(successor: Path, custody: Path) -> dict[str, object]:
    arm = readiness.generate_arm_receipt(PACK, {}, custody)
    freeze = readiness.generate_freeze_receipt(
        successor, predecessor_pack_root=PACK
    )
    return {
        "arm": {"reason_codes": arm["reason_codes"], "status": arm["status"]},
        "freeze": {
            "reason_codes": freeze["reason_codes"],
            "status": freeze["status"],
        },
    }


def fail_clone(command, *args, **kwargs):
    if tuple(command[:2]) == ("git", "clone"):
        raise OSError("simulated historical clone failure")
    return REAL_RUN(command, *args, **kwargs)


class CleanupFailure:
    def __init__(self, *args, **kwargs):
        self.inner = REAL_TEMPORARY_DIRECTORY(*args, **kwargs)

    def __enter__(self):
        return self.inner.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self.inner.__exit__(exc_type, exc_value, traceback)
        raise OSError("simulated historical workspace cleanup failure")


def main() -> None:
    with REAL_TEMPORARY_DIRECTORY(prefix="joulewise-f3-probe-") as temporary:
        root = Path(temporary)
        successor = root / "successor"
        successor.mkdir()
        with mock.patch.object(readiness.subprocess, "run", side_effect=fail_clone):
            materialization = boundary_results(
                successor, root / "materialization-custody"
            )
        with mock.patch.object(
            readiness.tempfile, "TemporaryDirectory", CleanupFailure
        ):
            cleanup = boundary_results(successor, root / "cleanup-custody")
    print(
        json.dumps(
            {"cleanup": cleanup, "materialization": materialization},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
