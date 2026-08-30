#!/usr/bin/env python3
"""Verify one model-panel entry against an offline local mirror."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.model_panel import ModelPanelError, load_model_panel  # noqa: E402


RECEIPT_SCHEMA = "joulewise.model_panel_admission_receipt.v1"
ADMISSION_REFUSAL_REASONS = frozenset(
    {
        "model_panel_invalid",
        "model_not_found",
        "admission_status_refused",
        "mirror_missing",
        "mirror_not_directory",
        "provenance_missing",
        "revision_mismatch",
        "provenance_json_invalid",
        "tokenizer_missing",
        "tokenizer_sha256_mismatch",
        "config_missing",
        "config_json_invalid",
        "vocab_size_mismatch",
        "weight_files_missing",
        "weight_file_empty",
        "weight_size_mismatch",
    }
)
MEASUREMENT_MACHINE_GATES = (
    {
        "gate": "three_runtime_generation_check",
        "status": "needs_measurement_machine",
        "authority": "D-074",
    },
    {
        "gate": "g10_peak_memory_cap",
        "status": "needs_measurement_machine",
        "authority": "D-073/D-074",
    },
    {
        "gate": "kv_receipts",
        "status": "needs_measurement_machine",
        "authority": "D-074",
    },
)
_WEIGHT_SUFFIXES = frozenset({".safetensors", ".bin", ".gguf", ".pth", ".pt"})


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check(status: str, **details: Any) -> dict[str, Any]:
    return {"status": status, **details}


def _weight_files(mirror: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in mirror.iterdir()
            if path.is_file() and path.suffix.lower() in _WEIGHT_SUFFIXES
        ),
        key=lambda path: path.name,
    )


def verify_entry(panel_path: Path, entry: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic receipt; callers decide where to serialize it."""

    mirror = Path(str(entry["source"])).expanduser()
    revision = str(entry["revision"])
    reasons: set[str] = set()
    checks: dict[str, Any] = {}

    if entry["admission"]["status"] == "refused":
        reasons.add("admission_status_refused")

    if not mirror.exists():
        reasons.add("mirror_missing")
        checks["mirror"] = _check("refused", path=str(mirror), observed="missing")
    elif not mirror.is_dir():
        reasons.add("mirror_not_directory")
        checks["mirror"] = _check("refused", path=str(mirror), observed="not_directory")
    else:
        checks["mirror"] = _check("passed", path=str(mirror))

    provenance: Mapping[str, Any] | None = None
    tree_dir = mirror / ".cache" / "huggingface" / "trees"
    expected_tree = tree_dir / f"{revision}.json"
    if mirror.is_dir():
        observed_revisions = sorted(
            path.stem
            for path in tree_dir.glob("*.json")
            if path.is_file()
        ) if tree_dir.is_dir() else []
        if not tree_dir.is_dir() or not observed_revisions:
            reasons.add("provenance_missing")
            checks["revision_provenance"] = _check(
                "refused",
                expected_revision=revision,
                observed_revisions=observed_revisions,
            )
        elif not expected_tree.is_file():
            reasons.add("revision_mismatch")
            checks["revision_provenance"] = _check(
                "refused",
                expected_revision=revision,
                observed_revisions=observed_revisions,
            )
        else:
            try:
                parsed = json.loads(expected_tree.read_text(encoding="utf-8"))
                if not isinstance(parsed, dict) or not isinstance(parsed.get("files"), dict):
                    raise ValueError("tree receipt must contain an object-valued files map")
                provenance = parsed
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                reasons.add("provenance_json_invalid")
                checks["revision_provenance"] = _check(
                    "refused", expected_revision=revision, detail=str(exc)
                )
            else:
                checks["revision_provenance"] = _check(
                    "passed",
                    expected_revision=revision,
                    observed_revisions=observed_revisions,
                    tree_receipt=str(expected_tree),
                    tree_receipt_sha256=sha256_file(expected_tree),
                )

    tokenizer = mirror / "tokenizer.json"
    expected_tokenizer_sha = str(entry["tokenizer_json_sha256"])
    if mirror.is_dir():
        if not tokenizer.is_file():
            reasons.add("tokenizer_missing")
            checks["tokenizer_json"] = _check(
                "refused", path=str(tokenizer), expected_sha256=expected_tokenizer_sha
            )
        else:
            observed_tokenizer_sha = sha256_file(tokenizer)
            tokenizer_status = (
                "passed" if observed_tokenizer_sha == expected_tokenizer_sha else "refused"
            )
            if tokenizer_status == "refused":
                reasons.add("tokenizer_sha256_mismatch")
            checks["tokenizer_json"] = _check(
                tokenizer_status,
                path=str(tokenizer),
                expected_sha256=expected_tokenizer_sha,
                observed_sha256=observed_tokenizer_sha,
            )

    config = mirror / "config.json"
    expected_vocab_size = entry["vocab_size"]
    if mirror.is_dir():
        if not config.is_file():
            reasons.add("config_missing")
            checks["config_vocab_size"] = _check(
                "refused", path=str(config), expected=expected_vocab_size
            )
        else:
            try:
                config_value = json.loads(config.read_text(encoding="utf-8"))
                if not isinstance(config_value, dict):
                    raise ValueError("config.json must contain an object")
                observed_vocab_size = config_value.get("vocab_size")
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                reasons.add("config_json_invalid")
                checks["config_vocab_size"] = _check(
                    "refused", path=str(config), detail=str(exc)
                )
            else:
                vocab_status = (
                    "passed" if observed_vocab_size == expected_vocab_size else "refused"
                )
                if vocab_status == "refused":
                    reasons.add("vocab_size_mismatch")
                checks["config_vocab_size"] = _check(
                    vocab_status,
                    path=str(config),
                    expected=expected_vocab_size,
                    observed=observed_vocab_size,
                    config_sha256=sha256_file(config),
                )

    if mirror.is_dir():
        weights = _weight_files(mirror)
        weight_rows: list[dict[str, Any]] = []
        if not weights:
            reasons.add("weight_files_missing")
        provenance_files = provenance.get("files", {}) if provenance is not None else {}
        for weight in weights:
            observed_size = weight.stat().st_size
            provenance_row = provenance_files.get(weight.name)
            expected_size = (
                provenance_row.get("size") if isinstance(provenance_row, dict) else None
            )
            status = "passed"
            if observed_size <= 0:
                reasons.add("weight_file_empty")
                status = "refused"
            if expected_size is not None and observed_size != expected_size:
                reasons.add("weight_size_mismatch")
                status = "refused"
            weight_rows.append(
                {
                    "path": str(weight),
                    "size_bytes": observed_size,
                    "provenance_size_bytes": expected_size,
                    "status": status,
                }
            )
        checks["weights"] = _check(
            "passed" if weights and all(row["status"] == "passed" for row in weight_rows) else "refused",
            files=weight_rows,
            total_size_bytes=sum(row["size_bytes"] for row in weight_rows),
        )

    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "status": "passed" if not reasons else "refused",
        "reason_codes": sorted(reasons),
        "panel": {
            "path": str(panel_path),
            "sha256": sha256_file(panel_path),
        },
        "model_entry": {
            "model_id": entry["model_id"],
            "canonical_sha256": sha256_bytes(canonical_json_bytes(entry)),
            "admission_status": entry["admission"]["status"],
        },
        "checks": checks,
        "measurement_machine_gates": list(MEASUREMENT_MACHINE_GATES),
    }
    unknown = set(receipt["reason_codes"]) - ADMISSION_REFUSAL_REASONS
    if unknown:
        raise AssertionError(f"unregistered admission refusal reasons: {sorted(unknown)}")
    return receipt


