#!/usr/bin/env python3
"""Judge an already-recorded supervised T-0 rehearsal custody tree."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise import t0_rehearsal  # noqa: E402
from joulewise.arm_readiness import _production_inventory as _read_production_inventory  # noqa: E402


MANIFEST_NAME = "t0-rehearsal-bundle.json"
MANIFEST_SCHEMA = "joulewise.t0_unattended_rehearsal_bundle.v1"
RECORD_NAMES = frozenset(
    {
        "execution",
        "hid_idle",
        "d149_go",
        "rehearsal_receipt",
        "process_lineage",
        "lifecycle",
        "falsifier_controls",
        "positive_control",
    }
)
_MANIFEST_KEYS = {
    "schema_version",
    "t0_namespace",
    "records",
    "production_roots",
}


class BundleLoadError(ValueError):
    """The custody root cannot describe an evidence bundle safely."""


def _safe_relative(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BundleLoadError(f"{label} must be a nonempty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise BundleLoadError(f"{label} must stay inside the custody root")
    return path.as_posix()


def _regular_bytes(path: Path, *, label: str) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("not a regular non-symlink file")
        return path.read_bytes()
    except OSError as exc:
        raise BundleLoadError(f"{label} is unreadable: {path}: {exc}") from exc


def _artifact(root: Path, path: Path) -> t0_rehearsal.EvidenceArtifact:
    raw = _regular_bytes(path, label="custody artifact")
    relative = path.relative_to(root).as_posix()
    value: object | None = None
    parse_error: str | None = None
    if path.suffix == ".json":
        try:
            value = readiness.parse_json_bytes(raw, require_canonical=True)
        except readiness.ArmReadinessError as exc:
            parse_error = str(exc)
    return t0_rehearsal.EvidenceArtifact(
        relative_path=relative,
        path=path,
        raw=raw,
        sha256=readiness.sha256_bytes(raw),
        value=value,
        parse_error=parse_error,
    )


def _crawl(root: Path) -> tuple[tuple[t0_rehearsal.EvidenceArtifact, ...], tuple[str, ...]]:
    artifacts = []
    issues = []
    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        current = Path(directory)
        kept_directories = []
        for name in sorted(directory_names):
            candidate = current / name
            if candidate.is_symlink():
                issues.append(f"custody contains symlink directory: {candidate.relative_to(root)}")
            else:
                kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            candidate = current / name
            if candidate.is_symlink() or not candidate.is_file():
                issues.append(f"custody contains non-regular artifact: {candidate.relative_to(root)}")
                continue
            artifacts.append(_artifact(root, candidate))
    return tuple(artifacts), tuple(issues)


def _production_inventory(plan):
    """Preserve the bundle loader's byte-reader seam and error vocabulary."""
    try:
        return _read_production_inventory(
            plan,
            read_bytes=lambda path: _regular_bytes(path, label="production custody inventory"))
    except ValueError as exc:
        raise BundleLoadError(str(exc)) from exc


