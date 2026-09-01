#!/usr/bin/env python3
"""Build and authenticate the non-claim G2-a prefill probe inputs.

The three commands in this module are desk-only operations.  ``build-probes``
creates the fixed prompt ladder, ordinary benchmark configs, and their order
manifests.  ``bind-window`` binds those bytes to one calibration window.
``check`` replays every binding without writing anything.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.adapters.mlx_runtime import _encode as runtime_encode  # noqa: E402
from joulewise.calibration_bracketing import (  # noqa: E402
    DEFAULT_ACCEPTANCE_BOUND_PATH,
)
from joulewise.doctor import inspect_configs  # noqa: E402
from joulewise.model_panel import ModelPanelError, load_model_panel  # noqa: E402
from joulewise.provenance import prompt_token_ids_sha256  # noqa: E402
from joulewise.schemas import BenchmarkConfig, CampaignPolicy, SchemaError  # noqa: E402


PROMPT_LADDER_SCHEMA = "joulewise.g2a_prefill_prompt_ladder.v1"
INPUT_INVENTORY_SCHEMA = "joulewise.g2a_input_inventory.v1"
PROBE_PLAN_SCHEMA = "joulewise.g2a_probe_plan.v1"
ORDER_MANIFEST_SCHEMA = "joulewise.order_manifest.v1"

PROMPT_SENTENCE = "The plan remains easy to audit."
PROMPT_FINAL_SENTENCE = "The plan remains easy to audit and simple to review."
PREFILL_LENGTHS = (512, 1024, 2048, 4096)
CLOSING_SENTENCES = {
    512: "The record remains easy to inspect today.",
    1024: "The plan remains easy to audit and verify.",
    2048: PROMPT_FINAL_SENTENCE,
    4096: "The evidence remains easy to audit today.",
}
EXPECTED_CLOSING_TOKEN_COUNTS = {512: 8, 1024: 9, 2048: 11, 4096: 8}

SMALL_MODEL_ID = "qwen3-1p7b"
LARGE_MODEL_ID = "qwen3-8b"
MODEL_ROLES = ("small", "large")
EXPECTED_MODEL_IDS = {"small": SMALL_MODEL_ID, "large": LARGE_MODEL_ID}
EXPECTED_REVISIONS = {
    "small": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
    "large": "545dc4251c05440727734bcd94334791f6ab0192",
}
EXPECTED_QUANTIZATION = {"name": "int4", "bits": 4, "group_size": 64}

CANONICAL_PANEL_PATH = REPO_ROOT / "configs/model_panels/qwen3_4bit.json"
CONFIG_ROOT_LEAF = "prefill-probe-configs"
WINDOW_PLAN_LEAF = "window-plan"
PROMPT_LADDER_NAME = "prefill-prompt-ladder.json"
INVENTORY_NAME = "g2a-input-inventory.json"
IDENTITY_EPOCH_NAME = "identity-epoch.json"
T1_BINDINGS_NAME = "t1-bindings.json"
CALIBRATION_PLAN_NAME = "calibration_plan.json"
MANIFEST_NAME = "order_manifest.json"
POWER_POLICY = "ac_high_power"
HEX64_RE = re.compile(r"[0-9a-f]{64}")

LADDER_KEYS = frozenset(
    {
        "schema_version",
        "prompt_sentence",
        "tokenizer_json_sha256",
        "panel_thinking_policy",
        "rungs",
    }
)
RUNG_KEYS = frozenset(
    {
        "prefill_tokens",
        "repeat_count",
        "closing_sentence",
        "prompt_text",
        "prompt_text_utf8_sha256",
        "prompt_token_ids",
        "prompt_token_ids_sha256",
        "generation_method",
    }
)
INVENTORY_KEYS = frozenset(
    {
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
)
HASH_REFERENCE_KEYS = frozenset({"path", "sha256"})
PLAN_REFERENCE_KEYS = frozenset({"path", "sha256", "plan_id"})
STAGE_KEYS = frozenset(
    {
        "stage_id",
        "model_role",
        "model_name",
        "prefill_tokens",
        "manifest",
        "members",
    }
)
MEMBER_KEYS = frozenset({"index", "run_id", "config_path", "config_sha256"})
MANIFEST_KEYS = frozenset(
    {
        "schema_version",
        "manifest_id",
        "stage_id",
        "model_role",
        "model_name",
        "prefill_tokens",
        "planned_n_bundles",
        "executed_order",
    }
)
MANIFEST_MEMBER_KEYS = frozenset(
    {
        "index",
        "config",
        "config_sha256",
        "run_id",
        "model_role",
        "prefill_tokens",
        "repetition",
    }
)


class G2AProbeError(ValueError):
    """One fail-closed producer or checker refusal."""


class _DuplicateKeyError(ValueError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise G2AProbeError(f"{label}_unreadable: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise G2AProbeError(f"{label}_malformed: top level must be an object")
    return value


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise G2AProbeError(f"input_unreadable: {path}: {exc}") from exc


def _require_exact_keys(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise G2AProbeError(
            f"{label}_field_set_mismatch: missing={sorted(expected - observed)} "
            f"extra={sorted(observed - expected)}"
        )


def _require_nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise G2AProbeError(f"{label}_invalid: expected a nonempty trimmed string")
    return value


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64_RE.fullmatch(value) is None:
        raise G2AProbeError(f"{label}_invalid: expected 64 lowercase hexadecimal characters")
    return value


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _resolve_reference(path_text: str, *, root: Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    repo_candidate = REPO_ROOT / path
    root_candidate = root / path
    if repo_candidate.exists() or not root_candidate.exists():
        return repo_candidate
    return root_candidate


def _publish_exact(outputs: Mapping[Path, bytes]) -> None:
    """Publish complete bytes atomically without replacing an existing file."""

    for path, expected in outputs.items():
        if path.exists():
            try:
                observed = path.read_bytes()
            except OSError as exc:
                raise G2AProbeError(f"output_unreadable: {path}: {exc}") from exc
            if observed != expected:
                raise G2AProbeError(f"preexisting_output_mismatch: {path}")
    for path, expected in outputs.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = -1
        temporary_path: Path | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
            )
            temporary_path = Path(temporary_name)
            os.fchmod(descriptor, 0o644)
            with os.fdopen(descriptor, "wb") as stream:
                descriptor = -1
                stream.write(expected)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary_path, path)
            except FileExistsError:
                try:
                    observed = path.read_bytes()
                except OSError as exc:
                    raise G2AProbeError(f"output_unreadable: {path}: {exc}") from exc
                if observed != expected:
                    raise G2AProbeError(f"preexisting_output_mismatch: {path}") from None
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
        except Exception:
            raise
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass


def _validate_lengths(lengths: Sequence[int]) -> tuple[int, ...]:
    normalized = tuple(lengths)
    if normalized != PREFILL_LENGTHS:
        raise G2AProbeError(
            f"prefill_length_set_invalid: expected {list(PREFILL_LENGTHS)}, "
            f"observed {list(normalized)}"
        )
    return normalized


def _validate_member_counts(small_members: int, large_members: int) -> None:
    if isinstance(small_members, bool) or small_members < 5:
        raise G2AProbeError("small_member_count_below_five")
    if isinstance(large_members, bool) or large_members < 1:
        raise G2AProbeError("large_member_count_below_one")


def _validate_panel(panel_path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    try:
        panel = load_model_panel(panel_path)
    except ModelPanelError as exc:
        raise G2AProbeError(f"model_panel_refused: {exc}") from exc
    raw = _read_json(panel_path, label="model_panel")
    entries = raw.get("entries")
    if not isinstance(entries, list) or [row.get("model_id") for row in entries if isinstance(row, dict)] != [
        SMALL_MODEL_ID,
        LARGE_MODEL_ID,
    ]:
        raise G2AProbeError("model_panel_pair_mismatch: exact small/large pair required")

    selected: dict[str, dict[str, Any]] = {}
    tokenizer_hash: str | None = None
    for role in MODEL_ROLES:
        model_id = EXPECTED_MODEL_IDS[role]
        try:
            entry = dict(panel.get(model_id))
        except ModelPanelError as exc:
            raise G2AProbeError(f"model_panel_pair_mismatch: {exc}") from exc
        if entry.get("revision") != EXPECTED_REVISIONS[role]:
            raise G2AProbeError(f"model_revision_mismatch: {model_id}")
        if entry.get("admission", {}).get("status") != "admitted":
            raise G2AProbeError(f"model_not_admitted: {model_id}")
        if entry.get("weight_format") != "mlx":
            raise G2AProbeError(f"model_weight_format_mismatch: {model_id}")
        if entry.get("quantization") != EXPECTED_QUANTIZATION:
            raise G2AProbeError(f"model_quantization_mismatch: {model_id}")
        if entry.get("enable_thinking") != "false":
            raise G2AProbeError(f"panel_thinking_policy_mismatch: {model_id}")
        current_hash = _require_sha256(
            entry.get("tokenizer_json_sha256"), f"{model_id}_tokenizer_json_sha256"
        )
        if tokenizer_hash is not None and current_hash != tokenizer_hash:
            raise G2AProbeError("pair_tokenizer_identity_mismatch")
        tokenizer_hash = current_hash
        source = Path(_require_nonempty(entry.get("source"), f"{model_id}_source")).expanduser()
        if _sha256_path(source / "tokenizer.json") != current_hash:
            raise G2AProbeError(f"model_tokenizer_json_sha256_mismatch: {model_id}")
        selected[role] = entry
    assert tokenizer_hash is not None
    return selected, tokenizer_hash


def _load_runtime_tokenizer(model_entry: Mapping[str, Any]) -> Any:
    """Load the tokenizer class used by the MLX runtime, without loading weights."""

    try:
        transformers = importlib.import_module("transformers")
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            model_entry["source"],
            revision=model_entry["revision"],
            local_files_only=True,
        )
    except Exception as exc:  # noqa: BLE001 - optional runtime dependency boundary
        raise G2AProbeError(
            "runtime_tokenizer_unavailable: install the [mac] extra and keep the "
            f"panel-pinned local tokenizer complete: {type(exc).__name__}: {exc}"
        ) from exc
    return tokenizer


def _token_ids(tokenizer: Any, text: str) -> list[int]:
    try:
        ids = runtime_encode(tokenizer, text, add_special_tokens=True)
    except Exception as exc:  # noqa: BLE001 - tokenizer implementations vary
        raise G2AProbeError(f"runtime_tokenization_failed: {type(exc).__name__}: {exc}") from exc
    if not ids or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in ids):
        raise G2AProbeError("runtime_tokenization_invalid_ids")
    return ids


def _validate_prompt_corpus(path: Path, tokenizer: Any) -> None:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise G2AProbeError(f"prompt_source_unreadable: {path}: {exc}") from exc
    if len(_token_ids(tokenizer, source)) < max(PREFILL_LENGTHS):
        raise G2AProbeError("prompt_source_shorter_than_4096_tokens")


def _build_prompt_ladder(
    *, tokenizer: Any, tokenizer_hash: str, panel_sha256: str
) -> dict[str, Any]:
    sentence_ids = _token_ids(tokenizer, PROMPT_SENTENCE)
    if len(sentence_ids) != 7:
        raise G2AProbeError(
            f"prompt_sentence_token_count_mismatch: expected 7 observed {len(sentence_ids)}"
        )
    rungs: list[dict[str, Any]] = []
    for length in PREFILL_LENGTHS:
        closing = CLOSING_SENTENCES[length]
        closing_ids = _token_ids(tokenizer, closing)
        expected_closing = EXPECTED_CLOSING_TOKEN_COUNTS[length]
        if len(closing_ids) != expected_closing:
            raise G2AProbeError(
                f"closing_sentence_token_count_mismatch: length={length} "
                f"expected={expected_closing} observed={len(closing_ids)}"
            )
        remaining = length - len(closing_ids)
        if remaining <= 0 or remaining % len(sentence_ids):
            raise G2AProbeError(f"prompt_rung_not_integral: length={length}")
        repeat_count = remaining // len(sentence_ids)
        prompt_text = " ".join([PROMPT_SENTENCE] * repeat_count + [closing])
        prompt_ids = _token_ids(tokenizer, prompt_text)
        if len(prompt_ids) != length:
            raise G2AProbeError(
                f"prompt_rung_token_count_mismatch: length={length} observed={len(prompt_ids)}"
            )
        method = (
            f"{repeat_count} x '{PROMPT_SENTENCE}' + '{closing}' under tokenizer "
            f"sha256:{tokenizer_hash}"
        )
        rungs.append(
            {
                "prefill_tokens": length,
                "repeat_count": repeat_count,
                "closing_sentence": closing,
                "prompt_text": prompt_text,
                "prompt_text_utf8_sha256": _sha256_bytes(prompt_text.encode("utf-8")),
                "prompt_token_ids": prompt_ids,
                "prompt_token_ids_sha256": prompt_token_ids_sha256(prompt_ids),
                "generation_method": method,
            }
        )
    return {
        "schema_version": PROMPT_LADDER_SCHEMA,
        "prompt_sentence": PROMPT_SENTENCE,
        "tokenizer_json_sha256": tokenizer_hash,
        "panel_thinking_policy": {
            "enable_thinking": "false",
            "panel_sha256": panel_sha256,
        },
        "rungs": rungs,
    }


def _model_config(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: entry[key]
        for key in (
            "name",
            "family",
            "source",
            "revision",
            "weight_format",
            "context_window",
            "tokenizer_json_sha256",
            "chat_template_sha256",
        )
    }


def _config_for(
    *, role: str, entry: Mapping[str, Any], rung: Mapping[str, Any], run_id: str, panel_sha: str
) -> dict[str, Any]:
    length = rung["prefill_tokens"]
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "model": _model_config(entry),
        "quantization": dict(entry["quantization"]),
        "hardware_target": {
            "id": "macbook_m3_max",
            "transport": "local",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "device_kind": "apple_silicon_unified_memory",
            "notes": "G2-a diagnostic prefill probe; not claim-bearing.",
        },
        "workload_profile": {
            "name": f"g2a_prefill_p{length}_diagnostic",
            "repetitions": 1,
            "warmup_runs": 1,
            "output_tokens": 512,
            "prompt_text": rung["prompt_text"],
        },
        "interconnect": {"name": "local"},
        "sampling": {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0},
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": [
                "phase2",
                "g2a-prefill-probe",
                "diagnostic-non-claim",
                f"model-role={role}",
                f"prompt-tokens={length}",
                f"prompt-text-sha256={rung['prompt_text_utf8_sha256']}",
                f"panel-thinking-off-policy-sha256={panel_sha}",
                "mlx-greedy-runtime",
            ],
        },
    }


def _stage_id(role: str, length: int) -> str:
    return f"{role}-p{length}"


def _run_id(role: str, length: int, repetition: int) -> str:
    return f"g2a-{role}-p{length:04d}-r{repetition:02d}"


def _expected_stage_sequence() -> list[tuple[str, int]]:
    return [(role, length) for role in MODEL_ROLES for length in PREFILL_LENGTHS]


def _stage_outputs(
    *,
    config_root: Path,
    models: Mapping[str, Mapping[str, Any]],
    ladder: Mapping[str, Any],
    panel_sha: str,
    small_members: int,
    large_members: int,
) -> dict[Path, bytes]:
    rungs = {row["prefill_tokens"]: row for row in ladder["rungs"]}
    outputs: dict[Path, bytes] = {}
    seen_run_ids: set[str] = set()
    for role, length in _expected_stage_sequence():
        member_count = small_members if role == "small" else large_members
        stage_id = _stage_id(role, length)
        stage_root = config_root / stage_id
        manifest_rows: list[dict[str, Any]] = []
        for repetition in range(1, member_count + 1):
            run_id = _run_id(role, length, repetition)
            if run_id in seen_run_ids:
                raise G2AProbeError(f"duplicate_run_id: {run_id}")
            seen_run_ids.add(run_id)
            filename = f"{run_id}.json"
            config_bytes = _json_bytes(
                _config_for(
                    role=role,
                    entry=models[role],
                    rung=rungs[length],
                    run_id=run_id,
                    panel_sha=panel_sha,
                )
            )
            outputs[stage_root / filename] = config_bytes
            manifest_rows.append(
                {
                    "index": repetition,
                    "config": filename,
                    "config_sha256": _sha256_bytes(config_bytes),
                    "run_id": run_id,
                    "model_role": role,
                    "prefill_tokens": length,
                    "repetition": repetition,
                }
            )
        manifest = {
            "schema_version": ORDER_MANIFEST_SCHEMA,
            "manifest_id": f"g2a-{stage_id}-order-v1",
            "stage_id": stage_id,
            "model_role": role,
            "model_name": models[role]["name"],
            "prefill_tokens": length,
            "planned_n_bundles": member_count,
            "executed_order": manifest_rows,
        }
        outputs[stage_root / MANIFEST_NAME] = _json_bytes(manifest)
    return outputs


def _refuse_unknown_stage_json(config_root: Path, expected_paths: set[Path] | None = None) -> None:
    for role, length in _expected_stage_sequence():
        stage_root = config_root / _stage_id(role, length)
        if not stage_root.exists():
            continue
        for path in stage_root.glob("*.json"):
            if expected_paths is not None and path not in expected_paths:
                raise G2AProbeError(f"unknown_stage_json: {path}")


def build_probes(
    *,
    root: Path,
    panel_path: Path,
    prompt_corpus: Path,
    small_members: int,
    large_members: int,
    lengths: Sequence[int] = PREFILL_LENGTHS,
) -> None:
    _validate_lengths(lengths)
    _validate_member_counts(small_members, large_members)
    models, tokenizer_hash = _validate_panel(panel_path)
    tokenizer = _load_runtime_tokenizer(models["small"])
    _validate_prompt_corpus(prompt_corpus, tokenizer)
    panel_sha = _sha256_path(panel_path)
    ladder = _build_prompt_ladder(
        tokenizer=tokenizer,
        tokenizer_hash=tokenizer_hash,
        panel_sha256=panel_sha,
    )
    config_root = root.resolve() / CONFIG_ROOT_LEAF
    outputs = _stage_outputs(
        config_root=config_root,
        models=models,
        ladder=ladder,
        panel_sha=panel_sha,
        small_members=small_members,
        large_members=large_members,
    )
    ladder_path = root.resolve() / WINDOW_PLAN_LEAF / PROMPT_LADDER_NAME
    outputs[ladder_path] = _json_bytes(ladder)
    _refuse_unknown_stage_json(config_root, set(outputs))
    _publish_exact(outputs)


def _derive_live_vectors(power_policy: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Use the calibration writer's constants and T1 projection helper."""

    try:
        from joulewise.calibration_bracketing import load_calibration_acceptance_bound  # noqa: PLC0415
        from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
            PROTOCOL_ID,
            RESIDUAL_REGION_METHOD,
            SAMPLING_INTERVAL_MS,
            _derive_preflight_systematic_screen_s,
            _planned_t1_bindings,
            _sysctl_identity,
        )

        planned_epoch = {
            "os_build": _sysctl_identity("kern.osversion"),
            "hardware_model": _sysctl_identity("hw.model"),
            "power_policy": power_policy,
            "sampling_interval_ms": SAMPLING_INTERVAL_MS,
            "estimator_revision": RESIDUAL_REGION_METHOD,
            "pulse_protocol_id": PROTOCOL_ID,
        }
        _derive_preflight_systematic_screen_s(planned_epoch)
        mx = importlib.import_module("mlx.core")
        planned_t1 = _planned_t1_bindings(
            planned_epoch=planned_epoch,
            sampler_binary=Path("/usr/bin/powermetrics"),
            mlx_version=getattr(mx, "__version__", None),
        )
        acceptance = load_calibration_acceptance_bound(DEFAULT_ACCEPTANCE_BOUND_PATH)
    except Exception as exc:  # noqa: BLE001 - one named desk preflight boundary
        raise G2AProbeError(
            f"calibration_vector_derivation_refused: {type(exc).__name__}: {exc}"
        ) from exc
    if not isinstance(acceptance, Mapping):
        raise G2AProbeError("acceptance_artifact_unauthenticated")
    return planned_epoch, planned_t1, dict(acceptance)


