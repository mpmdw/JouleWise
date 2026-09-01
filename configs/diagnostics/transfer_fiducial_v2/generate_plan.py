#!/usr/bin/env python3
"""Generate the Qwen3-small TRANSFER-FIDUCIAL-01 successor plan.

The generator deliberately needs three G2-a artifacts.  The four-row summary
contains the measured sample counts, the selection record chooses a prefill
rung and authenticates those exact summary bytes, and the prompt pin supplies
the exact text and token identifiers at that rung.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from configs.campaigns.d117_contrast_v5 import generate_configs as v5  # noqa: E402
from joulewise.schemas import BenchmarkConfig  # noqa: E402
from joulewise.transfer_fiducial import (  # noqa: E402
    TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND_V2,
    TRANSFER_FIDUCIAL_GAP_S_V1,
    TRANSFER_FIDUCIAL_PLAN_SCHEMA_V2,
    transfer_fiducial_rule_constants,
)


OUTPUT_REL = Path("configs/diagnostics/transfer_fiducial_v2")
SELECTION_SCHEMA = "joulewise.g2a_prefill_selection.v1"
LADDER = (512, 1024, 2048, 4096)
MODEL_PANEL = REPO_ROOT / "configs/model_panels/qwen3_4bit.json"
SMALL_MODEL_ID = "qwen3-1p7b"
RUN_COUNT = 10
OUTPUT_TOKENS = 512
GENERATION_METHOD_RE = re.compile(
    r"^\d+ x '.+' \+ '.+' under tokenizer sha256:[0-9a-f]{64}$"
)


class PlanGenerationError(ValueError):
    """A named refusal to generate a transfer-fiducial plan."""


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PlanGenerationError("selection_record_duplicate_key")
        value[key] = item
    return value


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PlanGenerationError(f"{label}_missing") from exc
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_strict_object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PlanGenerationError(f"{label}_invalid_json") from exc
    if not isinstance(value, dict):
        raise PlanGenerationError(f"{label}_not_object")
    return value, raw


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _read_bytes(path: Path, label: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PlanGenerationError(f"{label}_missing") from exc


def load_authenticated_selection(
    path: Path, summary_path: Path
) -> tuple[dict[str, Any], bytes]:
    """Load exactly the successful selector record shape, or name a refusal."""

    record, raw = _read_json(path, "selection_record")
    expected_keys = {
        "collection_prefill_tokens",
        "qualifying_prefill_tokens",
        "refusal",
        "rule",
        "schema_version",
        "selected_prefill_tokens",
        "status",
        "summary_sha256",
    }
    if set(record) != expected_keys:
        raise PlanGenerationError("selection_record_unauthenticated_shape")
    if record["schema_version"] != SELECTION_SCHEMA:
        raise PlanGenerationError("selection_record_unauthenticated_schema")
    if record["status"] != "selected" or record["refusal"] is not None:
        raise PlanGenerationError("selection_record_not_selected")
    selected = record["selected_prefill_tokens"]
    if selected not in LADDER:
        raise PlanGenerationError("selection_record_rung_not_supported")
    if record["collection_prefill_tokens"] != selected:
        raise PlanGenerationError("selection_record_unauthenticated_collection_rung")
    qualifying = record["qualifying_prefill_tokens"]
    if (
        not isinstance(qualifying, list)
        or not qualifying
        or any(item not in LADDER for item in qualifying)
        or selected != min(qualifying)
    ):
        raise PlanGenerationError("selection_record_unauthenticated_qualification")
    expected_rule = {
        "all_small_count_ge_5_required": True,
        "ladder_prefill_tokens": list(LADDER),
        "minimum_overlapping_power_interval_count": 5,
        "minimum_small_members_per_rung": 5,
        "reducer_min_phase_samples": 3,
        "selection": "shortest_qualifying_rung",
    }
    if record["rule"] != expected_rule:
        raise PlanGenerationError("selection_record_unauthenticated_rule")
    if not _is_sha256(record["summary_sha256"]):
        raise PlanGenerationError("selection_record_unauthenticated_summary_sha256")
    summary_raw = _read_bytes(summary_path, "summary")
    if _sha256(summary_raw) != record["summary_sha256"]:
        raise PlanGenerationError("selection_record_summary_sha256_mismatch")
    return record, raw


def v5_small_model_identity() -> tuple[dict[str, Any], dict[str, Any]]:
    """Import, rather than duplicate, the v5 model identity-pin projection."""

    try:
        panel = v5.load_model_panel(MODEL_PANEL)
        entry = dict(panel.get(SMALL_MODEL_ID))
        model = v5._model_config(entry)
    except (v5.ModelPanelError, KeyError, TypeError, ValueError) as exc:
        # The v5 loader provides the detailed refusal.
        raise PlanGenerationError(f"v5_small_model_identity_unavailable:{exc}") from exc
    if model.get("name") != "Qwen3-1.7B-4bit":
        raise PlanGenerationError("v5_small_model_identity_name_mismatch")
    return model, dict(entry["quantization"])


def _runtime_tokenize_prompt(
    model: Mapping[str, Any], prompt_text: str
) -> list[int]:
    """Load the panel-named local mirror and use the runtime's encode helper."""

    try:
        import mlx_lm

        from joulewise.adapters.mlx_runtime import _encode

        loaded = mlx_lm.load(
            str(model["source"]),
            revision=str(model["revision"]),
            return_config=True,
        )
        if not isinstance(loaded, tuple) or len(loaded) != 3:
            raise TypeError("mlx_lm.load did not return model, tokenizer, config")
        return _encode(loaded[1], prompt_text, add_special_tokens=True)
    except (ImportError, KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise PlanGenerationError(
            f"prefill_prompt_pin_runtime_tokenization_unavailable:{exc}"
        ) from exc


def _selection_authority_path_matches(recorded: str, supplied: Path) -> bool:
    """Match an absolute path or the ruled path relative to its plan root."""

    recorded_path = Path(recorded)
    if recorded_path.is_absolute():
        return recorded_path.resolve() == supplied.resolve()
    if not recorded_path.parts or any(part in ("", ".", "..") for part in recorded_path.parts):
        return False
    supplied_parts = supplied.resolve().parts
    return len(supplied_parts) >= len(recorded_path.parts) and (
        supplied_parts[-len(recorded_path.parts) :] == recorded_path.parts
    )


def _load_prompt_pin(
    path: Path,
    *,
    rung: int,
    model: Mapping[str, Any],
    selection_path: Path,
    selection_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    """Use the v5 validator, then bind its authority to this exact record."""

    value, raw = _read_json(path, "prefill_prompt_pin")
    try:
        pin = v5._load_prefill_prompt_pin(
            path,
            prefill_length=rung,
            tokenizer_json_sha256=str(model["tokenizer_json_sha256"]),
        )
    except (OSError, ValueError) as exc:
        raise PlanGenerationError(f"prefill_prompt_pin_unauthenticated:{exc}") from exc
    if pin.get("g2a_record_sha256") != selection_sha256:
        raise PlanGenerationError("prefill_prompt_pin_selection_record_mismatch")
    authority = pin["selection_authority"]["g2a_record"]
    if authority["record_id"] != f"sha256:{selection_sha256}":
        raise PlanGenerationError("prefill_prompt_pin_record_id_mismatch")
    if not _selection_authority_path_matches(authority["path"], selection_path):
        raise PlanGenerationError("prefill_prompt_pin_selection_record_path_mismatch")
    if GENERATION_METHOD_RE.fullmatch(pin["generation_method"]) is None:
        raise PlanGenerationError("prefill_prompt_pin_generation_method_invalid")
    observed_ids = _runtime_tokenize_prompt(model, pin["prompt_text"])
    if observed_ids != pin["prompt_token_ids"]:
        raise PlanGenerationError("prefill_prompt_pin_runtime_token_ids_mismatch")
    return value, raw


def _config_mapping(
    *, run_id: str, model: Mapping[str, Any], quantization: Mapping[str, Any], prompt: str
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "model": dict(model),
        "quantization": dict(quantization),
        "hardware_target": {
            "id": "macbook_m3_max",
            "transport": "local",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "device_kind": "apple_silicon_unified_memory",
            "notes": "TRANSFER-FIDUCIAL-01 Qwen3-small diagnostic; non-claim-bearing.",
        },
        "workload_profile": {
            "name": "transfer_fiducial_v2_qwen3_small",
            "prompt_text": prompt,
            "output_tokens": OUTPUT_TOKENS,
            "repetitions": 1,
            "warmup_runs": 1,
            "transfer_fiducial_gap_s": TRANSFER_FIDUCIAL_GAP_S_V1,
        },
        "interconnect": {"name": "local"},
        "sampling": {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0},
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "notes": "Diagnostic and non-claim-bearing; separate from the _v5 campaign runs root.",
            "tags": [
                "transfer-fiducial-01",
                "transfer-fiducial-v2",
                "qwen3-small",
                "diagnostic",
                "non-claim-bearing",
                "launch_lineage_required",
            ],
        },
    }


def _render_config(mapping: Mapping[str, Any]) -> bytes:
    normalized = BenchmarkConfig.from_mapping(dict(mapping)).to_dict()
    return (json.dumps(normalized, indent=2, sort_keys=True) + "\n").encode("utf-8")


def generate(
    output_root: Path,
    *,
    selection_record: Path,
    summary: Path,
    prefill_prompt_pin: Path,
) -> dict[str, str]:
    """Write one successor plan and its ten normalised configuration files."""

    selection, selection_raw = load_authenticated_selection(selection_record, summary)
    rung = int(selection["selected_prefill_tokens"])
    model, quantization = v5_small_model_identity()
    prompt_pin, prompt_pin_raw = _load_prompt_pin(
        prefill_prompt_pin,
        rung=rung,
        model=model,
        selection_path=selection_record,
        selection_sha256=_sha256(selection_raw),
    )
    destination = Path(output_root) / OUTPUT_REL
    destination.mkdir(parents=True, exist_ok=True)
    descriptors: list[dict[str, str]] = []
    for index in range(1, RUN_COUNT + 1):
        run_id = f"tf-q3s-p{rung}-o{OUTPUT_TOKENS}-r{index:02d}"
        filename = f"{run_id}.json"
        rendered = _render_config(
            _config_mapping(
                run_id=run_id,
                model=model,
                quantization=quantization,
                prompt=str(prompt_pin["prompt_text"]),
            )
        )
        (destination / filename).write_bytes(rendered)
        descriptors.append(
            {
                "bundle_id": run_id,
                "config_path": (OUTPUT_REL / filename).as_posix(),
                "config_sha256": _sha256(rendered),
            }
        )
    constants = transfer_fiducial_rule_constants()
    plan = {
        "schema_version": TRANSFER_FIDUCIAL_PLAN_SCHEMA_V2,
        "diagnostic": True,
        "claim_bearing": False,
        "diagnostic_kind": TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND_V2,
        "pooling": "forbidden",
        "pre_data_receipt_required": True,
        "fit_rule_constants": constants,
        "strata": [
            {
                "stratum_id": f"qwen3_1p7b_p{rung}_o{OUTPUT_TOKENS}_m3max",
                "model": model,
                "quantization": quantization,
                "hardware_target": {
                    "id": "macbook_m3_max",
                    "transport": "local",
                    "runtime_backend": "mlx",
                    "telemetry_backend": "powermetrics",
                    "device_kind": "apple_silicon_unified_memory",
                },
                "prompt_tokens": rung,
                "prompt_text_utf8_sha256": prompt_pin["prompt_text_utf8_sha256"],
                "prompt_token_ids_sha256": prompt_pin["prompt_token_ids_sha256"],
                "prefill_prompt_pin_sha256": _sha256(prompt_pin_raw),
                "g2a_selection_record_sha256": _sha256(selection_raw),
                "output_tokens": OUTPUT_TOKENS,
                "repetitions": 1,
                "transfer_fiducial_gap_s": TRANSFER_FIDUCIAL_GAP_S_V1,
                "minimum_prefill_s": constants["minimum_prefill_s"],
                "minimum_decode_s": constants["minimum_decode_s"],
                "post_window_sampling_dwell_s": constants[
                    "post_window_sampling_dwell_s"
                ],
                "planned_runs": RUN_COUNT,
                "configs": descriptors,
            }
        ],
    }
    plan_bytes = (json.dumps(plan, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (destination / "plan.json").write_bytes(plan_bytes)
    return {"plan_sha256": _sha256(plan_bytes), "selection_sha256": _sha256(selection_raw)}


def _inventory(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and path.name != "generate_plan.py" and "__pycache__" not in path.parts
    }


def check(
    committed_root: Path,
    *,
    selection_record: Path,
    summary: Path,
    prefill_prompt_pin: Path,
) -> dict[str, str]:
    """Regenerate in a temporary directory and require byte-identical output."""

    committed = Path(committed_root) / OUTPUT_REL
    with tempfile.TemporaryDirectory(prefix="transfer-fiducial-v2-check-") as temporary:
        temporary_root = Path(temporary)
        result = generate(
            temporary_root,
            selection_record=selection_record,
            summary=summary,
            prefill_prompt_pin=prefill_prompt_pin,
        )
        generated = temporary_root / OUTPUT_REL
        expected_paths = _inventory(generated)
        actual_paths = _inventory(committed) if committed.is_dir() else set()
        if expected_paths != actual_paths:
            raise PlanGenerationError("committed_output_inventory_mismatch")
        for relative in sorted(expected_paths):
            if (generated / relative).read_bytes() != (committed / relative).read_bytes():
                raise PlanGenerationError(f"committed_output_bytes_mismatch:{relative}")
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-record", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--prefill-prompt-pin", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = (
            check(
                args.output_root,
                selection_record=args.selection_record,
                summary=args.summary,
                prefill_prompt_pin=args.prefill_prompt_pin,
            )
            if args.check
            else generate(
                args.output_root,
                selection_record=args.selection_record,
                summary=args.summary,
                prefill_prompt_pin=args.prefill_prompt_pin,
            )
        )
    except PlanGenerationError as exc:
        print(f"transfer fiducial v2 generation refused: {exc}", file=sys.stderr)
        return 2
    print(
        f"{'checked' if args.check else 'generated'} transfer fiducial v2 "
        f"plan_sha256={result['plan_sha256']} selection_sha256={result['selection_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