def error_receipt(panel_path: Path, model_id: str, error: ModelPanelError) -> dict[str, Any]:
    reason_codes = (
        ["model_not_found"]
        if len(error.refusals) == 1
        and error.refusals[0].reason == "model_panel_model_not_found"
        else ["model_panel_invalid"]
    )
    return {
        "schema_version": RECEIPT_SCHEMA,
        "status": "refused",
        "reason_codes": reason_codes,
        "panel": {
            "path": str(panel_path),
            "sha256": sha256_file(panel_path) if panel_path.is_file() else None,
        },
        "model_entry": {"model_id": model_id, "canonical_sha256": None},
        "checks": {
            "model_panel": _check(
                "refused",
                refusals=[
                    {"reason": row.reason, "path": row.path, "detail": row.detail}
                    for row in error.refusals
                ],
            )
        },
        "measurement_machine_gates": list(MEASUREMENT_MACHINE_GATES),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", required=True, type=Path)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--out", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    panel_path = args.panel.absolute()
    try:
        panel = load_model_panel(panel_path)
        entry = panel.get(args.model_id)
    except ModelPanelError as exc:
        receipt = error_receipt(panel_path, args.model_id, exc)
    else:
        receipt = verify_entry(panel_path, entry)

    raw = canonical_json_bytes(receipt)
    if args.out is None:
        sys.stdout.buffer.write(raw)
    else:
        output_path = args.out.absolute()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(raw)
        print(output_path)
    if receipt["status"] != "passed":
        print(
            "admission refused: " + ",".join(receipt["reason_codes"]),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