def _authenticate_ledger_and_acceptance(
    *, ledger: Path, head_pin: Path, acceptance: Mapping[str, Any]
) -> dict[str, Any]:
    try:
        from joulewise.calibration_ledger import load_calibration_ledger_snapshot  # noqa: PLC0415

        cutoff = acceptance["ledger_cutoff"]
        snapshot = load_calibration_ledger_snapshot(
            ledger,
            head_pin,
            baseline_sequence=cutoff["sequence"],
            baseline_digest=cutoff["head_digest"],
            require_committed_pin=True,
            verify_custody=False,
            repo_root=REPO_ROOT,
        )
    except Exception as exc:  # noqa: BLE001 - ledger exposes typed and parse failures
        raise G2AProbeError(f"calibration_ledger_refused: {type(exc).__name__}: {exc}") from exc
    return {
        "ledger": {
            "path": _display_path(ledger),
            "sha256": _sha256_path(ledger),
            "head_sequence": snapshot.head_sequence,
            "head_digest": snapshot.head_digest,
        },
        "head_pin": {"path": _display_path(head_pin), "sha256": _sha256_path(head_pin)},
    }


def _read_ladder(path: Path) -> dict[str, Any]:
    ladder = _read_json(path, label="prompt_ladder")
    _require_exact_keys(ladder, LADDER_KEYS, "prompt_ladder")
    if ladder.get("schema_version") != PROMPT_LADDER_SCHEMA:
        raise G2AProbeError("prompt_ladder_schema_mismatch")
    if ladder.get("prompt_sentence") != PROMPT_SENTENCE:
        raise G2AProbeError("prompt_ladder_sentence_mismatch")
    policy = ladder.get("panel_thinking_policy")
    if not isinstance(policy, dict) or set(policy) != {"enable_thinking", "panel_sha256"}:
        raise G2AProbeError("prompt_ladder_thinking_policy_malformed")
    if policy.get("enable_thinking") != "false":
        raise G2AProbeError("prompt_ladder_thinking_policy_mismatch")
    _require_sha256(policy.get("panel_sha256"), "prompt_ladder_panel_sha256")
    rungs = ladder.get("rungs")
    if not isinstance(rungs, list) or len(rungs) != 4:
        raise G2AProbeError("prompt_ladder_rungs_malformed")
    for row in rungs:
        if not isinstance(row, dict):
            raise G2AProbeError("prompt_ladder_rung_malformed")
        _require_exact_keys(row, RUNG_KEYS, "prompt_ladder_rung")
    return ladder


