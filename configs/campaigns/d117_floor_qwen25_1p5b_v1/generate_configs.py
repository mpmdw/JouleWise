#!/usr/bin/env python3
"""Generate the D-117 Qwen2.5-1.5B floor campaign draft deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
PACK_REL = Path("configs/campaigns/d117_floor_qwen25_1p5b_v1")
CALIBRATION_PLAN_REFERENCE = "calibration_plan.json"
CURRENT_FAMILY_SUFFIX = "_v1"
SPEC_REL = Path("configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json")
SOURCE_PATH = Path(__file__).resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.detection_floor import (  # noqa: E402
    COMMON_MODE_ESTIMATOR_ID,
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    two_shared_edge_common_mode_registration,
)
from joulewise.floor_extraction import (  # noqa: E402
    validate_condition_family_definition,
    validate_extraction_spec,
)
from joulewise.identity_pins import (  # noqa: E402
    IDENTITY_PIN_DERIVATION_CONTRACT,
    IDENTITY_PIN_PROJECTION_WORK_ORDER,
    validate_identity_pin_projection,
)
from joulewise.arm_readiness import (  # noqa: E402
    plan_arm_readiness_attachment,
)
from joulewise.receipt_oracle import (  # noqa: E402
    derive_bracket_session_receipt_oracle,
)


N = 10
PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-1p5b-v1"
CLAIM_ROOT_LEAF = "runs_d117_floor_qwen25_1p5b_v1"
BOUND_ROOT_LEAF = "runs_d117_floor_qwen25_1p5b_v1_bound"
CAMPAIGN_TAG = "d117-floor-qwen25-1p5b-v1"
DRAFT_STATUS = "unfrozen_draft"
FROZEN_STATUS = "frozen_by_d134_receipt"
CURRENT_FROZEN_RECEIPT_SHA256 = (
    "ddbbb40974c1b747516f403b3d319079519269892ee48e052a028d9f16b1e738"
)
CURRENT_FROZEN_GENERATOR_SHA256 = (
    "ea0d93ac653bf2b0610691aff668e4f4f7941ae7734ca2e0500589ddfd325c06"
)
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
TREE_SCHEMA = "joulewise.d117_plan_tree.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
DECODE_FAMILY_ID = "df-ph-decode"
PREFILL_FAMILY_ID = "df-ph-prefill-p128-qwen25-1p5b"
P256_FAMILY_ID = "df-ph-prefill-p256-qwen25-1p5b"
DECODE_FAMILY_REL = PACK_REL / "condition_families/condition_family_df_ph_decode.json"
PREFILL_FAMILY_REL = (
    PACK_REL
    / "condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json"
)
P256_FAMILY_REL = (
    PACK_REL
    / "condition_families/condition_family_df_ph_prefill_p256_qwen25_1p5b.json"
)
P256_PROMPT_REL = Path(
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/"
    "prefill_prompt_candidate.json"
)
P256_PROMPT_ARTIFACT_SHA256 = (
    "9e1d8eecb688a4ae54c76d24d71be618411c011fa5bebffa44ad6a91ef03d456"
)
P256_PROMPT_UTF8_SHA256 = (
    "f149dddcb4b9d27b3d68b0455c5f774e56e37bfc04430b53e139a4c08f044faf"
)
P256_SHARED_TOKENIZER_JSON_SHA256 = (
    "a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf"
)
P256_RULED_TOKEN_ID_SHA256_PREFIX = "83099a66"
LEGACY_DECODE_PLAN_SHA256 = (
    "56b164904cd0ffd0b9af5710ab60e4794cbd47b866a1053de5a7548475bda182"
)
SOURCE_DECODE_FAMILY_REL = Path("configs/floor_mint/condition_family_df_ph_decode.json")
POLICY_REL = Path("configs/campaign_policies/quiet_mac_p2_production.json")
ACCEPTANCE_REL = Path("configs/calibration/calibration_acceptance_d079_v2.json")
LEDGER_HEAD_REL = Path("configs/calibration/calibration_ledger_head.json")
POLICY_SHA256 = "b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd"
DECODE_FAMILY_BYTE_SHA256 = (
    "c9054d11a2bf9c4b1718d93ededc44864cfffb34417d19f1178a9d18addcf8a8"
)
DECODE_FAMILY_DOMAIN_SHA256 = (
    "e38e2a2f3e76b8cdd6b3ef4f5d3d7090ef4846dbf83279001ff4df8a9a762bfe"
)
PREFILL_FAMILY_BYTE_SHA256 = (
    "985a4e5370724698b601303b2ba99027d298060eedc95a65d20112df413043ad"
)
PREFILL_FAMILY_DOMAIN_SHA256 = (
    "974014e096806423b866a167510787482397cb4f68bb9e6f9f0ba7fd34f93f36"
)
P256_FAMILY_BYTE_SHA256 = (
    "c7d2b28276791ab8c5c10b27460bbccba6cb7aad75470e9d74ba4b64ed4ef9f2"
)
P256_FAMILY_DOMAIN_SHA256 = (
    "93c9ee9b32c8c2b25675cff263e2c98882fe5f0c7f81f3ad6899f55f6f9d3c39"
)
ACCEPTANCE_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)
ACCEPTANCE_DERIVATION_SHA256 = (
    "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
)
LEDGER_HEAD_FILE_SHA256 = (
    "6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902"
)
LEDGER_HEAD_SHA256 = (
    "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
)
NEG8_MANIFEST_REL = Path("configs/campaigns/neg8_reference_corpus/order_manifest.json")
NEG8_SETTLED_REL = Path(
    "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json"
)
START_MANIFEST_REL = Path(
    "configs/campaigns/window_references/start_triplet/order_manifest.json"
)
MIDPOINT_MANIFEST_REL = Path(
    "configs/campaigns/window_references/midpoint/order_manifest.json"
)
END_MANIFEST_REL = Path(
    "configs/campaigns/window_references/end_triplet/order_manifest.json"
)
EXTERNAL_MANIFEST_SHAS = {
    NEG8_MANIFEST_REL: "0ec9d68aa4265cc9378bb682091a973fc92879b76506fa25af828050a608509f",
    START_MANIFEST_REL: "9cac197255bdc9a0a1a0b8ee8ceb587ba3c8cabc20b976b2543dc3a400d37cb0",
    MIDPOINT_MANIFEST_REL: "9ccedd91307985ba5641e791f4ac89f4e250fca414a4ba713cc7977ced6abb21",
    END_MANIFEST_REL: "8e65a4347aafa0722a60a2bd58c7e8061b860db66fa06f6acec24d1a1ade5c67",
}
NEG8_SETTLED_SHA256 = (
    "74ccdaec74497c3aa7c074ef1129ec2bf2cc01d8ac14d3d07be77ab468599688"
)

def freeze_aware_status(freeze_reference: object) -> str:
    """Return future-pack status without rewriting the 2026-08-13 frozen bytes."""

    if not isinstance(freeze_reference, dict):
        return DRAFT_STATUS
    if freeze_reference.get("sha256") == CURRENT_FROZEN_RECEIPT_SHA256:
        return DRAFT_STATUS
    return FROZEN_STATUS


ARM_READINESS_ATTACHMENT = plan_arm_readiness_attachment(
    REPO_ROOT / PACK_REL,
    "ALPHA",
    REPO_ROOT,
)
_FREEZE_REFERENCE = ARM_READINESS_ATTACHMENT["freeze_receipt"]
PRESERVE_CURRENT_FROZEN_BYTES = (
    isinstance(_FREEZE_REFERENCE, dict)
    and _FREEZE_REFERENCE.get("sha256") == CURRENT_FROZEN_RECEIPT_SHA256
)
PACK_STATUS = freeze_aware_status(_FREEZE_REFERENCE)


class GenerationIdentity:
    def __init__(
        self,
        pack_id: str = PACK_REL.name,
        family_suffix: str = CURRENT_FAMILY_SUFFIX,
        preserve_current_frozen_bytes: bool = PRESERVE_CURRENT_FROZEN_BYTES,
    ) -> None:
        self.pack_id = pack_id
        self.family_suffix = family_suffix
        self.preserve_current_frozen_bytes = preserve_current_frozen_bytes
        if not self.family_suffix.startswith("_v") or not self.family_suffix[2:].isdigit():
            raise ValueError("family suffix must use the _v<positive integer> form")
        if int(self.family_suffix[2:]) < 1:
            raise ValueError("family suffix ordinal must be positive")
        expected_pack_id = (
            PACK_REL.name.removesuffix(CURRENT_FAMILY_SUFFIX) + self.family_suffix
        )
        if self.pack_id != expected_pack_id:
            raise ValueError(
                f"pack id must equal {expected_pack_id!r} for {self.family_suffix}"
            )
        if self.preserve_current_frozen_bytes and not self.target_is_current:
            raise ValueError(
                "preserve mode requires the current target identity"
            )
        if (
            not self.preserve_current_frozen_bytes
            and self.target_is_current
            and (PRESERVE_CURRENT_FROZEN_BYTES or self.target_status == FROZEN_STATUS)
        ):
            raise ValueError("the current frozen identity requires preserve mode")

    @property
    def pack_rel(self) -> Path:
        return PACK_REL.with_name(self.pack_id)

    @property
    def current_ordinal(self) -> int:
        return int(CURRENT_FAMILY_SUFFIX[2:])

    @property
    def target_ordinal(self) -> int:
        return int(self.family_suffix[2:])

    @property
    def target_is_current(self) -> bool:
        return self.pack_id == PACK_REL.name and self.target_ordinal == self.current_ordinal

    @property
    def target_is_successor_family(self) -> bool:
        return self.target_ordinal >= 2

    @property
    def target_status(self) -> str:
        if not self.target_is_current:
            return DRAFT_STATUS
        return freeze_aware_status(ARM_READINESS_ATTACHMENT["freeze_receipt"])


_ACTIVE_GENERATION: GenerationIdentity | None = None
_SUCCESSOR_IDENTITY_TOKENS = (
    "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1",
    "evidence-d117-floor-qwen25-1p5b-v1",
    "plan-set-d117-qwen25-1p5b-7b-phase-floor-v1",
    "d117-qwen25-phase-floor-set-v1",
    "d117-qwen25-1p5b-phase-floor-component-v1",
    "d117-qwen25-1p5b-prefill-p256-floor-v1",
    "d117-qwen25-1p5b-prefill-p128-floor-v1",
    "d117-qwen25-1p5b-decode-floor-v1",
    "tg-d117-qwen25-1p5b-prefill-p256-v1",
    "tg-d117-qwen25-1p5b-prefill-p128-v1",
    "tg-d117-qwen25-1p5b-decode-v1",
    "d117_contrast_qwen25_1p5b_vs_7b_v1",
    "d117_floor_qwen25_1p5b_v1",
    "d117-floor-qwen25-1p5b-v1",
)


def active_generation() -> GenerationIdentity:
    return _ACTIVE_GENERATION or GenerationIdentity()


@contextmanager
def generation_context(identity: GenerationIdentity):
    global _ACTIVE_GENERATION
    previous = _ACTIVE_GENERATION
    _ACTIVE_GENERATION = identity
    try:
        yield
    finally:
        _ACTIVE_GENERATION = previous


def _successor_token(token: str, identity: GenerationIdentity) -> str:
    if token == PACK_REL.name:
        return identity.pack_id
    current_version = CURRENT_FAMILY_SUFFIX.removeprefix("_")
    version = identity.family_suffix.removeprefix("_")
    hyphen_suffix = f"-{current_version}"
    if token.endswith(hyphen_suffix):
        return token[: -len(hyphen_suffix)] + f"-{version}"
    if token.endswith(CURRENT_FAMILY_SUFFIX):
        return token[: -len(CURRENT_FAMILY_SUFFIX)] + identity.family_suffix
    raise ValueError(f"successor identity token has no version suffix: {token}")


def thread_generation_identity(value: Any) -> Any:
    identity = active_generation()
    if identity.target_is_current:
        return value
    if isinstance(value, str):
        for token in _SUCCESSOR_IDENTITY_TOKENS:
            value = value.replace(token, _successor_token(token, identity))
        return value
    if isinstance(value, dict):
        return {
            thread_generation_identity(key): thread_generation_identity(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [thread_generation_identity(item) for item in value]
    if isinstance(value, tuple):
        return tuple(thread_generation_identity(item) for item in value)
    return value


def embedded_generator_bytes() -> bytes:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    identity = active_generation()
    if identity.target_is_current:
        return source.encode("utf-8")
    source = thread_generation_identity(source)
    current_declaration = f'CURRENT_FAMILY_SUFFIX = "{CURRENT_FAMILY_SUFFIX}"'
    successor_declaration = f'CURRENT_FAMILY_SUFFIX = "{identity.family_suffix}"'
    if source.count(current_declaration) != 1:
        raise ValueError("generator family-suffix declaration is not unique")
    return source.replace(current_declaration, successor_declaration).encode("utf-8")


def generated_relative_path(relative: Path) -> Path:
    identity = active_generation()
    try:
        inside_pack = relative.relative_to(PACK_REL)
    except ValueError:
        if relative == extraction_spec_rel(identity):
            return relative
        raise ValueError(f"output path is outside the target allowlist: {relative}")
    return identity.pack_rel / inside_pack


def extraction_spec_rel(identity: GenerationIdentity | None = None) -> Path:
    selected = identity or active_generation()
    if selected.target_ordinal == 1:
        return SPEC_REL
    stem_suffix = "_extraction_spec"
    family_stem = SPEC_REL.stem.removesuffix(stem_suffix)
    return SPEC_REL.with_name(
        f"{family_stem}{selected.family_suffix}{stem_suffix}{SPEC_REL.suffix}"
    )


def emitted_plan_reference() -> str:
    if active_generation().target_ordinal == 1:
        return (PACK_REL / CALIBRATION_PLAN_REFERENCE).as_posix()
    return CALIBRATION_PLAN_REFERENCE


def emitted_plan_sidecar_reference() -> str:
    if active_generation().target_ordinal == 1:
        return (PACK_REL / "calibration_plan.sha256").as_posix()
    return "calibration_plan.sha256"


def generation_arm_readiness_attachment() -> dict[str, Any]:
    identity = active_generation()
    return plan_arm_readiness_attachment(
        REPO_ROOT / identity.pack_rel,
        "ALPHA",
        REPO_ROOT,
    )


def freeze_aware_projection(generated: dict[str, Any]) -> dict[str, Any]:
    if not active_generation().preserve_current_frozen_bytes:
        return generated
    current = json.loads(
        (REPO_ROOT / PACK_REL / "producer_contract.json").read_text(
            encoding="utf-8"
        )
    )
    return current["identity_pin_projection"]


def preserved_generator_sha256() -> str:
    tree = json.loads(
        (REPO_ROOT / active_generation().pack_rel / "plan_tree.json").read_text(
            encoding="utf-8"
        )
    )
    return tree["generator"]["sha256"]


SUCCESSOR_REGENERATION_RULE = (
    "A successor acceptance artifact issuing before arm REQUIRES pack regeneration "
    "(packs are unfrozen drafts; the D-125 lineage-envelope alternative is recorded "
    "as a freeze-time lead decision)."
    if PACK_STATUS == DRAFT_STATUS
    else "A successor acceptance artifact issuing before arm REQUIRES a newly "
    "generated and newly frozen pack; the D-134 freeze receipt is authoritative."
)

MODEL = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "mlx",
    "context_window": 32768,
}
QUANTIZATION = {"name": "int4", "bits": 4}
HARDWARE = {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": (
        "D-117 alpha Qwen2.5-1.5B production floor campaign on the current "
        "M3 Max; normal powermetrics sampler set only."
    ),
}
WORKLOAD = {
    "name": "df_ph_decode",
    "repetitions": 1,
    "warmup_runs": 1,
    "prompt_tokens": 128,
    "output_tokens": 512,
}
P256_WORKLOAD_NAME = "df_ph_prefill_p256_candidate"
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}
STAGES = (
    {
        "stage_id": "01_phase_decode_absolute",
        "role": "absolute_phase_decode",
        "ordering_note": "Ten fixed absolute decode repeats in repetition order.",
    },
    {
        "stage_id": "02_phase_decode_abba_blocks_01_05",
        "role": "comparative_phase_decode_first_half",
        "ordering_note": "Fixed contiguous null A/B/B/A decode blocks 1-5.",
    },
    {
        "stage_id": "03_phase_decode_abba_blocks_06_10",
        "role": "comparative_phase_decode_second_half",
        "ordering_note": "Fixed contiguous null A/B/B/A decode blocks 6-10.",
    },
    {
        "stage_id": "04_phase_prefill_p256_absolute",
        "role": "absolute_phase_prefill_p256",
        "ordering_note": "Ten fixed absolute p256 prefill repeats in repetition order.",
    },
    {
        "stage_id": "05_phase_prefill_p256_abba_blocks_01_05",
        "role": "comparative_phase_prefill_p256_first_half",
        "ordering_note": "Fixed contiguous null A/B/B/A p256 prefill blocks 1-5.",
    },
    {
        "stage_id": "06_phase_prefill_p256_abba_blocks_06_10",
        "role": "comparative_phase_prefill_p256_second_half",
        "ordering_note": "Fixed contiguous null A/B/B/A p256 prefill blocks 6-10.",
    },
)


def render_json(value: Any) -> bytes:
    return (
        json.dumps(thread_generation_identity(value), indent=2, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        thread_generation_identity(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_bytes(output_root: Path, relative: Path, raw: bytes) -> None:
    resolved = generated_relative_path(relative)
    if resolved not in validate_generation_output_inventory(active_generation()):
        raise ValueError(f"output path is outside the closed inventory: {resolved}")
    path = output_root / resolved
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def validate_generation_write_boundary(
    output_root: Path, outputs: Iterable[Path]
) -> None:
    """Refuse link traversal or anomalous existing nodes before any write."""

    root = output_root.absolute()

    def refuse(path: Path, reason: str) -> None:
        destination = path.resolve(strict=False)
        raise ValueError(
            f"refusing generation: {reason}: {path} -> {destination}"
        )

    if root.is_symlink():
        refuse(root, "output root is a symlink")
    if root.exists() and not root.is_dir():
        refuse(root, "output root is not a real directory")

    for relative in sorted(outputs, key=lambda path: path.as_posix()):
        current = root
        for component in relative.parts[:-1]:
            current = current / component
            if current.is_symlink():
                refuse(current, "write ancestor is a symlink")
            if current.exists() and not current.is_dir():
                refuse(current, "write ancestor is not a real directory")
        target = current / relative.name
        if target.is_symlink():
            refuse(target, "write target is a symlink")
        if target.exists() and not target.is_file():
            refuse(target, "existing write target is not a regular file")


def write_json(output_root: Path, relative: Path, value: Any) -> bytes:
    raw = render_json(value)
    write_bytes(output_root, relative, raw)
    return raw


def sidecar_bytes(digest: str, filename: str) -> bytes:
    return f"{digest}  {filename}\n".encode("utf-8")


def prefill_family_definition() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": PREFILL_FAMILY_ID,
        "workload_profile": {
            "name": "df_ph_decode",
            "prompt_tokens": 128,
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "measurement_target": {
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def p256_family_definition() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": P256_FAMILY_ID,
        "workload_profile": {
            "name": P256_WORKLOAD_NAME,
            "prompt_tokens": 256,
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "measurement_target": {
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def load_p256_prompt_text() -> str:
    prompt_raw = (REPO_ROOT / P256_PROMPT_REL).read_bytes()
    if sha256_bytes(prompt_raw) != P256_PROMPT_ARTIFACT_SHA256:
        raise ValueError("p256 prompt artifact bytes drifted")
    prompt = json.loads(prompt_raw)
    text = prompt.get("prompt_text") if isinstance(prompt, dict) else None
    if not isinstance(text, str) or not text:
        raise ValueError("p256 prompt artifact has no prompt_text")
    if sha256_bytes(text.encode("utf-8")) != P256_PROMPT_UTF8_SHA256:
        raise ValueError("p256 prompt UTF-8 hash differs from the Q1 pin")
    if prompt.get("prompt_text_utf8_sha256") != P256_PROMPT_UTF8_SHA256:
        raise ValueError("p256 prompt artifact declares the wrong UTF-8 hash")
    if prompt.get("planned_token_count") != 256:
        raise ValueError("p256 prompt artifact does not declare 256 planned tokens")
    token_basis = prompt.get("token_count_basis")
    if not isinstance(token_basis, dict) or token_basis.get(
        "shared_tokenizer_json_sha256"
    ) != P256_SHARED_TOKENIZER_JSON_SHA256:
        raise ValueError("p256 prompt shared-tokenizer pin drifted")
    return text


def load_and_verify_families() -> tuple[
    dict[str, Any], bytes, dict[str, Any], bytes, dict[str, Any], bytes
]:
    decode_raw = (REPO_ROOT / SOURCE_DECODE_FAMILY_REL).read_bytes()
    if sha256_bytes(decode_raw) != DECODE_FAMILY_BYTE_SHA256:
        raise ValueError("decode condition-family source bytes drifted")
    decode = json.loads(decode_raw)
    if validate_condition_family_definition(decode):
        raise ValueError("decode condition-family source is invalid")
    if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, decode) != DECODE_FAMILY_DOMAIN_SHA256:
        raise ValueError("decode condition-family domain hash drifted")

    prefill = prefill_family_definition()
    errors = validate_condition_family_definition(prefill)
    if errors:
        raise ValueError(f"prefill condition-family definition is invalid: {errors[0]}")
    prefill_raw = render_json(prefill)
    if sha256_bytes(prefill_raw) != PREFILL_FAMILY_BYTE_SHA256:
        raise ValueError("prefill condition-family byte hash differs from the reviewed pin")
    if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, prefill) != PREFILL_FAMILY_DOMAIN_SHA256:
        raise ValueError("prefill condition-family domain hash differs from the reviewed pin")
    p256 = p256_family_definition()
    errors = validate_condition_family_definition(p256)
    if errors:
        raise ValueError(f"p256 condition-family definition is invalid: {errors[0]}")
    p256_raw = render_json(p256)
    if sha256_bytes(p256_raw) != P256_FAMILY_BYTE_SHA256:
        raise ValueError("p256 condition-family byte hash differs from the reviewed pin")
    if canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, p256) != P256_FAMILY_DOMAIN_SHA256:
        raise ValueError("p256 condition-family domain hash differs from the reviewed pin")
    return decode, decode_raw, prefill, prefill_raw, p256, p256_raw


def build_assembly() -> tuple[
    list[dict[str, Any]],
    list[str],
    list[dict[str, Any]],
    list[str],
    list[dict[str, Any]],
]:
    stages = [{**stage, "runs": []} for stage in STAGES]
    absolute_ids: list[str] = []
    for rep in range(1, N + 1):
        run_id = f"d117f15-df-ph-decode-abs-r{rep:02d}"
        run = {
            "run_id": run_id,
            "filename": f"{run_id}.json",
            "rep": rep,
            "role": "absolute_repeat",
            "block_id": None,
            "block_index": rep,
            "position": None,
            "position_in_block": 1,
            "arm": None,
            "collection_tags": [f"rep{rep}"],
        }
        stages[0]["runs"].append(run)
        absolute_ids.append(run_id)

    blocks: list[dict[str, Any]] = []
    positions = (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2"))
    for block in range(1, N + 1):
        block_id = f"d117-df-cmp-abba-ph-decode-qwen25-1p5b-b{block:02d}"
        members: dict[str, str] = {}
        for sequence_index, (label, position) in enumerate(positions, start=1):
            run_id = (
                f"d117f15-df-cmp-abba-ph-decode-b{block:02d}-"
                f"{position.lower()}"
            )
            run = {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": block,
                "role": "comparative_abba_member",
                "block_id": block_id,
                "block_index": block,
                "position": position,
                "position_in_block": sequence_index,
                "arm": label,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stages[1 if block <= 5 else 2]["runs"].append(run)
            members[position] = run_id
        blocks.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": members,
            }
        )

    p256_absolute_ids: list[str] = []
    for rep in range(1, N + 1):
        run_id = f"d117f15-df-ph-prefill-p256-abs-r{rep:02d}"
        run = {
            "run_id": run_id,
            "filename": f"{run_id}.json",
            "rep": rep,
            "role": "absolute_repeat",
            "block_id": None,
            "block_index": rep,
            "position": None,
            "position_in_block": 1,
            "arm": None,
            "condition_family_id": P256_FAMILY_ID,
            "collection_tags": [f"rep{rep}"],
        }
        stages[3]["runs"].append(run)
        p256_absolute_ids.append(run_id)

    p256_blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = (
            f"d117-df-cmp-abba-ph-prefill-p256-qwen25-1p5b-b{block:02d}"
        )
        members: dict[str, str] = {}
        for sequence_index, (label, position) in enumerate(positions, start=1):
            run_id = (
                f"d117f15-df-cmp-abba-ph-prefill-p256-b{block:02d}-"
                f"{position.lower()}"
            )
            run = {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": block,
                "role": "comparative_abba_member",
                "block_id": block_id,
                "block_index": block,
                "position": position,
                "position_in_block": sequence_index,
                "arm": label,
                "condition_family_id": P256_FAMILY_ID,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stages[4 if block <= 5 else 5]["runs"].append(run)
            members[position] = run_id
        p256_blocks.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": members,
            }
        )
    return stages, absolute_ids, blocks, p256_absolute_ids, p256_blocks


def calibration_plan_blocks(
    blocks: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    positions = (("A1", "A"), ("B1", "B"), ("B2", "B"), ("A2", "A"))
    return [
        {
            "block_id": block["block_id"],
            "executed_labels": ["A", "B", "B", "A"],
            "members": [
                {
                    "position": position,
                    "plan_label": label,
                    "plan_sequence_index": index,
                    "bundle_id": block["members"][position],
                }
                for index, (position, label) in enumerate(positions, start=1)
            ],
        }
        for block in blocks
    ]


def config_for(
    run: dict[str, Any], plan_sha256: str, p256_prompt_text: str
) -> dict[str, Any]:
    family_id = run.get("condition_family_id", DECODE_FAMILY_ID)
    workload = (
        {
            "name": P256_WORKLOAD_NAME,
            "repetitions": 1,
            "warmup_runs": 1,
            "output_tokens": 512,
            "prompt_text": p256_prompt_text,
        }
        if family_id == P256_FAMILY_ID
        else WORKLOAD
    )
    tags = [
        "phase2",
        CAMPAIGN_TAG,
        "production-window",
        "floor-calibration",
        f"df-condition={family_id}",
        f"calibration-plan-sha256={plan_sha256}",
        *run["collection_tags"],
    ]
    if active_generation().target_is_successor_family:
        tags.append("launch_lineage_required")
    return {
        "schema_version": "0.1",
        "run_id": run["run_id"],
        "model": MODEL,
        "quantization": QUANTIZATION,
        "hardware_target": HARDWARE,
        "workload_profile": workload,
        "interconnect": {"name": "local"},
        "sampling": SAMPLING,
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": tags,
        },
    }


def manifest_entry(
    run: dict[str, Any], index: int, config: str, config_sha256: str
) -> dict[str, Any]:
    return {
        "index": index,
        "config": config,
        "config_sha256": config_sha256,
        "run_id": run["run_id"],
        "model_tag": "qwen25-1p5b-mlx",
        "rep": run["rep"],
        "workload": run.get("condition_family_id", DECODE_FAMILY_ID),
        "role": run["role"],
        "block_id": run["block_id"],
        "block_index": run["block_index"],
        "position": run["position"],
        "position_in_block": run["position_in_block"],
        "arm": run["arm"],
    }


def external_manifest(external_id: str, manifest_rel: Path) -> dict[str, Any]:
    expected_sha = EXTERNAL_MANIFEST_SHAS[manifest_rel]
    if sha256_file(REPO_ROOT / manifest_rel) != expected_sha:
        raise ValueError(f"external manifest drifted: {manifest_rel.as_posix()}")
    manifest = json.loads((REPO_ROOT / manifest_rel).read_text(encoding="utf-8"))
    rows = manifest.get("executed_order")
    if not isinstance(rows, list):
        raise ValueError(f"external manifest has no executed_order: {manifest_rel}")
    members: list[dict[str, Any]] = []
    for row in rows:
        config = row.get("config") if isinstance(row, dict) else None
        run_id = row.get("run_id") if isinstance(row, dict) else None
        if not isinstance(config, str) or not isinstance(run_id, str):
            raise ValueError(f"external manifest row is malformed: {manifest_rel}")
        config_rel = manifest_rel.parent / config
        members.append(
            {
                "ordinal": len(members) + 1,
                "run_id": run_id,
                "path": config_rel.as_posix(),
                "sha256": sha256_file(REPO_ROOT / config_rel),
            }
        )
    return {
        "external_input_id": external_id,
        "manifest": {
            "path": manifest_rel.as_posix(),
            "manifest_id": manifest.get("manifest_id"),
            "sha256": expected_sha,
        },
        "expected_count": len(members),
        "members": members,
    }


def argument(kind: str, value: str, relative: str | None = None) -> dict[str, str]:
    row = {"kind": kind, "value": value}
    if relative is not None:
        row["relative"] = relative
    return row


def literal(value: str) -> dict[str, str]:
    return argument("literal", value)


def repo_path(value: str | Path) -> dict[str, str]:
    return argument("repo_path", Path(value).as_posix())


def binding(value: str) -> dict[str, str]:
    return argument("binding", value)


def binding_path(value: str, relative: str) -> dict[str, str]:
    return argument("binding_path", value, relative)


def tree_pointer(value: str) -> dict[str, str]:
    return argument("tree_pointer", value)


def launch_recipe(
    command_id: str,
    command_kind: str,
    tool_id: str,
    interface_id: str,
    arguments: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.stage_launch.v1",
        "commands": [
            {
                "command_id": command_id,
                "command_kind": command_kind,
                "argv_template": {
                    "tool_id": tool_id,
                    "interface_id": interface_id,
                    "arguments": arguments,
                },
                "cwd": {"kind": "binding", "value": "repo_root"},
                "success_exit_codes": [0],
            }
        ],
    }


def campaign_launch(
    stage_id: str, config_dir: Path, root_binding: str
) -> dict[str, Any]:
    return launch_recipe(
        f"{stage_id}.collect",
        "campaign_collection",
        "campaign_runner",
        "joulewise.run_campaign.cli.v1",
        [
            repo_path(config_dir),
            literal("--runs-dir"),
            binding(root_binding),
            literal("--log"),
            binding_path(root_binding, "campaign_log.jsonl"),
            literal("--campaign-policy"),
            repo_path(POLICY_REL),
            literal("--instrument-calibration-dir"),
            binding("pre_calibration_dir"),
            literal("--instrument-power-policy"),
            literal("ac_high_power"),
            literal("--arm-quiet-mode"),
            literal("--arm-countdown-s"),
            literal("20"),
            literal("--max-failures"),
            literal("1"),
        ],
    )


def freeze_aware_reservation_plan_arguments(
    identity: GenerationIdentity | None = None,
    *,
    pack_rel: Path | None = None,
    plan_reference: str = CALIBRATION_PLAN_REFERENCE,
) -> list[dict[str, str]]:
    selected = identity or active_generation()
    if selected.target_ordinal == 1:
        return []
    if plan_reference != CALIBRATION_PLAN_REFERENCE:
        raise ValueError("reservation plan must use the canonical pack-relative reference")
    resolved_pack_rel = pack_rel or selected.pack_rel
    return [literal("--plan"), repo_path(resolved_pack_rel / plan_reference)]


def stage_graph(
    stage_manifest_refs: dict[str, dict[str, Any]],
    external_inputs: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    bracket_args = [
        literal("--ledger"), binding("ledger_path"),
        literal("--head-pin"), repo_path(LEDGER_HEAD_REL),
        *freeze_aware_reservation_plan_arguments(
            active_generation(),
            pack_rel=active_generation().pack_rel,
            plan_reference=CALIBRATION_PLAN_REFERENCE,
        ),
        literal("--session-id"), binding("bracket_session_id"),
        literal("--window-id"), tree_pointer("/window_identity/window_id"),
        literal("--plan-id"), tree_pointer("/plan/plan_id"),
        literal("--plan-sha256"), tree_pointer("/plan/actual_sha256"),
        literal("--evidence-root-id"), tree_pointer("/window_identity/evidence_root_id"),
        literal("--runs-root"), binding("claim_runs_root"),
        literal("--pre-attempt-id"), binding("pre_attempt_id"),
        literal("--post-attempt-id"), binding("post_attempt_id"),
        literal("--pre-custody-locator"), binding("pre_calibration_dir"),
        literal("--post-custody-locator"), binding("post_calibration_dir"),
        literal("--identity-epoch-json"), binding("identity_epoch_json"),
        literal("--t1-bindings-json"), binding("t1_bindings_json"),
        literal("--execute"),
    ]
    capture_common = [
        literal("--allow-live"),
        literal("--output-root"), binding_path("claim_runs_root", "instrument_validation"),
        literal("--session-id"), binding("bracket_session_id"),
    ]
    pre_capture = capture_common + [
        literal("--slot"), literal("pre"),
        literal("--attempt-id"), binding("pre_attempt_id"),
        literal("--power-policy"), literal("ac_high_power"),
    ]
    post_capture = capture_common + [
        literal("--slot"), literal("post"),
        literal("--attempt-id"), binding("post_attempt_id"),
        literal("--power-policy"), literal("ac_high_power"),
    ]
    stages: list[dict[str, Any]] = [
        {
            "stage_id": "alpha-bracket-reservation",
            "kind": "bracket_reservation",
            "expected_count": 1,
            "input": {"kind": "arm_bindings"},
            "launch": launch_recipe(
                "alpha-bracket-reservation.reserve",
                "bracket_reservation",
                "bracket_reserver",
                "joulewise.calibration_window_bracket_reservation.cli.v1",
                bracket_args,
            ),
        },
        {
            "stage_id": "alpha-pre-calibration",
            "kind": "calibration_capture",
            "expected_count": 1,
            "input": {"kind": "arm_bindings", "slot": "pre"},
            "launch": launch_recipe(
                "alpha-pre-calibration.capture",
                "calibration_capture",
                "fiducial_capture",
                "joulewise.powermetrics_fiducial.cli.v1",
                pre_capture,
            ),
        },
        {
            "stage_id": "alpha-bound-collection",
            "kind": "campaign_collection",
            "expected_count": 12,
            "input": external_inputs["neg8_bound"]["manifest"],
            "launch": campaign_launch(
                "alpha-bound-collection",
                NEG8_MANIFEST_REL.parent,
                "bound_runs_root",
            ),
        },
        {
            "stage_id": "alpha-bound-derivation",
            "kind": "bound_derivation",
            "expected_count": 1,
            "input": {
                "kind": "external_artifact",
                "path": NEG8_SETTLED_REL.as_posix(),
                "sha256": NEG8_SETTLED_SHA256,
            },
            "launch": launch_recipe(
                "alpha-bound-derivation.derive",
                "bound_derivation",
                "campaign_runner",
                "joulewise.run_campaign.cli.v1",
                [
                    literal("--derive-neg8-drift-bound"), repo_path(NEG8_SETTLED_REL),
                    literal("--neg8-drift-bound-output"), binding_path("bound_runs_root", "neg8-drift-bound.json"),
                    literal("--runs-dir"), binding("bound_runs_root"),
                ],
            ),
        },
        {
            "stage_id": "alpha-reference-start",
            "kind": "campaign_collection",
            "expected_count": 3,
            "input": external_inputs["start_reference"]["manifest"],
            "launch": campaign_launch(
                "alpha-reference-start", START_MANIFEST_REL.parent, "claim_runs_root"
            ),
        },
        {
            "stage_id": "alpha-science-absolute",
            "kind": "campaign_collection",
            "expected_count": 10,
            "input": stage_manifest_refs["01_phase_decode_absolute"],
            "launch": campaign_launch(
                "alpha-science-absolute",
                PACK_REL / "01_phase_decode_absolute",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-science-abba-01-05",
            "kind": "campaign_collection",
            "expected_count": 20,
            "input": stage_manifest_refs["02_phase_decode_abba_blocks_01_05"],
            "launch": campaign_launch(
                "alpha-science-abba-01-05",
                PACK_REL / "02_phase_decode_abba_blocks_01_05",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-science-abba-06-10",
            "kind": "campaign_collection",
            "expected_count": 20,
            "input": stage_manifest_refs["03_phase_decode_abba_blocks_06_10"],
            "launch": campaign_launch(
                "alpha-science-abba-06-10",
                PACK_REL / "03_phase_decode_abba_blocks_06_10",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-reference-midpoint",
            "kind": "campaign_collection",
            "expected_count": 1,
            "input": external_inputs["midpoint_reference"]["manifest"],
            "launch": campaign_launch(
                "alpha-reference-midpoint", MIDPOINT_MANIFEST_REL.parent, "claim_runs_root"
            ),
        },
        {
            "stage_id": "alpha-science-prefill-p256-absolute",
            "kind": "campaign_collection",
            "expected_count": 10,
            "input": stage_manifest_refs["04_phase_prefill_p256_absolute"],
            "launch": campaign_launch(
                "alpha-science-prefill-p256-absolute",
                PACK_REL / "04_phase_prefill_p256_absolute",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-science-prefill-p256-abba-01-05",
            "kind": "campaign_collection",
            "expected_count": 20,
            "input": stage_manifest_refs["05_phase_prefill_p256_abba_blocks_01_05"],
            "launch": campaign_launch(
                "alpha-science-prefill-p256-abba-01-05",
                PACK_REL / "05_phase_prefill_p256_abba_blocks_01_05",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-science-prefill-p256-abba-06-10",
            "kind": "campaign_collection",
            "expected_count": 20,
            "input": stage_manifest_refs["06_phase_prefill_p256_abba_blocks_06_10"],
            "launch": campaign_launch(
                "alpha-science-prefill-p256-abba-06-10",
                PACK_REL / "06_phase_prefill_p256_abba_blocks_06_10",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-reference-end",
            "kind": "campaign_collection",
            "expected_count": 3,
            "input": external_inputs["end_reference"]["manifest"],
            "launch": campaign_launch(
                "alpha-reference-end", END_MANIFEST_REL.parent, "claim_runs_root"
            ),
        },
        {
            "stage_id": "alpha-post-calibration",
            "kind": "calibration_capture",
            "expected_count": 1,
            "input": {"kind": "arm_bindings", "slot": "post"},
            "launch": launch_recipe(
                "alpha-post-calibration.capture",
                "calibration_capture",
                "fiducial_capture",
                "joulewise.powermetrics_fiducial.cli.v1",
                post_capture,
            ),
        },
        {
            "stage_id": "alpha-whole-window-verdict",
            "kind": "whole_window_verdict",
            "expected_count": 1,
            "input": {"kind": "collected_roots"},
            "launch": launch_recipe(
                "alpha-whole-window-verdict.evaluate",
                "whole_window_verdict",
                "campaign_runner",
                "joulewise.run_campaign.cli.v1",
                [
                    literal("--whole-window-verdict"),
                    literal("--runs-dir"), binding("claim_runs_root"),
                    literal("--log"), binding_path("claim_runs_root", "campaign_log.jsonl"),
                    literal("--campaign-policy"), repo_path(POLICY_REL),
                    literal("--neg8-drift-bound"), binding_path("bound_runs_root", "neg8-drift-bound.json"),
                ],
            ),
        },
        {
            "stage_id": "alpha-backup",
            "kind": "backup",
            "expected_count": 2,
            "input": {"kind": "collected_roots"},
            "launch": {
                "schema_version": "joulewise.stage_launch.v1",
                "commands": [
                    {
                        "command_id": "alpha-backup.claim",
                        "command_kind": "backup",
                        "argv_template": {
                            "tool_id": "backup_runs",
                            "interface_id": "joulewise.backup_runs.cli.v1",
                            "arguments": [binding("claim_runs_root"), binding("claim_backup_destination")],
                        },
                        "cwd": {"kind": "binding", "value": "repo_root"},
                        "success_exit_codes": [0],
                    },
                    {
                        "command_id": "alpha-backup.bound",
                        "command_kind": "backup",
                        "argv_template": {
                            "tool_id": "backup_runs",
                            "interface_id": "joulewise.backup_runs.cli.v1",
                            "arguments": [binding("bound_runs_root"), binding("bound_backup_destination")],
                        },
                        "cwd": {"kind": "binding", "value": "repo_root"},
                        "success_exit_codes": [0],
                    },
                ],
            },
        },
    ]
    for index, stage in enumerate(stages):
        stage["ordinal"] = index + 1
        stage["predecessor"] = stages[index - 1]["stage_id"] if index else None
        stage["successor"] = stages[index + 1]["stage_id"] if index + 1 < len(stages) else None
    return stages


def definition_binding(
    family_id: str, definition: dict[str, Any], domain_sha256: str
) -> dict[str, Any]:
    return {
        "condition_family_id": family_id,
        "condition_family_definition": definition,
        "condition_family_sha256": domain_sha256,
    }


def calibration_basis() -> dict[str, Any]:
    return {
        "calibration_scope": "production_window",
        "acceptance_selection": "issued_d116_artifact_only",
        "issued_acceptance": {
            "acceptance_id": "d079_calibration_acceptance_v2_n19",
            "path": ACCEPTANCE_REL.as_posix(),
            "artifact_sha256": ACCEPTANCE_SHA256,
            "derivation_sha256": ACCEPTANCE_DERIVATION_SHA256,
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
        },
        "allowance_rule": "max(observed_drift_s,0.010818)",
        "allowance_embedding_count": 1,
        "component_composition": "componentwise_max_never_sum.v1",
    }


def build_extraction_spec(
    decode_definition: dict[str, Any],
    prefill_definition: dict[str, Any],
    p256_definition: dict[str, Any],
    absolute_ids: list[str],
    blocks: list[dict[str, Any]],
    p256_absolute_ids: list[str],
    p256_blocks: list[dict[str, Any]],
    config_rows: list[dict[str, str]],
    order_manifest_sha256: str,
) -> dict[str, Any]:
    config_by_id = {row["bundle_id"]: row["config_sha256"] for row in config_rows}
    comparative_ids = [
        block["members"][position]
        for block in blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    p256_comparative_ids = [
        block["members"][position]
        for block in p256_blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    order_binding = {
        "path": (PACK_REL / "order_manifest.json").as_posix(),
        "manifest_id": "d117-floor-qwen25-1p5b-v1-order-v1",
        "sha256": order_manifest_sha256,
    }

    def member_hashes(ids: Iterable[str]) -> list[dict[str, str]]:
        return [
            {"bundle_id": bundle_id, "config_sha256": config_by_id[bundle_id]}
            for bundle_id in ids
        ]

    def absolute_cell(
        cell_id: str,
        metric: str,
        precheck: list[str],
        family_id: str,
        definition: dict[str, Any],
        definition_sha256: str,
        member_ids: list[str] = absolute_ids,
    ) -> dict[str, Any]:
        return {
            "cell_id": cell_id,
            "kind": "absolute",
            "metric": metric,
            "window_class": "phase",
            "target_precheck_path": precheck,
            "condition_family_id": family_id,
            "condition_family_definitions": {
                "all": definition_binding(family_id, definition, definition_sha256)
            },
            "expected_n": N,
            "estimator": "d054_false_effect_guard.v1",
            "order_manifest": order_binding,
            "evidence_root_id": EVIDENCE_ROOT_ID,
            "member_config_sha256": member_hashes(member_ids),
            "calibration_basis": calibration_basis(),
            "members": [
                {"slot": bundle_id, "bundle_id": bundle_id}
                for bundle_id in member_ids
            ],
        }

    def comparative_cell(
        cell_id: str,
        metric: str,
        precheck: list[str],
        family_id: str,
        definition: dict[str, Any],
        definition_sha256: str,
        member_blocks: list[dict[str, Any]] = blocks,
        member_ids: list[str] = comparative_ids,
    ) -> dict[str, Any]:
        family = definition_binding(family_id, definition, definition_sha256)
        return {
            "cell_id": cell_id,
            "kind": "comparative",
            "metric": metric,
            "window_class": "phase",
            "target_precheck_path": precheck,
            "condition_family_id": family_id,
            "condition_family_definitions": {"A": family, "B": dict(family)},
            "expected_n": N,
            "estimator": COMMON_MODE_ESTIMATOR_ID,
            "estimator_registration": two_shared_edge_common_mode_registration(),
            "order_manifest": order_binding,
            "evidence_root_id": EVIDENCE_ROOT_ID,
            "member_config_sha256": member_hashes(member_ids),
            "calibration_basis": calibration_basis(),
            "blocks": [
                {"block_id": block["block_id"], "members": block["members"]}
                for block in member_blocks
            ],
        }

    cells = [
        absolute_cell(
            "d117-df-ph-decode-qwen25-1p5b-absolute",
            "phase_energy_j.decode",
            ["phase", "decode"],
            DECODE_FAMILY_ID,
            decode_definition,
            DECODE_FAMILY_DOMAIN_SHA256,
        ),
        comparative_cell(
            "d117-df-cmp-abba-ph-decode-qwen25-1p5b",
            "phase_energy_j.decode",
            ["phase", "decode"],
            DECODE_FAMILY_ID,
            decode_definition,
            DECODE_FAMILY_DOMAIN_SHA256,
        ),
        absolute_cell(
            "d117-df-ph-prefill-p128-qwen25-1p5b-absolute",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            PREFILL_FAMILY_ID,
            prefill_definition,
            PREFILL_FAMILY_DOMAIN_SHA256,
        ),
        comparative_cell(
            "d117-df-cmp-abba-ph-prefill-p128-qwen25-1p5b",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            PREFILL_FAMILY_ID,
            prefill_definition,
            PREFILL_FAMILY_DOMAIN_SHA256,
        ),
        absolute_cell(
            "d117-df-ph-prefill-p256-qwen25-1p5b-absolute",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            P256_FAMILY_ID,
            p256_definition,
            P256_FAMILY_DOMAIN_SHA256,
            p256_absolute_ids,
        ),
        comparative_cell(
            "d117-df-cmp-abba-ph-prefill-p256-qwen25-1p5b",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            P256_FAMILY_ID,
            p256_definition,
            P256_FAMILY_DOMAIN_SHA256,
            p256_blocks,
            p256_comparative_ids,
        ),
    ]
    decode_ids = [*absolute_ids, *comparative_ids]
    p256_ids = [*p256_absolute_ids, *p256_comparative_ids]

    def reported_members(ids: list[str]) -> list[dict[str, Any]]:
        return [
        {
            "ordinal": index,
            "bundle_id": bundle_id,
            "config_sha256": config_by_id[bundle_id],
        }
        for index, bundle_id in enumerate(ids, start=1)
    ]

    decode_reported_members = reported_members(decode_ids)
    reported_cells = [
        {
            "cell_id": "d117-reported-mean-ph-decode-qwen25-1p5b",
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
            "target_precheck_path": ["phase", "decode"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": decode_reported_members,
            "missing_or_invalid_member": "refuse_reported_mean",
            "numeric_value": None,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p128-qwen25-1p5b",
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
            "target_precheck_path": ["phase", "prefill"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": decode_reported_members,
            "missing_or_invalid_member": "refuse_reported_mean",
            "numeric_value": None,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p256-qwen25-1p5b",
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
            "target_precheck_path": ["phase", "prefill"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": reported_members(p256_ids),
            "missing_or_invalid_member": "refuse_reported_mean",
            "numeric_value": None,
        },
    ]
    spec = {
        "schema_version": "joulewise.detection_floor_extraction_spec.v1",
        # The frozen plan test pins the extraction-spec artifact SHA.
        "draft_status": active_generation().target_status,
        "successor_acceptance_artifact_policy": SUCCESSOR_REGENERATION_RULE,
        "cells": cells,
        "reported_energy_cells": reported_cells,
        "reported_energy_registration": {
            "authority": "D-123",
            "procedure_only": True,
            "postcollection_numeric_values": "structurally_absent_until_governed_reduction",
            "floor_projection_sha256": canonical_sha256(cells),
            "no_semantics_change_rule": (
                "Floor extraction consumes only cells; reported_energy_cells is a "
                "disjoint registered projection over the same physical bundle universe."
            ),
        },
        "reference_counts": {
            "floor_cell_references": 150,
            "reported_energy_references": 150,
            "total_registered_references": 300,
            "unique_physical_bundles": 100,
            "unique_config_paths": 100,
        },
        "phase_presence_contract": {
            "required_metrics": ["phase_energy_j.decode", "phase_energy_j.prefill"],
            "required_precheck_paths": [["phase", "decode"], ["phase", "prefill"]],
            "missing_registered_phase": "refuse_before_floor_or_reported_mean_emission",
        },
    }
    errors = validate_extraction_spec(spec)
    if errors:
        raise ValueError(f"generated extraction spec is invalid: {errors[0]}")
    return spec


def build_producer_contract(
    plan_sha256: str,
    plan_sidecar_sha256: str,
    order_manifest_sha256: str,
    spec_sha256: str,
    decode_config_rows: list[dict[str, str]],
    p256_config_rows: list[dict[str, str]],
    decode_identity_config_inventory: list[dict[str, str]],
    p256_identity_config_inventory: list[dict[str, str]],
    p256_prompt_text: str,
) -> dict[str, Any]:
    config_rows = [*decode_config_rows, *p256_config_rows]
    config_set_sha256 = canonical_sha256(config_rows)
    roles = [
        {
            "role": "decode",
            "artifact_cell_id": "d117-qwen25-1p5b-decode-floor-v1",
            "transport_group_id": "tg-d117-qwen25-1p5b-decode-v1",
            "metric": "phase_energy_j.decode",
            "target_precheck_path": ["phase", "decode"],
            "condition_family_id": DECODE_FAMILY_ID,
            "absolute_calibration_cell_id": "d117-df-ph-decode-qwen25-1p5b-absolute",
            "comparative_calibration_cell_id": "d117-df-cmp-abba-ph-decode-qwen25-1p5b",
            "allowed_consumer_families": ["sw-decode-a-qwen25-1p5b"],
            "members": decode_config_rows,
        },
        {
            "role": "prefill",
            "artifact_cell_id": "d117-qwen25-1p5b-prefill-p128-floor-v1",
            "transport_group_id": "tg-d117-qwen25-1p5b-prefill-p128-v1",
            "metric": "phase_energy_j.prefill",
            "target_precheck_path": ["phase", "prefill"],
            "condition_family_id": PREFILL_FAMILY_ID,
            "absolute_calibration_cell_id": "d117-df-ph-prefill-p128-qwen25-1p5b-absolute",
            "comparative_calibration_cell_id": "d117-df-cmp-abba-ph-prefill-p128-qwen25-1p5b",
            "allowed_consumer_families": ["df-ph-prefill-p128-qwen25-1p5b"],
            "members": decode_config_rows,
        },
        {
            "role": "prefill_p256",
            "artifact_cell_id": "d117-qwen25-1p5b-prefill-p256-floor-v1",
            "transport_group_id": "tg-d117-qwen25-1p5b-prefill-p256-v1",
            "metric": "phase_energy_j.prefill",
            "target_precheck_path": ["phase", "prefill"],
            "condition_family_id": P256_FAMILY_ID,
            "absolute_calibration_cell_id": "d117-df-ph-prefill-p256-qwen25-1p5b-absolute",
            "comparative_calibration_cell_id": "d117-df-cmp-abba-ph-prefill-p256-qwen25-1p5b",
            "allowed_consumer_families": ["sw-prefill-p256-a-qwen25-1p5b"],
            "members": p256_config_rows,
        },
    ]
    return {
        "schema_version": "joulewise.d117_floor_producer_contract.v1",
        # The frozen plan test pins the producer-contract artifact SHA.
        "draft_status": active_generation().target_status,
        "plan_set_id": "plan-set-d117-qwen25-1p5b-7b-phase-floor-v1",
        "aggregate_artifact_id": "d117-qwen25-phase-floor-set-v1",
        "producer_index": 1,
        "component_artifact_id": "d117-qwen25-1p5b-phase-floor-component-v1",
        "cell_composition_rule": "componentwise_max_never_sum.v1",
        "consumer_floor_rule": "cross_stack_armwise_max.v1",
        "plan": {
            "path": emitted_plan_reference(),
            "plan_id": PLAN_ID,
            "sha256": plan_sha256,
            "sidecar_sha256": plan_sidecar_sha256,
        },
        "evidence_root_id": EVIDENCE_ROOT_ID,
        "stack_identity": {
            "hardware_target": HARDWARE["id"],
            "runtime_backend": HARDWARE["runtime_backend"],
            "telemetry_backend": HARDWARE["telemetry_backend"],
            "model_name": MODEL["name"],
            "model_source": MODEL["source"],
            "model_revision": MODEL["revision"],
            "quantization": "int4",
            "workload_profile": WORKLOAD,
            "workload_profiles": {
                "decode_and_prefill_p128": WORKLOAD,
                "prefill_p256": {
                    "name": P256_WORKLOAD_NAME,
                    "repetitions": 1,
                    "warmup_runs": 1,
                    "output_tokens": 512,
                    "prompt_text_utf8_sha256": P256_PROMPT_UTF8_SHA256,
                },
            },
        },
        "order_manifest": {
            "path": (PACK_REL / "order_manifest.json").as_posix(),
            "manifest_id": "d117-floor-qwen25-1p5b-v1-order-v1",
            "sha256": order_manifest_sha256,
        },
        "extraction_spec": {
            "path": extraction_spec_rel().as_posix(),
            "sha256": spec_sha256,
            "member_count": 100,
            "floor_cell_count": 6,
            "floor_cell_member_references": 150,
            "reported_energy_cell_count": 3,
        },
        "config_set_sha256": config_set_sha256,
        "roles": roles,
        "identity_pin_projection": validate_identity_pin_projection(freeze_aware_projection({
            "work_order": IDENTITY_PIN_PROJECTION_WORK_ORDER,
            "mode": "derive_never_operator_enter",
            "state": "unprojected",
            "required_before_arm": True,
            "derivation_contract": IDENTITY_PIN_DERIVATION_CONTRACT,
            "identity_units": [
                {
                    "identity_unit_id": "alpha",
                    "producer_plan_reference": {
                        "plan_id": PLAN_ID,
                        "path": emitted_plan_reference(),
                    },
                    "consumer_bindings": [
                        {
                            "arm": "A",
                            "family": "sw-decode-a-qwen25-1p5b",
                            "measurement_arm": "decode",
                        },
                        {
                            "arm": "A",
                            "family": PREFILL_FAMILY_ID,
                            "measurement_arm": "prefill_p128",
                        },
                    ],
                    "declared_identity": {
                        "hardware_target": HARDWARE["id"],
                        "runtime_backend": HARDWARE["runtime_backend"],
                        "telemetry_backend": HARDWARE["telemetry_backend"],
                        "model_name": MODEL["name"],
                        "model_source": MODEL["source"],
                        "model_revision": MODEL["revision"],
                        "quantization": {**QUANTIZATION, "group_size": None},
                        "workload_profile": {
                            **WORKLOAD,
                            "prompt_text": None,
                            "dataset_ref": None,
                        },
                    },
                    "config_inventory": decode_identity_config_inventory,
                    "model_runtime_config": {
                        "model_artifact_sha256": None,
                        "runtime_identity_sha256": None,
                        "config_set_sha256": None,
                    },
                },
                {
                    "identity_unit_id": "alpha/prefill_p256",
                    "producer_plan_reference": {
                        "plan_id": PLAN_ID,
                        "path": emitted_plan_reference(),
                    },
                    "consumer_bindings": [
                        {
                            "arm": "A",
                            "family": "sw-prefill-p256-a-qwen25-1p5b",
                            "measurement_arm": "prefill_p256",
                        }
                    ],
                    "declared_identity": {
                        "hardware_target": HARDWARE["id"],
                        "runtime_backend": HARDWARE["runtime_backend"],
                        "telemetry_backend": HARDWARE["telemetry_backend"],
                        "model_name": MODEL["name"],
                        "model_source": MODEL["source"],
                        "model_revision": MODEL["revision"],
                        "quantization": {**QUANTIZATION, "group_size": None},
                        "workload_profile": {
                            "name": P256_WORKLOAD_NAME,
                            "repetitions": 1,
                            "warmup_runs": 1,
                            "output_tokens": 512,
                            "prompt_tokens": None,
                            "prompt_text": p256_prompt_text,
                            "dataset_ref": None,
                        },
                    },
                    "config_inventory": p256_identity_config_inventory,
                    "model_runtime_config": {
                        "model_artifact_sha256": None,
                        "runtime_identity_sha256": None,
                        "config_set_sha256": None,
                    },
                },
            ],
            "projection_receipt": None,
            "supersedes": [],
        })),
        "postcollection": {"status": "unresolved"},
        "dependencies": [
            "D117-POSTCOLLECTION-TRUST-01 before mint",
            "D117-U2 successor engine before arm",
            f"{IDENTITY_PIN_PROJECTION_WORK_ORDER} before arm",
            "shared-bundle unique-physical-union mint order repair before mint",
        ],
    }


def readme_bytes() -> bytes:
    oracle = derive_bracket_session_receipt_oracle()
    identity = active_generation()
    status = identity.target_status
    identity_statement = (
        ""
        if identity.target_ordinal == 1
        else f"Pack identity: `{identity.pack_id}` (`{identity.family_suffix}`).\n\n"
    )
    if status != DRAFT_STATUS:
        content = (
            "# D-117 Qwen2.5-1.5B floor campaign — frozen by D-134 receipt\n\n"
            f"{identity_statement}"
            "This generated description is freeze-aware. The D-134 freeze receipt "
            "and plan-tree pin are authoritative for frozen state; an external "
            "unexpired PASS/GO arm receipt is still required before launch.\n\n"
            f"{SUCCESSOR_REGENERATION_RULE}\n"
        )
        return thread_generation_identity(content).encode("utf-8")
    content = (
        "# D-117 Qwen2.5-1.5B floor campaign — unfrozen draft\n\n"
        f"{identity_statement}"
        "This pack pre-registers the alpha window's 10 absolute decode members, "
        "ten null A/B/B/A blocks (40 members), and a zero-member prefill metric "
        "rider over the same 50 physical bundles. It also carries a dedicated "
        "Q8 p256 prefill domain with 10 absolute members and ten null A/B/B/A "
        "blocks (50 additional members), plus three D-123 reported phase-energy "
        "means. The p256 workload name remains `df_ph_prefill_p256_candidate` "
        "for byte identity with the gamma consumer even though Q1 has frozen its "
        "prompt.\n\n"
        "The pack is not armable. Its receipt oracle is replay-derived from "
        f"`{oracle['source']['module']}`: {oracle['receipt_count']} physical "
        f"receipts for {oracle['logical_operation_count']} logical operations per "
        "finalized pre/post bracket session. Actual receipt bytes and the absolute "
        "terminal sequence remain arm-time evidence. Arm-time identities require "
        "U11 projection, "
        "and lead review must complete before any later release step.\n\n"
        f"{SUCCESSOR_REGENERATION_RULE}\n\n"
        "Generate or verify with:\n\n"
        "```text\n"
        "python3 configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py\n"
        "python3 configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py --check\n"
        "```\n\n"
            "Integrity SHA-256 values in this draft detect drift; they do not mark release.\n"
    )
    return thread_generation_identity(content).encode("utf-8")


def generate(
    output_root: Path,
    identity: GenerationIdentity | None = None,
) -> tuple[int, str, str]:
    with generation_context(identity or GenerationIdentity()):
        return _generate(output_root)


def _generate(output_root: Path) -> tuple[int, str, str]:
    outputs = validate_generation_output_inventory(active_generation())
    validate_generation_write_boundary(output_root, outputs)
    if active_generation().preserve_current_frozen_bytes:
        for relative in sorted(outputs, key=lambda path: path.as_posix()):
            write_bytes(output_root, relative, (REPO_ROOT / relative).read_bytes())
        plan_raw = (REPO_ROOT / active_generation().pack_rel / "calibration_plan.json").read_bytes()
        tree_raw = (REPO_ROOT / active_generation().pack_rel / "plan_tree.json").read_bytes()
        return 100, sha256_bytes(plan_raw), sha256_bytes(tree_raw)
    source_raw = embedded_generator_bytes()
    source_sha256 = (
        preserved_generator_sha256()
        if active_generation().preserve_current_frozen_bytes
        else sha256_bytes(source_raw)
    )
    (
        decode_definition,
        decode_raw,
        prefill_definition,
        prefill_raw,
        p256_definition,
        p256_raw,
    ) = load_and_verify_families()
    p256_prompt_text = load_p256_prompt_text()
    for path, expected in (
        (POLICY_REL, POLICY_SHA256),
        (ACCEPTANCE_REL, ACCEPTANCE_SHA256),
        (LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256),
        (NEG8_SETTLED_REL, NEG8_SETTLED_SHA256),
        (P256_PROMPT_REL, P256_PROMPT_ARTIFACT_SHA256),
    ):
        if sha256_file(REPO_ROOT / path) != expected:
            raise ValueError(f"pinned input drifted: {path.as_posix()}")

    write_bytes(output_root, PACK_REL / "generate_configs.py", source_raw)
    write_bytes(output_root, PACK_REL / "README.md", readme_bytes())
    write_bytes(output_root, DECODE_FAMILY_REL, decode_raw)
    write_bytes(output_root, PREFILL_FAMILY_REL, prefill_raw)
    write_bytes(output_root, P256_FAMILY_REL, p256_raw)

    stages, absolute_ids, blocks, p256_absolute_ids, p256_blocks = build_assembly()
    decode_ids = absolute_ids + [
        block["members"][position]
        for block in blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    p256_ids = p256_absolute_ids + [
        block["members"][position]
        for block in p256_blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    reported_cells = [
        {
            "cell_id": "d117-reported-mean-ph-decode-qwen25-1p5b",
            "metric": "phase_energy_j.decode",
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "ordered_bundle_ids": decode_ids,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p128-qwen25-1p5b",
            "metric": "phase_energy_j.prefill",
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "ordered_bundle_ids": decode_ids,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p256-qwen25-1p5b",
            "metric": "phase_energy_j.prefill",
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "ordered_bundle_ids": p256_ids,
        },
    ]
    canonical_blocks = calibration_plan_blocks(blocks)
    plan = {
        "schema_version": PLAN_SCHEMA,
        # The D-134 freeze receipt pins calibration_plan.json by SHA.
        "draft_status": active_generation().target_status,
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "fixed_n": N,
        "authorities": ["D-116", "D-117", "D-123", "D-124"],
        "stack_scope": {
            "hardware_target": HARDWARE["id"],
            "runtime_backend": HARDWARE["runtime_backend"],
            "telemetry_backend": HARDWARE["telemetry_backend"],
            "model_name": MODEL["name"],
            "model_revision": MODEL["revision"],
            "model_source": MODEL["source"],
            "quantization": "int4",
            "sampling": SAMPLING,
            "decode_condition_family_id": DECODE_FAMILY_ID,
            "decode_condition_family_sha256": DECODE_FAMILY_DOMAIN_SHA256,
            "prefill_condition_family_id": PREFILL_FAMILY_ID,
            "prefill_condition_family_sha256": PREFILL_FAMILY_DOMAIN_SHA256,
            "prefill_p256_condition_family_id": P256_FAMILY_ID,
            "prefill_p256_condition_family_sha256": P256_FAMILY_DOMAIN_SHA256,
        },
        "replacement_rule": {
            "policy": "abort_window_on_any_required_member_failure",
            "predeclared_before_data": True,
            "calibration_retries": 0,
            "science_member_replacements": 0,
            "outcome_dependent_top_up": "forbidden",
            "missing_failed_or_strict_invalid_member": "abort_non_claim_bearing",
        },
        "floor_cells": [
            {
                "cell_id": "d117-df-ph-decode-qwen25-1p5b-absolute",
                "kind": "absolute",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": "d117-df-cmp-abba-ph-decode-qwen25-1p5b",
                "kind": "comparative_abba",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_blocks": canonical_blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
            },
            {
                "cell_id": "d117-df-ph-prefill-p128-qwen25-1p5b-absolute",
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": "d117-df-cmp-abba-ph-prefill-p128-qwen25-1p5b",
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_blocks": canonical_blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
            },
            {
                "cell_id": "d117-df-ph-prefill-p256-qwen25-1p5b-absolute",
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": P256_FAMILY_ID,
                "ordered_bundle_ids": p256_absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": "d117-df-cmp-abba-ph-prefill-p256-qwen25-1p5b",
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": P256_FAMILY_ID,
                "ordered_blocks": calibration_plan_blocks(p256_blocks),
                "estimator": COMMON_MODE_ESTIMATOR_ID,
            },
        ],
        "reported_energy_cells": reported_cells,
        "execution_mode": {
            "ordered_science_stage_ids": [stage["stage_id"] for stage in stages],
            "planned_science_bundles": 100,
            "planned_bound_bundles": 12,
            "planned_reference_bundles": 7,
            "planned_calibration_observations": 2,
        },
        "roots": {
            "claim_root_leaf": CLAIM_ROOT_LEAF,
            "bound_root_leaf": BOUND_ROOT_LEAF,
        },
        "runs_dir": CLAIM_ROOT_LEAF,
        "order_manifest": "order_manifest.json",
        "campaign_log": f"{CLAIM_ROOT_LEAF}/campaign_log.jsonl",
        "campaign_policy": {
            "policy_id": "quiet-mac-p2-production",
            "path": POLICY_REL.as_posix(),
            "sha256": POLICY_SHA256,
        },
    }
    plan_raw = write_json(output_root, PACK_REL / "calibration_plan.json", plan)
    plan_sha256 = sha256_bytes(plan_raw)
    plan_sidecar_raw = sidecar_bytes(plan_sha256, "calibration_plan.json")
    write_bytes(output_root, PACK_REL / "calibration_plan.sha256", plan_sidecar_raw)

    root_entries: list[dict[str, Any]] = []
    root_index = 1
    stage_manifest_refs: dict[str, dict[str, Any]] = {}
    config_rows: list[dict[str, str]] = []
    science_rows: list[dict[str, Any]] = []
    for stage in stages:
        stage_id = stage["stage_id"]
        local_entries: list[dict[str, Any]] = []
        for local_index, run in enumerate(stage["runs"], start=1):
            config_rel = PACK_REL / stage_id / run["filename"]
            config_plan_sha256 = (
                plan_sha256
                if run.get("condition_family_id") == P256_FAMILY_ID
                else LEGACY_DECODE_PLAN_SHA256
            )
            config_raw = write_json(
                output_root,
                config_rel,
                config_for(run, config_plan_sha256, p256_prompt_text),
            )
            config_sha256 = sha256_bytes(config_raw)
            local_entries.append(
                manifest_entry(run, local_index, run["filename"], config_sha256)
            )
            root_entry = manifest_entry(
                run,
                root_index,
                f"{stage_id}/{run['filename']}",
                config_sha256,
            )
            root_entries.append(root_entry)
            config_rows.append(
                {"bundle_id": run["run_id"], "config_sha256": config_sha256}
            )
            science_rows.append(
                {
                    "ordinal": root_index,
                    "stage_id": stage_id,
                    "config_path": config_rel.as_posix(),
                    "config_sha256": config_sha256,
                    "run_id": run["run_id"],
                    "role": run["role"],
                    "block_id": run["block_id"],
                    "block_index": run["block_index"],
                    "position": run["position"],
                    "arm": run["arm"],
                }
            )
            root_index += 1
        manifest_id = f"d117-floor-qwen25-1p5b-v1-{stage_id.replace('_', '-')}-order-v1"
        stage_manifest = {
            "schema_version": ORDER_SCHEMA,
            # The frozen plan-tree manifest reference pins these bytes by SHA.
            "draft_status": active_generation().target_status,
            "manifest_id": manifest_id,
            "plan_id": PLAN_ID,
            "calibration_plan_sha256": plan_sha256,
            "ordering_note": stage["ordering_note"],
            "planned_n_bundles": len(local_entries),
            "executed_order": local_entries,
        }
        manifest_rel = PACK_REL / stage_id / "order_manifest.json"
        manifest_raw = write_json(output_root, manifest_rel, stage_manifest)
        stage_manifest_refs[stage_id] = {
            "kind": "manifest",
            "path": manifest_rel.as_posix(),
            "manifest_id": manifest_id,
            "sha256": sha256_bytes(manifest_raw),
        }

    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        # The frozen producer contract pins the root manifest by SHA.
        "draft_status": active_generation().target_status,
        "manifest_id": "d117-floor-qwen25-1p5b-v1-order-v1",
        "plan_id": PLAN_ID,
        "calibration_plan_sha256": plan_sha256,
        "planned_n_bundles": len(root_entries),
        "subcampaign_order": [
            {
                "index": index,
                "subcampaign_id": stage["stage_id"],
                "role": stage["role"],
                "optional": False,
                "planned_n_bundles": len(stage["runs"]),
                "ordering_note": stage["ordering_note"],
                "manifest_path": stage_manifest_refs[stage["stage_id"]]["path"],
                "manifest_id": stage_manifest_refs[stage["stage_id"]]["manifest_id"],
                "manifest_sha256": stage_manifest_refs[stage["stage_id"]]["sha256"],
            }
            for index, stage in enumerate(stages, start=1)
        ],
        "executed_order": root_entries,
    }
    root_manifest_raw = write_json(output_root, PACK_REL / "order_manifest.json", root_manifest)
    root_manifest_sha256 = sha256_bytes(root_manifest_raw)

    spec = build_extraction_spec(
        decode_definition,
        prefill_definition,
        p256_definition,
        absolute_ids,
        blocks,
        p256_absolute_ids,
        p256_blocks,
        config_rows,
        root_manifest_sha256,
    )
    spec_raw = write_json(output_root, extraction_spec_rel(), spec)
    spec_sha256 = sha256_bytes(spec_raw)

    producer = build_producer_contract(
        plan_sha256,
        sha256_bytes(plan_sidecar_raw),
        root_manifest_sha256,
        spec_sha256,
        config_rows[:50],
        config_rows[50:],
        sorted(
            [
                {
                    "path": Path(row["config_path"])
                    .relative_to(PACK_REL)
                    .as_posix(),
                    "sha256": row["config_sha256"],
                }
                for row in science_rows[:50]
            ],
            key=lambda row: row["path"],
        ),
        sorted(
            [
                {
                    "path": Path(row["config_path"])
                    .relative_to(PACK_REL)
                    .as_posix(),
                    "sha256": row["config_sha256"],
                }
                for row in science_rows[50:]
            ],
            key=lambda row: row["path"],
        ),
        p256_prompt_text,
    )
    if active_generation().preserve_current_frozen_bytes:
        producer_raw = (REPO_ROOT / PACK_REL / "producer_contract.json").read_bytes()
        producer = json.loads(producer_raw)
        write_bytes(output_root, PACK_REL / "producer_contract.json", producer_raw)
    else:
        producer_raw = write_json(
            output_root, PACK_REL / "producer_contract.json", producer
        )
    producer_sha256 = sha256_bytes(producer_raw)

    external_inputs = {
        "neg8_bound": external_manifest("neg8_bound", NEG8_MANIFEST_REL),
        "start_reference": external_manifest("start_reference", START_MANIFEST_REL),
        "midpoint_reference": external_manifest("midpoint_reference", MIDPOINT_MANIFEST_REL),
        "end_reference": external_manifest("end_reference", END_MANIFEST_REL),
    }
    graph = stage_graph(stage_manifest_refs, external_inputs)
    tree = {
        "schema_version": TREE_SCHEMA,
        # The D-134 plan-tree sidecar pins this artifact by SHA.
        "draft_status": active_generation().target_status,
        "plan": {
            "path": emitted_plan_reference(),
            "plan_id": PLAN_ID,
            "actual_sha256": plan_sha256,
            "declared_sha256": plan_sha256,
            "sidecar_path": emitted_plan_sidecar_reference(),
            "sidecar_sha256": sha256_bytes(plan_sidecar_raw),
        },
        "generator": {
            "path": (PACK_REL / "generate_configs.py").as_posix(),
            "sha256": source_sha256,
        },
        "window_identity": {
            "window_id": PLAN_ID,
            "evidence_root_id": EVIDENCE_ROOT_ID,
        },
        "roots": {
            "claim_root_leaf": CLAIM_ROOT_LEAF,
            "bound_root_leaf": BOUND_ROOT_LEAF,
        },
        "campaign_policy": {
            "path": POLICY_REL.as_posix(),
            "sha256": POLICY_SHA256,
        },
        "acceptance_policy": {
            "selection": "issued_d116_artifact_only",
            "issued_acceptance": {
                "acceptance_id": "d079_calibration_acceptance_v2_n19",
                "path": ACCEPTANCE_REL.as_posix(),
                "artifact_sha256": ACCEPTANCE_SHA256,
                "derivation_sha256": ACCEPTANCE_DERIVATION_SHA256,
            },
            "issued_ledger_head": {
                "path": LEDGER_HEAD_REL.as_posix(),
                "file_sha256": LEDGER_HEAD_FILE_SHA256,
                "head_sha256": LEDGER_HEAD_SHA256,
            },
            "successor_effect": "invalidate_and_reissue_readiness_and_pin_projection",
            "arming_prerequisites": [
                {"id": "D117-U2", "status": "required_before_arm"},
                {"id": "D117-POSTCOLLECTION-TRUST-01", "status": "required_before_mint"},
                {
                    "id": IDENTITY_PIN_PROJECTION_WORK_ORDER,
                    "status": "required_before_arm",
                },
            ],
        },
        "condition_families": [
            {
                "path": DECODE_FAMILY_REL.as_posix(),
                "byte_sha256": DECODE_FAMILY_BYTE_SHA256,
                "condition_family_id": DECODE_FAMILY_ID,
                "domain_sha256": DECODE_FAMILY_DOMAIN_SHA256,
            },
            {
                "path": PREFILL_FAMILY_REL.as_posix(),
                "byte_sha256": PREFILL_FAMILY_BYTE_SHA256,
                "condition_family_id": PREFILL_FAMILY_ID,
                "domain_sha256": PREFILL_FAMILY_DOMAIN_SHA256,
            },
            {
                "path": P256_FAMILY_REL.as_posix(),
                "byte_sha256": P256_FAMILY_BYTE_SHA256,
                "condition_family_id": P256_FAMILY_ID,
                "domain_sha256": P256_FAMILY_DOMAIN_SHA256,
                "prompt_artifact_path": P256_PROMPT_REL.as_posix(),
                "prompt_artifact_sha256": P256_PROMPT_ARTIFACT_SHA256,
                "prompt_text_utf8_sha256": P256_PROMPT_UTF8_SHA256,
                "shared_tokenizer_json_sha256": P256_SHARED_TOKENIZER_JSON_SHA256,
                "ruled_token_id_sha256_prefix": P256_RULED_TOKEN_ID_SHA256_PREFIX,
                "prompt_identity_ruling": (
                    "Q1, docs/strategy/2026-08-09-pack-freeze-plan.md"
                ),
                "token_id_sha256_pin_status": (
                    "prefix_only; no full-hex token-ID pin exists in-tree"
                ),
            },
        ],
        "science": science_rows,
        "stage_graph": graph,
        "external_inputs": {
            "manifests": list(external_inputs.values()),
            "artifacts": [
                {"path": NEG8_SETTLED_REL.as_posix(), "sha256": NEG8_SETTLED_SHA256},
                {
                    "path": P256_PROMPT_REL.as_posix(),
                    "sha256": P256_PROMPT_ARTIFACT_SHA256,
                },
            ],
        },
        "attempt_policy": {
            "policy": "abort_window_on_any_required_member_failure",
            "predeclared_before_data": True,
            "calibration_retries": 0,
            "science_member_replacements": 0,
            "outcome_dependent_top_up": "forbidden",
            "missing_failed_or_strict_invalid_member": "abort_non_claim_bearing",
        },
        "arm_attachments": {
            "arm_readiness": generation_arm_readiness_attachment(),
            "launch": {
                "schema_version": "joulewise.stage_launch_bindings.v1",
                "bindings": [
                    {"name": "repo_root", "type": "existing_absolute_directory"},
                    {"name": "ledger_path", "type": "existing_absolute_file"},
                    {"name": "claim_runs_root", "type": "fresh_absolute_directory", "leaf": CLAIM_ROOT_LEAF},
                    {"name": "bound_runs_root", "type": "fresh_absolute_directory", "leaf": BOUND_ROOT_LEAF},
                    {"name": "operator_log_root", "type": "absolute_directory"},
                    {"name": "pre_calibration_dir", "type": "absolute_directory"},
                    {"name": "post_calibration_dir", "type": "absolute_directory"},
                    {"name": "claim_backup_destination", "type": "absolute_path"},
                    {"name": "bound_backup_destination", "type": "absolute_path"},
                    {"name": "bracket_session_id", "type": "nonempty_string"},
                    {"name": "pre_attempt_id", "type": "nonempty_string"},
                    {"name": "post_attempt_id", "type": "nonempty_string"},
                    {"name": "identity_epoch_json", "type": "authenticated_absolute_file"},
                    {"name": "t1_bindings_json", "type": "authenticated_absolute_file"},
                ],
                "derived_path_rules": [
                    "pre_calibration_dir=claim_runs_root/instrument_validation/pre_attempt_id",
                    "post_calibration_dir=claim_runs_root/instrument_validation/post_attempt_id",
                ],
            },
            "identity_pin_projection": producer["identity_pin_projection"],
            "receipt_oracle": derive_bracket_session_receipt_oracle(),
        },
        "closeout_attachments": {
            "bracket_binding_sha256": None,
            "terminal_ledger_head": None,
            "whole_window_verdict_sha256": None,
            "evaluation_basis_sha256": None,
            "extraction_report_sha256": None,
            "postcollection_receipt_digests": [],
            "todo": (
                "TODO(postcollection): leave receipt-derived closeout fields empty "
                "until a completed claim window supplies authenticated evidence."
            ),
            "backup_requirements": {
                "claim_root_verified": True,
                "bound_root_verified": True,
                "required_successful_backups": 2,
            },
        },
        "downstream_contract": {
            "extraction_spec": {
                "path": extraction_spec_rel().as_posix(),
                "sha256": spec_sha256,
            },
            "producer_contract": {
                "path": (PACK_REL / "producer_contract.json").as_posix(),
                "sha256": producer_sha256,
            },
            "prefill_phase_presence": "required_for_all_100_physical_bundles",
            "missing_registered_phase": "refuse",
        },
        "runtime_budget": {
            "planning_estimate_minutes_with_margin": 376.8,
            "planning_estimate_hours_with_margin": 6.28,
            "margin_percent": 20,
            "margin_authority": "time_headroom_only_never_member_replacement",
            "science_count": 100,
            "bound_count": 12,
            "reference_count": 7,
            "calibration_observation_count": 2,
        },
    }
    if active_generation().preserve_current_frozen_bytes:
        tree_raw = (REPO_ROOT / PACK_REL / "plan_tree.json").read_bytes()
        tree_sidecar_raw = (REPO_ROOT / PACK_REL / "plan_tree.sha256").read_bytes()
        write_bytes(output_root, PACK_REL / "plan_tree.json", tree_raw)
        write_bytes(output_root, PACK_REL / "plan_tree.sha256", tree_sidecar_raw)
    else:
        tree_raw = write_json(output_root, PACK_REL / "plan_tree.json", tree)
        write_bytes(
            output_root,
            PACK_REL / "plan_tree.sha256",
            sidecar_bytes(sha256_bytes(tree_raw), "plan_tree.json"),
        )
    tree_sha256 = sha256_bytes(tree_raw)
    return len(root_entries), plan_sha256, tree_sha256


def expected_pack_paths() -> list[Path]:
    paths = [
        Path("README.md"),
        Path("generate_configs.py"),
        Path("calibration_plan.json"),
        Path("calibration_plan.sha256"),
        Path("order_manifest.json"),
        Path("plan_tree.json"),
        Path("plan_tree.sha256"),
        Path("producer_contract.json"),
        Path("condition_families/condition_family_df_ph_decode.json"),
        Path("condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json"),
        Path("condition_families/condition_family_df_ph_prefill_p256_qwen25_1p5b.json"),
        Path("01_phase_decode_absolute/order_manifest.json"),
        Path("02_phase_decode_abba_blocks_01_05/order_manifest.json"),
        Path("03_phase_decode_abba_blocks_06_10/order_manifest.json"),
        Path("04_phase_prefill_p256_absolute/order_manifest.json"),
        Path("05_phase_prefill_p256_abba_blocks_01_05/order_manifest.json"),
        Path("06_phase_prefill_p256_abba_blocks_06_10/order_manifest.json"),
    ]
    paths.extend(
        Path(f"01_phase_decode_absolute/d117f15-df-ph-decode-abs-r{rep:02d}.json")
        for rep in range(1, 11)
    )
    for block in range(1, 11):
        stage = (
            "02_phase_decode_abba_blocks_01_05"
            if block <= 5
            else "03_phase_decode_abba_blocks_06_10"
        )
        paths.extend(
            Path(
                f"{stage}/d117f15-df-cmp-abba-ph-decode-b{block:02d}-{position}.json"
            )
            for position in ("a1", "b1", "b2", "a2")
        )
    paths.extend(
        Path(
            f"04_phase_prefill_p256_absolute/"
            f"d117f15-df-ph-prefill-p256-abs-r{rep:02d}.json"
        )
        for rep in range(1, 11)
    )
    for block in range(1, 11):
        stage = (
            "05_phase_prefill_p256_abba_blocks_01_05"
            if block <= 5
            else "06_phase_prefill_p256_abba_blocks_06_10"
        )
        paths.extend(
            Path(
                f"{stage}/d117f15-df-cmp-abba-ph-prefill-p256-"
                f"b{block:02d}-{position}.json"
            )
            for position in ("a1", "b1", "b2", "a2")
        )
    return paths


def validate_generation_output_inventory(identity: GenerationIdentity) -> set[Path]:
    pack_outputs = {identity.pack_rel / path for path in expected_pack_paths()}
    spec_output = extraction_spec_rel(identity)
    outputs = pack_outputs | {spec_output}
    if len(pack_outputs) != len(expected_pack_paths()) or spec_output in pack_outputs:
        raise ValueError("generation output inventory is not exactly contained")
    if any(
        path != spec_output and identity.pack_rel not in path.parents
        for path in outputs
    ):
        raise ValueError("generation output inventory escapes the target allowlist")
    return outputs


def actual_pack_paths(pack_root: Path) -> set[Path]:
    return {
        path.relative_to(pack_root)
        for path in pack_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def check_current(
    check_root: Path = REPO_ROOT,
    identity: GenerationIdentity | None = None,
) -> tuple[int, str, str]:
    selected_identity = identity or GenerationIdentity()
    with tempfile.TemporaryDirectory(prefix="d117-u5-check-") as tmp:
        temp_root = Path(tmp)
        count, plan_sha256, tree_sha256 = generate(temp_root, selected_identity)
        pack_rel = selected_identity.pack_rel
        generated_paths = set(expected_pack_paths())
        generated_tree = json.loads(
            (temp_root / pack_rel / "plan_tree.json").read_text(encoding="utf-8")
        )
        freeze_reference = generated_tree["arm_attachments"]["arm_readiness"][
            "freeze_receipt"
        ]
        expected_paths = set(generated_paths)
        if freeze_reference is not None:
            freeze_path = Path(freeze_reference["path"])
            expected_paths |= {
                freeze_path,
                freeze_path.with_name(f"{freeze_path.name}.sha256"),
            }
            freeze_receipt = json.loads(
                (check_root / pack_rel / freeze_path).read_text(encoding="utf-8")
            )
            for item in freeze_receipt["evidence"]:
                evidence_path = Path(item["path"])
                evidence_sidecar = (
                    evidence_path.with_suffix(".sha256")
                    if evidence_path.parent.name
                    == "identity_pin_projection.receipts"
                    else evidence_path.with_name(f"{evidence_path.name}.sha256")
                )
                expected_paths |= {
                    evidence_path,
                    evidence_sidecar,
                }
                evidence_receipt = json.loads(
                    (check_root / pack_rel / evidence_path).read_text(
                        encoding="utf-8"
                    )
                )
                expected_paths.update(
                    Path(fact["source_path"])
                    for fact in evidence_receipt.get("facts", [])
                    if "source_path" in fact
                )
        projection_reference = generated_tree["arm_attachments"][
            "identity_pin_projection"
        ]["projection_receipt"]
        if projection_reference is not None:
            projection_path = Path(projection_reference["path"])
            expected_paths |= {
                projection_path,
                projection_path.with_suffix(".sha256"),
            }
        observed_paths = actual_pack_paths(check_root / pack_rel)
        missing = sorted(expected_paths - observed_paths)
        extras = sorted(observed_paths - expected_paths)
        if missing or extras:
            detail = []
            if missing:
                detail.append(
                    "missing=" + ",".join(path.as_posix() for path in missing)
                )
            if extras:
                detail.append(
                    "extras=" + ",".join(path.as_posix() for path in extras)
                )
            raise ValueError("pack inventory differs: " + "; ".join(detail))
        for relative in generated_paths:
            expected = (temp_root / pack_rel / relative).read_bytes()
            actual_path = check_root / pack_rel / relative
            if actual_path.read_bytes() != expected:
                raise ValueError(f"generated file drifted: {(pack_rel / relative).as_posix()}")
        spec_rel = extraction_spec_rel(selected_identity)
        if (check_root / spec_rel).read_bytes() != (temp_root / spec_rel).read_bytes():
            raise ValueError(f"generated file drifted: {spec_rel.as_posix()}")
        return count, plan_sha256, tree_sha256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify checked-in bytes")
    parser.add_argument(
        "--output-root",
        type=Path,
        help="write under this temporary repository root instead of the checkout",
    )
    parser.add_argument("--pack-id", default=PACK_REL.name)
    parser.add_argument("--family-suffix", default=CURRENT_FAMILY_SUFFIX)
    parser.add_argument(
        "--preserve-current-frozen-bytes",
        action=argparse.BooleanOptionalAction,
        default=PRESERVE_CURRENT_FROZEN_BYTES,
    )
    args = parser.parse_args()
    return args


def main() -> int:
    args = parse_args()
    identity = GenerationIdentity(
        pack_id=args.pack_id,
        family_suffix=args.family_suffix,
        preserve_current_frozen_bytes=args.preserve_current_frozen_bytes,
    )
    if args.check:
        check_root = args.output_root.resolve() if args.output_root else REPO_ROOT
        count, plan_sha256, tree_sha256 = check_current(check_root, identity)
        verb = "verified"
    else:
        output_root = args.output_root.absolute() if args.output_root else REPO_ROOT
        count, plan_sha256, tree_sha256 = generate(output_root, identity)
        verb = "generated"
    status = identity.target_status
    identity_label = (
        "" if identity.target_ordinal == 1 else f"{identity.pack_id} "
    )
    print(
        f"{verb} {identity_label}{status.replace('_', ' ')}: "
        f"{count} science configs; "
        f"calibration_plan_sha256={plan_sha256}; plan_tree_sha256={tree_sha256}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
