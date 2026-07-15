#!/usr/bin/env python3
"""Package strict-valid JouleWise bundles for external publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
from joulewise.publication_privacy import (
    POLICY_SCHEMA,
    TRANSFORMATION_SCHEMA,
    PrivacyAuditError,
    audit_private_bundle,
    classification_for_path,
    public_bundle_id,
    source_provenance_problems,
    transform_public_bundle,
    tree_identity_descriptor,
    tree_sha256,
    verify_public_bundle,
)
from joulewise.suite import suite_manifest_sha256

PACK_SCHEMA = "joulewise.public_bundle_pack.v2"
MANIFEST_NAME = "MANIFEST.json"
TRANSFORMATION_MANIFEST_NAME = "TRANSFORMATION_MANIFEST.json"
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
    provenance_problems = source_provenance_problems(
        metadata.get("source_provenance"),
        require_eligible=True,
    )
    if provenance_problems:
        rendered = "; ".join(provenance_problems)
        raise BundlePackError(
            f"bundle source provenance is not claim-eligible and cannot be packed: "
            f"{bundle}: {rendered}"
        )
    summary_status = _summary_status(bundle)
    if summary_status != "succeeded":
        raise BundlePackError(
            f"bundle summary status must be succeeded for publication packs: "
            f"{bundle}: {summary_status}"
        )
    try:
        privacy_audit = audit_private_bundle(bundle)
    except PrivacyAuditError as exc:
        raise BundlePackError(f"bundle failed publication privacy audit: {bundle}: {exc}") from exc
    return {
        "source_bundle_id": _bundle_id(bundle),
        "bundle_id": public_bundle_id(privacy_audit.source_bundle_sha256),
        "source_path": str(bundle),
        "source_bundle_sha256": privacy_audit.source_bundle_sha256,
        "source_config_sha256": sha256_file(bundle / "config.json"),
        "effective_manifest_sha256": _suite_effective_manifest_sha256(bundle),
        "summary_status": summary_status,
        "classification_counts": privacy_audit.classification_counts,
    }


def _readme(manifest: dict[str, Any]) -> str:
    commit = manifest["project_commit"]
    bundles_dir_name = manifest.get("bundles_dir", "bundles")
    bundle_list = "\n".join(
        f"- `{bundles_dir_name}/{entry['bundle_id']}`: source status "
        f"`{entry['summary_status']}`, public tree `{entry['public_bundle_sha256']}`"
        for entry in manifest["bundles"]
    )
    if not bundle_list:
        bundle_list = "- No bundles."
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
    return f"""# JouleWise Transformed Public Bundle Pack

This is a privacy-transformed publication artifact, not a byte-identical copy of a private run bundle. The private source bundles remain immutable and are not included. Reviewed numeric power traces and transformed config/metadata/event/summary projections remain; prompt and response content, token streams, suite source manifests, logs, worker logs, backend-native raw captures, and rich telemetry are omitted.

## Contents

{bundle_list}

`MANIFEST.json` records every public file hash and binds `TRANSFORMATION_MANIFEST.json`. The transformation manifest records each private source file hash, its reviewed classification and operation, its public output hash (or `null` for an omission), and explicit non-byte-identity. It contains no private source path or private run id.

The transformed directories are intentionally not strict-valid private bundles and must not be described as independently re-reducible raw evidence. `power_trace.csv` is retained as a reviewed measurement projection; omitted backend-native artifacts remain available only under the private evidence controls.

## One-command pack verification

{one_command_source}

```sh
python3 scripts/package_bundle_pack.py --verify /path/to/this-pack
```

The verifier checks both manifest hash chains, the exact public file set, every source/output transformation record, explicit non-byte-identity, and the fail-closed public privacy policy. It does not claim strict re-reduction of omitted private evidence.

## Source provenance

{source_checkout}

## License