def _collect_stage_bindings(
    *, config_root: Path, models: Mapping[str, Mapping[str, Any]]
) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    for role, length in _expected_stage_sequence():
        stage_id = _stage_id(role, length)
        stage_root = config_root / stage_id
        manifest_path = stage_root / MANIFEST_NAME
        manifest = _read_json(manifest_path, label="order_manifest")
        rows = manifest.get("executed_order")
        if not isinstance(rows, list):
            raise G2AProbeError(f"order_manifest_members_malformed: {manifest_path}")
        members = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise G2AProbeError(f"order_manifest_member_malformed: {manifest_path}")
            config_path = stage_root / str(row.get("config"))
            members.append(
                {
                    "index": index,
                    "run_id": row.get("run_id"),
                    "config_path": f"{stage_id}/{row.get('config')}",
                    "config_sha256": _sha256_path(config_path),
                }
            )
        stages.append(
            {
                "stage_id": stage_id,
                "model_role": role,
                "model_name": models[role]["name"],
                "prefill_tokens": length,
                "manifest": {
                    "path": f"{stage_id}/{MANIFEST_NAME}",
                    "sha256": _sha256_path(manifest_path),
                },
                "members": members,
            }
        )
    return stages


def _probe_plan(
    *,
    root: Path,
    panel_path: Path,
    campaign_policy: Path,
    ladder_path: Path,
    identity_path: Path,
    t1_path: Path,
    stages: list[dict[str, Any]],
    power_policy: str,
    window_id: str,
    session_id: str,
    evidence_root_id: str,
    acceptance: Mapping[str, Any],
    ledger_binding: Mapping[str, Any],
    identity_sha256: str | None = None,
    t1_sha256: str | None = None,
) -> dict[str, Any]:
    plan_id = f"plan-{window_id}-g2a-probe-v1"
    return {
        "schema_version": PROBE_PLAN_SCHEMA,
        "plan_id": plan_id,
        "status": {
            "diagnostic": True,
            "claim_eligible": False,
            "purpose": "Choose a prefill length whose power-sample overlap is resolvable.",
        },
        "power_policy": power_policy,
        "window_id": window_id,
        "session_id": session_id,
        "evidence_root_id": evidence_root_id,
        "config_root": str((root / CONFIG_ROOT_LEAF).resolve()),
        "panel": {"path": _display_path(panel_path), "sha256": _sha256_path(panel_path)},
        "campaign_policy": {
            "path": _display_path(campaign_policy),
            "sha256": _sha256_path(campaign_policy),
        },
        "prompt_ladder": {"path": str(ladder_path.resolve()), "sha256": _sha256_path(ladder_path)},
        "identity_epoch": {
            "path": str(identity_path.resolve()),
            "sha256": identity_sha256 or _sha256_path(identity_path),
        },
        "t1_bindings": {
            "path": str(t1_path.resolve()),
            "sha256": t1_sha256 or _sha256_path(t1_path),
        },
        "active_acceptance": {
            "path": _display_path(DEFAULT_ACCEPTANCE_BOUND_PATH),
            "sha256": _sha256_path(DEFAULT_ACCEPTANCE_BOUND_PATH),
            "acceptance_id": acceptance.get("acceptance_id"),
        },
        "calibration_ledger": dict(ledger_binding["ledger"]),
        "ledger_head_pin": dict(ledger_binding["head_pin"]),
        "stages": stages,
    }


