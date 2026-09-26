"""Build the closed pre-battery-float bundle digest inventory from S1's base.

Only tracked artifact sources and tracked fixture bundle directories are read.
Unresolved cited digests are printed so a source never silently disappears.
"""

from __future__ import annotations

import json
import io
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

BASE = "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.detection_floor import complete_bundle_sha256  # noqa: E402


OUTPUT = ROOT / "configs/battery_float/historical_bundles.json"
_DIGEST_KEY = re.compile(
    r'"(?:complete_bundle_sha256|bundle_sha256)"\s*:\s*"([0-9a-f]{64})"'
)
_PIN = re.compile(r'PINNED_BUNDLE_SHA256\s*=\s*\(?\s*"([0-9a-f]{64})"')


def _tracked() -> list[str]:
    return subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "-z", BASE], cwd=ROOT
    ).decode().rstrip("\0").split("\0")


def _source_class(path: str) -> str | None:
    if path.startswith("docs/paper/") and "registry" in path:
        return "paper_registry"
    if "detection_floor" in path and path.endswith((".json", ".md")):
        return "detection_floor"
    if "analysis_manifest" in path and path.endswith(".json"):
        return "analysis_manifest"
    if "receipt" in path and path.endswith((".json", ".jsonl")):
        return "window_receipt"
    if path.startswith("scripts/") and path.endswith(".py"):
        return "pinned_constant"
    return None


def _bundle_digest_at_base(directory: Path) -> str:
    """Hash only the committed base bytes, independent of the worktree."""
    archive = subprocess.check_output(
        ["git", "archive", BASE, directory.as_posix()], cwd=ROOT
    )
    with tempfile.TemporaryDirectory() as temp:
        target = Path(temp)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar:
                destination = target / member.name
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    source = tar.extractfile(member)
                    assert source is not None
                    destination.write_bytes(source.read())
                else:
                    raise ValueError(f"non-regular bundle member at base: {member.name}")
        return complete_bundle_sha256(target / directory)


def build() -> tuple[list[dict[str, str]], dict[str, list[str]]]:
    tracked = _tracked()
    tracked_set = set(tracked)
    by_digest: dict[str, dict[str, str]] = {}
    for name in tracked:
        if not name.endswith("/metadata.json") or not name.startswith(
            ("tests/fixtures/", "docs/process_traces/")
        ):
            continue
        directory = Path(name).parent
        if (directory / "events.jsonl").as_posix() not in tracked_set:
            continue
        metadata = json.loads(subprocess.check_output(
            ["git", "show", f"{BASE}:{name}"], cwd=ROOT,
        ))
        if not isinstance(metadata, dict):
            continue
        digest = _bundle_digest_at_base(directory)
        run_id = metadata.get("run_id") or directory.name
        by_digest[digest] = {
            "complete_bundle_sha256": digest,
            "run_id": run_id,
            "source": name,
        }

    unresolved: dict[str, list[str]] = {}
    for name in tracked:
        source_class = _source_class(name)
        if source_class is None:
            continue
        try:
            content = subprocess.check_output(
                ["git", "show", f"{BASE}:{name}"], cwd=ROOT,
                stderr=subprocess.DEVNULL,
            ).decode("utf-8")
        except (subprocess.CalledProcessError, UnicodeDecodeError):
            continue
        cited = set(_DIGEST_KEY.findall(content))
        if source_class == "pinned_constant":
            cited.update(_PIN.findall(content))
        for digest in cited:
            if digest in by_digest:
                # The fixture is itself a cited, committed source. Preserve it
                # as the reproducible source for its run identity.
                continue
            unresolved.setdefault(digest, []).append(name)
    return sorted(by_digest.values(), key=lambda row: row["complete_bundle_sha256"]), unresolved


def main() -> int:
    rows, unresolved = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(f"entries={len(rows)}", file=sys.stderr)
    for digest, sources in sorted(unresolved.items()):
        print(f"unresolved {digest}: {', '.join(sorted(sources))}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
