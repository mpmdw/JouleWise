#!/usr/bin/env python3
"""Compare D-117 V5 generator output with a named pre-extraction revision."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import tempfile
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_REL = Path("configs/campaigns/d117_contrast_v5/generate_configs.py")
OUTPUT_PACK_REL = Path(
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
)
SELF_BOUND_OUTPUTS = frozenset(
    {"generate_configs.py", "plan_tree.json", "plan_tree.sha256"}
)


def load_source(name: str, source: bytes, path: Path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def load_worktree(path: Path):
    spec = importlib.util.spec_from_file_location("generator_core_after", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def artifact_inventory(root: Path) -> dict[Path, bytes]:
    pack = root / OUTPUT_PACK_REL
    return {
        path.relative_to(pack): path.read_bytes()
        for path in pack.rglob("*")
        if path.is_file() and path.name not in SELF_BOUND_OUTPUTS
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-ref",
        required=True,
        help="Git revision containing the pre-extraction generator",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generator_path = ROOT / GENERATOR_REL
    baseline_source = subprocess.check_output(
        ["git", "show", f"{args.baseline_ref}:{GENERATOR_REL.as_posix()}"],
        cwd=ROOT,
    )
    baseline = load_source("generator_core_before", baseline_source, generator_path)
    baseline.embedded_generator_bytes = lambda: baseline_source
    current = load_worktree(generator_path)

    # Reuse the fixture issuer that the production-generator tests exercise.
    from tests.test_d117_contrast_v5_pack import (  # noqa: PLC0415
        D117ContrastV5PackTests,
        PANEL,
        WORKLOAD,
    )

    with tempfile.TemporaryDirectory(prefix="generator-core-parity-") as temp:
        temporary = Path(temp)
        helper = D117ContrastV5PackTests()
        helper.generator = current
        pin = helper.write_prefill_pin(temporary)
        for module in (baseline, current):
            module.configure_model_pair(
                PANEL,
                "qwen3-1p7b",
                "qwen3-8b",
                decode_workload_path=WORKLOAD,
                prefill_length=512,
                prefill_prompt_pin_path=pin,
            )
        before = temporary / "before"
        after = temporary / "after"
        baseline.generate(before, baseline.GenerationIdentity())
        current.generate(after, current.GenerationIdentity())
        left = artifact_inventory(before)
        right = artifact_inventory(after)

    missing = sorted(set(left) ^ set(right))
    changed = sorted(
        path for path in set(left) & set(right) if left[path] != right[path]
    )
    if missing or changed:
        raise SystemExit(
            "PARITY_FAIL "
            f"inventory_difference={[path.as_posix() for path in missing]} "
            f"byte_difference={[path.as_posix() for path in changed]}"
        )
    print(
        f"PARITY_OK files={len(left)} "
        f"excluded={sorted(SELF_BOUND_OUTPUTS)} baseline={args.baseline_ref}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