def bind_window(
    *,
    root: Path,
    ledger: Path,
    head_pin: Path,
    campaign_policy: Path,
    power_policy: str,
    window_id: str,
    session_id: str,
    evidence_root_id: str,
) -> None:
    if power_policy != POWER_POLICY:
        raise G2AProbeError(f"power_policy_mismatch: expected {POWER_POLICY!r}")
    for label, value in (
        ("window_id", window_id),
        ("session_id", session_id),
        ("evidence_root_id", evidence_root_id),
    ):
        _require_nonempty(value, label)
    try:
        CampaignPolicy.from_mapping(_read_json(campaign_policy, label="campaign_policy"))
    except SchemaError as exc:
        raise G2AProbeError(f"campaign_policy_refused: {exc}") from exc

    root = root.resolve()
    config_root = root / CONFIG_ROOT_LEAF
    ladder_path = root / WINDOW_PLAN_LEAF / PROMPT_LADDER_NAME
    ladder = _read_ladder(ladder_path)
    models, tokenizer_hash = _validate_panel(CANONICAL_PANEL_PATH)
    panel_sha = _sha256_path(CANONICAL_PANEL_PATH)
    if ladder["tokenizer_json_sha256"] != tokenizer_hash:
        raise G2AProbeError("prompt_ladder_tokenizer_sha256_mismatch")
    if ladder["panel_thinking_policy"]["panel_sha256"] != panel_sha:
        raise G2AProbeError("prompt_ladder_panel_sha256_mismatch")

    tokenizer = _load_runtime_tokenizer(models["small"])
    _validate_ladder_with_tokenizer(
        ladder=ladder,
        tokenizer=tokenizer,
        tokenizer_hash=tokenizer_hash,
        panel_sha=panel_sha,
    )

    stages = _collect_stage_bindings(config_root=config_root, models=models)
    rungs = {row["prefill_tokens"]: row for row in ladder["rungs"]}
    config_paths: list[Path] = []
    seen_run_ids: set[str] = set()
    for stage, (role, length) in zip(stages, _expected_stage_sequence(), strict=True):
        config_paths.extend(
            _check_stage(
                stage=stage,
                role=role,
                length=length,
                config_root=config_root,
                model=models[role],
                rung=rungs[length],
                panel_sha=panel_sha,
                seen_run_ids=seen_run_ids,
            )
        )
    doctor = inspect_configs(config_paths)
    if doctor["errors"]:
        raise G2AProbeError(f"doctor_config_errors: {doctor['errors']}")
    if doctor["warnings"]:
        raise G2AProbeError(f"doctor_config_warnings: {doctor['warnings']}")

    identity, t1, acceptance = _derive_live_vectors(power_policy)
    ledger_binding = _authenticate_ledger_and_acceptance(
        ledger=ledger, head_pin=head_pin, acceptance=acceptance
    )

    window_plan_root = root / WINDOW_PLAN_LEAF
    identity_path = window_plan_root / IDENTITY_EPOCH_NAME
    t1_path = window_plan_root / T1_BINDINGS_NAME
    plan_path = window_plan_root / CALIBRATION_PLAN_NAME
    inventory_path = window_plan_root / INVENTORY_NAME
    identity_bytes = _json_bytes(identity)
    t1_bytes = _json_bytes(t1)
    identity_sha = _sha256_bytes(identity_bytes)
    t1_sha = _sha256_bytes(t1_bytes)

    plan = _probe_plan(
        root=root,
        panel_path=CANONICAL_PANEL_PATH,
        campaign_policy=campaign_policy,
        ladder_path=ladder_path,
        identity_path=identity_path,
        t1_path=t1_path,
        stages=stages,
        power_policy=power_policy,
        window_id=window_id,
        session_id=session_id,
        evidence_root_id=evidence_root_id,
        acceptance=acceptance,
        ledger_binding=ledger_binding,
        identity_sha256=identity_sha,
        t1_sha256=t1_sha,
    )
    plan_bytes = _json_bytes(plan)
    inventory = {
        "schema_version": INPUT_INVENTORY_SCHEMA,
        "config_root": str(config_root.resolve()),
        "panel": {"path": _display_path(CANONICAL_PANEL_PATH), "sha256": panel_sha},
        "campaign_policy": {
            "path": _display_path(campaign_policy),
            "sha256": _sha256_path(campaign_policy),
        },
        "prompt_ladder": {"path": str(ladder_path.resolve()), "sha256": _sha256_path(ladder_path)},
        "identity_epoch": {"path": str(identity_path.resolve()), "sha256": identity_sha},
        "t1_bindings": {"path": str(t1_path.resolve()), "sha256": t1_sha},
        "calibration_plan": {
            "path": str(plan_path.resolve()),
            "sha256": _sha256_bytes(plan_bytes),
            "plan_id": plan["plan_id"],
        },
        "power_policy": power_policy,
        "evidence_root_id": evidence_root_id,
        "window_id": window_id,
        "session_id": session_id,
        "stages": stages,
    }
    _publish_exact(
        {
            identity_path: identity_bytes,
            t1_path: t1_bytes,
            plan_path: plan_bytes,
            inventory_path: _json_bytes(inventory),
        }
    )


