"""Check whether histsem fails closed or lazy-fetches a partial clone."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402


PACK_RELATIVE = "configs/campaigns/d117_floor_qwen25_1p5b_v1"
HISTORICAL_HEAD = "3c8677d982cfdf2651fca6809cae5b8ee0c0d9f1"


def run(*command: str, cwd: Path | None = None, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def missing_blobs(repository: Path) -> list[str]:
    env = dict(os.environ)
    env["GIT_NO_LAZY_FETCH"] = "1"
    result = run(
        "git",
        "-C",
        str(repository),
        "rev-list",
        "--objects",
        "--missing=print",
        HISTORICAL_HEAD,
        "--",
        PACK_RELATIVE,
        env=env,
    )
    return [line for line in result.stdout.splitlines() if line.startswith("?")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="joulewise-delta2-partial-") as temporary:
        root = Path(temporary)
        origin = root / "origin.git"
        partial = root / "partial"
        run("git", "clone", "-q", "--bare", "--no-local", str(ROOT), str(origin))
        run("git", "config", "uploadpack.allowFilter", "true", cwd=origin)
        run("git", "config", "uploadpack.allowAnySHA1InWant", "true", cwd=origin)
        run(
            "git",
            "clone",
            "-q",
            "--filter=blob:none",
            f"file://{origin}",
            str(partial),
        )
        promisor = run(
            "git", "-C", str(partial), "config", "--get", "remote.origin.promisor"
        ).stdout.strip()
        before = missing_blobs(partial)
        try:
            digest, paths = readiness._historical_pack_tree(
                partial, PACK_RELATIVE, HISTORICAL_HEAD
            )
            outcome = {"status": "PASS", "digest": digest, "path_count": len(paths)}
        except readiness.HistoricalSemanticsError as exc:
            outcome = {
                "status": "REFUSE",
                "reason_code": exc.reason_code,
                "detail": str(exc),
            }
        after = missing_blobs(partial)
        result = {
            "missing_after": len(after),
            "missing_before": len(before),
            "histsem": outcome["status"],
            "promisor": promisor == "true",
        }
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))

    lazy_fetch_defect = (
        promisor == "true"
        and len(before) > 0
        and outcome["status"] == "PASS"
        and len(after) < len(before)
    )
    return 0 if lazy_fetch_defect else 1


if __name__ == "__main__":
    raise SystemExit(main())
