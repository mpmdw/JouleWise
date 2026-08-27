"""Execute all three `_v3` emitters through the current composed histsem path."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise import arm_readiness_evidence as evidence  # noqa: E402


PACK_IDS = (
    "d117_contrast_qwen25_1p5b_vs_7b_v3",
    "d117_floor_qwen25_1p5b_v3",
    "d117_floor_qwen25_7b_v3",
)


def main() -> int:
    pinset = json.loads(
        (
            ROOT / "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"
        ).read_bytes()
    )
    rows = {row["pack_id"]: row for row in pinset["packs"]}
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="joulewise-delta2-v4-") as temporary:
        repository = Path(temporary) / "repository"
        subprocess.run(
            ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
            check=True,
            capture_output=True,
            timeout=60,
        )
        for pack_id in PACK_IDS:
            row = rows[pack_id]
            pack_relative = str(row["pack_path"])
            pack_auth = next(
                item
                for item in row["receipts"]
                if item["receipt_kind"] == "PACK_AUTHENTICATION"
            )
            receipt = json.loads((ROOT / pack_relative / pack_auth["path"]).read_bytes())
            head = str(receipt.get("derivation_commit", receipt.get("head_commit")))
            pack_digest = str(receipt["pack_sha256"])
            subprocess.run(
                ("git", "checkout", "-q", "--detach", head),
                cwd=repository,
                check=True,
                capture_output=True,
                timeout=60,
            )
            pack = repository / pack_relative
            tree, _ = readiness._plan_tree(pack)
            context = evidence._DerivationContext(
                pack_root=pack,
                repository=repository.resolve(strict=True),
                tree=tree,
                pack_sha256=pack_digest,
                head_commit=head,
            )
            generator, raw = evidence._pinned_artifact(
                context,
                tree["generator"],
                kind="PACK_AUTHENTICATION",
                label="pack generator",
            )
            capability = evidence._generator_preserve_capability(
                raw, kind="PACK_AUTHENTICATION"
            )
            generator_result = evidence._recorded_generator_check(
                context,
                generator["path"],
                raw,
                kind="PACK_AUTHENTICATION",
                preserve_current_frozen_bytes=False,
            )
            bare = subprocess.run(
                evidence._generator_command(str(repository / generator["path"])),
                cwd=repository,
                check=False,
                capture_output=True,
                timeout=180,
                env=evidence._generator_environment(),
            )
            started = time.monotonic()
            readiness._histsem_rederive_pack_authentication(
                repository, pack_relative, head, pack_digest
            )
            elapsed = time.monotonic() - started
            results.append(
                {
                    "bare_exit": bare.returncode,
                    "capability": capability,
                    "composed_command": generator_result["command"],
                    "composed_derivation_mode": generator_result["derivation_mode"],
                    "composed_exit": generator_result["exit_code"],
                    "histsem_seconds": round(elapsed, 6),
                    "pack_id": pack_id,
                }
            )
    correct = all(
        item["capability"]
        == {
            "has_preserve_mechanism": True,
            "supports_boolean_optional_preserve_flag": True,
        }
        and item["composed_derivation_mode"] == "regenerated"
        and item["composed_exit"] == 0
        and "--no-preserve-current-frozen-bytes" in item["composed_command"]
        for item in results
    )
    print(
        json.dumps(
            {
                "explicit": sum(
                    item["capability"]
                    == {
                        "has_preserve_mechanism": True,
                        "supports_boolean_optional_preserve_flag": True,
                    }
                    for item in results
                ),
                "no_preserve": sum(
                    "--no-preserve-current-frozen-bytes" in item["composed_command"]
                    for item in results
                ),
                "regenerated": sum(
                    item["composed_derivation_mode"] == "regenerated"
                    for item in results
                ),
                "seconds": [item["histsem_seconds"] for item in results],
                "status": "PASS" if correct else "FAIL",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if correct else 1


if __name__ == "__main__":
    raise SystemExit(main())