def _validate_hash_reference(
    value: Any,
    *,
    label: str,
    root: Path,
    expected_keys: frozenset[str] = HASH_REFERENCE_KEYS,
) -> Path:
    if not isinstance(value, dict):
        raise G2AProbeError(f"{label}_malformed")
    _require_exact_keys(value, expected_keys, label)
    path = _resolve_reference(_require_nonempty(value.get("path"), f"{label}_path"), root=root)
    expected = _require_sha256(value.get("sha256"), f"{label}_sha256")
    if _sha256_path(path) != expected:
        raise G2AProbeError(f"{label}_sha256_mismatch")
    return path


def _validate_ladder_with_tokenizer(
    *, ladder: Mapping[str, Any], tokenizer: Any, tokenizer_hash: str, panel_sha: str
) -> None:
    expected = _build_prompt_ladder(
        tokenizer=tokenizer,
        tokenizer_hash=tokenizer_hash,
        panel_sha256=panel_sha,
    )
    if ladder != expected:
        raise G2AProbeError("prompt_ladder_content_mismatch")


def _expected_config_keys() -> frozenset[str]:
    return frozenset(
        {
            "schema_version",
            "run_id",
            "model",
            "quantization",
            "hardware_target",
            "workload_profile",
            "interconnect",
            "sampling",
            "run_metadata",
        }
    )


