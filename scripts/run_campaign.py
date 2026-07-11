#!/usr/bin/env python3
"""Run a generated Slice 2M config directory sequentially.

The JouleWise CLI has two bundle layouts. A config with
``workload_profile.repetitions == 1`` creates one bundle at
``<runs_dir>/<run_id>/``. A config with repetitions greater than one dispatches
to the experiment runner and creates one member bundle per repetition at
``<runs_dir>/<run_id>__r1`` ... ``<runs_dir>/<run_id>__rN`` plus an incremental
manifest at ``<runs_dir>/experiments/<run_id>.json``.

The manifest is not a completion marker. Completion is detected only from each
member bundle's ``summary_metrics.json``. If a process is interrupted after some
members have been created, a later campaign sees those partial members as
``incomplete_existing`` and does not re-run; the operator must inspect or move
the member bundles before retrying because the real CLI would collide on the
existing run IDs.

Dry-run mode prints the exact plan and invokes nothing. It also writes no
campaign log entries; JSONL logging is reserved for actual campaign attempts.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.bundle import sanitize_id_component  # noqa: E402
from joulewise.cli import validate_bundle  # noqa: E402


STATUSES = (
    "ok",
    "failed",
    "skipped",
    "waived",
    "incomplete_existing",
    "config_error",
    "dry_run",
)
ORDER_MANIFEST_NAME = "order_manifest.json"
ANALYSIS_MANIFEST_NAME = "analysis_manifest.json"
CONFIG_SIDECAR_NAMES = frozenset({ORDER_MANIFEST_NAME, ANALYSIS_MANIFEST_NAME})
KNOWN_NON_PROMPT_SIDECAR_SCHEMAS = frozenset(
    {
        "affine_smoke_annotations.v1",
    }
)


@dataclass(frozen=True)
class ConfigInfo:
    path: Path
    run_id: str
    raw_run_id: str
    repetitions: int
    generator_sidecar_ref: str | None = None
    suite_manifest_ref: str | None = None


@dataclass(frozen=True)
class ConfigError:
    path: Path
    message: str
    run_id: str | None = None


@dataclass(frozen=True)
class ExistingState:
    action: str
    members_succeeded: int | None = None
    members_total: int | None = None
    non_succeeded_members: tuple[str, ...] = ()
    inspect_members: tuple[str, ...] = ()
    malformed_summaries: tuple[str, ...] = ()


@dataclass(frozen=True)
class Waiver:
    target_kind: str
    target: str
    reason: str
    approver: str
    timestamp: str
    scope: str


@dataclass(frozen=True)
class PromptHashCheck:
    status: str
    sidecar_path: str | None = None
    checked_items: int = 0
    matches: tuple[dict[str, Any], ...] = ()
    problems: tuple[str, ...] = ()

    def quality_flags(self) -> tuple[str, ...]:
        if self.status == "mismatch":
            return ("prompt_hash_mismatch",)
        if self.status == "error":
            return ("prompt_hash_check_error",)
        return ()

    def to_log(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "status": self.status,
            "checked_items": self.checked_items,
        }
        if self.sidecar_path is not None:
            row["sidecar_path"] = self.sidecar_path
        if self.matches:
            row["matches"] = list(self.matches)
        if self.problems:
            row["problems"] = list(self.problems)
        return row


@dataclass(frozen=True)
class MemberEvaluation:
    bundle_id: str
    bundle_path: Path
    config_name: str
    status: str | None
    strict_valid: bool
    validation_problems: tuple[str, ...] = ()
    quality_flags: tuple[str, ...] = ()
    prompt_hash_check: PromptHashCheck = field(
        default_factory=lambda: PromptHashCheck("not_applicable")
    )
    suite_order_policy: str | None = None
    suite_order_row: int | None = None
    suite_order_seed: str | None = None
    waiver: Waiver | None = None

    def failure_classes(self) -> tuple[str, ...]:
        classes: list[str] = []
        if self.status is not None and self.status != "succeeded":
            classes.append("status_failed")
        if not self.strict_valid:
            classes.append("strict_invalid")
        classes.extend(self.quality_flags)
        return tuple(dict.fromkeys(classes))

    @property
    def usable(self) -> bool:
        return (
            self.status == "succeeded"
            and self.strict_valid
            and not self.quality_flags
            and self.waiver is None
        )

    @property
    def waived(self) -> bool:
        if self.waiver is None:
            return False
        classes = self.failure_classes()
        if not classes:
            return False
        if self.waiver.scope == "any":
            return True
        scopes = {part.strip() for part in self.waiver.scope.split(",") if part.strip()}
        return all(failure_class in scopes for failure_class in classes)

    @property
    def failed(self) -> bool:
        return not self.usable and not self.waived

    def to_log(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "bundle_id": self.bundle_id,
            "bundle_path": str(self.bundle_path),
            "status": self.status,
            "strict_valid": self.strict_valid,
            "validation_problems": list(self.validation_problems),
            "quality_flags": list(self.quality_flags),
            "prompt_hash_check": self.prompt_hash_check.to_log(),
            "classification": (
                "usable" if self.usable else "waived" if self.waived else "failed"
            ),
        }
        if self.waiver is not None:
            row["waiver"] = {
                "target_kind": self.waiver.target_kind,
                "target": self.waiver.target,
                "reason": self.waiver.reason,
                "approver": self.waiver.approver,
                "timestamp": self.waiver.timestamp,
                "scope": self.waiver.scope,
            }
        if self.suite_order_policy is not None:
            row["suite_order_policy"] = self.suite_order_policy
        if self.suite_order_row is not None:
            row["suite_order_row"] = self.suite_order_row
        if self.suite_order_seed is not None:
            row["suite_order_seed"] = self.suite_order_seed
        return row


@dataclass(frozen=True)
class OrderEntry:
    index: int
    config: str
    run_id: str | None = None
    model_tag: str | None = None
    rep: int | None = None
    workload: str | None = None
    role: str | None = None
    block_index: int | None = None
    position_in_block: int | None = None
    sentinel_position: str | None = None

    def to_log(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "index": self.index,
            "config": self.config,
            "model_tag": self.model_tag,
            "rep": self.rep,
            "workload": self.workload,
        }
        for field_name in (
            "run_id",
            "role",
            "block_index",
            "position_in_block",
            "sentinel_position",
        ):
            value = getattr(self, field_name)
            if value is not None:
                row[field_name] = value
        return row


VALID_WAIVER_SCOPES = {
    "any",
    "status_failed",
    "strict_invalid",
    "idle_window_suspect",
    "prompt_hash_mismatch",
    "prompt_hash_check_error",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_dir", nargs="?", help="Directory containing generated JSON configs")
    parser.add_argument("--runs-dir", default="runs", help="Bundle output directory")
    parser.add_argument("--log", help="JSONL campaign log path")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without invoking benchmarks")
    parser.add_argument(
        "--backup",
        nargs="?",
        const="",
        help="Run scripts/backup_runs.sh, or a supplied backup command path, after each success",
    )
    parser.add_argument("--max-failures", type=int, default=1, help="Stop after this many failures")
    parser.add_argument(
        "--cli-cmd",
        help="Command prefix replacing '<python> -m joulewise'; 'run <config> --runs-dir <dir>' is appended",
    )
    parser.add_argument(
        "--waivers",
        help="Optional JSON file listing campaign waivers; waivers are never written into bundles",
    )
    parser.add_argument(
        "--check-prompt-hashes",
        nargs=2,
        metavar=("BUNDLE_DIR", "SIDECAR_JSON"),
        help="Post-hoc expected-vs-realized prompt-hash check for one suite bundle",
    )
    args = parser.parse_args(argv)
    if args.config_dir is None and args.check_prompt_hashes is None:
        parser.error("config_dir is required unless --check-prompt-hashes is used")
    if args.config_dir is not None and args.check_prompt_hashes is not None:
        parser.error("config_dir cannot be combined with --check-prompt-hashes")
    return args


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def best_effort_run_id(config_path: Path) -> str | None:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    run_id = data.get("run_id")
    return run_id if isinstance(run_id, str) else None


def generator_sidecar_ref_from_config(data: dict[str, Any]) -> str | None:
    candidate_keys = (
        "generator_sidecar_ref",
        "suite_annotations_ref",
        "suite_sidecar_ref",
        "suite_generator_sidecar_ref",
    )
    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    workload_profile = data.get("workload_profile")
    if isinstance(workload_profile, dict):
        for key in candidate_keys:
            value = workload_profile.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def suite_manifest_ref_from_config(data: dict[str, Any]) -> str | None:
    workload_profile = data.get("workload_profile")
    if not isinstance(workload_profile, dict):
        return None
    value = workload_profile.get("suite_manifest_ref")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def load_config_info(config_path: Path) -> ConfigInfo:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read config {config_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"config is not valid JSON: {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"config must be a JSON object: {config_path}")
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError(f"config missing non-empty run_id: {config_path}")
    sanitized_run_id = sanitize_id_component(run_id)
    if sanitized_run_id != run_id:
        print(
            f"note: sanitized run_id for {config_path}: {run_id!r} -> {sanitized_run_id!r}",
            file=sys.stderr,
        )
    workload_profile = data.get("workload_profile", {})
    if workload_profile is None:
        workload_profile = {}
    if not isinstance(workload_profile, dict):
        raise ValueError(f"workload_profile must be an object: {config_path}")
    repetitions = workload_profile.get("repetitions", 1)
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError(f"workload_profile.repetitions must be a positive integer: {config_path}")
    return ConfigInfo(
        path=config_path,
        run_id=sanitized_run_id,
        raw_run_id=run_id,
        repetitions=repetitions,
        generator_sidecar_ref=generator_sidecar_ref_from_config(data),
        suite_manifest_ref=suite_manifest_ref_from_config(data),
    )


def command_for(config_path: Path, runs_dir: Path, cli_cmd: str | None) -> list[str]:
    prefix = shlex.split(cli_cmd) if cli_cmd else [sys.executable, "-m", "joulewise"]
    return prefix + ["run", str(config_path), "--runs-dir", str(runs_dir)]


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def append_log(log_path: Path, row: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() and log_path.stat().st_size > 0:
        with log_path.open("rb+") as handle:
            handle.seek(-1, os.SEEK_END)
            if handle.read(1) != b"\n":
                handle.write(b"\n")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def log_row(
    *,
    config_path: Path,
    run_id: str | None,
    status: str,
    exit_code: int | None,
    duration_s: float | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "timestamp": utc_timestamp(),
        "config": str(config_path),
        "run_id": run_id,
        "status": status,
        "exit_code": exit_code,
        "duration_s": duration_s,
    }
    if extra:
        row.update(extra)
    return row


def print_quiet_machine_warning() -> None:
    print("WARNING: This campaign needs a quiet machine with no other workloads.")
    print("WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.")


def discover_configs(config_dir: Path) -> list[Path]:
    if not config_dir.is_dir():
        raise ValueError(f"config_dir is not a directory: {config_dir}")
    return sorted(path for path in config_dir.glob("*.json") if path.name not in CONFIG_SIDECAR_NAMES)


def print_config_file_list(configs: list[Path]) -> None:
    print("Config files to execute:")
    if not configs:
        print("  <none>")
        return
    for config in configs:
        print(f"  {config}")


def backup_script_path(backup_arg: str) -> Path:
    if backup_arg:
        return Path(backup_arg)
    return Path(__file__).resolve().parent / "backup_runs.sh"


def backup_runs(runs_dir: Path, script: Path) -> None:
    result = subprocess.run([str(script), str(runs_dir)], check=False)
    if result.returncode != 0:
        print(
            f"warning: backup command failed with exit {result.returncode}: {script} {runs_dir}",
            file=sys.stderr,
        )


def member_bundle_dirs(runs_dir: Path, run_id: str, repetitions: int) -> list[Path]:
    return [runs_dir / f"{run_id}__r{rep}" for rep in range(1, repetitions + 1)]


def expected_member_dirs(info: ConfigInfo, runs_dir: Path) -> list[Path]:
    if info.repetitions == 1:
        return [runs_dir / info.run_id]
    return member_bundle_dirs(runs_dir, info.run_id, info.repetitions)


WaiverMap = dict[tuple[str, str], Waiver]


def load_waivers(path_text: str | None) -> WaiverMap:
    if path_text is None:
        return {}
    path = Path(path_text)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read waiver file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"waiver file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError(f"waiver file must be a JSON list: {path}")
    waivers: WaiverMap = {}
    seen_targets: set[tuple[str, str]] = set()
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"waiver {index} must be an object")
        target_fields = [field for field in ("bundle_id", "config", "run_id") if field in item]
        if len(target_fields) != 1:
            raise ValueError(
                f"waiver {index} requires exactly one of bundle_id, config, or run_id"
            )
        target_kind = target_fields[0]
        raw_target = item[target_kind]
        if not isinstance(raw_target, str) or not raw_target.strip():
            raise ValueError(f"waiver {index} requires non-empty {target_kind}")
        target = raw_target.strip()
        for key in ("reason", "approver", "timestamp", "scope"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"waiver {index} requires non-empty {key}")
        scope_value = item["scope"].strip()
        scope_tokens = (
            {"any"}
            if scope_value == "any"
            else {part.strip() for part in scope_value.split(",") if part.strip()}
        )
        unknown_scopes = scope_tokens - VALID_WAIVER_SCOPES
        if unknown_scopes:
            raise ValueError(
                f"waiver {index} has unknown scope class(es) "
                f"{sorted(unknown_scopes)}; valid: {sorted(VALID_WAIVER_SCOPES)}"
            )
        duplicate_key = (
            target_kind,
            Path(target).stem if target_kind == "config" else target,
        )
        if duplicate_key in seen_targets:
            raise ValueError(f"duplicate waiver target: {target_kind}={target}")
        seen_targets.add(duplicate_key)
        key = (target_kind, target)
        waivers[key] = Waiver(
            target_kind=target_kind,
            target=target,
            reason=item["reason"],
            approver=item["approver"],
            timestamp=item["timestamp"],
            scope=item["scope"].strip(),
        )
    return waivers


def matching_waiver(
    waivers: WaiverMap,
    *,
    bundle_id: str,
    config_name: str,
    config_stem: str,
    run_id: str,
) -> Waiver | None:
    candidates = (
        ("bundle_id", bundle_id),
        ("config", config_name),
        ("config", config_stem),
        ("run_id", run_id),
    )
    for target_kind, target in candidates:
        waiver = waivers.get((target_kind, target))
        if waiver is not None:
            return waiver
    return None


def resolve_sidecar_path(config_path: Path, sidecar_ref: str | None) -> Path | None:
    if sidecar_ref is None:
        return None
    path = Path(sidecar_ref)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.is_file():
        return root_relative
    config_relative = config_path.parent / path
    if config_relative.is_file():
        return config_relative
    return root_relative


def resolve_config_ref_path(config_path: Path, ref: str | None) -> Path | None:
    if ref is None:
        return None
    path = Path(ref)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.is_file():
        return root_relative
    config_relative = config_path.parent / path
    if config_relative.is_file():
        return config_relative
    return root_relative


def inferred_prompt_sidecar_path(config_path: Path, suite_manifest_ref: str | None) -> Path | None:
    manifest_path = resolve_config_ref_path(config_path, suite_manifest_ref)
    if manifest_path is None:
        return None
    candidate = manifest_path.with_name(f"{manifest_path.stem}_annotations.json")
    if candidate.is_file():
        return candidate
    return None


def _sidecar_schema_string(sidecar: dict[str, Any]) -> str | None:
    for key in ("schema", "schema_version"):
        value = sidecar.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _is_recognizable_other_sidecar(sidecar: dict[str, Any]) -> bool:
    if "annotations" in sidecar:
        return True
    schema = _sidecar_schema_string(sidecar)
    return schema in KNOWN_NON_PROMPT_SIDECAR_SCHEMAS


def _classify_inferred_prompt_sidecar(sidecar_path: Path) -> PromptHashCheck | None:
    sidecar_label = str(sidecar_path)
    sidecar, sidecar_problem = _load_json_object(sidecar_path, "inferred generator sidecar")
    if sidecar_problem is not None:
        return PromptHashCheck("error", sidecar_label, problems=(sidecar_problem,))
    assert sidecar is not None
    if isinstance(sidecar.get("items"), dict):
        return None
    if "items" in sidecar:
        return PromptHashCheck(
            "error",
            sidecar_label,
            problems=("inferred generator sidecar items is not an object",),
        )
    if _is_recognizable_other_sidecar(sidecar):
        return PromptHashCheck("not_applicable", sidecar_label)
    return PromptHashCheck(
        "error",
        sidecar_label,
        problems=(
            "inferred generator sidecar is ambiguous: "
            "missing prompt-hash items and no recognized other-type marker",
        ),
    )


def _load_json_object(path: Path, label: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"{label} cannot be read: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"{label} is not valid JSON: {exc}"
    if not isinstance(raw, dict):
        return None, f"{label} is not a JSON object"
    return raw, None


def _load_suite_item_records_for_prompt_check(
    bundle_dir: Path,
) -> tuple[list[dict[str, Any]] | None, list[str]]:
    path = bundle_dir / "outputs" / "suite_items.jsonl"
    if not path.is_file():
        return None, ["outputs/suite_items.jsonl is missing for prompt-hash check"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"outputs/suite_items.jsonl cannot be read: {exc}"]
    records: list[dict[str, Any]] = []
    problems: list[str] = []
    for line_index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(
                f"outputs/suite_items.jsonl line {line_index} is not valid JSON: {exc}"
            )
            continue
        if not isinstance(record, dict):
            problems.append(
                f"outputs/suite_items.jsonl line {line_index} is not a JSON object"
            )
            continue
        records.append(record)
    return records, problems


def _manifest_text_items(
    bundle_dir: Path,
) -> tuple[dict[str, Any] | None, list[tuple[int, str]] | None, list[str]]:
    manifest, problem = _load_json_object(bundle_dir / "suite_manifest.json", "suite_manifest.json")
    if problem is not None:
        return None, None, [problem]
    assert manifest is not None
    raw_items = manifest.get("items")
    if not isinstance(raw_items, list):
        return manifest, None, ["suite_manifest.json items is not a list"]
    text_items: list[tuple[int, str]] = []
    problems: list[str] = []
    for item_index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            problems.append(f"suite_manifest.json items[{item_index}] is not an object")
            continue
        item_id = raw_item.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            problems.append(f"suite_manifest.json items[{item_index}].item_id is missing")
            continue
        source = raw_item.get("source")
        if not isinstance(source, dict):
            problems.append(f"suite_manifest.json items[{item_index}].source is not an object")
            continue
        if source.get("prompt_token_ids") is not None or raw_item.get("item_type") == "ids_prompt":
            continue
        if source.get("prompt_text") is None and raw_item.get("item_type") != "text_prompt":
            continue
        text_items.append((item_index, item_id))
    return manifest, text_items, problems


def _sidecar_manifest_pairing_problems(
    sidecar: dict[str, Any],
    manifest: dict[str, Any],
) -> list[str]:
    sidecar_source = sidecar.get("source_manifest")
    if sidecar_source is None:
        return ["generator sidecar source_manifest is missing"]
    if not isinstance(sidecar_source, dict):
        return ["generator sidecar source_manifest is not an object"]
    manifest_source = manifest.get("source_manifest")
    if not isinstance(manifest_source, dict):
        return ["suite_manifest.json source_manifest is not an object"]
    problems: list[str] = []
    for key in ("source_id", "subset_sha256"):
        sidecar_value = sidecar_source.get(key)
        manifest_value = manifest_source.get(key)
        if not isinstance(sidecar_value, str) or not sidecar_value:
            problems.append(f"generator sidecar source_manifest.{key} is missing")
        elif sidecar_value != manifest_value:
            problems.append(
                f"generator sidecar source_manifest.{key} mismatch: "
                f"sidecar has {sidecar_value!r}, suite_manifest.json has {manifest_value!r}"
            )
    return problems


def check_prompt_hashes_for_bundle(bundle_dir: Path, sidecar_path: Path | None) -> PromptHashCheck:
    if sidecar_path is None:
        return PromptHashCheck("not_applicable")
    sidecar_label = str(sidecar_path)
    sidecar, sidecar_problem = _load_json_object(sidecar_path, "generator sidecar")
    if sidecar_problem is not None:
        return PromptHashCheck("error", sidecar_label, problems=(sidecar_problem,))
    assert sidecar is not None
    expected_items = sidecar.get("items")
    if not isinstance(expected_items, dict):
        return PromptHashCheck(
            "error",
            sidecar_label,
            problems=("generator sidecar items is not an object",),
        )

    records, record_problems = _load_suite_item_records_for_prompt_check(bundle_dir)
    manifest, text_items, manifest_problems = _manifest_text_items(bundle_dir)
    problems = [*record_problems, *manifest_problems]
    if records is None or text_items is None:
        return PromptHashCheck("error", sidecar_label, problems=tuple(problems))
    assert manifest is not None
    problems.extend(_sidecar_manifest_pairing_problems(sidecar, manifest))

    records_by_index: dict[int, dict[str, Any]] = {}
    for line_index, record in enumerate(records, start=1):
        item_index = record.get("item_index")
        if isinstance(item_index, bool) or not isinstance(item_index, int):
            problems.append(
                f"outputs/suite_items.jsonl line {line_index} item_index is not an integer"
            )
            continue
        if item_index in records_by_index:
            problems.append(f"outputs/suite_items.jsonl duplicates item_index {item_index}")
            continue
        records_by_index[item_index] = record

    matches: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for item_index, item_id in text_items:
        expected_row = expected_items.get(item_id)
        if not isinstance(expected_row, dict):
            problems.append(
                f"item {item_id!r} index {item_index} is missing from generator sidecar"
            )
            continue
        expected_hash = expected_row.get("token_ids_sha256")
        if not isinstance(expected_hash, str) or not expected_hash:
            problems.append(
                f"item {item_id!r} index {item_index} sidecar token_ids_sha256 is missing"
            )
            continue
        record = records_by_index.get(item_index)
        if record is None:
            problems.append(
                f"item {item_id!r} index {item_index} is missing from outputs/suite_items.jsonl"
            )
            continue
        realized_item_id = record.get("item_id")
        if realized_item_id != item_id:
            problems.append(
                f"item index {item_index} item_id mismatch: manifest has {item_id!r}, "
                f"outputs/suite_items.jsonl has {realized_item_id!r}"
            )
            continue
        prompt = record.get("prompt")
        realized_hash = prompt.get("token_ids_sha256") if isinstance(prompt, dict) else None
        if realized_hash != expected_hash:
            mismatches.append(
                f"item {item_id!r} index {item_index} prompt.token_ids_sha256 mismatch: "
                f"expected {expected_hash!r}, realized {realized_hash!r}"
            )
            continue
        matches.append(
            {
                "item_id": item_id,
                "item_index": item_index,
                "expected": expected_hash,
                "realized": realized_hash,
            }
        )

    if problems:
        return PromptHashCheck(
            "error",
            sidecar_label,
            checked_items=len(matches) + len(mismatches),
            matches=tuple(matches),
            problems=tuple([*problems, *mismatches]),
        )
    if mismatches:
        return PromptHashCheck(
            "mismatch",
            sidecar_label,
            checked_items=len(matches) + len(mismatches),
            matches=tuple(matches),
            problems=tuple(mismatches),
        )
    return PromptHashCheck(
        "matched",
        sidecar_label,
        checked_items=len(matches),
        matches=tuple(matches),
    )


def check_prompt_hashes_for_config_bundle(bundle_dir: Path, info: ConfigInfo) -> PromptHashCheck:
    explicit = resolve_sidecar_path(info.path, info.generator_sidecar_ref)
    if explicit is not None:
        return check_prompt_hashes_for_bundle(bundle_dir, explicit)
    inferred = inferred_prompt_sidecar_path(info.path, info.suite_manifest_ref)
    if inferred is None:
        return PromptHashCheck("not_applicable")
    inferred_classification = _classify_inferred_prompt_sidecar(inferred)
    if inferred_classification is not None:
        return inferred_classification
    return check_prompt_hashes_for_bundle(bundle_dir, inferred)


def quality_flags(summary: dict[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(summary, dict):
        return ()
    quality = summary.get("measurement_quality")
    if not isinstance(quality, dict):
        return ()
    flags: list[str] = []
    if quality.get("idle_window_suspect") is True:
        flags.append("idle_window_suspect")
    return tuple(flags)


def suite_order_evidence(bundle_dir: Path) -> tuple[str | None, int | None, str | None]:
    policy: str | None = None
    row: int | None = None
    seed: str | None = None
    manifest, _ = _load_json_object(bundle_dir / "suite_manifest.json", "suite_manifest.json")
    if manifest is not None:
        execution_policy = manifest.get("execution_policy")
        if isinstance(execution_policy, dict) and isinstance(
            execution_policy.get("order_policy"), str
        ):
            policy = execution_policy["order_policy"]
    metadata, _ = _load_json_object(bundle_dir / "metadata.json", "metadata.json")
    if metadata is not None:
        suite = metadata.get("suite")
        if isinstance(suite, dict):
            if policy is None and isinstance(suite.get("order_policy"), str):
                policy = suite["order_policy"]
            if isinstance(suite.get("order_row"), int) and not isinstance(
                suite.get("order_row"), bool
            ):
                row = suite["order_row"]
            if isinstance(suite.get("order_seed"), str):
                seed = suite["order_seed"]
    return policy, row, seed


def evaluate_member(
    bundle_dir: Path,
    *,
    info: ConfigInfo,
    waivers: WaiverMap,
) -> MemberEvaluation:
    status, malformed = summary_status(bundle_dir / "summary_metrics.json")
    problems: list[str] = []
    strict_valid = False
    if bundle_dir.exists():
        try:
            problems = validate_bundle(bundle_dir, strict=True)
        except Exception as exc:
            problems = [f"strict validation raised {type(exc).__name__}: {exc}"]
        strict_valid = not problems
    else:
        problems = ["bundle directory is missing"]
    if malformed is not None:
        problems = [malformed, *problems]
    summary: dict[str, Any] | None = None
    if (bundle_dir / "summary_metrics.json").is_file():
        try:
            parsed = json.loads((bundle_dir / "summary_metrics.json").read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                summary = parsed
        except (OSError, json.JSONDecodeError):
            summary = None
    prompt_hash_check = check_prompt_hashes_for_config_bundle(bundle_dir, info)
    suite_order_policy, suite_order_row, suite_order_seed = suite_order_evidence(bundle_dir)
    waiver = matching_waiver(
        waivers,
        bundle_id=bundle_dir.name,
        config_name=info.path.name,
        config_stem=info.path.stem,
        run_id=info.run_id,
    )
    return MemberEvaluation(
        bundle_id=bundle_dir.name,
        bundle_path=bundle_dir,
        config_name=info.path.name,
        status=status,
        strict_valid=strict_valid,
        validation_problems=tuple(problems),
        quality_flags=tuple(
            dict.fromkeys([*quality_flags(summary), *prompt_hash_check.quality_flags()])
        ),
        prompt_hash_check=prompt_hash_check,
        suite_order_policy=suite_order_policy,
        suite_order_row=suite_order_row,
        suite_order_seed=suite_order_seed,
        waiver=waiver,
    )


def evaluate_members(
    info: ConfigInfo, runs_dir: Path, waivers: WaiverMap
) -> list[MemberEvaluation]:
    return [
        evaluate_member(bundle_dir, info=info, waivers=waivers)
        for bundle_dir in expected_member_dirs(info, runs_dir)
    ]


def summary_status(summary_path: Path) -> tuple[str | None, str | None]:
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"{summary_path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"{summary_path}: malformed JSON ({exc.msg})"
    if not isinstance(summary, dict):
        return None, f"{summary_path}: summary_metrics.json is not a JSON object"
    status = summary.get("status")
    if not isinstance(status, str):
        return None, f"{summary_path}: summary_metrics.json lacks string status"
    return status, None


def existing_state(info: ConfigInfo, runs_dir: Path) -> ExistingState:
    if info.repetitions == 1:
        bundle_dir = runs_dir / info.run_id
        summary_path = bundle_dir / "summary_metrics.json"
        if summary_path.is_file():
            status, malformed = summary_status(summary_path)
            if malformed is not None:
                return ExistingState(
                    action="incomplete existing",
                    inspect_members=(bundle_dir.name,),
                    malformed_summaries=(malformed,),
                )
            return ExistingState(action="skip complete")
        if bundle_dir.exists():
            return ExistingState(action="incomplete existing", inspect_members=(bundle_dir.name,))
        return ExistingState(action="would run")

    members = member_bundle_dirs(runs_dir, info.run_id, info.repetitions)
    summary_paths = [member / "summary_metrics.json" for member in members]
    malformed_summaries: list[str] = []
    statuses: list[str | None] = []
    for summary_path in summary_paths:
        if summary_path.is_file():
            status, malformed = summary_status(summary_path)
            statuses.append(status)
            if malformed is not None:
                malformed_summaries.append(malformed)
        else:
            statuses.append(None)
    if malformed_summaries:
        inspect = tuple(member.name for member in members if member.exists())
        return ExistingState(
            action="incomplete existing",
            inspect_members=inspect,
            malformed_summaries=tuple(malformed_summaries),
        )
    if all(summary_path.is_file() for summary_path in summary_paths):
        non_succeeded = tuple(
            member.name
            for member, status in zip(members, statuses, strict=True)
            if status != "succeeded"
        )
        return ExistingState(
            action="skip complete",
            members_succeeded=sum(status == "succeeded" for status in statuses),
            members_total=len(members),
            non_succeeded_members=non_succeeded,
        )
    if any(member.exists() for member in members):
        inspect = tuple(member.name for member in members if member.exists())
        return ExistingState(action="incomplete existing", inspect_members=inspect)
    return ExistingState(action="would run")


def read_config_infos(config_paths: list[Path]) -> list[ConfigInfo | ConfigError]:
    items: list[ConfigInfo | ConfigError] = []
    for config_path in config_paths:
        try:
            items.append(load_config_info(config_path))
        except Exception as exc:
            items.append(
                ConfigError(
                    path=config_path,
                    message=str(exc),
                    run_id=best_effort_run_id(config_path),
                )
            )
    return items


def load_order_entries(config_dir: Path) -> tuple[list[OrderEntry], str | None]:
    path = config_dir / ORDER_MANIFEST_NAME
    if not path.is_file():
        return [], (
            f"WARNING: no {ORDER_MANIFEST_NAME} found; falling back to sorted "
            "config order. D-014 forbids silent sorted model blocks."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read order manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"order manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"order manifest must be a JSON object: {path}")
    raw_order = data.get("executed_order")
    if not isinstance(raw_order, list):
        raise ValueError(f"order manifest missing executed_order list: {path}")
    entries: list[OrderEntry] = []
    seen_configs: set[str] = set()
    seen_indexes: set[int] = set()
    for index, raw in enumerate(raw_order, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"order manifest entry {index} is not an object")
        config = raw.get("config")
        if not isinstance(config, str) or not config:
            raise ValueError(f"order manifest entry {index} missing config")
        raw_index = raw.get("index", index)
        if isinstance(raw_index, bool) or not isinstance(raw_index, int):
            raise ValueError(f"order manifest entry {index} has invalid index")
        if config in seen_configs:
            raise ValueError(f"order manifest has duplicate config entry: {config}")
        if raw_index in seen_indexes:
            raise ValueError(f"order manifest has duplicate index: {raw_index}")
        seen_configs.add(config)
        seen_indexes.add(raw_index)
        rep = raw.get("rep")
        if rep is not None and (isinstance(rep, bool) or not isinstance(rep, int)):
            raise ValueError(f"order manifest entry {index} has invalid rep")
        block_index = raw.get("block_index")
        if block_index is not None and (
            isinstance(block_index, bool) or not isinstance(block_index, int)
        ):
            raise ValueError(f"order manifest entry {index} has invalid block_index")
        position_in_block = raw.get("position_in_block")
        if position_in_block is not None and (
            isinstance(position_in_block, bool) or not isinstance(position_in_block, int)
        ):
            raise ValueError(f"order manifest entry {index} has invalid position_in_block")
        entries.append(
            OrderEntry(
                index=raw_index,
                config=config,
                run_id=raw.get("run_id") if isinstance(raw.get("run_id"), str) else None,
                model_tag=raw.get("model_tag") if isinstance(raw.get("model_tag"), str) else None,
                rep=rep,
                workload=raw.get("workload") if isinstance(raw.get("workload"), str) else None,
                role=raw.get("role") if isinstance(raw.get("role"), str) else None,
                block_index=block_index,
                position_in_block=position_in_block,
                sentinel_position=(
                    raw.get("sentinel_position")
                    if isinstance(raw.get("sentinel_position"), str)
                    else None
                ),
            )
        )
    expected_indexes = set(range(1, len(entries) + 1))
    if seen_indexes != expected_indexes:
        raise ValueError(
            "order manifest indexes must be contiguous 1.."
            f"{len(entries)} (found {sorted(seen_indexes)})"
        )
    return entries, None


def apply_order_manifest(
    config_paths: list[Path],
    order_entries: list[OrderEntry],
) -> list[Path]:
    if not order_entries:
        return config_paths
    by_name = {path.name: path for path in config_paths}
    ordered: list[Path] = []
    missing: list[str] = []
    seen: set[str] = set()
    for entry in order_entries:
        path = by_name.get(entry.config)
        if path is None:
            missing.append(entry.config)
            continue
        ordered.append(path)
        seen.add(entry.config)
    extras = sorted(name for name in by_name if name not in seen)
    if missing or extras:
        parts: list[str] = []
        if missing:
            parts.append("manifest references missing config(s): " + ", ".join(missing))
        if extras:
            parts.append("config(s) absent from manifest: " + ", ".join(extras))
        raise ValueError("; ".join(parts))
    return ordered


def order_entry_by_config(order_entries: list[OrderEntry]) -> dict[str, OrderEntry]:
    return {entry.config: entry for entry in order_entries}


def duplicate_run_id_error(items: list[ConfigInfo | ConfigError]) -> str | None:
    by_run_id: dict[str, list[Path]] = {}
    for item in items:
        if isinstance(item, ConfigInfo):
            by_run_id.setdefault(item.run_id, []).append(item.path)
    collisions = {run_id: paths for run_id, paths in by_run_id.items() if len(paths) > 1}
    if not collisions:
        return None
    parts = [
        f"{run_id}: {', '.join(str(path) for path in paths)}"
        for run_id, paths in sorted(collisions.items())
    ]
    return "duplicate sanitized run_id(s): " + "; ".join(parts)


def acquire_campaign_lock(runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    lock_path = runs_dir / "campaign.lock"
    content = f"pid={os.getpid()} created_at={utc_timestamp()}\n"
    try:
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        try:
            existing = lock_path.read_text(encoding="utf-8").strip()
        except OSError:
            existing = "<unreadable>"
        raise RuntimeError(
            f"another campaign appears to be running (lock {lock_path}, created {existing}); "
            "if no campaign is running, delete the lock file and retry"
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    return lock_path


def skipped_log_extra(state: ExistingState) -> dict[str, Any] | None:
    if state.members_total is None:
        return None
    return {
        "members_succeeded": state.members_succeeded,
        "members_total": state.members_total,
    }


def classify_campaign_members(
    evaluations: list[MemberEvaluation],
    missing: list[str],
) -> dict[str, list[str]]:
    categories = {"usable": [], "waived": [], "failed": [], "missing": []}
    for evaluation in evaluations:
        if evaluation.usable:
            categories["usable"].append(evaluation.bundle_id)
        elif evaluation.waived:
            categories["waived"].append(evaluation.bundle_id)
        else:
            categories["failed"].append(evaluation.bundle_id)
    categories["missing"].extend(missing)
    return categories


def evaluation_failure_detail(evaluation: MemberEvaluation) -> str:
    parts = [
        f"{evaluation.bundle_id}: status={evaluation.status!r}",
        f"strict_valid={evaluation.strict_valid}",
        f"quality_flags={list(evaluation.quality_flags)}",
        f"validation_problems={list(evaluation.validation_problems)}",
    ]
    if evaluation.prompt_hash_check.status != "not_applicable":
        parts.append(f"prompt_hash_check={evaluation.prompt_hash_check.to_log()!r}")
    return ", ".join(parts)


def verdict_for(categories: dict[str, list[str]]) -> tuple[str, list[str]]:
    usable = categories["usable"]
    waived = categories["waived"]
    failed = categories["failed"]
    missing = categories["missing"]
    reasons: list[str] = []
    if missing:
        reasons.append("missing member bundle(s): " + ", ".join(missing))
    if failed:
        reasons.append("invalid unwaived member bundle(s): " + ", ".join(failed))
    if waived:
        reasons.append("waived member bundle(s): " + ", ".join(waived))
    if not usable and not waived and not failed and not missing:
        return "invalid", ["no campaign members were evaluated"]
    if missing:
        return "blocked", reasons
    if failed:
        return "invalid", reasons
    if usable and not waived:
        return "publishable", ["all campaign members are usable"]
    if usable and waived:
        return "partial", reasons
    if waived:
        return "invalid", reasons + ["no usable unwaived members"]
    return "invalid", reasons or ["no usable members"]


def print_verdict(verdict: str, reasons: list[str], categories: dict[str, list[str]]) -> None:
    print("VERDICT:")
    print(f"  verdict: {verdict}")
    for reason in reasons:
        print(f"  reason: {reason}")
    for key in ("usable", "waived", "failed", "missing"):
        members = ", ".join(categories[key]) if categories[key] else "<none>"
        print(f"  {key}: {members}")


def append_verdict(
    log_path: Path,
    *,
    verdict: str,
    reasons: list[str],
    categories: dict[str, list[str]],
    warning: str | None,
) -> None:
    row: dict[str, Any] = {
        "timestamp": utc_timestamp(),
        "record_type": "campaign_verdict",
        "status": "verdict",
        "verdict": verdict,
        "reasons": reasons,
        "usable": categories["usable"],
        "waived": categories["waived"],
        "failed": categories["failed"],
        "missing": categories["missing"],
        "taxonomy": {
            "publishable": "all members usable",
            "partial": "at least one usable member and at least one waived or failed member; all-waived is invalid",
            "blocked": "one or more expected member bundles are missing",
            "invalid": "one or more invalid unwaived members, or no members were evaluated",
        },
    }
    if warning is not None:
        row["block_order_warning"] = warning
    append_log(log_path, row)


def run_campaign(args: argparse.Namespace) -> int:
    assert args.config_dir is not None
    config_dir = Path(args.config_dir)
    runs_dir = Path(args.runs_dir)
    log_path = Path(args.log) if args.log else runs_dir / "campaign_log.jsonl"

    if args.max_failures < 1:
        raise ValueError("--max-failures must be >= 1")

    order_entries, order_warning = load_order_entries(config_dir)
    if order_warning is not None:
        print(order_warning, file=sys.stderr)
    configs = apply_order_manifest(discover_configs(config_dir), order_entries)
    order_by_config = order_entry_by_config(order_entries)
    print_config_file_list(configs)
    items = read_config_infos(configs)
    waivers = load_waivers(args.waivers)
    config_errors = [item for item in items if isinstance(item, ConfigError)]
    if config_errors:
        for item in config_errors:
            print(f"error: {item.message}", file=sys.stderr)
        return 2
    duplicate_error = duplicate_run_id_error(items)
    if duplicate_error is not None:
        print(f"error: {duplicate_error}", file=sys.stderr)
        return 2

    counts: Counter[str] = Counter()
    failures = 0
    lock_path: Path | None = None
    all_evaluations: list[MemberEvaluation] = []
    missing_members: list[str] = []
    previous_model_tag: str | None = None

    print_quiet_machine_warning()
    if args.dry_run:
        print("Dry run: no commands will be invoked and no campaign log will be written.")
    else:
        try:
            lock_path = acquire_campaign_lock(runs_dir)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    try:
        for item in items:
            if isinstance(item, ConfigError):
                if args.dry_run:
                    counts["dry_run"] += 1
                    print(f"dry_run {item.path}: config error: {item.message}", file=sys.stderr)
                    continue
                failures += 1
                print(f"error: {item.message}", file=sys.stderr)
                append_log(
                    log_path,
                    log_row(
                        config_path=item.path,
                        run_id=item.run_id,
                        status="config_error",
                        exit_code=None,
                        duration_s=None,
                        extra={"error": item.message},
                    ),
                )
                counts["config_error"] += 1
                if failures >= args.max_failures:
                    break
                continue

            info = item
            config_path = info.path
            order_entry = order_by_config.get(config_path.name)
            model_boundary = (
                order_entry is not None
                and order_entry.model_tag is not None
                and order_entry.model_tag != previous_model_tag
            )
            if order_entry is not None and order_entry.model_tag is not None:
                previous_model_tag = order_entry.model_tag
            order_extra: dict[str, Any] = {}
            if order_entry is not None:
                order_extra = {
                    "run_index": order_entry.index,
                    "executed_order": order_entry.to_log(),
                    "model_load_boundary": model_boundary,
                }
            elif order_warning is not None:
                order_extra = {"block_order_warning": order_warning}
            state = existing_state(info, runs_dir)
            command = command_for(config_path, runs_dir, args.cli_cmd)

            if args.dry_run:
                counts["dry_run"] += 1
                print(f"dry_run {info.run_id}: {state.action}: {shell_quote(command)}")
                continue

            if state.action == "skip complete":
                evaluations = evaluate_members(info, runs_dir, waivers)
                all_evaluations.extend(evaluations)
                failed = [evaluation for evaluation in evaluations if evaluation.failed]
                if failed:
                    failures += 1
                    status = "failed"
                    details = "; ".join(evaluation_failure_detail(evaluation) for evaluation in failed)
                    print(
                        f"failed {info.run_id}: existing bundle(s) are not skippable: "
                        f"{details}; inspect or move those bundle(s), or provide an "
                        "explicit campaign waiver",
                        file=sys.stderr,
                    )
                else:
                    status = (
                        "waived"
                        if any(evaluation.waived for evaluation in evaluations)
                        else "skipped"
                    )
                exit_code = None
                duration_s = None
                if status != "failed" and state.members_total is None:
                    print(f"skipped {info.run_id}: complete bundle already exists")
                elif status != "failed":
                    print(
                        f"skipped {info.run_id}: complete experiment already exists "
                        f"({state.members_succeeded}/{state.members_total} members succeeded)"
                    )
                    waived = [evaluation.bundle_id for evaluation in evaluations if evaluation.waived]
                    if waived:
                        print(
                            f"note: skipped experiment {info.run_id} has waived member(s): "
                            f"{', '.join(waived)}",
                            file=sys.stderr,
                        )
                extra = {
                    **(skipped_log_extra(state) or {}),
                    **order_extra,
                    "members": [evaluation.to_log() for evaluation in evaluations],
                }
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status=status,
                        exit_code=exit_code,
                        duration_s=duration_s,
                        extra=extra,
                    ),
                )
                counts[status] += 1
                if failures >= args.max_failures:
                    break
                continue

            if state.action == "incomplete existing":
                status = "incomplete_existing"
                exit_code = None
                duration_s = None
                failures += 1
                if state.inspect_members:
                    missing_members.extend(
                        member.name
                        for member in expected_member_dirs(info, runs_dir)
                        if not member.exists()
                    )
                inspect = ", ".join(state.inspect_members) if state.inspect_members else info.run_id
                if state.malformed_summaries:
                    detail = "malformed summary_metrics.json: " + "; ".join(state.malformed_summaries)
                elif info.repetitions == 1:
                    detail = f"{inspect} lacks summary_metrics.json"
                else:
                    detail = f"partial experiment members exist: {inspect}"
                print(
                    f"incomplete_existing {info.run_id}: {detail}; inspect or move those "
                    "bundle(s) before retrying",
                    file=sys.stderr,
                )
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status=status,
                        exit_code=exit_code,
                        duration_s=duration_s,
                        extra=order_extra,
                    ),
                )
                counts[status] += 1
                if failures >= args.max_failures:
                    break
                continue

            start = time.monotonic()
            result = subprocess.run(command, check=False)
            duration_s = time.monotonic() - start
            exit_code = result.returncode
            evaluations = evaluate_members(info, runs_dir, waivers)
            all_evaluations.extend(evaluations)
            missing_after_run = [
                evaluation.bundle_id
                for evaluation in evaluations
                if not evaluation.bundle_path.exists()
            ]
            missing_members.extend(missing_after_run)
            failed_members = [evaluation for evaluation in evaluations if evaluation.failed]
            if exit_code == 0 and not failed_members and not missing_after_run:
                status = (
                    "waived"
                    if any(evaluation.waived for evaluation in evaluations)
                    else "ok"
                )
            else:
                status = "failed"
            if status == "failed":
                failures += 1
                if exit_code == 0:
                    details = "; ".join(
                        evaluation_failure_detail(evaluation)
                        for evaluation in failed_members
                    )
                    if missing_after_run:
                        details = (details + "; " if details else "") + (
                            "missing: " + ", ".join(missing_after_run)
                        )
                    print(
                        f"failed {info.run_id}: exit=0 but strict campaign validation "
                        f"did not pass: {details}",
                        file=sys.stderr,
                    )
            extra = {
                **order_extra,
                "members": [evaluation.to_log() for evaluation in evaluations],
            }
            append_log(
                log_path,
                log_row(
                    config_path=config_path,
                    run_id=info.run_id,
                    status=status,
                    exit_code=exit_code,
                    duration_s=duration_s,
                    extra=extra,
                ),
            )
            counts[status] += 1
            print(f"{status} {info.run_id}: exit={exit_code} duration_s={duration_s:.3f}")

            if status == "ok" and args.backup is not None:
                backup_runs(runs_dir, backup_script_path(args.backup))

            if failures >= args.max_failures:
                break
    finally:
        if lock_path is not None:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    print("Summary:")
    for status in STATUSES:
        if counts[status]:
            print(f"  {status}: {counts[status]}")
    if args.dry_run:
        return 0
    categories = classify_campaign_members(all_evaluations, missing_members)
    verdict, reasons = verdict_for(categories)
    print_verdict(verdict, reasons, categories)
    if not args.dry_run:
        append_verdict(
            log_path,
            verdict=verdict,
            reasons=reasons,
            categories=categories,
            warning=order_warning,
        )
    return 1 if failures or verdict in {"blocked", "invalid"} else 0


def run_prompt_hash_check(args: argparse.Namespace) -> int:
    bundle_text, sidecar_text = args.check_prompt_hashes
    result = check_prompt_hashes_for_bundle(Path(bundle_text), Path(sidecar_text))
    print(json.dumps(result.to_log(), sort_keys=True))
    if result.status in {"matched", "not_applicable"}:
        return 0
    if result.status == "mismatch":
        return 1
    return 2


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check_prompt_hashes is not None:
            return run_prompt_hash_check(args)
        return run_campaign(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
