#!/usr/bin/env python3
"""Compare all live D-117 V5 outputs with a pre-extraction revision."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
GENERATOR_CASES = (
    (
        "ALPHA",
        Path("configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py"),
        Path("configs/campaigns/d117_floor_qwen3-1p7b_v5"),
    ),
    (
        "BETA",
        Path("configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py"),
        Path("configs/campaigns/d117_floor_qwen3-8b_v5"),
    ),
    (
        "GAMMA",
        Path("configs/campaigns/d117_contrast_v5/generate_configs.py"),
        Path("configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"),
    ),
)
SELF_BOUND_OUTPUTS = frozenset(
    {"generate_configs.py", "plan_tree.json", "plan_tree.sha256"}
)


def load_source(name: str, source: bytes, path: Path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def load_worktree(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def artifact_inventory(root: Path, output_pack_rel: Path) -> dict[Path, bytes]:
    pack = root / output_pack_rel
    return {
        path.relative_to(pack): path.read_bytes()
        for path in pack.rglob("*")
        if path.is_file() and path.name not in SELF_BOUND_OUTPUTS
    }


def configure_generator(label: str, module: Any, pin: Path) -> None:
    from tests.test_d117_floor_qwen3_v5_generate import (  # noqa: PLC0415
        PANEL,
        WORKLOAD,
    )

    if label in {"ALPHA", "BETA"}:
        module.configure_prefill_pin(pin)
        return
    module.configure_model_pair(
        PANEL,
        "qwen3-1p7b",
        "qwen3-8b",
        decode_workload_path=WORKLOAD,
        prefill_length=512,
        prefill_prompt_pin_path=pin,
    )


def generate(module: Any, label: str, output_root: Path) -> None:
    if label == "GAMMA":
        module.generate(output_root, module.GenerationIdentity())
    else:
        module.generate(output_root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-ref",
        required=True,
        help="Git revision containing the pre-extraction generators",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    from tests.test_d117_floor_qwen3_v5_generate import (  # noqa: PLC0415
        fixture_prefill_pin,
    )

    compared: list[tuple[str, int]] = []
    with tempfile.TemporaryDirectory(prefix="generator-core-parity-") as temp:
        temporary = Path(temp)
        fixture_root = temporary / "fixture"
        fixture_root.mkdir()
        pin = fixture_prefill_pin(fixture_root)
        for label, generator_rel, output_pack_rel in GENERATOR_CASES:
            generator_path = ROOT / generator_rel
            baseline_source = subprocess.check_output(
                ["git", "show", f"{args.baseline_ref}:{generator_rel.as_posix()}"],
                cwd=ROOT,
            )
            baseline = load_source(
                f"generator_core_before_{label.lower()}",
                baseline_source,
                generator_path,
            )
            baseline.embedded_generator_bytes = (
                lambda source=baseline_source: source
            )
            current = load_worktree(
                f"generator_core_after_{label.lower()}", generator_path
            )
            configure_generator(label, baseline, pin)
            configure_generator(label, current, pin)

            before = temporary / label.lower() / "before"
            after = temporary / label.lower() / "after"
            generate(baseline, label, before)
            generate(current, label, after)
            left = artifact_inventory(before, output_pack_rel)
            right = artifact_inventory(after, output_pack_rel)

            missing = sorted(set(left) ^ set(right))
            changed = sorted(
                path for path in set(left) & set(right) if left[path] != right[path]
            )
            if missing or changed:
                raise SystemExit(
                    "PARITY_FAIL "
                    f"generator={label} "
                    f"inventory_difference={[path.as_posix() for path in missing]} "
                    f"byte_difference={[path.as_posix() for path in changed]}"
                )
            compared.append((label, len(left)))

    for label, count in compared:
        print(f"PARITY_DIFF_EMPTY generator={label} files={count}")
    print(
        f"PARITY_OK generators={len(compared)} files={sum(count for _, count in compared)} "
        f"excluded={sorted(SELF_BOUND_OUTPUTS)} baseline={args.baseline_ref}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