def _check_stage(
    *,
    stage: Mapping[str, Any],
    role: str,
    length: int,
    config_root: Path,
    model: Mapping[str, Any],
    rung: Mapping[str, Any],
    panel_sha: str,
    seen_run_ids: set[str],
) -> list[Path]:
    _require_exact_keys(stage, STAGE_KEYS, "inventory_stage")
    stage_id = _stage_id(role, length)
    if (
        stage.get("stage_id") != stage_id
        or stage.get("model_role") != role
        or stage.get("model_name") != model["name"]
        or stage.get("prefill_tokens") != length
    ):
        raise G2AProbeError(f"inventory_stage_identity_mismatch: {stage_id}")

    manifest_ref = stage.get("manifest")
    manifest_path = _validate_hash_reference(
        manifest_ref, label=f"{stage_id}_manifest", root=config_root
    )
    if manifest_path != config_root / stage_id / MANIFEST_NAME:
        raise G2AProbeError(f"inventory_manifest_path_mismatch: {stage_id}")
    manifest = _read_json(manifest_path, label="order_manifest")
    _require_exact_keys(manifest, MANIFEST_KEYS, "order_manifest")
    rows = manifest.get("executed_order")
    members = stage.get("members")
    if not isinstance(rows, list) or not isinstance(members, list):
        raise G2AProbeError(f"stage_members_malformed: {stage_id}")
    minimum = 5 if role == "small" else 1
    if len(rows) < minimum or len(members) != len(rows):
        raise G2AProbeError(f"stage_member_count_invalid: {stage_id}")
    if manifest != {
        "schema_version": ORDER_MANIFEST_SCHEMA,
        "manifest_id": f"g2a-{stage_id}-order-v1",
        "stage_id": stage_id,
        "model_role": role,
        "model_name": model["name"],
        "prefill_tokens": length,
        "planned_n_bundles": len(rows),
        "executed_order": rows,
    }:
        raise G2AProbeError(f"order_manifest_identity_mismatch: {stage_id}")

    config_paths: list[Path] = []
    for zero_index, (row, member) in enumerate(zip(rows, members, strict=True)):
        if not isinstance(row, dict) or not isinstance(member, dict):
            raise G2AProbeError(f"stage_member_malformed: {stage_id}")
        _require_exact_keys(row, MANIFEST_MEMBER_KEYS, "order_manifest_member")
        _require_exact_keys(member, MEMBER_KEYS, "inventory_member")
        actual_run_id = row.get("run_id")
        if actual_run_id in seen_run_ids:
            raise G2AProbeError(f"duplicate_run_id: {actual_run_id}")
        repetition = zero_index + 1
        expected_run_id = _run_id(role, length, repetition)
        expected_rel = f"{stage_id}/{expected_run_id}.json"
        expected_row = {
            "index": repetition,
            "config": f"{expected_run_id}.json",
            "config_sha256": row.get("config_sha256"),
            "run_id": expected_run_id,
            "model_role": role,
            "prefill_tokens": length,
            "repetition": repetition,
        }
        if row != expected_row:
            raise G2AProbeError(f"order_manifest_member_identity_mismatch: {expected_run_id}")
        if member != {
            "index": zero_index,
            "run_id": expected_run_id,
            "config_path": expected_rel,
            "config_sha256": row["config_sha256"],
        }:
            raise G2AProbeError(f"inventory_member_identity_mismatch: {expected_run_id}")
        seen_run_ids.add(expected_run_id)
        config_path = config_root / expected_rel
        observed_sha = _sha256_path(config_path)
        if observed_sha != _require_sha256(row["config_sha256"], "config_sha256"):
            raise G2AProbeError(f"config_sha256_mismatch: {expected_run_id}")
        config = _read_json(config_path, label="benchmark_config")
        _require_exact_keys(config, _expected_config_keys(), "benchmark_config")
        tags = config.get("run_metadata", {}).get("tags", [])
        if "launch_lineage_required" in tags:
            raise G2AProbeError(f"launch_lineage_marker_forbidden: {expected_run_id}")
        try:
            parsed = BenchmarkConfig.from_mapping(config)
        except Exception as exc:  # noqa: BLE001 - normalize schema and extension errors
            raise G2AProbeError(
                f"benchmark_config_refused: {expected_run_id}: {type(exc).__name__}: {exc}"
            ) from exc
        if parsed.config_warnings:
            raise G2AProbeError(f"benchmark_config_warning: {expected_run_id}")
        expected_config = _config_for(
            role=role,
            entry=model,
            rung=rung,
            run_id=expected_run_id,
            panel_sha=panel_sha,
        )
        if config != expected_config:
            raise G2AProbeError(f"benchmark_config_content_mismatch: {expected_run_id}")
        config_paths.append(config_path)

    expected_json = {manifest_path, *config_paths}
    observed_json = set((config_root / stage_id).glob("*.json"))
    if observed_json != expected_json:
        extra = sorted(str(path) for path in observed_json - expected_json)
        missing = sorted(str(path) for path in expected_json - observed_json)
        raise G2AProbeError(f"stage_json_cover_mismatch: extra={extra} missing={missing}")
    return config_paths


