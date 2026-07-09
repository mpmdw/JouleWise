#!/usr/bin/env python3
"""Package strict-valid JouleWise bundles for external publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.bundle_read import BundleReader
from joulewise.cli import validate_bundle
from joulewise.suite import suite_manifest_sha256

PACK_SCHEMA = "joulewise.bundle_pack.v1"
MANIFEST_NAME = "MANIFEST.json"
README_NAME = "README.md"
GITHUB_REPO = "https://github.com/mpmdw/JouleWise"
TREE_STATE_CLEAN = "clean"
TREE_STATE_DIRTY = "dirty"
TREE_STATE_UNKNOWN = "unknown"


class BundlePackError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _git_provenance() -> dict[str, str]:
    result = _run_git(["rev-parse", "HEAD"])
    if result is None or result.returncode != 0:
        return {
            "project_commit": "unknown",
            "project_tree_state": TREE_STATE_UNKNOWN,
        }
    commit = result.stdout.strip() or "unknown"
    if commit == "unknown":
        return {
            "project_commit": "unknown",
            "project_tree_state": TREE_STATE_UNKNOWN,
        }

    status = _run_git(["status", "--porcelain", "--untracked-files=all"])
    if status is None or status.returncode != 0:
        tree_state = TREE_STATE_UNKNOWN
    else:
        tree_state = TREE_STATE_DIRTY if status.stdout.strip() else TREE_STATE_CLEAN
    return {
        "project_commit": commit,
        "project_tree_state": tree_state,
    }


def _git_commit() -> str:
    return _git_provenance()["project_commit"]


def _validate_plain_name(value: str, label: str) -> None:
    if (
        value in {".", ".."}
        or "/" in value
        or "\\" in value
        or Path(value).is_absolute()
    ):
        raise BundlePackError(f"{label} must be a plain path component: {value!r}")


def _validate_bundle_id(bundle_id: str, bundle: Path) -> None:
    try:
        _validate_plain_name(bundle_id, "metadata.run_id")
    except BundlePackError as exc:
        raise BundlePackError(f"{exc}: {bundle}") from exc


def _validate_bundles_dir_name(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        _validate_plain_name(value, "manifest.bundles_dir")
    except BundlePackError:
        return None
    return value


def _load_json_file(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundlePackError(f"{label} is not readable JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BundlePackError(f"{label} is not a JSON object: {path}")
    return value


def _bundle_id(bundle: Path) -> str:
    metadata = _load_json_file(bundle / "metadata.json", "metadata.json")
    run_id = metadata.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise BundlePackError(f"metadata.run_id is missing or not a string: {bundle}")
    _validate_bundle_id(run_id, bundle)
    return run_id


def _file_entries(bundle: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(bundle.rglob("*")):
        rel = path.relative_to(bundle).as_posix()
        if path.is_symlink():
            raise BundlePackError(f"bundle contains a symlink, refusing non-verbatim copy: {bundle}/{rel}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise BundlePackError(f"bundle contains a non-file artifact: {bundle}/{rel}")
        entries.append(
            {
                "path": rel,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return entries


def _suite_effective_manifest_sha256(bundle: Path) -> str | None:
    manifest_path = bundle / "suite_manifest.json"
    if not manifest_path.is_file():
        return None
    raw = _load_json_file(manifest_path, "suite_manifest.json")
    return suite_manifest_sha256(raw)


def _summary_status(bundle: Path) -> str:
    summary = _load_json_file(bundle / "summary_metrics.json", "summary_metrics.json")
    status = summary.get("status")
    if not isinstance(status, str) or not status:
        raise BundlePackError(f"summary_metrics.json status is missing or not a string: {bundle}")
    return status


def _preflight_bundle(bundle: Path) -> dict[str, Any]:
    bundle = Path(bundle)
    problems = validate_bundle(bundle, strict=True)
    if problems:
        rendered = "; ".join(problems)
        raise BundlePackError(f"bundle is not strict-valid and cannot be packed: {bundle}: {rendered}")
    reader = BundleReader(bundle)
    metadata = reader.raw_metadata()
    if not isinstance(metadata, dict):
        raise BundlePackError(f"metadata.json is not readable after strict validation: {bundle}")
    summary_status = _summary_status(bundle)
    if summary_status != "succeeded":
        raise BundlePackError(
            f"bundle summary status must be succeeded for publication packs: "
            f"{bundle}: {summary_status}"
        )
    return {
        "bundle_id": _bundle_id(bundle),
        "source_path": str(bundle),
        "config_sha256": sha256_file(bundle / "config.json"),
        "effective_manifest_sha256": _suite_effective_manifest_sha256(bundle),
        "summary_status": summary_status,
        "files": _file_entries(bundle),
    }


def _copy_bundle(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, symlinks=False)


def _readme(commit: str, manifest: dict[str, Any]) -> str:
    bundle_list = "\n".join(
        f"- `bundles/{entry['bundle_id']}`: status `{entry['summary_status']}`, "
        f"config `{entry['config_sha256']}`"
        for entry in manifest["bundles"]
    )
    if not bundle_list:
        bundle_list = "- No bundles."
    first_bundle = (
        f"bundles/{manifest['bundles'][0]['bundle_id']}"
        if manifest["bundles"]
        else "bundles/<bundle-id>"
    )
    tree_state = manifest.get("project_tree_state")
    clean_provenance = commit != "unknown" and tree_state == TREE_STATE_CLEAN
    if clean_provenance:
        one_command_source = "From a clone of the project at the pinned commit below, run:"
        source_checkout = f"""Use the project source pinned to the same commit as this pack:

