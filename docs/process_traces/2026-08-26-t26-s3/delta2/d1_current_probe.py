"""Independent current-code probe for the round-2 flagless-generator cure."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise import arm_readiness_evidence as evidence  # noqa: E402


PACK_RELATIVE = "configs/campaigns/d117_floor_qwen25_1p5b_v1"


def git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    results: dict[str, object] = {}
    foreign_raw = (
        "import sys\n"
        "from pathlib import Path\n"
        "if '--check' not in sys.argv:\n"
        "    raise SystemExit(2)\n"
        "saved = Path(__file__).with_name('plan_tree.json').read_bytes()\n"
        "candidate = saved\n"
        "if candidate != saved:\n"
        "    raise SystemExit(1)\n"
        "print('accepted existing bytes', len(candidate))\n"
    ).encode("utf-8")
    foreign_digest = hashlib.sha256(foreign_raw).hexdigest()

    # Prove the retained identifier scan is denial-only: even if this probe
    # temporarily treats the exact blob as reviewed, a preserve identifier
    # still causes refusal instead of admission.
    named_raw = b"preserve_current_frozen_bytes = True\n"
    named_digest = hashlib.sha256(named_raw).hexdigest()
    with mock.patch.object(
        evidence,
        "_REVIEWED_FLAGLESS_GENERATOR_SHA256_ALLOWLIST",
        frozenset({named_digest}),
    ):
        try:
            evidence._generator_invocation(
                "generate_configs.py",
                named_raw,
                kind="PACK_AUTHENTICATION",
                preserve_current_frozen_bytes=False,
            )
        except evidence.EvidenceAuthoringError as exc:
            results["name_scan"] = {
                "reason_code": exc.reason_code,
                "detail": str(exc),
            }
        else:
            results["name_scan"] = {"admitted": True}

    with tempfile.TemporaryDirectory(prefix="joulewise-delta2-d1-") as temporary:
        repository = Path(temporary) / "repository"
        subprocess.run(
            ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
            check=True,
            capture_output=True,
        )
        git(repository, "config", "user.name", "delta2 probe")
        git(repository, "config", "user.email", "delta2@invalid")
        current_pack = repository / PACK_RELATIVE
        source = json.loads(
            (current_pack / "arm_readiness.sources/pack-authentication.json").read_bytes()
        )
        historical_head = str(source["head_commit"])
        historical_digest = str(source["pack_sha256"])
        git(repository, "checkout", "-q", "--detach", historical_head)
        historical_pack = repository / PACK_RELATIVE
        tree, _ = readiness._plan_tree(historical_pack)
        context = evidence._DerivationContext(
            pack_root=historical_pack,
            repository=repository.resolve(strict=True),
            tree=tree,
            pack_sha256=historical_digest,
            head_commit=historical_head,
        )
        generator_artifact, generator_raw = evidence._pinned_artifact(
            context,
            tree["generator"],
            kind="PACK_AUTHENTICATION",
            label="pack generator",
        )
        reviewed_digest = hashlib.sha256(generator_raw).hexdigest()
        admitted = evidence._recorded_generator_check(
            context,
            generator_artifact["path"],
            generator_raw,
            kind="PACK_AUTHENTICATION",
            preserve_current_frozen_bytes=False,
        )
        readiness._histsem_rederive_pack_authentication(
            repository, PACK_RELATIVE, historical_head, historical_digest
        )
        results["reviewed_historical"] = {
            "allowlisted": (
                reviewed_digest
                in evidence._REVIEWED_FLAGLESS_GENERATOR_SHA256_ALLOWLIST
            ),
            "derivation_mode": admitted["derivation_mode"],
            "histsem": "PASS",
            "sha256": reviewed_digest,
        }

        generator_path = repository / generator_artifact["path"]
        generator_path.write_bytes(foreign_raw)
        tree["generator"]["sha256"] = foreign_digest
        mutated_tree_raw = readiness.render_json(tree)
        (historical_pack / "plan_tree.json").write_bytes(mutated_tree_raw)
        (historical_pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(mutated_tree_raw).hexdigest(), "plan_tree.json"
            )
        )
        git(repository, "add", PACK_RELATIVE)
        git(repository, "commit", "-qm", "install foreign same-bytes echo")
        foreign_head = git(repository, "rev-parse", "HEAD")
        foreign_pack_digest = readiness.committed_pack_tree_sha256(historical_pack)
        bare = subprocess.run(
            evidence._generator_command(str(generator_path)),
            cwd=repository,
            check=False,
            capture_output=True,
            timeout=180,
            env=evidence._generator_environment(),
        )

        foreign_tree, _ = readiness._plan_tree(historical_pack)
        foreign_context = evidence._DerivationContext(
            pack_root=historical_pack,
            repository=repository.resolve(strict=True),
            tree=foreign_tree,
            pack_sha256=foreign_pack_digest,
            head_commit=foreign_head,
        )
        try:
            evidence._recorded_generator_check(
                foreign_context,
                foreign_tree["generator"]["path"],
                foreign_raw,
                kind="PACK_AUTHENTICATION",
                preserve_current_frozen_bytes=False,
            )
        except evidence.EvidenceAuthoringError as exc:
            results["foreign_author"] = {
                "bare_exit": bare.returncode,
                "reason_code": exc.reason_code,
                "detail": str(exc),
            }
        else:
            results["foreign_author"] = {"admitted": True, "bare_exit": bare.returncode}

        try:
            readiness._histsem_rederive_pack_authentication(
                repository, PACK_RELATIVE, foreign_head, foreign_pack_digest
            )
        except readiness.HistoricalSemanticsError as exc:
            results["foreign_histsem"] = {
                "reason_code": exc.reason_code,
                "detail": str(exc),
            }
        else:
            results["foreign_histsem"] = {"admitted": True}

    correct = (
        results.get("reviewed_historical", {}).get("histsem") == "PASS"
        and results.get("reviewed_historical", {}).get("allowlisted") is True
        and results.get("foreign_author", {}).get("bare_exit") == 0
        and results.get("foreign_author", {}).get("reason_code")
        == "evidence_author_pack_authentication_underivable"
        and results.get("foreign_histsem", {}).get("reason_code")
        == "histsem_historical_digest_mismatch"
        and "preserve mechanism" in results.get("name_scan", {}).get("detail", "")
    )
    print(
        json.dumps(
            {
                "author_bare": results.get("foreign_author", {}).get(
                    "bare_exit"
                ),
                "author_refuse": results.get("foreign_author", {}).get(
                    "reason_code"
                ),
                "histsem_refuse": results.get("foreign_histsem", {}).get(
                    "reason_code"
                ),
                "name_scan_refuse": "preserve mechanism"
                in results.get("name_scan", {}).get("detail", ""),
                "reviewed": results.get(
                    "reviewed_historical", {}
                ).get("histsem"),
                "status": "PASS" if correct else "FAIL",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if correct else 1


if __name__ == "__main__":
    raise SystemExit(main())