JouleWise is distributed under the MIT License. See the project's `LICENSE` file at the pinned commit for the full license text.
"""


def build_manifest(
    bundle_entries: list[dict[str, Any]],
    provenance: dict[str, str],
    transformation_manifest_sha256: str,
    readme_sha256: str | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "tool": "scripts/package_bundle_pack.py",
        "project_commit": provenance["project_commit"],
        "project_tree_state": provenance["project_tree_state"],
        "privacy_policy_schema": POLICY_SCHEMA,
        "transformation_schema": TRANSFORMATION_SCHEMA,
        "bundle_tree_identity": tree_identity_descriptor(),
        "transformation_manifest": TRANSFORMATION_MANIFEST_NAME,
        "transformation_manifest_sha256": transformation_manifest_sha256,
        "byte_identical_to_private_sources": False,
        "bundles_dir": "bundles",
        "bundle_count": len(bundle_entries),
        "bundles": [
            {
                key: value
                for key, value in entry.items()
                if key not in {"source_path", "source_bundle_id"}
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

    entries = [_preflight_bundle(Path(bundle)) for bundle in bundle_dirs]
    seen: set[str] = set()
    duplicates: set[str] = set()
    for entry in entries:
        bundle_id = entry["source_bundle_id"]
        if bundle_id in seen:
            duplicates.add(bundle_id)
        seen.add(bundle_id)
    if duplicates:
        raise BundlePackError(f"duplicate bundle id(s): {', '.join(sorted(duplicates))}")

    provenance = _git_provenance()
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise BundlePackError(f"output directory already exists: {output_dir}") from exc

    try:
        bundles_dir = output_dir / "bundles"
        bundles_dir.mkdir()
        public_entries: list[dict[str, Any]] = []
        transformation_entries: list[dict[str, Any]] = []
        for entry in entries:
            destination = bundles_dir / entry["bundle_id"]
            try:
                transformation = transform_public_bundle(
                    Path(entry["source_path"]), destination
                )
            except PrivacyAuditError as exc:
                raise BundlePackError(
                    f"privacy transformation failed for {entry['source_bundle_id']}: {exc}"
                ) from exc
            if transformation["public_bundle_id"] != entry["bundle_id"]:
                raise BundlePackError(
                    "privacy transformation public id diverged from preflight: "
                    f"{entry['bundle_id']} -> {transformation['public_bundle_id']}"
                )
            public_files = _file_entries(destination)
            if tree_sha256(public_files) != transformation["output_bundle_sha256"]:
                raise BundlePackError(
                    f"public output tree diverged after transformation: {entry['bundle_id']}"
                )
            public_entries.append(
                {
                    "bundle_id": entry["bundle_id"],
                    "source_path": entry["source_path"],
                    "source_bundle_id": entry["source_bundle_id"],
                    "source_bundle_sha256": entry["source_bundle_sha256"],
                    "public_bundle_sha256": transformation["output_bundle_sha256"],
                    "source_config_sha256": entry["source_config_sha256"],
                    "config_sha256": sha256_file(destination / "config.json"),
                    "effective_manifest_sha256": entry["effective_manifest_sha256"],
                    "summary_status": entry["summary_status"],
                    "classification_counts": entry["classification_counts"],
                    "files": public_files,
                }
            )
            transformation_entries.append(transformation)
        transformation_manifest = {
            "schema": TRANSFORMATION_SCHEMA,
            "privacy_policy_schema": POLICY_SCHEMA,
            "bundle_tree_identity": tree_identity_descriptor(),
            "byte_identical_to_private_sources": False,
            "bundle_count": len(transformation_entries),
            "bundles": transformation_entries,
        }
        transformation_bytes = (
            json.dumps(transformation_manifest, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        transformation_sha256 = hashlib.sha256(transformation_bytes).hexdigest()
        (output_dir / TRANSFORMATION_MANIFEST_NAME).write_bytes(transformation_bytes)
        manifest_without_readme = build_manifest(
            public_entries, provenance, transformation_sha256
        )
        readme = _readme(manifest_without_readme)
        readme_sha256 = hashlib.sha256(readme.encode("utf-8")).hexdigest()
        manifest = build_manifest(
            public_entries, provenance, transformation_sha256, readme_sha256
        )
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
            if rel in result:
                problems.append(f"duplicate manifest file path: {rel}")
                continue
            result[rel] = {"sha256": digest, "size_bytes": size_bytes}
        else:
            problems.append(f"manifest file entry {index} is malformed")
    return result, problems


def _readme_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in manifest.items()
        if key != "readme_sha256"
    }


def _transformation_bundle_map(
    value: Any,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    problems: list[str] = []
    if not isinstance(value, dict):
        return {}, [f"{TRANSFORMATION_MANIFEST_NAME} is not a JSON object"]
    if value.get("schema") != TRANSFORMATION_SCHEMA:
        problems.append(
            f"transformation schema is not {TRANSFORMATION_SCHEMA!r}: {value.get('schema')!r}"
        )
    if value.get("privacy_policy_schema") != POLICY_SCHEMA:
        problems.append("transformation privacy policy schema does not match the packer")
    if value.get("bundle_tree_identity") != tree_identity_descriptor():
        problems.append("transformation bundle-tree identity does not match the packer")
    if value.get("byte_identical_to_private_sources") is not False:
        problems.append("transformation manifest must assert non-byte-identity")
    bundles = value.get("bundles")
    if not isinstance(bundles, list):
        return {}, problems + ["transformation manifest bundles is not a list"]
    if value.get("bundle_count") != len(bundles):
        problems.append("transformation manifest bundle_count does not match bundles length")
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(bundles):
        if not isinstance(item, dict):
            problems.append(f"transformation bundles[{index}] is not an object")
            continue
        bundle_id = item.get("public_bundle_id")
        if not isinstance(bundle_id, str) or not bundle_id:
            problems.append(f"transformation bundles[{index}].public_bundle_id is invalid")
            continue
        if bundle_id in result:
            problems.append(f"duplicate transformation public_bundle_id: {bundle_id}")
            continue
        result[bundle_id] = item
    return result, problems


def _verify_transformation_entry(
    bundle_id: str,
    bundle_path: Path,
    pack_entry: dict[str, Any],
    transformation: dict[str, Any],
) -> list[str]:
    problems: list[str] = []
    if transformation.get("schema") != TRANSFORMATION_SCHEMA:
        problems.append(f"{bundle_id}: transformation entry schema is invalid")
    if transformation.get("privacy_policy_schema") != POLICY_SCHEMA:
        problems.append(f"{bundle_id}: transformation privacy policy is invalid")
    if transformation.get("bundle_tree_identity") != tree_identity_descriptor():
        problems.append(f"{bundle_id}: transformation bundle-tree identity is invalid")
    if transformation.get("byte_identical_to_private_source") is not False:
        problems.append(f"{bundle_id}: transformation must assert source non-byte-identity")
    if transformation.get("source_bundle_sha256") != pack_entry.get("source_bundle_sha256"):
        problems.append(f"{bundle_id}: source bundle hash differs across manifests")
    if transformation.get("output_bundle_sha256") != pack_entry.get("public_bundle_sha256"):
        problems.append(f"{bundle_id}: public bundle hash differs across manifests")
    files = transformation.get("files")
    if not isinstance(files, list):
        return problems + [f"{bundle_id}: transformation files is not a list"]
    actual_files = {
        path.relative_to(bundle_path).as_posix(): path
        for path in bundle_path.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    expected_outputs: set[str] = set()
    seen_sources: set[str] = set()
    source_entries: list[dict[str, Any]] = []
    classification_counts: dict[str, int] = {}
    saw_non_identity = False
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            problems.append(f"{bundle_id}: transformation file {index} is not an object")
            continue
        rel = item.get("path")
        operation = item.get("operation")
        source_hash = item.get("source_sha256")
        source_size = item.get("source_size_bytes")
        output_hash = item.get("output_sha256")
        byte_identical = item.get("byte_identical")
        if not isinstance(rel, str) or not rel:
            problems.append(f"{bundle_id}: transformation file {index} path is invalid")
            continue
        if rel in seen_sources:
            problems.append(f"{bundle_id}: duplicate transformation source path: {rel}")
            continue
        seen_sources.add(rel)
        if not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", source_hash):
            problems.append(f"{bundle_id}: transformation source hash is invalid for {rel}")
        if not isinstance(source_size, int) or source_size < 0:
            problems.append(f"{bundle_id}: transformation source size is invalid for {rel}")
        policy = classification_for_path(rel)
        if policy is None:
            problems.append(f"{bundle_id}: unclassified transformation source path: {rel}")
        else:
            expected_classification, expected_operation = policy
            if item.get("classification") != expected_classification:
                problems.append(f"{bundle_id}: transformation classification is wrong for {rel}")
            if operation != expected_operation:
                problems.append(f"{bundle_id}: transformation operation is wrong for {rel}")
            classification_counts[expected_classification] = (
                classification_counts.get(expected_classification, 0) + 1
            )
        if isinstance(source_hash, str) and isinstance(source_size, int) and source_size >= 0:
            source_entries.append(
                {"path": rel, "sha256": source_hash, "size_bytes": source_size}
            )
        if operation == "omit":
            saw_non_identity = True
            if output_hash is not None or item.get("output_size_bytes") is not None:
                problems.append(f"{bundle_id}: omitted {rel} has an output hash or size")
            if byte_identical is not False:
                problems.append(f"{bundle_id}: omitted {rel} claims byte identity")
            if rel in actual_files:
                problems.append(f"{bundle_id}: omitted source path is present: {rel}")
            continue
        expected_outputs.add(rel)
        if rel not in actual_files:
            problems.append(f"{bundle_id}: transformed output is missing: {rel}")
            continue
        actual_hash = sha256_file(actual_files[rel])
        actual_size = actual_files[rel].stat().st_size
        if output_hash != actual_hash:
            problems.append(
                f"{bundle_id}: transformation output hash mismatch for {rel}: "
                f"record has {output_hash}, file hashes to {actual_hash}"
            )
        if item.get("output_size_bytes") != actual_size:
            problems.append(f"{bundle_id}: transformation output size mismatch for {rel}")
        actual_identity = (
            source_hash == actual_hash
            and source_size == actual_size
        )
        if byte_identical is not actual_identity:
            problems.append(f"{bundle_id}: byte-identity flag is wrong for {rel}")
        if not actual_identity:
            saw_non_identity = True
    if expected_outputs != set(actual_files):
        problems.append(f"{bundle_id}: transformation output path set does not match public files")
    public_entries = [
        {"path": rel, "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
        for rel, path in actual_files.items()
    ]
    if tree_sha256(public_entries) != transformation.get("output_bundle_sha256"):
        problems.append(f"{bundle_id}: transformed public tree hash mismatch")
    source_tree_hash = tree_sha256(source_entries)
    if source_tree_hash != transformation.get("source_bundle_sha256"):
        problems.append(f"{bundle_id}: transformed source inventory hash mismatch")
    if public_bundle_id(source_tree_hash) != bundle_id:
        problems.append(f"{bundle_id}: public id does not derive from source inventory hash")
    if transformation.get("classification_counts") != dict(sorted(classification_counts.items())):
        problems.append(f"{bundle_id}: transformation classification counts are wrong")
    if pack_entry.get("classification_counts") != dict(sorted(classification_counts.items())):
        problems.append(f"{bundle_id}: pack classification counts are wrong")
    if not saw_non_identity:
        problems.append(f"{bundle_id}: transformation does not prove non-byte-identity")
    return problems


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
    if manifest.get("privacy_policy_schema") != POLICY_SCHEMA:
        problems.append("manifest privacy_policy_schema does not match the packer")
    if manifest.get("transformation_schema") != TRANSFORMATION_SCHEMA:
        problems.append("manifest transformation_schema does not match the packer")
    if manifest.get("bundle_tree_identity") != tree_identity_descriptor():
        problems.append("manifest bundle_tree_identity does not match the packer")
    if manifest.get("transformation_manifest") != TRANSFORMATION_MANIFEST_NAME:
        problems.append("manifest transformation_manifest filename is invalid")
    if manifest.get("byte_identical_to_private_sources") is not False:
        problems.append("manifest must explicitly assert private-source non-byte-identity")
    transformation_path = pack_dir / TRANSFORMATION_MANIFEST_NAME
    transformation_map: dict[str, dict[str, Any]] = {}
    if not transformation_path.is_file() or transformation_path.is_symlink():
        problems.append(f"missing {TRANSFORMATION_MANIFEST_NAME}: {transformation_path}")
    else:
        try:
            transformation_bytes = transformation_path.read_bytes()
            transformation_value = json.loads(transformation_bytes)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            problems.append(f"{TRANSFORMATION_MANIFEST_NAME} is not readable JSON: {exc}")
        else:
            expected_transform_hash = manifest.get("transformation_manifest_sha256")
            actual_transform_hash = hashlib.sha256(transformation_bytes).hexdigest()
            if expected_transform_hash != actual_transform_hash:
                problems.append(
                    f"{TRANSFORMATION_MANIFEST_NAME} hash mismatch: manifest has "
                    f"{expected_transform_hash}, file hashes to {actual_transform_hash}"
                )
            transformation_map, transformation_problems = _transformation_bundle_map(
                transformation_value
            )
            problems.extend(transformation_problems)
    bundles_dir_name = _validate_bundles_dir_name(manifest.get("bundles_dir", "bundles"))
    if bundles_dir_name is None:
        return problems + [
            f"manifest.bundles_dir is not a plain path component: {manifest.get('bundles_dir')!r}"
        ]
    readme_path = pack_dir / README_NAME
    if not readme_path.is_file() or readme_path.is_symlink():
        problems.append(f"missing {README_NAME}: {readme_path}")
    else:
        try:
            actual_readme = readme_path.read_bytes()
        except OSError as exc:
            problems.append(f"{README_NAME} is not readable: {exc}")
            actual_readme = None
        expected_readme_sha256 = manifest.get("readme_sha256")
        if not isinstance(expected_readme_sha256, str):
            problems.append("manifest.readme_sha256 is missing or not a string")
        elif actual_readme is not None:
            actual_readme_sha256 = hashlib.sha256(actual_readme).hexdigest()
            if actual_readme_sha256 != expected_readme_sha256:
                problems.append(
                    f"{README_NAME} hash mismatch: manifest has "
                    f"{expected_readme_sha256}, file hashes to {actual_readme_sha256}"
                )
        try:
            expected_readme = _readme(_readme_manifest(manifest)).encode("utf-8")
        except (KeyError, TypeError, IndexError) as exc:
            problems.append(f"{README_NAME} cannot be regenerated from manifest fields: {exc}")
        else:
            if actual_readme is not None and actual_readme != expected_readme:
                problems.append(f"{README_NAME} does not match manifest-derived contents")
    for child in pack_dir.iterdir():
        if child.is_symlink():
            problems.append(f"unexpected symlink at pack root: {child.name}")
        elif child.is_file() and child.name not in {
            MANIFEST_NAME,
            TRANSFORMATION_MANIFEST_NAME,
            README_NAME,
        }:
            problems.append(f"unexpected file at pack root: {child.name}")
        elif child.is_dir() and child.name != bundles_dir_name:
            problems.append(f"unexpected directory at pack root: {child.name}")
    bundles = manifest.get("bundles")
    if not isinstance(bundles, list):
        return problems + ["manifest.bundles is not a list"]
    bundles_dir = pack_dir / bundles_dir_name
    expected_bundle_ids: set[str] = set()
    seen_bundle_ids: set[str] = set()
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
        if bundle_id in seen_bundle_ids:
            problems.append(f"duplicate manifest bundle_id: {bundle_id}")
        seen_bundle_ids.add(bundle_id)
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
        for problem in verify_public_bundle(bundle_path, bundle_id):
            problems.append(f"{bundle_id}: privacy verification failed: {problem}")
        transformation = transformation_map.get(bundle_id)
        if transformation is None:
            problems.append(f"{bundle_id}: missing transformation manifest entry")
        else:
            problems.extend(
                _verify_transformation_entry(bundle_id, bundle_path, entry, transformation)
            )
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
    for bundle_id in sorted(set(transformation_map) - expected_bundle_ids):
        problems.append(f"unexpected transformation entry not listed in manifest: {bundle_id}")
    return problems


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit strict-valid private JouleWise bundles, create a transformed "
            "public pack, or verify a transformed pack."
        )
    )
    parser.add_argument(
        "--verify",
        metavar="PACK_DIR",
        help="verify public privacy, transformation records, and pack hash chains",
    )
    parser.add_argument(
        "--output",
        help="output directory for a new bundle pack",
    )
    parser.add_argument(
        "bundles", nargs="*", help="strict-valid private bundle directories to audit and transform"
    )
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