def load_evidence_bundle(root: Path | str, *, home=None, inventory=None) -> t0_rehearsal.EvidenceBundle:
    """Read one fixed-layout custody tree without synthesizing evidence."""

    try:
        original = Path(root)
        if not original.is_absolute() or any(p.is_symlink() for p in (original, *original.parents)):
            raise BundleLoadError("custody root must be absolute and non-symlink")
        custody = original.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise BundleLoadError(f"custody root is unavailable: {root}: {exc}") from exc
    if custody.is_symlink() or not custody.is_dir():
        raise BundleLoadError("custody root must be a regular directory")
    manifest_path = custody / MANIFEST_NAME
    manifest_raw = _regular_bytes(manifest_path, label="rehearsal bundle manifest")
    try:
        manifest_value = readiness.parse_json_bytes(
            manifest_raw, require_canonical=True
        )
    except readiness.ArmReadinessError as exc:
        raise BundleLoadError(f"bundle manifest is not canonical strict JSON: {exc}") from exc
    if (
        not isinstance(manifest_value, Mapping)
        or set(manifest_value) != _MANIFEST_KEYS
        or manifest_value.get("schema_version") != MANIFEST_SCHEMA
    ):
        raise BundleLoadError("bundle manifest schema or exact keys are invalid")
    records = manifest_value.get("records")
    if not isinstance(records, Mapping) or set(records) != RECORD_NAMES:
        raise BundleLoadError("bundle manifest record census is not exact")
    record_paths = {
        name: _safe_relative(records[name], label=f"records.{name}")
        for name in sorted(RECORD_NAMES)
    }
    namespace_relative = _safe_relative(
        manifest_value.get("t0_namespace"), label="t0_namespace"
    )
    namespace = custody / PurePosixPath(namespace_relative)
    try:
        namespace_resolved = namespace.resolve(strict=True)
        namespace_resolved.relative_to(custody)
    except (OSError, ValueError) as exc:
        raise BundleLoadError(f"T-0 namespace is unavailable or escapes custody: {exc}") from exc
    if not namespace_resolved.is_dir() or namespace_resolved.is_symlink():
        raise BundleLoadError("T-0 namespace must be a regular directory")

    production_items = manifest_value.get("production_roots")
    if not isinstance(production_items, list):
        raise BundleLoadError("production_roots must be a list")
    try:
        # The pack GO retains the plan's repo/measurement pins. G5 separately
        # authenticates that GO; the loader must not substitute its own HEAD.
        if inventory is None:
            go = readiness.parse_json_bytes(_regular_bytes(
                custody / record_paths["d149_go"], label="pack GO inventory pins"))
            inventory = _production_inventory(go)
        production_roots = readiness.production_custody_roots(
            home=Path.home() if home is None else home,
            inventory=inventory,
        )
        recorded = {}
        for item in production_items:
            if (not isinstance(item, Mapping) or set(item) != {"role", "path"}
                    or not isinstance(item["role"], str) or item["role"] in recorded
                    or not isinstance(item["path"], str) or not Path(item["path"]).is_absolute()):
                raise ValueError("invalid census record")
            recorded[item["role"]] = Path(item["path"]).resolve(strict=False)
        if recorded != {item.role: item.path for item in production_roots}:
            raise ValueError("census mismatch")
    except (OSError, RuntimeError, ValueError) as exc:
        raise BundleLoadError("production-root census incomplete") from exc

    artifacts, crawl_issues = _crawl(custody)
    manifest_artifact = next(
        (item for item in artifacts if item.relative_path == MANIFEST_NAME), None
    )
    if manifest_artifact is None:
        raise BundleLoadError("manifest disappeared during custody census")
    load_issues = list(crawl_issues)
    known_paths = {item.relative_path for item in artifacts}
    for name, relative in record_paths.items():
        if relative not in known_paths:
            load_issues.append(f"declared {name} record is absent: {relative}")
    return t0_rehearsal.EvidenceBundle(
        custody_root=custody,
        t0_namespace_root=namespace_resolved,
        manifest=manifest_artifact,
        artifacts=artifacts,
        record_paths=record_paths,
        production_roots=tuple(production_roots),
        load_issues=tuple(load_issues),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    roots = parser.add_mutually_exclusive_group(required=True)
    roots.add_argument(
        "--fixture-root",
        type=Path,
        help="read a synthesized custody tree; the CLI still invents no evidence",
    )
    roots.add_argument(
        "--custody-root",
        type=Path,
        help="read a real supervised-rehearsal custody tree",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: BinaryIO | None = None,
    home=None, inventory=None,
) -> int:
    args = _parser().parse_args(argv)
    root = args.fixture_root if args.fixture_root is not None else args.custody_root
    try:
        bundle = load_evidence_bundle(root, home=home, inventory=inventory)
        verdict = t0_rehearsal.evaluate_rehearsal(bundle)
    except BundleLoadError as exc:
        verdict = {
            "schema_version": "joulewise.t0_unattended_rehearsal_verdict.v1",
            "overall_verdict": "FAIL",
            "gate_counts": {"PASS": 0, "FAIL": 1, "UNRULED": 0},
            "gates": [],
            "load_issues": [str(exc)],
        }
    output = sys.stdout.buffer if stdout is None else stdout
    output.write(readiness.render_json(verdict))
    if verdict["overall_verdict"] == "PASS":
        return 0
    if verdict["overall_verdict"] == "INCOMPLETE":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