```sh
git clone {GITHUB_REPO} JouleWise
cd JouleWise
git checkout {commit}
```
"""
    else:
        one_command_source = "From the exact JouleWise source tree used to build this pack, run:"
        source_checkout = f"""This pack was built from project commit `{commit}` with tree state `{tree_state}`. A plain checkout of `project_commit` may not contain the exact packager or validation code that produced this pack, so use the exact source tree recorded by the publisher rather than treating the commit as clean provenance.
"""
    return f"""# JouleWise Bundle Pack

A JouleWise bundle is a self-contained run evidence directory: normalized configuration, run metadata, lifecycle events, raw telemetry evidence, derived power trace, outputs/logs, and `summary_metrics.json`. The summary is derived from the recorded artifacts, while the raw evidence remains the audit source of truth.

## Contents

{bundle_list}

`MANIFEST.json` records each bundle id, config SHA-256, suite effective-manifest SHA-256 when present, summary status, and SHA-256 for every file in each packed bundle.

Powermetrics raw plists are included verbatim when present, including `raw/powermetrics.plist` and `raw/powermetrics_idle.plist` (D-002). Derived powermetrics files and `power_trace.csv` are not substitutes for those raw plists.

## One-command pack verification

{one_command_source}

```sh
python3 scripts/package_bundle_pack.py --verify /path/to/this-pack
```

The verifier checks the manifest's exact file list and SHA-256 values, then runs strict bundle validation on every packed bundle.

## Manual bundle verification

{source_checkout}

```sh
python3 -m joulewise validate-bundle --strict /path/to/this-pack/{first_bundle}
```

To re-derive the summary without mutating the packed evidence, work on a scratch copy:

```sh
cp -R /path/to/this-pack/{first_bundle} /tmp/jw-bundle-check
cp /tmp/jw-bundle-check/summary_metrics.json /tmp/jw-summary-original.json
python3 -m joulewise reduce /tmp/jw-bundle-check
```

`validate-bundle --strict` is the authoritative re-derivation check. It compares the stored summary against a fresh reduction with the project's legacy additive-key tolerance; a byte-for-byte `cmp` can differ for older strict-valid bundles when the current reducer materializes additive summary keys.

Strict validation proves re-derivation of the recorded evidence, not independent rerunning of the hardware session. It checks that succeeded summaries follow from the bundle artifacts and, for powermetrics bundles, that `power_trace.csv` is re-derived from the raw plist evidence.

## License

