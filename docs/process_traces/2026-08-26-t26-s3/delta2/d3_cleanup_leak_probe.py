"""Prove whether a cleanup failure before removal can leak the histsem tree."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from tests.test_receipt_histsem import REPRESENTATIVE_PACK  # noqa: E402


def main() -> int:
    real_temporary_directory = tempfile.TemporaryDirectory
    retained: list[tempfile.TemporaryDirectory[str]] = []
    with real_temporary_directory(prefix="joulewise-delta2-d3-") as outer:
        root = Path(outer)
        workspace_parent = root / "workspaces"
        workspace_parent.mkdir()
        successor = root / "successor"
        successor.mkdir()

        class CleanupFailsBeforeRemoval:
            def __init__(self, *args, **kwargs):
                kwargs.setdefault("dir", workspace_parent)
                self.inner = real_temporary_directory(*args, **kwargs)
                retained.append(self.inner)

            def __enter__(self):
                return self.inner.__enter__()

            def __exit__(self, exc_type, exc_value, traceback):
                raise OSError("simulated cleanup failure before removal")

        with mock.patch.object(
            readiness.tempfile, "TemporaryDirectory", CleanupFailsBeforeRemoval
        ):
            arm = readiness.generate_arm_receipt(
                REPRESENTATIVE_PACK, {}, root / "custody"
            )
            freeze = readiness.generate_freeze_receipt(
                successor, predecessor_pack_root=REPRESENTATIVE_PACK
            )

        created = [Path(item.name) for item in retained]
        leaked = [path for path in created if path.exists()]
        leaked_nonempty = [path for path in leaked if any(path.iterdir())]
        result = {
            "arm": arm["reason_codes"][0],
            "freeze": freeze["reason_codes"][0],
            "leaked_nonempty": len(leaked_nonempty),
        }
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        for item in retained:
            item.cleanup()

    defect_reproduced = (
        arm["status"] == "REFUSE"
        and arm["reason_codes"] == ["histsem_history_unavailable"]
        and freeze["status"] == "REFUSE"
        and freeze["reason_codes"] == ["histsem_history_unavailable"]
        and len(created) == 2
        and len(leaked_nonempty) == 2
    )
    return 0 if defect_reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
