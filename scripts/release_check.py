#!/usr/bin/env python3
"""Exercise the non-secret publication seams in an isolated clean snapshot.

``--dry-run`` is deliberately not a command preview.  It creates a temporary
Git repository and executes the source-only capstone check, a deterministic
mock run, transformed bundle-pack construction and verification, the local
site build, and capsule packing.  It never regenerates from the private corpus,
uses the network, reads credentials, or deploys the Lakebed site.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class ReleaseCheckError(RuntimeError):
    """Raised when the release smoke cannot prove a required seam."""


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    rendered = " ".join(command)
    print(f"release_check: RUN {rendered}", flush=True)
    try:
        subprocess.run(command, cwd=cwd, env=env, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseCheckError(f"command failed: {rendered}: {exc}") from exc


def git_output(command: list[str], *, cwd: Path) -> bytes:
    try:
        return subprocess.run(
            ["git", *command], cwd=cwd, check=True, capture_output=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseCheckError(f"git {' '.join(command)} failed: {exc}") from exc


def require_clean_source() -> None:
    status = git_output(
        ["status", "--porcelain=v1", "--untracked-files=no"], cwd=ROOT
    )
    if status:
        first = status.decode("utf-8", errors="replace").splitlines()[0]
        raise ReleaseCheckError(
            "tracked source is not clean; release checks require a clean clone "
            f"(first entry: {first})"
        )
    print(
        "release_check: BOUNDARY source: tracked tree CLEAN; untracked and "
        "ignored files are excluded from the temporary snapshot",
        flush=True,
    )


def copy_tracked_snapshot(destination: Path) -> None:
    raw_paths = git_output(["ls-files", "-z"], cwd=ROOT)
    for raw_path in raw_paths.split(b"\0"):
        if not raw_path:
            continue
        relative = Path(os.fsdecode(raw_path))
        source = ROOT / relative
        target = destination / relative
        if not source.exists() and not source.is_symlink():
            raise ReleaseCheckError(f"tracked source is missing: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        elif source.is_file():
            shutil.copy2(source, target)
        else:
            raise ReleaseCheckError(f"tracked source is not a file: {relative}")


def initialize_snapshot(snapshot: Path) -> None:
    run(["git", "init", "--quiet"], cwd=snapshot)
    run(["git", "add", "--all"], cwd=snapshot)
    run(
        [
            "git",
            "-c",
            "user.name=JouleWise release check",
            "-c",
            "user.email=release-check@invalid",
            "commit",
            "--quiet",
            "-m",
            "release-check snapshot",
        ],
        cwd=snapshot,
    )


def executable_boundary(
    snapshot: Path, env_name: str, relative: str, label: str
) -> None:
    configured = os.environ.get(env_name)
    candidate = Path(configured) if configured else snapshot / relative
    if candidate.is_file() and os.access(candidate, os.X_OK):
        print(
            f"release_check: BOUNDARY {label}: AVAILABLE at {candidate}; "
            "the pinned executable seam will be measured",
            flush=True,
        )
    else:
        print(
            f"release_check: BOUNDARY {label}: UNAVAILABLE in the clean snapshot; "
            "the repository's loud offline fallback/advisory will run, and no "
            "pinned-tool measurement is claimed",
            flush=True,
        )


def execute_smoke(snapshot: Path, scratch: Path) -> None:
    python = sys.executable
    runs = scratch / "fixture-runs"
    bundle = runs / "example-mock-local"
    pack = scratch / "fixture-public-pack"

    print(
        "release_check: BOUNDARY corpus: FIXTURE/COMPONENT SMOKE ONLY; the "
        "controlled six-bundle private corpus is unavailable and full capstone "
        "regeneration is not claimed",
        flush=True,
    )
    print(
        "release_check: BOUNDARY network: CLOSED; this checker executes no "
        "network command",
        flush=True,
    )
    print(
        "release_check: BOUNDARY credentials: CLOSED; no release or Lakebed "
        "credential is read, and deployment is never invoked",
        flush=True,
    )
    executable_boundary(
        snapshot, "JOULEWISE_MARKED_BIN", "node_modules/.bin/marked", "Node/Marked"
    )
    executable_boundary(
        snapshot,
        "JOULEWISE_LAKEBED_BIN",
        "site_capsule/node_modules/.bin/lakebed",
        "Node/Lakebed",
    )

    run(
        [python, "scripts/build_capstone.py", "--profile", "rpt001", "--offline", "--check"],
        cwd=snapshot,
    )
    run(
        [
            python,
            "-m",
            "joulewise",
            "run",
            "configs/examples/mock_local.json",
            "--runs-dir",
            str(runs),
        ],
        cwd=snapshot,
    )
    if not bundle.is_dir():
        raise ReleaseCheckError(f"mock fixture bundle was not created: {bundle}")
    run(
        [
            python,
            "scripts/package_bundle_pack.py",
            "--output",
            str(pack),
            str(bundle),
        ],
        cwd=snapshot,
    )
    run(
        [python, "scripts/package_bundle_pack.py", "--verify", str(pack)],
        cwd=snapshot,
    )
    run([python, "scripts/build_site.py"], cwd=snapshot)
    run([python, "scripts/pack_capsule.py"], cwd=snapshot)

    required = [
        snapshot / "docs/site/build_manifest.json",
        snapshot / "site_capsule/server/content/pages.ts",
        snapshot / "site_capsule/server/content/buildinfo.ts",
        pack / "MANIFEST.json",
        pack / "TRANSFORMATION_MANIFEST.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ReleaseCheckError(f"required smoke artifact is missing: {missing[0]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "execute every non-secret publication seam in a temporary clean "
            "snapshot; never print-only and never deploy"
        ),
    )
    args = parser.parse_args(argv)
    if not args.dry_run:
        parser.error(
            "--dry-run is required; credentialed release and deployment are "
            "manual checklist steps"
        )

    try:
        require_clean_source()
        with tempfile.TemporaryDirectory(prefix="joulewise-release-check-") as temp:
            scratch = Path(temp)
            snapshot = scratch / "JouleWise"
            snapshot.mkdir()
            copy_tracked_snapshot(snapshot)
            initialize_snapshot(snapshot)
            execute_smoke(snapshot, scratch)
        print(
            "release_check: PASS: every non-secret fixture/component seam "
            "executed in a temporary directory; no deployment occurred"
        )
        return 0
    except ReleaseCheckError as exc:
        print(f"release_check: ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
