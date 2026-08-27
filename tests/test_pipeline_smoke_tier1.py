from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.arm_readiness import (
    ArmReadinessError,
    generate_arm_receipt,
    generate_freeze_receipt,
    gnu_sidecar,
    render_json,
)
from tests.test_arm_readiness_lifecycle import git, make_go_fixture
from tests.test_arm_readiness_schemas import sample_arm


def _stamp_pipeline_smoke(pack: Path) -> None:
    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    tree["generator"] = {
        "path": "configs/campaigns/smoke/generate_configs.py",
        "sha256": "0" * 64,
        "generation_kind": "pipeline_smoke",
    }
    raw = render_json(tree)
    tree_path.write_bytes(raw)
    (pack / "plan_tree.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(raw).hexdigest(), "plan_tree.json")
    )


class PipelineSmokeTier1Tests(unittest.TestCase):
    def test_production_freeze_and_arm_refuse_pipeline_smoke_generation(self) -> None:
        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        _stamp_pipeline_smoke(pack)
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "stamp pipeline smoke generation")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")

        operations = (
            lambda: generate_freeze_receipt(pack),
            lambda: generate_arm_receipt(
                pack,
                sample_arm(Path(temporary.name) / "arm-context")["arm_context"],
                custody,
            ),
        )
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(
                ArmReadinessError
            ) as caught:
                operation()
            self.assertEqual(
                caught.exception.reason_code,
                "readiness_dependency_refused",
            )
            self.assertIn("pipeline-smoke", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
