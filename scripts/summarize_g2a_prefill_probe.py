#!/usr/bin/env python3
"""Authenticate G2-a probe inputs and summarize prefill overlap counts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence


INVENTORY_SCHEMA = "joulewise.g2a_input_inventory.v1"
ORDER_MANIFEST_SCHEMA = "joulewise.order_manifest.v1"
LADDER = (512, 1024, 2048, 4096)
MODEL_ROLES = ("small", "large")
MIN_SMALL_MEMBERS = 5
MIN_LARGE_MEMBERS = 1
MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5
REDUCER_MIN_PHASE_SAMPLES = 3
REPO_ROOT = Path(__file__).resolve().parents[1]


class ProbeSummaryError(ValueError):
    """The probe inputs cannot authorize a G2-a summary."""


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProbeSummaryError(f"duplicate_key:{key}")
        value[key] = item
    return value


def _load_json(path: Path, *, label: str) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProbeSummaryError(f"{label}_unreadable:{path}:{exc}") from exc
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_strict_object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ProbeSummaryError(f"non_finite_number:{token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeSummaryError(f"{label}_invalid_json:{path}:{exc}") from exc
    return value, raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_exact_keys(value: Any, keys: set[str], *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ProbeSummaryError(f"{label}_closed_schema_mismatch")
    return value


def _require_int(value: Any, *, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ProbeSummaryError(f"{label}_invalid")
    return value


def _resolve_inventory_config_root(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ProbeSummaryError("inventory_config_root_invalid")
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def _confined_path(root: Path, relative: Any, *, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ProbeSummaryError(f"{label}_invalid")
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ProbeSummaryError(f"{label}_must_be_relative")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ProbeSummaryError(f"{label}_escapes_config_root") from exc
    return resolved


def _validate_bound_file(value: Any, *, label: str, plan_id: bool = False) -> None:
    keys = {"path", "sha256"}
    if plan_id:
        keys.add("plan_id")
    item = _require_exact_keys(value, keys, label=label)
    if not isinstance(item["path"], str) or not item["path"].strip():
        raise ProbeSummaryError(f"{label}_path_invalid")
    if not _is_sha256(item["sha256"]):
        raise ProbeSummaryError(f"{label}_sha256_invalid")
    if plan_id and (
        not isinstance(item["plan_id"], str) or not item["plan_id"].strip()
    ):
        raise ProbeSummaryError(f"{label}_plan_id_invalid")
    path = Path(item["path"])
    if not path.is_absolute():
        path = REPO_ROOT / path
    _value, raw = _load_json(path.resolve(), label=label)
    if _sha256(raw) != item["sha256"]:
        raise ProbeSummaryError(f"{label}_sha256_mismatch")
    if plan_id:
        if not isinstance(_value, dict) or _value.get("plan_id") != item["plan_id"]:
            raise ProbeSummaryError(f"{label}_plan_id_mismatch")


def _validate_inventory_header(inventory: Any, *, config_root: Path) -> list[Any]:
    keys = {
        "schema_version",
        "config_root",
        "panel",
        "campaign_policy",
        "prompt_ladder",
        "identity_epoch",
        "t1_bindings",
        "calibration_plan",
        "power_policy",
        "evidence_root_id",
        "window_id",
        "session_id",
        "stages",
    }
    value = _require_exact_keys(inventory, keys, label="inventory")
    if value["schema_version"] != INVENTORY_SCHEMA:
        raise ProbeSummaryError("inventory_schema_version_invalid")
    if _resolve_inventory_config_root(value["config_root"]) != config_root:
        raise ProbeSummaryError("inventory_config_root_mismatch")
    for label in (
        "panel",
        "campaign_policy",
        "prompt_ladder",
        "identity_epoch",
        "t1_bindings",
    ):
        _validate_bound_file(value[label], label=f"inventory_{label}")
    _validate_bound_file(
        value["calibration_plan"],
        label="inventory_calibration_plan",
        plan_id=True,
    )
    if value["power_policy"] != "ac_high_power":
        raise ProbeSummaryError("inventory_power_policy_invalid")
    for label in ("evidence_root_id", "window_id", "session_id"):
        if not isinstance(value[label], str) or not value[label].strip():
            raise ProbeSummaryError(f"inventory_{label}_invalid")
    stages = value["stages"]
    if not isinstance(stages, list) or len(stages) != 8:
        raise ProbeSummaryError("inventory_expected_eight_stages")
    return stages


def _validate_config(
    value: Any,
    *,
    run_id: str,
    model_name: str,
    prefill_tokens: int,
) -> None:
    if not isinstance(value, dict):
        raise ProbeSummaryError(f"config_not_object:{run_id}")
    if value.get("schema_version") != "0.1":
        raise ProbeSummaryError(f"config_schema_version_invalid:{run_id}")
    if value.get("run_id") != run_id:
        raise ProbeSummaryError(f"config_run_id_mismatch:{run_id}")
    model = value.get("model")
    if not isinstance(model, dict) or model.get("name") != model_name:
        raise ProbeSummaryError(f"config_model_mismatch:{run_id}")
    workload = value.get("workload_profile")
    if not isinstance(workload, dict):
        raise ProbeSummaryError(f"config_workload_missing:{run_id}")
    if (
        workload.get("repetitions") != 1
        or workload.get("warmup_runs") != 1
        or workload.get("output_tokens") != 512
        or not isinstance(workload.get("prompt_text"), str)
        or not workload["prompt_text"]
        or "prompt_tokens" in workload
    ):
        raise ProbeSummaryError(f"config_workload_shape_mismatch:{run_id}")
    metadata = value.get("run_metadata")
    tags = metadata.get("tags") if isinstance(metadata, dict) else None
    if not isinstance(tags, list) or f"prompt-tokens={prefill_tokens}" not in tags:
        raise ProbeSummaryError(f"config_prefill_length_unbound:{run_id}")


def _manifest_entries(
    value: Any,
    *,
    expected_count: int,
    label: str,
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise ProbeSummaryError(f"{label}_not_object")
    if value.get("schema_version") != ORDER_MANIFEST_SCHEMA:
        raise ProbeSummaryError(f"{label}_schema_version_invalid")
    if "planned_n_bundles" in value and value["planned_n_bundles"] != expected_count:
        raise ProbeSummaryError(f"{label}_planned_count_mismatch")
    rows = value.get("executed_order")
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ProbeSummaryError(f"{label}_member_count_mismatch")
    indexes: list[int] = []
    by_config: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ProbeSummaryError(f"{label}_entry_not_object")
        index = _require_int(row.get("index"), label=f"{label}_index", minimum=1)
        config = row.get("config")
        run_id = row.get("run_id")
        digest = row.get("config_sha256")
        if (
            not isinstance(config, str)
            or not config
            or Path(config).name != config
            or config in by_config
        ):
            raise ProbeSummaryError(f"{label}_config_invalid_or_duplicate")
        if not isinstance(run_id, str) or not run_id.strip():
            raise ProbeSummaryError(f"{label}_run_id_invalid")
        if not _is_sha256(digest):
            raise ProbeSummaryError(f"{label}_config_sha256_invalid")
        indexes.append(index)
        by_config[config] = row
    if sorted(indexes) != list(range(1, expected_count + 1)):
        raise ProbeSummaryError(f"{label}_indexes_not_contiguous")
    return by_config


def _prefill_count(summary: Any, *, run_id: str) -> int:
    try:
        count = summary["window_evidence_precheck"]["phase"]["prefill"][
            "windows"
        ][0]["in_window_sample_count"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProbeSummaryError(f"summary_prefill_count_missing:{run_id}") from exc
    return _require_int(count, label=f"summary_prefill_count:{run_id}")


def summarize(
    *,
    config_root: Path,
    input_inventory: Path,
    runs_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return authenticated member rows and the selector's four-row summary."""

    config_root = config_root.resolve()
    runs_root = runs_root.resolve()
    inventory, _inventory_raw = _load_json(input_inventory, label="inventory")
    stages = _validate_inventory_header(inventory, config_root=config_root)
    expected_stages = [
        (role, length) for role in MODEL_ROLES for length in LADDER
    ]
    member_rows: list[dict[str, Any]] = []
    seen_run_ids: set[str] = set()

    for stage, (expected_role, expected_length) in zip(
        stages, expected_stages, strict=True
    ):
        stage = _require_exact_keys(
            stage,
            {
                "stage_id",
                "model_role",
                "model_name",
                "prefill_tokens",
                "manifest",
                "members",
            },
            label="inventory_stage",
        )
        stage_id = f"{expected_role}-p{expected_length}"
        if (
            stage["stage_id"] != stage_id
            or stage["model_role"] != expected_role
            or stage["prefill_tokens"] != expected_length
            or not isinstance(stage["model_name"], str)
            or not stage["model_name"].strip()
        ):
            raise ProbeSummaryError(f"inventory_stage_order_or_identity_mismatch:{stage_id}")
        members = stage["members"]
        if not isinstance(members, list):
            raise ProbeSummaryError(f"inventory_stage_members_invalid:{stage_id}")
        minimum = MIN_SMALL_MEMBERS if expected_role == "small" else MIN_LARGE_MEMBERS
        if len(members) < minimum:
            raise ProbeSummaryError(f"inventory_stage_member_floor_not_met:{stage_id}")

        manifest_binding = _require_exact_keys(
            stage["manifest"], {"path", "sha256"}, label=f"{stage_id}_manifest_binding"
        )
        if not _is_sha256(manifest_binding["sha256"]):
            raise ProbeSummaryError(f"manifest_sha256_invalid:{stage_id}")
        manifest_path = _confined_path(
            config_root, manifest_binding["path"], label=f"{stage_id}_manifest_path"
        )
        expected_stage_dir = (config_root / stage_id).resolve()
        if manifest_path != expected_stage_dir / "order_manifest.json":
            raise ProbeSummaryError(f"manifest_path_mismatch:{stage_id}")
        manifest, manifest_raw = _load_json(manifest_path, label="manifest")
        if _sha256(manifest_raw) != manifest_binding["sha256"]:
            raise ProbeSummaryError(f"manifest_sha256_mismatch:{stage_id}")
        by_manifest_config = _manifest_entries(
            manifest, expected_count=len(members), label=f"manifest:{stage_id}"
        )

        by_inventory_config: set[str] = set()
        for expected_index, member in enumerate(members):
            member = _require_exact_keys(
                member,
                {"index", "run_id", "config_path", "config_sha256"},
                label=f"inventory_member:{stage_id}",
            )
            if member["index"] != expected_index:
                raise ProbeSummaryError(f"inventory_member_index_mismatch:{stage_id}")
            run_id = member["run_id"]
            if not isinstance(run_id, str) or not run_id.strip():
                raise ProbeSummaryError(f"inventory_member_run_id_invalid:{stage_id}")
            if run_id in seen_run_ids:
                raise ProbeSummaryError(f"duplicate_run_id:{run_id}")
            seen_run_ids.add(run_id)
            if not _is_sha256(member["config_sha256"]):
                raise ProbeSummaryError(f"inventory_config_sha256_invalid:{run_id}")
            config_path = _confined_path(
                config_root, member["config_path"], label=f"config_path:{run_id}"
            )
            if config_path.parent != expected_stage_dir:
                raise ProbeSummaryError(f"config_stage_mismatch:{run_id}")
            config_name = config_path.name
            if config_name in by_inventory_config:
                raise ProbeSummaryError(f"duplicate_config_path:{config_name}")
            by_inventory_config.add(config_name)
            manifest_row = by_manifest_config.get(config_name)
            if manifest_row is None:
                raise ProbeSummaryError(f"manifest_member_missing:{run_id}")
            if manifest_row["run_id"] != run_id:
                raise ProbeSummaryError(f"manifest_run_id_mismatch:{run_id}")
            if manifest_row["config_sha256"] != member["config_sha256"]:
                raise ProbeSummaryError(f"manifest_inventory_hash_mismatch:{run_id}")
            config, config_raw = _load_json(config_path, label="config")
            if _sha256(config_raw) != member["config_sha256"]:
                raise ProbeSummaryError(f"config_sha256_mismatch:{run_id}")
            _validate_config(
                config,
                run_id=run_id,
                model_name=stage["model_name"],
                prefill_tokens=expected_length,
            )
            summary_path = runs_root / run_id / "summary_metrics.json"
            summary, _summary_raw = _load_json(summary_path, label="summary")
            count = _prefill_count(summary, run_id=run_id)
            member_rows.append(
                {
                    "prefill_tokens": expected_length,
                    "run_id": run_id,
                    "model_role": expected_role,
                    "overlapping_power_interval_count": count,
                    "overlap_margin_above_three": (
                        count - REDUCER_MIN_PHASE_SAMPLES
                    ),
                }
            )

        discovered = {
            path.name
            for path in expected_stage_dir.glob("*.json")
            if path.name != "order_manifest.json"
        }
        if discovered != by_inventory_config:
            raise ProbeSummaryError(f"stage_config_cover_mismatch:{stage_id}")
        if set(by_manifest_config) != by_inventory_config:
            raise ProbeSummaryError(f"manifest_config_cover_mismatch:{stage_id}")

    summary_rows: list[dict[str, Any]] = []
    for length in LADDER:
        small = [
            row
            for row in member_rows
            if row["prefill_tokens"] == length and row["model_role"] == "small"
        ]
        large = [
            row
            for row in member_rows
            if row["prefill_tokens"] == length and row["model_role"] == "large"
        ]
        if len(small) < MIN_SMALL_MEMBERS or len(large) < MIN_LARGE_MEMBERS:
            raise ProbeSummaryError(f"authenticated_member_floor_not_met:{length}")
        minimum_count = min(
            row["overlapping_power_interval_count"] for row in small
        )
        summary_rows.append(
            {
                "length": length,
                "small_members": len(small),
                "large_members": len(large),
                "small_minimum_count": minimum_count,
                "all_small_count_ge_5": (
                    minimum_count >= MIN_OVERLAPPING_POWER_INTERVAL_COUNT
                ),
            }
        )
    return member_rows, summary_rows


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (
            json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        for row in rows
    )


def _summary_bytes(rows: list[dict[str, Any]]) -> bytes:
    return (
        json.dumps(rows, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write_new(path: Path, raw: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(raw)
    except OSError as exc:
        raise ProbeSummaryError(f"output_unwritable:{path}:{exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-root", required=True, type=Path)
    parser.add_argument("--input-inventory", required=True, type=Path)
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument("--counts-output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.counts_output.resolve() == args.summary_output.resolve():
            raise ProbeSummaryError("output_paths_must_differ")
        if args.counts_output.exists() or args.summary_output.exists():
            raise ProbeSummaryError("output_already_exists")
        member_rows, summary_rows = summarize(
            config_root=args.config_root,
            input_inventory=args.input_inventory,
            runs_root=args.runs_root,
        )
        _write_new(args.counts_output, _jsonl_bytes(member_rows))
        _write_new(args.summary_output, _summary_bytes(summary_rows))
    except ProbeSummaryError as exc:
        print(f"G2-a probe summary refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