JouleWise is distributed under the MIT License. See the project's `LICENSE` file at the pinned commit for the full license text.
"""


def build_manifest(
    bundle_entries: list[dict[str, Any]],
    provenance: dict[str, str],
    readme_sha256: str | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "tool": "scripts/package_bundle_pack.py",
        "project_commit": provenance["project_commit"],
        "project_tree_state": provenance["project_tree_state"],
        "bundles_dir": "bundles",
        "bundle_count": len(bundle_entries),
        "bundles": [
            {
                key: value
                for key, value in entry.items()
                if key != "source_path"
            }
            for entry in bundle_entries
        ],
    }
    if readme_sha256 is not None:
        manifest["readme_sha256"] = readme_sha256
    return manifest


def package_bundles(bundle_dirs: list[Path], output_dir: Path) -> dict[str, Any]:
    if not bundle_dirs:
        raise BundlePackError("at least one bundle directory is required")
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise BundlePackError(f"output directory already exists: {output_dir}")

    entries = [_preflight_bundle(Path(bundle)) for bundle in bundle_dirs]
    seen: set[str] = set()
    duplicates: set[str] = set()
    for entry in entries:
        bundle_id = entry["bundle_id"]
        if bundle_id in seen:
            duplicates.add(bundle_id)
        seen.add(bundle_id)
    if duplicates:
        raise BundlePackError(f"duplicate bundle id(s): {', '.join(sorted(duplicates))}")

    provenance = _git_provenance()

    bundles_dir = output_dir / "bundles"
    bundles_dir.mkdir(parents=True)
    try:
        copied_entries: list[dict[str, Any]] = []
        for entry in entries:
            destination = bundles_dir / entry["bundle_id"]
            _copy_bundle(Path(entry["source_path"]), destination)
            copied_entry = _preflight_bundle(destination)
            if copied_entry["bundle_id"] != entry["bundle_id"]:
                raise BundlePackError(
                    f"copied bundle id changed during packaging: "
                    f"{entry['bundle_id']} -> {copied_entry['bundle_id']}"
                )
            copied_entry["source_path"] = entry["source_path"]
            copied_entries.append(copied_entry)
        manifest_without_readme = build_manifest(copied_entries, provenance)
        readme = _readme(provenance["project_commit"], manifest_without_readme)
        readme_sha256 = hashlib.sha256(readme.encode("utf-8")).hexdigest()
        manifest = build_manifest(copied_entries, provenance, readme_sha256)
        (output_dir / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (output_dir / README_NAME).write_text(readme, encoding="utf-8")
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise
    return manifest


def _manifest_file_map(entry: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    files = entry.get("files")
    if not isinstance(files, list):
        return {}, ["manifest bundle entry files is not a list"]
    result: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            problems.append(f"manifest file entry {index} is not an object")
            continue
        rel = item.get("path")
        digest = item.get("sha256")
        size_bytes = item.get("size_bytes")
        if (
            isinstance(rel, str)
            and isinstance(digest, str)
            and isinstance(size_bytes, int)
            and size_bytes >= 0
        ):
            result[rel] = {"sha256": digest, "size_bytes": size_bytes}
        else:
            problems.append(f"manifest file entry {index} is malformed")
    return result, problems


def verify_pack(pack_dir: Path) -> list[str]:
    pack_dir = Path(pack_dir)
    problems: list[str] = []
    manifest_path = pack_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return [f"missing {MANIFEST_NAME}: {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"{MANIFEST_NAME} is not readable JSON: {exc}"]
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_NAME} is not a JSON object"]
    if manifest.get("schema") != PACK_SCHEMA:
        problems.append(f"manifest schema is not {PACK_SCHEMA!r}: {manifest.get('schema')!r}")
    bundles_dir_name = _validate_bundles_dir_name(manifest.get("bundles_dir", "bundles"))
    if bundles_dir_name is None:
        return problems + [
            f"manifest.bundles_dir is not a plain path component: {manifest.get('bundles_dir')!r}"
        ]
    readme_path = pack_dir / README_NAME
    if not readme_path.is_file() or readme_path.is_symlink():
        problems.append(f"missing {README_NAME}: {readme_path}")
    else:
        expected_readme_sha256 = manifest.get("readme_sha256")
        if not isinstance(expected_readme_sha256, str):
            problems.append("manifest.readme_sha256 is missing or not a string")
        else:
            actual_readme_sha256 = sha256_file(readme_path)
            if actual_readme_sha256 != expected_readme_sha256:
                problems.append(
                    f"{README_NAME} hash mismatch: manifest has "
                    f"{expected_readme_sha256}, file hashes to {actual_readme_sha256}"
                )
    for child in pack_dir.iterdir():
        if child.is_symlink():
            problems.append(f"unexpected symlink at pack root: {child.name}")
        elif child.is_file() and child.name not in {MANIFEST_NAME, README_NAME}:
            problems.append(f"unexpected file at pack root: {child.name}")
        elif child.is_dir() and child.name != bundles_dir_name:
            problems.append(f"unexpected directory at pack root: {child.name}")
    bundles = manifest.get("bundles")
    if not isinstance(bundles, list):
        return problems + ["manifest.bundles is not a list"]
    bundles_dir = pack_dir / bundles_dir_name
    expected_bundle_ids: set[str] = set()
    for index, entry in enumerate(bundles):
        if not isinstance(entry, dict):
            problems.append(f"manifest.bundles[{index}] is not an object")
            continue
        bundle_id = entry.get("bundle_id")
        if not isinstance(bundle_id, str) or not bundle_id:
            problems.append(f"manifest.bundles[{index}].bundle_id is missing or not a string")
            continue
        try:
            _validate_plain_name(bundle_id, f"manifest.bundles[{index}].bundle_id")
        except BundlePackError as exc:
            problems.append(str(exc))
            continue
        expected_bundle_ids.add(bundle_id)
        bundle_path = bundles_dir / bundle_id
        expected, file_entry_problems = _manifest_file_map(entry)
        for problem in file_entry_problems:
            problems.append(f"{bundle_id}: {problem}")
        if not bundle_path.is_dir():
            problems.append(f"missing packed bundle directory: {bundle_path}")
            continue
        actual_files: set[str] = set()
        for path in bundle_path.rglob("*"):
            rel = path.relative_to(bundle_path).as_posix()
            if path.is_symlink():
                problems.append(f"{bundle_id}: symlink not allowed in packed bundle: {rel}")
            elif path.is_file():
                actual_files.add(rel)
            elif not path.is_dir():
                problems.append(f"{bundle_id}: non-file artifact in packed bundle: {rel}")
        for rel in sorted(set(expected) - actual_files):
            problems.append(f"{bundle_id}: missing file listed in manifest: {rel}")
        for rel in sorted(actual_files - set(expected)):
            problems.append(f"{bundle_id}: extra file not listed in manifest: {rel}")
        for rel in sorted(set(expected) & actual_files):
            actual = sha256_file(bundle_path / rel)
            if actual != expected[rel]["sha256"]:
                problems.append(
                    f"{bundle_id}: hash mismatch for {rel}: "
                    f"manifest has {expected[rel]['sha256']}, file hashes to {actual}"
                )
            actual_size = (bundle_path / rel).stat().st_size
            if actual_size != expected[rel]["size_bytes"]:
                problems.append(
                    f"{bundle_id}: size mismatch for {rel}: "
                    f"manifest has {expected[rel]['size_bytes']}, file size is {actual_size}"
                )
        for problem in validate_bundle(bundle_path, strict=True):
            problems.append(f"{bundle_id}: strict validation failed: {problem}")
    if bundles_dir.is_dir():
        for child in bundles_dir.iterdir():
            if child.is_symlink():
                problems.append(f"unexpected symlink in bundles directory: {child.name}")
            elif child.is_dir() and child.name not in expected_bundle_ids:
                problems.append(f"unexpected bundle directory not listed in manifest: {child.name}")
            elif not child.is_dir():
                problems.append(f"unexpected non-directory in bundles directory: {child.name}")
    else:
        problems.append(f"missing bundles directory: {bundles_dir}")
    if manifest.get("bundle_count") != len(bundles):
        problems.append(
            f"manifest.bundle_count {manifest.get('bundle_count')!r} does not match "
            f"bundles length {len(bundles)}"
        )
    return problems


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package strict-valid JouleWise bundles or verify a bundle pack."
    )
    parser.add_argument(
        "--verify",
        metavar="PACK_DIR",
        help="verify an existing bundle pack manifest, hashes, and strict bundle validity",
    )
    parser.add_argument(
        "--output",
        help="output directory for a new bundle pack",
    )
    parser.add_argument("bundles", nargs="*", help="strict-valid bundle directories to pack")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.verify:
            if args.output or args.bundles:
                parser.error("--verify cannot be combined with --output or bundle directories")
            problems = verify_pack(Path(args.verify))
            if problems:
                for problem in problems:
                    print(f"invalid pack: {problem}")
                return 2
            print(f"valid bundle pack: {args.verify}")
            return 0
        if not args.output:
            parser.error("--output is required when packaging bundles")
        manifest = package_bundles([Path(bundle) for bundle in args.bundles], Path(args.output))
        print(f"bundle pack: {args.output} bundles={manifest['bundle_count']}")
        return 0
    except BundlePackError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