def check_inputs(*, root: Path, panel_path: Path, ledger: Path, head_pin: Path) -> None:
    root = root.resolve()
    inventory_path = root / WINDOW_PLAN_LEAF / INVENTORY_NAME
    inventory = _read_json(inventory_path, label="input_inventory")
    _require_exact_keys(inventory, INVENTORY_KEYS, "input_inventory")
    if inventory.get("schema_version") != INPUT_INVENTORY_SCHEMA:
        raise G2AProbeError("input_inventory_schema_mismatch")
    config_root = Path(_require_nonempty(inventory.get("config_root"), "config_root"))
    if not config_root.is_absolute():
        config_root = root / config_root
    if config_root.resolve() != (root / CONFIG_ROOT_LEAF).resolve():
        raise G2AProbeError("input_inventory_config_root_mismatch")

    panel_ref_path = _validate_hash_reference(
        inventory.get("panel"), label="panel", root=root
    )
    if panel_ref_path.resolve() != panel_path.resolve():
        raise G2AProbeError("input_inventory_panel_path_mismatch")
    models, tokenizer_hash = _validate_panel(panel_path)
    panel_sha = _sha256_path(panel_path)
    if inventory["panel"]["sha256"] != panel_sha:
        raise G2AProbeError("input_inventory_panel_sha256_mismatch")

    campaign_policy_path = _validate_hash_reference(
        inventory.get("campaign_policy"), label="campaign_policy", root=root
    )
    try:
        CampaignPolicy.from_mapping(_read_json(campaign_policy_path, label="campaign_policy"))
    except SchemaError as exc:
        raise G2AProbeError(f"campaign_policy_refused: {exc}") from exc
    ladder_path = _validate_hash_reference(
        inventory.get("prompt_ladder"), label="prompt_ladder", root=root
    )
    identity_path = _validate_hash_reference(
        inventory.get("identity_epoch"), label="identity_epoch", root=root
    )
    t1_path = _validate_hash_reference(
        inventory.get("t1_bindings"), label="t1_bindings", root=root
    )
    plan_path = _validate_hash_reference(
        inventory.get("calibration_plan"),
        label="calibration_plan",
        root=root,
        expected_keys=PLAN_REFERENCE_KEYS,
    )

    if inventory.get("power_policy") != POWER_POLICY:
        raise G2AProbeError("input_inventory_power_policy_mismatch")
    identity = _read_json(identity_path, label="identity_epoch")
    t1 = _read_json(t1_path, label="t1_bindings")
    current_identity, current_t1, acceptance = _derive_live_vectors(POWER_POLICY)
    if identity != current_identity:
        raise G2AProbeError("identity_epoch_mismatch")
    if t1 != current_t1:
        raise G2AProbeError("t1_bindings_mismatch")
    ledger_binding = _authenticate_ledger_and_acceptance(
        ledger=ledger, head_pin=head_pin, acceptance=acceptance
    )

    ladder = _read_ladder(ladder_path)
    tokenizer = _load_runtime_tokenizer(models["small"])
    _validate_ladder_with_tokenizer(
        ladder=ladder,
        tokenizer=tokenizer,
        tokenizer_hash=tokenizer_hash,
        panel_sha=panel_sha,
    )
    rungs = {row["prefill_tokens"]: row for row in ladder["rungs"]}

    stages = inventory.get("stages")
    if not isinstance(stages, list) or len(stages) != 8:
        raise G2AProbeError("input_inventory_stages_malformed")
    config_paths: list[Path] = []
    seen_run_ids: set[str] = set()
    for stage, (role, length) in zip(stages, _expected_stage_sequence(), strict=True):
        if not isinstance(stage, dict):
            raise G2AProbeError("input_inventory_stage_malformed")
        config_paths.extend(
            _check_stage(
                stage=stage,
                role=role,
                length=length,
                config_root=config_root,
                model=models[role],
                rung=rungs[length],
                panel_sha=panel_sha,
                seen_run_ids=seen_run_ids,
            )
        )
    doctor = inspect_configs(config_paths)
    if doctor["errors"]:
        raise G2AProbeError(f"doctor_config_errors: {doctor['errors']}")
    if doctor["warnings"]:
        raise G2AProbeError(f"doctor_config_warnings: {doctor['warnings']}")

    plan = _read_json(plan_path, label="calibration_plan")
    expected_plan = _probe_plan(
        root=root,
        panel_path=panel_path,
        campaign_policy=campaign_policy_path,
        ladder_path=ladder_path,
        identity_path=identity_path,
        t1_path=t1_path,
        stages=stages,
        power_policy=POWER_POLICY,
        window_id=_require_nonempty(inventory.get("window_id"), "window_id"),
        session_id=_require_nonempty(inventory.get("session_id"), "session_id"),
        evidence_root_id=_require_nonempty(
            inventory.get("evidence_root_id"), "evidence_root_id"
        ),
        acceptance=acceptance,
        ledger_binding=ledger_binding,
    )
    if plan != expected_plan:
        raise G2AProbeError("calibration_plan_content_mismatch")
    if inventory["calibration_plan"]["plan_id"] != plan.get("plan_id"):
        raise G2AProbeError("calibration_plan_id_mismatch")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build-probes", help="create prompt, config, and manifest bytes")
    build.add_argument("--root", type=Path, required=True)
    build.add_argument("--panel", type=Path, required=True)
    build.add_argument("--prompt-corpus", type=Path, required=True)
    build.add_argument("--small-members", type=int, default=5)
    build.add_argument("--large-members", type=int, default=1)
    build.add_argument("--lengths", type=int, nargs="+", default=list(PREFILL_LENGTHS))

    bind = commands.add_parser("bind-window", help="bind probe bytes to one calibration window")
    bind.add_argument("--root", type=Path, required=True)
    bind.add_argument("--ledger", type=Path, required=True)
    bind.add_argument("--head-pin", type=Path, required=True)
    bind.add_argument("--campaign-policy", type=Path, required=True)
    bind.add_argument("--power-policy", required=True)
    bind.add_argument("--window-id", required=True)
    bind.add_argument("--session-id", required=True)
    bind.add_argument("--evidence-root-id", required=True)

    check = commands.add_parser("check", help="replay every binding without writing")
    check.add_argument("--root", type=Path, required=True)
    check.add_argument("--panel", type=Path, required=True)
    check.add_argument("--ledger", type=Path, required=True)
    check.add_argument("--head-pin", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build-probes":
            build_probes(
                root=args.root,
                panel_path=args.panel,
                prompt_corpus=args.prompt_corpus,
                small_members=args.small_members,
                large_members=args.large_members,
                lengths=args.lengths,
            )
            print("PASS built G2-a prompt ladder, configs, and manifests")
        elif args.command == "bind-window":
            bind_window(
                root=args.root,
                ledger=args.ledger,
                head_pin=args.head_pin,
                campaign_policy=args.campaign_policy,
                power_policy=args.power_policy,
                window_id=args.window_id,
                session_id=args.session_id,
                evidence_root_id=args.evidence_root_id,
            )
            print("PASS bound G2-a inputs to the calibration window")
        else:
            check_inputs(
                root=args.root,
                panel_path=args.panel,
                ledger=args.ledger,
                head_pin=args.head_pin,
            )
            print("PASS G2-a inputs authenticate with no config warnings")
        return 0
    except G2AProbeError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
