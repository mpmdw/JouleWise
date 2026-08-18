#!/usr/bin/env python3
"""Generate the D-117 Qwen2.5-7B floor campaign draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
PACK_REL = Path("configs/campaigns/d117_floor_qwen25_7b_v2")
CALIBRATION_PLAN_REFERENCE = "calibration_plan.json"
CURRENT_FAMILY_SUFFIX = "_v2"
SPEC_REL = Path("configs/floor_mint/d117_qwen25_7b_extraction_spec.json")
SOURCE_GENERATOR = Path(__file__).resolve()
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
PLAN_ID = "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v2"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-7b-v2"
CLAIM_ROOT_LEAF = "runs_d117_floor_qwen25_7b_v2"
BOUND_ROOT_LEAF = "runs_d117_floor_qwen25_7b_v2_bound"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
PLAN_TREE_SCHEMA = "joulewise.d117_plan_tree.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
FAMILY_SCHEMA = "joulewise.condition_family_definition.v1"
MODEL_TAG = "qwen25-7b-mlx"
DECODE_FAMILY_ID = "df-ph-decode-qwen25-7b"
PREFILL_FAMILY_ID = "df-ph-prefill-p128-qwen25-7b"
P256_FAMILY_ID = "df-ph-prefill-p256-qwen25-7b"
CAMPAIGN_TAG = "d117-floor-qwen25-7b-v2"
DRAFT_STATUS = "unfrozen_draft"
FROZEN_STATUS = "frozen_by_d134_receipt"
# Freeze-neutral serialized status for successor (_v2 and later) packs.
#
# Cold-gate verdict of 2026-08-18 (composed; adopts option (a) as narrowed and
# option (d) as a gate condition -- holdings 1 and 6): the committed D-134
# freeze receipt plus its plan-tree attachment IS the draft->frozen transition,
# and the receipt's pack_identity pins calibration_plan.json -- which carries a
# serialized status site -- by SHA. A post-mint serialized transition therefore
# invalidates the receipt at the dry-run/arm/verify gates, and no re-mint path
# exists. Every status-bearing byte a successor pack emits must consequently be
# true on BOTH sides of the receipt: it states when the bytes were generated,
# never that the pack is unfrozen or unarmable. The dynamic authority remains
# GenerationIdentity.target_status, read from the authenticated attachment.
#
# The 2026-08-13 ordinal-1 packs keep their frozen wording verbatim; their
# committed bytes are never repaired (M-2 core).
SUCCESSOR_EMITTED_STATUS = "as_generated_pre_d134_freeze"
CURRENT_FROZEN_RECEIPT_SHA256 = (
    "a6dec2c238e5a5cb8a181ac1abd898943238c21edeb4d111ead0cd3b00df7870"
)
CURRENT_FROZEN_GENERATOR_SHA256 = (
    "5519b18ae971fd3655af5d7e7be67d4462ee1fd487e179ba9961cb971a1c6dca"
)
LEGACY_SUCCESSOR_REGENERATION_RULE = (
    "A successor acceptance artifact issuing before arm REQUIRES pack regeneration "
    "(packs are unfrozen drafts; the D-125 lineage-envelope alternative is recorded "
    "as a freeze-time lead decision)."
)

PLAN_SET_ID = "plan-set-d117-qwen25-1p5b-7b-phase-floor-v2"
AGGREGATE_ARTIFACT_ID = "d117-qwen25-phase-floor-set-v2"
COMPONENT_ARTIFACT_ID = "d117-qwen25-7b-phase-floor-component-v2"

DECODE_ARTIFACT_CELL_ID = "d117-qwen25-7b-decode-floor-v2"
PREFILL_ARTIFACT_CELL_ID = "d117-qwen25-7b-prefill-p128-floor-v2"
DECODE_TRANSPORT_ID = "tg-d117-qwen25-7b-decode-v2"
PREFILL_TRANSPORT_ID = "tg-d117-qwen25-7b-prefill-p128-v2"

DECODE_ABSOLUTE_CELL = "d117-df-ph-decode-qwen25-7b-absolute"
DECODE_COMPARATIVE_CELL = "d117-df-cmp-abba-ph-decode-qwen25-7b"
PREFILL_ABSOLUTE_CELL = "d117-df-ph-prefill-p128-qwen25-7b-absolute"
PREFILL_COMPARATIVE_CELL = (
    "d117-df-cmp-abba-ph-prefill-p128-qwen25-7b"
)
P256_ABSOLUTE_CELL = "d117-df-ph-prefill-p256-qwen25-7b-absolute"
P256_COMPARATIVE_CELL = "d117-df-cmp-abba-ph-prefill-p256-qwen25-7b"
P256_WORKLOAD_NAME = "df_ph_prefill_p256_candidate"
P256_PROMPT_UTF8_SHA256 = (
    "f149dddcb4b9d27b3d68b0455c5f774e56e37bfc04430b53e139a4c08f044faf"
)
P256_SHARED_TOKENIZER_JSON_SHA256 = (
    "a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf"
)
P256_RULED_TOKEN_ID_SHA256_PREFIX = "83099a66"
LEGACY_DECODE_PLAN_SHA256 = (
    "c20ef596f64a4a8d5367a963614c4db0f2c34a7077441e204bcf22e2b1033f40"
)

MODEL = {
    "name": "Qwen2.5-7B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
    "revision": "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
    "weight_format": "mlx",
    "context_window": 32768,
}
REFERENCE_MODEL = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
}
QUANTIZATION = {"name": "int4", "bits": 4}
HARDWARE = {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": (
        "D-117 beta Qwen2.5-7B phase-floor campaign on the current "
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
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}

STAGES = (
    {
        "subcampaign_id": "01_phase_decode_absolute",
        "role": "absolute_phase_decode",
        "ordering_note": "Ten fixed absolute decode repeats in repetition order.",
    },
    {
        "subcampaign_id": "02_phase_decode_abba_blocks_01_05",
        "role": "comparative_phase_decode_first_half",
        "ordering_note": (
            "Fixed contiguous same-condition A/B/B/A decode blocks 1-5."
        ),
    },
    {
        "subcampaign_id": "03_phase_decode_abba_blocks_06_10",
        "role": "comparative_phase_decode_second_half",
        "ordering_note": (
            "Fixed contiguous same-condition A/B/B/A decode blocks 6-10."
        ),
    },
    {
        "subcampaign_id": "04_phase_prefill_p256_absolute",
        "role": "absolute_phase_prefill_p256",
        "ordering_note": "Ten fixed absolute p256 prefill repeats in repetition order.",
    },
    {
        "subcampaign_id": "05_phase_prefill_p256_abba_blocks_01_05",
        "role": "comparative_phase_prefill_p256_first_half",
        "ordering_note": (
            "Fixed contiguous same-condition A/B/B/A p256 prefill blocks 1-5."
        ),
    },
    {
        "subcampaign_id": "06_phase_prefill_p256_abba_blocks_06_10",
        "role": "comparative_phase_prefill_p256_second_half",
        "ordering_note": (
            "Fixed contiguous same-condition A/B/B/A p256 prefill blocks 6-10."
        ),
    },
)

POLICY_REL = Path("configs/campaign_policies/quiet_mac_p2_production.json")
ACCEPTANCE_REL = Path("configs/calibration/calibration_acceptance_d079_v2.json")
# D-138 dual-generation acceptance. The frozen `_v1` identity is permanently
# bound to the D-116 initial issuance; successor generations bind the reissue
# derived at the integrated estimator head.
SUCCESSOR_ACCEPTANCE_REL = Path(
    "configs/calibration/calibration_acceptance_d079_v2_r2.json"
)
ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19"
SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19_r2"
ACCEPTANCE_DERIVATION_SHA256 = (
    "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
)
SUCCESSOR_ACCEPTANCE_DERIVATION_SHA256 = (
    "7d2044e861275adc723c18a2236258b3c3b862222c4a5f70d413539f2a6fa73b"
)
LEDGER_HEAD_REL = Path("configs/calibration/calibration_ledger_head.json")
NEG8_MANIFEST_REL = Path("configs/campaigns/neg8_reference_corpus/order_manifest.json")
NEG8_CORPUS_REL = Path(
    "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json"
)
START_MANIFEST_REL = Path(
    "configs/campaigns/window_references/start_triplet/order_manifest.json"
)
MID_MANIFEST_REL = Path(
    "configs/campaigns/window_references/midpoint/order_manifest.json"
)
END_MANIFEST_REL = Path(
    "configs/campaigns/window_references/end_triplet/order_manifest.json"
)
DECODE_TEMPLATE_REL = Path(
    "configs/campaigns/qwen25_7b_decode_floor_v1/condition_families/"
    "condition_family_df_ph_decode_qwen25_7b.json"
)
P256_PROMPT_REL = Path(
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/"
    "prefill_prompt_candidate.json"
)

EXPECTED_EXTERNAL_SHA256 = {
    POLICY_REL.as_posix(): "b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd",
    ACCEPTANCE_REL.as_posix(): "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
    SUCCESSOR_ACCEPTANCE_REL.as_posix(): "1c51e2d4e0d19c8e7f8602614ab97d7cbc9fd61858aa4d0bd63b8ef95e5c3a52",
    LEDGER_HEAD_REL.as_posix(): "6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902",
    NEG8_MANIFEST_REL.as_posix(): "0ec9d68aa4265cc9378bb682091a973fc92879b76506fa25af828050a608509f",
    NEG8_CORPUS_REL.as_posix(): "74ccdaec74497c3aa7c074ef1129ec2bf2cc01d8ac14d3d07be77ab468599688",
    START_MANIFEST_REL.as_posix(): "9cac197255bdc9a0a1a0b8ee8ceb587ba3c8cabc20b976b2543dc3a400d37cb0",
    MID_MANIFEST_REL.as_posix(): "9ccedd91307985ba5641e791f4ac89f4e250fca414a4ba713cc7977ced6abb21",
    END_MANIFEST_REL.as_posix(): "8e65a4347aafa0722a60a2bd58c7e8061b860db66fa06f6acec24d1a1ade5c67",
    DECODE_TEMPLATE_REL.as_posix(): "d90b8fec2ccc74f1e982e573789a32116cda78d625ce84e72f2717926edc0cdb",
    P256_PROMPT_REL.as_posix(): "9e1d8eecb688a4ae54c76d24d71be618411c011fa5bebffa44ad6a91ef03d456",
}

EXPECTED_DECODE_DOMAIN_SHA256 = (
    "a20018d57f06d69ffcc14e1e9365ab0121b73804ec480f9b08302384bd583843"
)
EXPECTED_PREFILL_FILE_SHA256 = (
    "e896aeae5eff911dbe14d09de9ebddcafe37b20c67ba059b2a6b7f6d3a6cee25"
)
EXPECTED_PREFILL_DOMAIN_SHA256 = (
    "b95688675b5518ab6675b8688ce4475b0d756653ecfb10ec80fa913ee49d69f1"
)
EXPECTED_P256_FILE_SHA256 = (
    "d34252b4ebe6e379c9e724688c7398b5f96ff79fbddd90ab876e23316ecd1252"
)
EXPECTED_P256_DOMAIN_SHA256 = (
    "023a513fc4020c67d5866e8176dbb872bb3884109c63e3d57637fa6195ba9538"
)


def freeze_aware_status(freeze_reference: object) -> str:
    """Return future-pack status without rewriting the 2026-08-13 frozen bytes."""

    if not isinstance(freeze_reference, dict):
        return DRAFT_STATUS
    if freeze_reference.get("sha256") == CURRENT_FROZEN_RECEIPT_SHA256:
        return DRAFT_STATUS
    return FROZEN_STATUS


def emitted_draft_status() -> str:
    """Return the descriptive status byte written into generated artifacts.

    This is deliberately NOT ``GenerationIdentity.target_status``. That
    property is the dynamic, authenticated freeze state and remains the
    authority a reader should consult; this function returns the generation-
    time description that gets serialized into bytes the D-134 receipt pins.
    Under the 2026-08-18 cold-gate verdict (holding 6) those bytes must never
    transition, so the value they carry is freeze-neutral by construction and
    ``FROZEN_STATUS`` is unreachable from every serialization site by design.
    """

    identity = active_generation()
    if identity.target_is_successor_family:
        return SUCCESSOR_EMITTED_STATUS
    # Ordinal-1 packs were frozen on 2026-08-13 with this literal serialized;
    # preserve-mode replay reproduces those committed bytes verbatim.
    return DRAFT_STATUS


ARM_READINESS_ATTACHMENT = plan_arm_readiness_attachment(
    REPO_ROOT / PACK_REL,
    "BETA",
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
        # Downgrade guard (delta-7 F2). A generator whose own family ordinal is
        # N must refuse every target below N, in EVERY mode -- generate,
        # --check, preserve and no-preserve alike. Without it an emitted _v2
        # generator accepts `--pack-id <family>_v1 --family-suffix _v1
        # --no-preserve-current-frozen-bytes` and rewrites the predecessor's
        # tracked, frozen plan_tree.json / plan_tree.sha256 /
        # producer_contract.json: the ordinal-1 branches of every emitted_*
        # helper are selected, so the rewrite is silent and byte-plausible.
        # M-2's frozen-bytes-never-repaired doctrine bars that outright. This
        # runs in the constructor, which every mode builds before it opens a
        # single output path, so refusal is always pre-write. Same-ordinal
        # (N -> N) draft/preserve behaviour and successor (N -> N+1)
        # generation are untouched.
        if self.target_ordinal < self.current_ordinal:
            raise ValueError(
                f"generator family ordinal {self.current_ordinal} refuses the "
                f"downgrade target {self.pack_id!r} (family ordinal "
                f"{self.target_ordinal}): an earlier family's committed bytes "
                "are never rewritten by a later generator, in any mode"
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
    "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v2",
    "evidence-d117-floor-qwen25-7b-v2",
    "plan-set-d117-qwen25-1p5b-7b-phase-floor-v2",
    "d117-qwen25-phase-floor-set-v2",
    "d117-qwen25-7b-phase-floor-component-v2",
    "d117-qwen25-7b-prefill-p256-floor-v2",
    "d117-qwen25-7b-prefill-p128-floor-v2",
    "d117-qwen25-7b-decode-floor-v2",
    "tg-d117-qwen25-7b-prefill-p256-v2",
    "tg-d117-qwen25-7b-prefill-p128-v2",
    "tg-d117-qwen25-7b-decode-v2",
    # NOTE (round 6, 2026-08-18 cold-gate verdict holding 6): the gamma pack
    # name is deliberately NOT a threaded successor-identity token here. The
    # only thing this generator references inside that pack is the D-122
    # Q1-ratified p256 prompt ARTIFACT, an external ratified input pinned by
    # byte SHA -- the same treatment DECODE_TEMPLATE_REL/POLICY_REL get, and
    # they keep their committed v1 paths in successor generations too.
    # Threading it would point a successor floor pack at a sibling artifact
    # whose bytes this generator cannot read or pin: successor gamma packs now
    # carry a generation-specific freeze-neutral status value, so the threaded
    # reference and the pinned SHA would disagree, and the emitted
    # prompt_artifact_sha256 would be a false claim.
    "d117_floor_qwen25_7b_v2",
    "d117-floor-qwen25-7b-v2",
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
    source = SOURCE_GENERATOR.read_text(encoding="utf-8")
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
        "BETA",
        REPO_ROOT,
    )
FREEZE_NEUTRAL_SUCCESSOR_REGENERATION_RULE = (
    "A successor acceptance artifact issuing before arm REQUIRES a newly generated "
    "pack; the committed D-134 freeze receipt and its plan-tree attachment are "
    "authoritative for this pack's freeze state (the D-125 lineage-envelope "
    "alternative is recorded as a freeze-time lead decision)."
)


def successor_regeneration_rule() -> str:
    """Return the acceptance-artifact policy text for the target generation.

    Formerly a module constant keyed on the module-level ``PACK_STATUS``, which
    made a frozen-status string a live emission path (holding 6 of the
    2026-08-18 cold-gate verdict bars that). The ordinal-1 literal is the one
    the 2026-08-13 freeze receipts pin; successors get wording that is true on
    both sides of their own receipt.
    """

    if active_generation().target_is_successor_family:
        return FREEZE_NEUTRAL_SUCCESSOR_REGENERATION_RULE
    return LEGACY_SUCCESSOR_REGENERATION_RULE


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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sidecar_bytes(digest: str, filename: str) -> bytes:
    return f"{digest}  {filename}\n".encode("utf-8")


def verify_external_inputs() -> None:
    for relative, expected in EXPECTED_EXTERNAL_SHA256.items():
        observed = sha256_file(REPO_ROOT / relative)
        if observed != expected:
            raise ValueError(
                f"external input drift for {relative}: {observed} != {expected}"
            )


def load_p256_prompt_text() -> str:
    prompt_raw = (REPO_ROOT / P256_PROMPT_REL).read_bytes()
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
    if not isinstance(token_basis, Mapping) or token_basis.get(
        "shared_tokenizer_json_sha256"
    ) != P256_SHARED_TOKENIZER_JSON_SHA256:
        raise ValueError("p256 prompt shared-tokenizer pin drifted")
    return text


def condition_families() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], str, str, str
]:
    decode_raw = (REPO_ROOT / DECODE_TEMPLATE_REL).read_bytes()
    decode = json.loads(decode_raw)
    prefill = {
        "schema_version": FAMILY_SCHEMA,
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
    p256 = {
        "schema_version": FAMILY_SCHEMA,
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
    for name, value in (("decode", decode), ("prefill", prefill), ("p256", p256)):
        errors = validate_condition_family_definition(value)
        if errors:
            raise ValueError(f"{name} family invalid: {'; '.join(errors)}")
    decode_domain = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, decode)
    prefill_domain = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, prefill)
    p256_domain = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, p256)
    if decode_domain != EXPECTED_DECODE_DOMAIN_SHA256:
        raise ValueError("D-085 decode condition-family domain changed")
    if sha256_bytes(render_json(prefill)) != EXPECTED_PREFILL_FILE_SHA256:
        raise ValueError("prefill-rider bytes changed")
    if prefill_domain != EXPECTED_PREFILL_DOMAIN_SHA256:
        raise ValueError("prefill-rider condition-family domain changed")
    if sha256_bytes(render_json(p256)) != EXPECTED_P256_FILE_SHA256:
        raise ValueError("p256 condition-family bytes changed")
    if p256_domain != EXPECTED_P256_DOMAIN_SHA256:
        raise ValueError("p256 condition-family domain changed")
    return decode, prefill, p256, decode_domain, prefill_domain, p256_domain


def build_science() -> tuple[
    list[dict[str, Any]],
    list[str],
    list[dict[str, Any]],
    list[str],
    list[dict[str, Any]],
]:
    stages = [{**stage, "runs": []} for stage in STAGES]
    absolute_ids: list[str] = []
    for rep in range(1, N + 1):
        run_id = f"d117f7-df-ph-decode-abs-r{rep:02d}"
        stages[0]["runs"].append(
            {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": rep,
                "role": "absolute_repeat",
                "block_id": None,
                "block_index": rep,
                "position_in_block": 1,
                "position": None,
                "label": None,
                "collection_tags": [f"rep{rep}"],
            }
        )
        absolute_ids.append(run_id)

    blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = f"d117-df-cmp-abba-ph-decode-qwen25-7b-b{block:02d}"
        members: list[dict[str, Any]] = []
        for sequence_index, (label, position) in enumerate(
            (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2")),
            start=1,
        ):
            run_id = (
                f"d117f7-df-cmp-abba-ph-decode-b{block:02d}-"
                f"{position.lower()}"
            )
            run = {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": block,
                "role": "comparative_abba_member",
                "block_id": block_id,
                "block_index": block,
                "position_in_block": sequence_index,
                "position": position,
                "label": label,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stages[1 if block <= 5 else 2]["runs"].append(run)
            members.append(
                {
                    "position": position,
                    "plan_label": label,
                    "plan_sequence_index": sequence_index,
                    "bundle_id": run_id,
                }
            )
        blocks.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": members,
            }
        )
    p256_absolute_ids: list[str] = []
    for rep in range(1, N + 1):
        run_id = f"d117f7-df-ph-prefill-p256-abs-r{rep:02d}"
        stages[3]["runs"].append(
            {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": rep,
                "role": "absolute_repeat",
                "block_id": None,
                "block_index": rep,
                "position_in_block": 1,
                "position": None,
                "label": None,
                "condition_family_id": P256_FAMILY_ID,
                "collection_tags": [f"rep{rep}"],
            }
        )
        p256_absolute_ids.append(run_id)

    p256_blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = f"d117-df-cmp-abba-ph-prefill-p256-qwen25-7b-b{block:02d}"
        members: list[dict[str, Any]] = []
        for sequence_index, (label, position) in enumerate(
            (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2")),
            start=1,
        ):
            run_id = (
                f"d117f7-df-cmp-abba-ph-prefill-p256-b{block:02d}-"
                f"{position.lower()}"
            )
            run = {
                "run_id": run_id,
                "filename": f"{run_id}.json",
                "rep": block,
                "role": "comparative_abba_member",
                "block_id": block_id,
                "block_index": block,
                "position_in_block": sequence_index,
                "position": position,
                "label": label,
                "condition_family_id": P256_FAMILY_ID,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stages[4 if block <= 5 else 5]["runs"].append(run)
            members.append(
                {
                    "position": position,
                    "plan_label": label,
                    "plan_sequence_index": sequence_index,
                    "bundle_id": run_id,
                }
            )
        p256_blocks.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": members,
            }
        )
    return stages, absolute_ids, blocks, p256_absolute_ids, p256_blocks


def config_for(
    run: Mapping[str, Any], plan_sha256: str, p256_prompt_text: str
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
    run: Mapping[str, Any], index: int, config_path: str, config_sha256: str
) -> dict[str, Any]:
    block_id = run.get("block_id")
    return {
        "index": index,
        "config": config_path,
        "config_sha256": config_sha256,
        "run_id": run["run_id"],
        "model_tag": MODEL_TAG,
        "rep": run["rep"],
        "workload": run.get("condition_family_id", DECODE_FAMILY_ID),
        "role": run["role"],
        "block_id": block_id,
        "block_index": run["block_index"],
        "position": run["position"],
        "position_in_block": run["position_in_block"],
        "arm": run["label"],
    }


def family_binding(
    definition: Mapping[str, Any], domain_sha256: str
) -> dict[str, Any]:
    return {
        "condition_family_id": definition["condition_family_id"],
        "condition_family_definition": definition,
        "condition_family_sha256": domain_sha256,
    }


def acceptance_pin() -> dict[str, Any]:
    """Return the acceptance generation this pack binds.

    Preserve mode replays the frozen `_v1` bytes, which are permanently bound
    to the D-116 initial issuance. Any successor generation binds the D-138
    reissue instead, so the two generations never share a pin.
    """

    if active_generation().preserve_current_frozen_bytes:
        return {
            "acceptance_id": ACCEPTANCE_ID,
            "rel": ACCEPTANCE_REL,
            "derivation_sha256": ACCEPTANCE_DERIVATION_SHA256,
        }
    return {
        "acceptance_id": SUCCESSOR_ACCEPTANCE_ID,
        "rel": SUCCESSOR_ACCEPTANCE_REL,
        "derivation_sha256": SUCCESSOR_ACCEPTANCE_DERIVATION_SHA256,
    }


def calibration_basis() -> dict[str, Any]:
    return {
        "calibration_scope": "production_window",
        "acceptance_selection": "issued_d116_artifact_only",
        "issued_acceptance": {
            "path": acceptance_pin()["rel"].as_posix(),
            "acceptance_id": acceptance_pin()["acceptance_id"],
            "artifact_sha256": EXPECTED_EXTERNAL_SHA256[
                acceptance_pin()["rel"].as_posix()
            ],
            "derivation_sha256": acceptance_pin()["derivation_sha256"],
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
        },
        "allowance_rule": "max(observed_drift_s,0.010818)",
        "allowance_embedding_count": 1,
        "component_composition": "componentwise_max_never_sum.v1",
    }


def extraction_spec(
    *,
    decode: Mapping[str, Any],
    prefill: Mapping[str, Any],
    p256: Mapping[str, Any],
    decode_domain: str,
    prefill_domain: str,
    p256_domain: str,
    absolute_rows: Sequence[Mapping[str, Any]],
    comparative_rows: Sequence[Mapping[str, Any]],
    p256_absolute_rows: Sequence[Mapping[str, Any]],
    p256_comparative_rows: Sequence[Mapping[str, Any]],
    root_manifest_id: str,
    root_manifest_sha256: str,
) -> dict[str, Any]:
    root_pin = {
        "path": f"{PACK_REL.as_posix()}/order_manifest.json",
        "manifest_id": root_manifest_id,
        "sha256": root_manifest_sha256,
    }
    def member_hashes(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
        return [
            {
                "bundle_id": row["run_id"],
                "config_sha256": row["config_sha256"],
            }
            for row in rows
        ]

    def comparative_blocks(
        rows: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for block in range(1, N + 1):
            selected = [row for row in rows if row["block_index"] == block]
            result.append(
                {
                    "block_id": selected[0]["block_id"],
                    "members": {
                        position: next(
                            row["run_id"]
                            for row in selected
                            if row["position"] == position
                        )
                        for position in ("A1", "B1", "B2", "A2")
                    },
                }
            )
        return result

    def absolute_cell(
        cell_id: str,
        metric: str,
        precheck: list[str],
        definition: Mapping[str, Any],
        domain_sha: str,
        rows: Sequence[Mapping[str, Any]] = absolute_rows,
    ) -> dict[str, Any]:
        return {
            "cell_id": cell_id,
            "kind": "absolute",
            "metric": metric,
            "window_class": "phase",
            "target_precheck_path": precheck,
            "condition_family_id": definition["condition_family_id"],
            "condition_family_definitions": {
                "all": family_binding(definition, domain_sha)
            },
            "expected_n": N,
            "estimator": "d054_false_effect_guard.v1",
            "order_manifest": root_pin,
            "evidence_root_id": EVIDENCE_ROOT_ID,
            "member_config_sha256": member_hashes(rows),
            "calibration_basis": calibration_basis(),
            "members": [
                {"slot": row["run_id"], "bundle_id": row["run_id"]}
                for row in rows
            ],
        }

    def comparative_cell(
        cell_id: str,
        metric: str,
        precheck: list[str],
        definition: Mapping[str, Any],
        domain_sha: str,
        rows: Sequence[Mapping[str, Any]] = comparative_rows,
    ) -> dict[str, Any]:
        family = family_binding(definition, domain_sha)
        return {
            "cell_id": cell_id,
            "kind": "comparative",
            "metric": metric,
            "window_class": "phase",
            "target_precheck_path": precheck,
            "condition_family_id": definition["condition_family_id"],
            "condition_family_definitions": {"A": family, "B": dict(family)},
            "expected_n": N,
            "estimator": COMMON_MODE_ESTIMATOR_ID,
            "estimator_registration": two_shared_edge_common_mode_registration(),
            "order_manifest": root_pin,
            "evidence_root_id": EVIDENCE_ROOT_ID,
            "member_config_sha256": member_hashes(rows),
            "calibration_basis": calibration_basis(),
            "blocks": comparative_blocks(rows),
        }

    cells = [
        absolute_cell(
            DECODE_ABSOLUTE_CELL,
            "phase_energy_j.decode",
            ["phase", "decode"],
            decode,
            decode_domain,
        ),
        comparative_cell(
            DECODE_COMPARATIVE_CELL,
            "phase_energy_j.decode",
            ["phase", "decode"],
            decode,
            decode_domain,
        ),
        absolute_cell(
            PREFILL_ABSOLUTE_CELL,
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            prefill,
            prefill_domain,
        ),
        comparative_cell(
            PREFILL_COMPARATIVE_CELL,
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            prefill,
            prefill_domain,
        ),
        absolute_cell(
            P256_ABSOLUTE_CELL,
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            p256,
            p256_domain,
            p256_absolute_rows,
        ),
        comparative_cell(
            P256_COMPARATIVE_CELL,
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            p256,
            p256_domain,
            p256_comparative_rows,
        ),
    ]
    all_rows = [*absolute_rows, *comparative_rows]
    p256_rows = [*p256_absolute_rows, *p256_comparative_rows]

    def reported_members(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "ordinal": index,
                "bundle_id": row["run_id"],
                "config_sha256": row["config_sha256"],
            }
            for index, row in enumerate(rows, start=1)
        ]

    decode_reported_members = reported_members(all_rows)
    reported_cells = [
        {
            "cell_id": "d117-reported-mean-ph-decode-qwen25-7b",
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
            "cell_id": "d117-reported-mean-ph-prefill-p128-qwen25-7b",
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
            "cell_id": "d117-reported-mean-ph-prefill-p256-qwen25-7b",
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
            "target_precheck_path": ["phase", "prefill"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": reported_members(p256_rows),
            "missing_or_invalid_member": "refuse_reported_mean",
            "numeric_value": None,
        },
    ]
    spec = {
        "schema_version": "joulewise.detection_floor_extraction_spec.v1",
        # The frozen plan test pins the extraction-spec artifact SHA.
        "draft_status": emitted_draft_status(),
        "successor_acceptance_artifact_policy": successor_regeneration_rule(),
        "cells": cells,
        "reported_energy_cells": reported_cells,
        "reported_energy_registration": {
            "authority": "D-123",
            "procedure_only": True,
            "postcollection_numeric_values": (
                "structurally_absent_until_governed_reduction"
            ),
            "floor_projection_sha256": canonical_sha256(cells),
            "no_semantics_change_rule": (
                "Floor extraction consumes only cells; reported_energy_cells is "
                "a disjoint registered projection over the same physical bundle "
                "universe."
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
            "required_precheck_paths": [
                ["phase", "decode"],
                ["phase", "prefill"],
            ],
            "missing_registered_phase": (
                "refuse_before_floor_or_reported_mean_emission"
            ),
        },
    }
    errors = validate_extraction_spec(spec)
    if errors:
        raise ValueError(f"generated extraction spec is invalid: {errors[0]}")
    return spec


def producer_contract(
    *,
    plan_sha256: str,
    plan_sidecar_sha256: str,
    spec_sha256: str,
    root_manifest_id: str,
    root_manifest_sha256: str,
    config_set_sha256: str,
    decode_domain: str,
    prefill_domain: str,
    p256_domain: str,
    absolute_rows: Sequence[Mapping[str, Any]],
    comparative_rows: Sequence[Mapping[str, Any]],
    p256_absolute_rows: Sequence[Mapping[str, Any]],
    p256_comparative_rows: Sequence[Mapping[str, Any]],
    decode_identity_config_inventory: list[dict[str, str]],
    p256_identity_config_inventory: list[dict[str, str]],
    p256_prompt_text: str,
) -> dict[str, Any]:
    decode_rows = [*absolute_rows, *comparative_rows]
    p256_rows = [*p256_absolute_rows, *p256_comparative_rows]
    config_rows = [
        {"bundle_id": row["run_id"], "config_sha256": row["config_sha256"]}
        for row in [*decode_rows, *p256_rows]
    ]
    decode_config_rows = config_rows[:50]
    p256_config_rows = config_rows[50:]
    expected_config_set_sha256 = canonical_sha256(config_rows)
    if config_set_sha256 != expected_config_set_sha256:
        raise ValueError("config-set SHA does not match the ordered member projection")

    return {
        "schema_version": "joulewise.d117_floor_producer_contract.v1",
        # The frozen plan test pins the producer-contract artifact SHA.
        "draft_status": emitted_draft_status(),
        "plan_set_id": PLAN_SET_ID,
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "producer_index": 2,
        "component_artifact_id": COMPONENT_ARTIFACT_ID,
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
            "path": f"{PACK_REL.as_posix()}/order_manifest.json",
            "manifest_id": root_manifest_id,
            "sha256": root_manifest_sha256,
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
        "roles": [
            {
                "role": "decode",
                "artifact_cell_id": DECODE_ARTIFACT_CELL_ID,
                "transport_group_id": DECODE_TRANSPORT_ID,
                "metric": "phase_energy_j.decode",
                "target_precheck_path": ["phase", "decode"],
                "condition_family_id": DECODE_FAMILY_ID,
                "absolute_calibration_cell_id": DECODE_ABSOLUTE_CELL,
                "comparative_calibration_cell_id": DECODE_COMPARATIVE_CELL,
                "allowed_consumer_families": ["sw-decode-b-qwen25-7b"],
                "members": decode_config_rows,
            },
            {
                "role": "prefill",
                "artifact_cell_id": PREFILL_ARTIFACT_CELL_ID,
                "transport_group_id": PREFILL_TRANSPORT_ID,
                "metric": "phase_energy_j.prefill",
                "target_precheck_path": ["phase", "prefill"],
                "condition_family_id": PREFILL_FAMILY_ID,
                "absolute_calibration_cell_id": PREFILL_ABSOLUTE_CELL,
                "comparative_calibration_cell_id": PREFILL_COMPARATIVE_CELL,
                "allowed_consumer_families": [PREFILL_FAMILY_ID],
                "members": decode_config_rows,
            },
            {
                "role": "prefill_p256",
                "artifact_cell_id": "d117-qwen25-7b-prefill-p256-floor-v2",
                "transport_group_id": "tg-d117-qwen25-7b-prefill-p256-v2",
                "metric": "phase_energy_j.prefill",
                "target_precheck_path": ["phase", "prefill"],
                "condition_family_id": P256_FAMILY_ID,
                "absolute_calibration_cell_id": P256_ABSOLUTE_CELL,
                "comparative_calibration_cell_id": P256_COMPARATIVE_CELL,
                "allowed_consumer_families": ["sw-prefill-p256-b-qwen25-7b"],
                "members": p256_config_rows,
            },
        ],
        "identity_pin_projection": validate_identity_pin_projection(freeze_aware_projection({
            "work_order": IDENTITY_PIN_PROJECTION_WORK_ORDER,
            "mode": "derive_never_operator_enter",
            "state": "unprojected",
            "required_before_arm": True,
            "derivation_contract": IDENTITY_PIN_DERIVATION_CONTRACT,
            "identity_units": [
                {
                    "identity_unit_id": "beta",
                    "producer_plan_reference": {
                        "plan_id": PLAN_ID,
                        "path": emitted_plan_reference(),
                    },
                    "consumer_bindings": [
                        {
                            "arm": "B",
                            "family": "sw-decode-b-qwen25-7b",
                            "measurement_arm": "decode",
                        },
                        {
                            "arm": "B",
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
                    "identity_unit_id": "beta/prefill_p256",
                    "producer_plan_reference": {
                        "plan_id": PLAN_ID,
                        "path": emitted_plan_reference(),
                    },
                    "consumer_bindings": [
                        {
                            "arm": "B",
                            "family": "sw-prefill-p256-b-qwen25-7b",
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
                            "prompt_tokens": None,
                            "output_tokens": 512,
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


def token(kind: str, value: str, relative: str | None = None) -> dict[str, str]:
    row = {"kind": kind, "value": value}
    if relative is not None:
        row["relative"] = relative
    return row


def launch(
    *,
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


def collection_arguments(config_path: str, runs_binding: str) -> list[dict[str, str]]:
    return [
        token("repo_path", config_path),
        token("literal", "--runs-dir"),
        token("binding", runs_binding),
        token("literal", "--log"),
        token("binding_path", runs_binding, "campaign_log.jsonl"),
        token("literal", "--campaign-policy"),
        token("repo_path", POLICY_REL.as_posix()),
        token("literal", "--instrument-calibration-dir"),
        token("binding", "pre_calibration_dir"),
        token("literal", "--instrument-power-policy"),
        token("literal", "ac_high_power"),
        token("literal", "--arm-quiet-mode"),
        token("literal", "--arm-countdown-s"),
        token("literal", "20"),
        token("literal", "--max-failures"),
        token("literal", "1"),
    ]


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
    return [
        token("literal", "--plan"),
        token("repo_path", (resolved_pack_rel / plan_reference).as_posix()),
    ]


def stage_graph(
    stage_manifest_refs: Mapping[str, Mapping[str, Any]],
    external_manifest_refs: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    stage_specs: list[tuple[str, str, int, dict[str, Any], str | None]] = []
    stage_specs.append(
        (
            "beta-bracket-reservation",
            "bracket_reservation",
            1,
            launch(
                command_id="beta-bracket-reservation.reserve",
                command_kind="bracket_reservation",
                tool_id="bracket_reserver",
                interface_id=(
                    "joulewise.calibration_window_bracket_reservation.cli.v1"
                ),
                arguments=[
                    token("literal", "--ledger"),
                    token("binding", "ledger_path"),
                    token("literal", "--head-pin"),
                    token("repo_path", LEDGER_HEAD_REL.as_posix()),
                    *freeze_aware_reservation_plan_arguments(
                        active_generation(),
                        pack_rel=active_generation().pack_rel,
                        plan_reference=CALIBRATION_PLAN_REFERENCE,
                    ),
                    token("literal", "--session-id"),
                    token("binding", "bracket_session_id"),
                    token("literal", "--window-id"),
                    token("tree_pointer", "/window_identity/window_id"),
                    token("literal", "--plan-id"),
                    token("tree_pointer", "/plan/plan_id"),
                    token("literal", "--plan-sha256"),
                    token("tree_pointer", "/plan/actual_sha256"),
                    token("literal", "--evidence-root-id"),
                    token("tree_pointer", "/window_identity/evidence_root_id"),
                    token("literal", "--runs-root"),
                    token("binding", "claim_runs_root"),
                    token("literal", "--pre-attempt-id"),
                    token("binding", "pre_attempt_id"),
                    token("literal", "--post-attempt-id"),
                    token("binding", "post_attempt_id"),
                    token("literal", "--pre-custody-locator"),
                    token("binding", "pre_calibration_dir"),
                    token("literal", "--post-custody-locator"),
                    token("binding", "post_calibration_dir"),
                    token("literal", "--identity-epoch-json"),
                    token("binding", "identity_epoch_json"),
                    token("literal", "--t1-bindings-json"),
                    token("binding", "t1_bindings_json"),
                    token("literal", "--execute"),
                ],
            ),
            None,
        )
    )
    for slot, attempt in (("pre", "pre_attempt_id"),):
        stage_specs.append(
            (
                "beta-pre-calibration",
                "calibration_capture",
                1,
                launch(
                    command_id="beta-pre-calibration.capture",
                    command_kind="calibration_capture",
                    tool_id="fiducial_capture",
                    interface_id="joulewise.powermetrics_fiducial.cli.v1",
                    arguments=[
                        token("literal", "--allow-live"),
                        token("literal", "--output-root"),
                        token(
                            "binding_path",
                            "claim_runs_root",
                            "instrument_validation",
                        ),
                        token("literal", "--session-id"),
                        token("binding", "bracket_session_id"),
                        token("literal", "--slot"),
                        token("literal", slot),
                        token("literal", "--attempt-id"),
                        token("binding", attempt),
                        token("literal", "--power-policy"),
                        token("literal", "ac_high_power"),
                    ],
                ),
                None,
            )
        )
    collection_stages = (
        (
            "beta-bound-collection",
            12,
            "configs/campaigns/neg8_reference_corpus",
            "bound_runs_root",
            NEG8_MANIFEST_REL.as_posix(),
        ),
        (
            "beta-reference-start",
            3,
            "configs/campaigns/window_references/start_triplet",
            "claim_runs_root",
            START_MANIFEST_REL.as_posix(),
        ),
        (
            "beta-science-absolute",
            10,
            f"{PACK_REL.as_posix()}/01_phase_decode_absolute",
            "claim_runs_root",
            f"{PACK_REL.as_posix()}/01_phase_decode_absolute/order_manifest.json",
        ),
        (
            "beta-science-abba-01-05",
            20,
            f"{PACK_REL.as_posix()}/02_phase_decode_abba_blocks_01_05",
            "claim_runs_root",
            (
                f"{PACK_REL.as_posix()}/02_phase_decode_abba_blocks_01_05/"
                "order_manifest.json"
            ),
        ),
        (
            "beta-science-abba-06-10",
            20,
            f"{PACK_REL.as_posix()}/03_phase_decode_abba_blocks_06_10",
            "claim_runs_root",
            (
                f"{PACK_REL.as_posix()}/03_phase_decode_abba_blocks_06_10/"
                "order_manifest.json"
            ),
        ),
        (
            "beta-reference-midpoint",
            1,
            "configs/campaigns/window_references/midpoint",
            "claim_runs_root",
            MID_MANIFEST_REL.as_posix(),
        ),
        (
            "beta-science-prefill-p256-absolute",
            10,
            f"{PACK_REL.as_posix()}/04_phase_prefill_p256_absolute",
            "claim_runs_root",
            f"{PACK_REL.as_posix()}/04_phase_prefill_p256_absolute/order_manifest.json",
        ),
        (
            "beta-science-prefill-p256-abba-01-05",
            20,
            f"{PACK_REL.as_posix()}/05_phase_prefill_p256_abba_blocks_01_05",
            "claim_runs_root",
            (
                f"{PACK_REL.as_posix()}/05_phase_prefill_p256_abba_blocks_01_05/"
                "order_manifest.json"
            ),
        ),
        (
            "beta-science-prefill-p256-abba-06-10",
            20,
            f"{PACK_REL.as_posix()}/06_phase_prefill_p256_abba_blocks_06_10",
            "claim_runs_root",
            (
                f"{PACK_REL.as_posix()}/06_phase_prefill_p256_abba_blocks_06_10/"
                "order_manifest.json"
            ),
        ),
        (
            "beta-reference-end",
            3,
            "configs/campaigns/window_references/end_triplet",
            "claim_runs_root",
            END_MANIFEST_REL.as_posix(),
        ),
    )
    for index, (stage_id, count, config_path, root_binding, manifest) in enumerate(
        collection_stages
    ):
        stage_specs.append(
            (
                stage_id,
                "campaign_collection",
                count,
                launch(
                    command_id=f"{stage_id}.collect",
                    command_kind="campaign_collection",
                    tool_id="campaign_runner",
                    interface_id="joulewise.run_campaign.cli.v1",
                    arguments=collection_arguments(config_path, root_binding),
                ),
                manifest,
            )
        )
        if index == 0:
            stage_specs.append(
                (
                    "beta-bound-derivation",
                    "bound_derivation",
                    1,
                    launch(
                        command_id="beta-bound-derivation.derive",
                        command_kind="bound_derivation",
                        tool_id="campaign_runner",
                        interface_id="joulewise.run_campaign.cli.v1",
                        arguments=[
                            token("literal", "--derive-neg8-drift-bound"),
                            token("repo_path", NEG8_CORPUS_REL.as_posix()),
                            token("literal", "--neg8-drift-bound-output"),
                            token(
                                "binding_path",
                                "bound_runs_root",
                                "neg8-drift-bound.json",
                            ),
                            token("literal", "--runs-dir"),
                            token("binding", "bound_runs_root"),
                        ],
                    ),
                    NEG8_CORPUS_REL.as_posix(),
                )
            )

    stage_specs.append(
        (
            "beta-post-calibration",
            "calibration_capture",
            1,
            launch(
                command_id="beta-post-calibration.capture",
                command_kind="calibration_capture",
                tool_id="fiducial_capture",
                interface_id="joulewise.powermetrics_fiducial.cli.v1",
                arguments=[
                    token("literal", "--allow-live"),
                    token("literal", "--output-root"),
                    token(
                        "binding_path", "claim_runs_root", "instrument_validation"
                    ),
                    token("literal", "--session-id"),
                    token("binding", "bracket_session_id"),
                    token("literal", "--slot"),
                    token("literal", "post"),
                    token("literal", "--attempt-id"),
                    token("binding", "post_attempt_id"),
                    token("literal", "--power-policy"),
                    token("literal", "ac_high_power"),
                ],
            ),
            None,
        )
    )
    stage_specs.append(
        (
            "beta-whole-window-verdict",
            "whole_window_verdict",
            1,
            launch(
                command_id="beta-whole-window-verdict.evaluate",
                command_kind="whole_window_verdict",
                tool_id="campaign_runner",
                interface_id="joulewise.run_campaign.cli.v1",
                arguments=[
                    token("literal", "--whole-window-verdict"),
                    token("literal", "--runs-dir"),
                    token("binding", "claim_runs_root"),
                    token("literal", "--log"),
                    token(
                        "binding_path", "claim_runs_root", "campaign_log.jsonl"
                    ),
                    token("literal", "--campaign-policy"),
                    token("repo_path", POLICY_REL.as_posix()),
                    token("literal", "--neg8-drift-bound"),
                    token(
                        "binding_path", "bound_runs_root", "neg8-drift-bound.json"
                    ),
                ],
            ),
            None,
        )
    )
    backup_launch = launch(
        command_id="beta-backup.claim",
        command_kind="backup",
        tool_id="backup_runs",
        interface_id="joulewise.backup_runs.cli.v1",
        arguments=[
            token("binding", "claim_runs_root"),
            token("binding", "claim_backup_destination"),
        ],
    )
    backup_launch["commands"].append(
        {
            "command_id": "beta-backup.bound",
            "command_kind": "backup",
            "argv_template": {
                "tool_id": "backup_runs",
                "interface_id": "joulewise.backup_runs.cli.v1",
                "arguments": [
                    token("binding", "bound_runs_root"),
                    token("binding", "bound_backup_destination"),
                ],
            },
            "cwd": {"kind": "binding", "value": "repo_root"},
            "success_exit_codes": [0],
        }
    )
    stage_specs.append(
        ("beta-backup", "backup", 2, backup_launch, None)
    )

    rows: list[dict[str, Any]] = []
    for ordinal, (stage_id, kind, count, recipe, reference) in enumerate(
        stage_specs, start=1
    ):
        if reference is None:
            if stage_id in ("beta-pre-calibration", "beta-post-calibration"):
                stage_input: dict[str, Any] = {
                    "kind": "arm_bindings",
                    "slot": "pre" if stage_id == "beta-pre-calibration" else "post",
                }
            elif stage_id == "beta-bracket-reservation":
                stage_input = {"kind": "arm_bindings"}
            else:
                stage_input = {"kind": "collected_roots"}
        elif reference == NEG8_CORPUS_REL.as_posix():
            stage_input = {
                "kind": "external_artifact",
                "path": reference,
                "sha256": EXPECTED_EXTERNAL_SHA256[reference],
            }
        elif reference == NEG8_MANIFEST_REL.as_posix():
            stage_input = dict(external_manifest_refs["neg8_bound"]["manifest"])
        elif reference == START_MANIFEST_REL.as_posix():
            stage_input = dict(external_manifest_refs["start_reference"]["manifest"])
        elif reference == MID_MANIFEST_REL.as_posix():
            stage_input = dict(
                external_manifest_refs["midpoint_reference"]["manifest"]
            )
        elif reference == END_MANIFEST_REL.as_posix():
            stage_input = dict(external_manifest_refs["end_reference"]["manifest"])
        else:
            matching = [
                dict(value)
                for value in stage_manifest_refs.values()
                if value["path"] == reference
            ]
            if len(matching) != 1:
                raise ValueError(f"unresolved stage input: {reference}")
            stage_input = matching[0]
        row = {
            "stage_id": stage_id,
            "ordinal": ordinal,
            "kind": kind,
            "expected_count": count,
            "predecessor": stage_specs[ordinal - 2][0] if ordinal > 1 else None,
            "successor": (
                stage_specs[ordinal][0] if ordinal < len(stage_specs) else None
            ),
            "input": stage_input,
            "launch": recipe,
        }
        rows.append(row)
    return rows


def external_input(input_id: str, manifest: Path) -> dict[str, Any]:
    manifest_data = json.loads((REPO_ROOT / manifest).read_text(encoding="utf-8"))
    executed_order = manifest_data.get("executed_order")
    if not isinstance(executed_order, list):
        raise ValueError(f"external manifest has no executed_order: {manifest}")
    members = []
    for ordinal, row in enumerate(executed_order, start=1):
        if not isinstance(row, Mapping):
            raise ValueError(f"malformed external manifest row: {manifest}")
        config = row.get("config")
        run_id = row.get("run_id")
        if not isinstance(config, str) or not isinstance(run_id, str):
            raise ValueError(f"malformed external manifest row: {manifest}")
        member_path = manifest.parent / config
        members.append(
            {
                "ordinal": ordinal,
                "run_id": run_id,
                "path": member_path.as_posix(),
                "sha256": sha256_file(REPO_ROOT / member_path),
            }
        )
    return {
        "external_input_id": input_id,
        "manifest": {
            "path": manifest.as_posix(),
            "manifest_id": manifest_data.get("manifest_id"),
            "sha256": EXPECTED_EXTERNAL_SHA256[manifest.as_posix()],
        },
        "expected_count": len(members),
        "members": members,
    }


def external_inputs() -> dict[str, dict[str, Any]]:
    return {
        "neg8_bound": external_input("neg8_bound", NEG8_MANIFEST_REL),
        "start_reference": external_input("start_reference", START_MANIFEST_REL),
        "midpoint_reference": external_input(
            "midpoint_reference", MID_MANIFEST_REL
        ),
        "end_reference": external_input("end_reference", END_MANIFEST_REL),
    }


def plan_tree(
    *,
    generator_sha256: str,
    plan_sha256: str,
    plan_sidecar_sha256: str,
    family_rows: list[dict[str, str]],
    science_rows: Sequence[Mapping[str, Any]],
    spec_sha256: str,
    producer_sha256: str,
    config_set_sha256: str,
    identity_pin_projection: Mapping[str, Any],
    stage_manifest_refs: Mapping[str, Mapping[str, Any]],
    external_manifest_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": PLAN_TREE_SCHEMA,
        # The D-134 plan-tree sidecar pins this artifact by SHA.
        "draft_status": emitted_draft_status(),
        "plan": {
            "path": emitted_plan_reference(),
            "plan_id": PLAN_ID,
            "actual_sha256": plan_sha256,
            "declared_sha256": plan_sha256,
            "sidecar_path": emitted_plan_sidecar_reference(),
            "sidecar_sha256": plan_sidecar_sha256,
        },
        "generator": {
            "path": f"{PACK_REL.as_posix()}/generate_configs.py",
            "sha256": generator_sha256,
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
            "sha256": EXPECTED_EXTERNAL_SHA256[POLICY_REL.as_posix()],
        },
        "acceptance_policy": {
            "selection": "issued_d116_artifact_only",
            "issued_acceptance": calibration_basis()["issued_acceptance"],
            "issued_ledger_head": {
                "path": LEDGER_HEAD_REL.as_posix(),
                "file_sha256": EXPECTED_EXTERNAL_SHA256[LEDGER_HEAD_REL.as_posix()],
                "head_sha256": (
                    "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
                ),
            },
            "successor_effect": (
                "invalidate_and_reissue_readiness_and_pin_projection"
            ),
            "arming_prerequisites": [
                {"id": "D117-U2", "status": "required_before_arm"},
                {
                    "id": "D117-POSTCOLLECTION-TRUST-01",
                    "status": "required_before_mint",
                },
                {
                    "id": IDENTITY_PIN_PROJECTION_WORK_ORDER,
                    "status": "required_before_arm",
                },
            ],
        },
        "condition_families": family_rows,
        "science": [dict(row) for row in science_rows],
        "stage_graph": stage_graph(stage_manifest_refs, external_manifest_refs),
        "external_inputs": {
            "manifests": list(external_manifest_refs.values()),
            "artifacts": [
                {
                    "path": NEG8_CORPUS_REL.as_posix(),
                    "sha256": EXPECTED_EXTERNAL_SHA256[
                        NEG8_CORPUS_REL.as_posix()
                    ],
                },
                {
                    "path": P256_PROMPT_REL.as_posix(),
                    "sha256": EXPECTED_EXTERNAL_SHA256[P256_PROMPT_REL.as_posix()],
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
                    {
                        "name": "claim_runs_root",
                        "type": "fresh_absolute_directory",
                        "leaf": CLAIM_ROOT_LEAF,
                    },
                    {
                        "name": "bound_runs_root",
                        "type": "fresh_absolute_directory",
                        "leaf": BOUND_ROOT_LEAF,
                    },
                    {"name": "operator_log_root", "type": "absolute_directory"},
                    {"name": "pre_calibration_dir", "type": "absolute_directory"},
                    {"name": "post_calibration_dir", "type": "absolute_directory"},
                    {"name": "claim_backup_destination", "type": "absolute_path"},
                    {"name": "bound_backup_destination", "type": "absolute_path"},
                    {"name": "bracket_session_id", "type": "nonempty_string"},
                    {"name": "pre_attempt_id", "type": "nonempty_string"},
                    {"name": "post_attempt_id", "type": "nonempty_string"},
                    {
                        "name": "identity_epoch_json",
                        "type": "authenticated_absolute_file",
                    },
                    {
                        "name": "t1_bindings_json",
                        "type": "authenticated_absolute_file",
                    },
                ],
                "derived_path_rules": [
                    (
                        "pre_calibration_dir=claim_runs_root/"
                        "instrument_validation/pre_attempt_id"
                    ),
                    (
                        "post_calibration_dir=claim_runs_root/"
                        "instrument_validation/post_attempt_id"
                    ),
                ],
            },
            "identity_pin_projection": identity_pin_projection,
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
                "path": f"{PACK_REL.as_posix()}/producer_contract.json",
                "sha256": producer_sha256,
            },
            "prefill_phase_presence": "required_for_all_100_physical_bundles",
            "missing_registered_phase": "refuse",
        },
        "runtime_budget": {
            "planning_estimate_minutes_with_margin": 388.8,
            "planning_estimate_hours_with_margin": 6.48,
            "margin_percent": 20,
            "margin_authority": "time_headroom_only_never_member_replacement",
            "science_count": 100,
            "bound_count": 12,
            "reference_count": 7,
            "calibration_observation_count": 2,
        },
    }


def readme() -> bytes:
    oracle = derive_bracket_session_receipt_oracle()
    identity = active_generation()
    identity_statement = (
        ""
        if identity.target_ordinal == 1
        else f"Pack identity: `{identity.pack_id}` (`{identity.family_suffix}`).\n\n"
    )
    # Holding 6 of the 2026-08-18 cold-gate verdict: the successor README is
    # selected by target GENERATION, never by freeze status, and its wording is
    # true on both sides of the pack's own D-134 receipt. The former
    # frozen-status branch is removed, not merely unreachable: under option (a)
    # a frozen pack's README is the one committed before the receipt was
    # minted, so a second variant could only ever be emitted into bytes the
    # receipt already pins.
    #
    # The ordinal-1 literal below is retained because THIS generator, at
    # ordinal 1, must replay the 2026-08-13 committed bytes verbatim. In an
    # EMITTED successor generator it is unreachable by design (Opus F8): that
    # generator's family ordinal is >= 2 and GenerationIdentity refuses every
    # lower-ordinal target before any write, so its legacy "unfrozen draft" /
    # "not armable" wording can never reach emitted bytes.
    if identity.target_is_successor_family:
        content = (
            "# D-117 Qwen2.5-7B phase-floor campaign — status governed by the "
            "D-134 freeze receipt\n\n"
            f"{identity_statement}"
            "This description does not carry freeze status. The committed D-134 "
            "freeze receipt and its plan-tree attachment are authoritative for "
            "this pack's frozen state; the receipt pins `calibration_plan.json` "
            "by SHA, so this text and every serialized `draft_status` field stay "
            "exactly as generated on both sides of the freeze. An external "
            "unexpired PASS/GO arm receipt is required before launch.\n\n"
            "This pack pre-registers the beta window's 10 absolute decode members, "
            "ten null A/B/B/A blocks (40 members), and a zero-member prefill metric "
            "rider over the same 50 physical bundles. It also carries a dedicated "
            "Q8 p256 prefill domain with 10 absolute members and ten null A/B/B/A "
            "blocks (50 additional members), while retaining the D-085 7B stack "
            "identity and registering three D-123 reported phase-energy means. The "
            "p256 workload name remains `df_ph_prefill_p256_candidate` for byte "
            "identity with the gamma consumer even though Q1 has frozen its prompt.\n\n"
            "Its receipt oracle is replay-derived from "
            f"`{oracle['source']['module']}`: {oracle['receipt_count']} physical "
            f"receipts for {oracle['logical_operation_count']} logical operations per "
            "finalized pre/post bracket session. Actual receipt bytes and the absolute "
            "terminal sequence remain arm-time evidence. Arm-time identities require "
            "U11 projection, "
            "and lead review must complete before any later release step.\n\n"
            f"{successor_regeneration_rule()}\n\n"
            "Regenerate or check with:\n\n"
            "```text\n"
            "python3 configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py\n"
            "python3 configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py --check\n"
            "```\n\n"
            "Integrity SHA-256 values in this pack detect drift; they do not mark "
            "release.\n"
        )
        return thread_generation_identity(content).encode("utf-8")
    content = (
        "# D-117 Qwen2.5-7B phase-floor campaign — unfrozen draft\n\n"
        f"{identity_statement}"
        "This pack pre-registers the beta window's 10 absolute decode members, "
        "ten null A/B/B/A blocks (40 members), and a zero-member prefill metric "
        "rider over the same 50 physical bundles. It also carries a dedicated "
        "Q8 p256 prefill domain with 10 absolute members and ten null A/B/B/A "
        "blocks (50 additional members), while retaining the D-085 7B stack "
        "identity and registering three D-123 reported phase-energy means. The "
        "p256 workload name remains `df_ph_prefill_p256_candidate` for byte "
        "identity with the gamma consumer even though Q1 has frozen its prompt.\n\n"
        "The pack is not armable. Its receipt oracle is replay-derived from "
        f"`{oracle['source']['module']}`: {oracle['receipt_count']} physical "
        f"receipts for {oracle['logical_operation_count']} logical operations per "
        "finalized pre/post bracket session. Actual receipt bytes and the absolute "
        "terminal sequence remain arm-time evidence. Arm-time identities require "
        "U11 projection, "
        "and lead review must complete before any later release step.\n\n"
        f"{successor_regeneration_rule()}\n\n"
        "Regenerate or check with:\n\n"
        "```text\n"
        "python3 configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py\n"
        "python3 configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py --check\n"
        "```\n\n"
        "Integrity SHA-256 values in this draft detect drift; they do not mark release.\n"
    )
    return thread_generation_identity(content).encode("utf-8")


def expected_pack_files() -> list[Path]:
    paths = [
        Path("README.md"),
        Path("generate_configs.py"),
        Path("calibration_plan.json"),
        Path("calibration_plan.sha256"),
        Path("order_manifest.json"),
        Path("plan_tree.json"),
        Path("plan_tree.sha256"),
        Path("producer_contract.json"),
        Path("condition_families/condition_family_df_ph_decode_qwen25_7b.json"),
        Path(
            "condition_families/"
            "condition_family_df_ph_prefill_p128_qwen25_7b.json"
        ),
        Path(
            "condition_families/"
            "condition_family_df_ph_prefill_p256_qwen25_7b.json"
        ),
    ]
    paths.append(Path("01_phase_decode_absolute/order_manifest.json"))
    paths.extend(
        Path(
            f"01_phase_decode_absolute/"
            f"d117f7-df-ph-decode-abs-r{rep:02d}.json"
        )
        for rep in range(1, 11)
    )
    for stage, first, last in (
        ("02_phase_decode_abba_blocks_01_05", 1, 5),
        ("03_phase_decode_abba_blocks_06_10", 6, 10),
    ):
        paths.append(Path(f"{stage}/order_manifest.json"))
        for block in range(first, last + 1):
            for position in ("a1", "b1", "b2", "a2"):
                paths.append(
                    Path(
                        f"{stage}/d117f7-df-cmp-abba-ph-decode-"
                        f"b{block:02d}-{position}.json"
                    )
                )
    paths.append(Path("04_phase_prefill_p256_absolute/order_manifest.json"))
    paths.extend(
        Path(
            f"04_phase_prefill_p256_absolute/"
            f"d117f7-df-ph-prefill-p256-abs-r{rep:02d}.json"
        )
        for rep in range(1, 11)
    )
    for stage, first, last in (
        ("05_phase_prefill_p256_abba_blocks_01_05", 1, 5),
        ("06_phase_prefill_p256_abba_blocks_06_10", 6, 10),
    ):
        paths.append(Path(f"{stage}/order_manifest.json"))
        for block in range(first, last + 1):
            for position in ("a1", "b1", "b2", "a2"):
                paths.append(
                    Path(
                        f"{stage}/d117f7-df-cmp-abba-ph-prefill-p256-"
                        f"b{block:02d}-{position}.json"
                    )
                )
    return paths


def validate_artifact_inventory(
    identity: GenerationIdentity, artifacts: Mapping[Path, bytes]
) -> None:
    expected = {
        *(identity.pack_rel / path for path in expected_pack_files()),
        extraction_spec_rel(identity),
    }
    observed = set(artifacts)
    if observed != expected:
        missing = sorted(expected - observed)
        extras = sorted(observed - expected)
        raise ValueError(
            "generation output inventory differs from target allowlist: "
            f"missing={missing}; extras={extras}"
        )


def build_artifacts(
    identity: GenerationIdentity | None = None,
) -> dict[Path, bytes]:
    selected = identity or GenerationIdentity()
    with generation_context(selected):
        if selected.preserve_current_frozen_bytes:
            outputs = {
                *(selected.pack_rel / path for path in expected_pack_files()),
                extraction_spec_rel(selected),
            }
            artifacts = {
                relative: (REPO_ROOT / relative).read_bytes()
                for relative in outputs
            }
            validate_artifact_inventory(selected, artifacts)
            return artifacts
        artifacts = _build_artifacts()
        validate_artifact_inventory(selected, artifacts)
        return artifacts


def _build_artifacts() -> dict[Path, bytes]:
    verify_external_inputs()
    (
        decode,
        prefill,
        p256,
        decode_domain,
        prefill_domain,
        p256_domain,
    ) = condition_families()
    p256_prompt_text = load_p256_prompt_text()
    stages, absolute_ids, blocks, p256_absolute_ids, p256_blocks = build_science()

    plan = {
        "schema_version": PLAN_SCHEMA,
        # The D-134 freeze receipt pins calibration_plan.json by SHA, so this
        # serialized status can never transition after the receipt is minted --
        # the committed receipt IS the freeze state (cold-gate verdict
        # 2026-08-18, holdings 1 and 6). Do not make this field freeze-reactive.
        "draft_status": emitted_draft_status(),
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "fixed_n": N,
        "authorities": ["D-116", "D-117", "D-123", "D-124"],
        "stack_scope": {
            "hardware_target": "macbook_m3_max",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "model_name": MODEL["name"],
            "model_revision": MODEL["revision"],
            "model_source": MODEL["source"],
            "quantization": "int4",
            "sampling": SAMPLING,
            "decode_condition_family_id": DECODE_FAMILY_ID,
            "decode_condition_family_sha256": decode_domain,
            "prefill_condition_family_id": PREFILL_FAMILY_ID,
            "prefill_condition_family_sha256": prefill_domain,
            "prefill_p256_condition_family_id": P256_FAMILY_ID,
            "prefill_p256_condition_family_sha256": p256_domain,
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
                "cell_id": DECODE_ABSOLUTE_CELL,
                "kind": "absolute",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": DECODE_COMPARATIVE_CELL,
                "kind": "comparative_abba",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_blocks": blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
            },
            {
                "cell_id": PREFILL_ABSOLUTE_CELL,
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": PREFILL_COMPARATIVE_CELL,
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_blocks": blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
            },
            {
                "cell_id": P256_ABSOLUTE_CELL,
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": P256_FAMILY_ID,
                "ordered_bundle_ids": p256_absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": P256_COMPARATIVE_CELL,
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": P256_FAMILY_ID,
                "ordered_blocks": p256_blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
            },
        ],
        "reported_energy_cells": [
            {
                "cell_id": "d117-reported-mean-ph-decode-qwen25-7b",
                "metric": "phase_energy_j.decode",
                "measurand": "gross_phase_energy_j",
                "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
                "ordered_bundle_ids": [
                    *absolute_ids,
                    *[
                        member["bundle_id"]
                        for block in blocks
                        for member in block["members"]
                    ],
                ],
            },
            {
                "cell_id": "d117-reported-mean-ph-prefill-p128-qwen25-7b",
                "metric": "phase_energy_j.prefill",
                "measurand": "gross_phase_energy_j",
                "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
                "ordered_bundle_ids": [
                    *absolute_ids,
                    *[
                        member["bundle_id"]
                        for block in blocks
                        for member in block["members"]
                    ],
                ],
            },
            {
                "cell_id": "d117-reported-mean-ph-prefill-p256-qwen25-7b",
                "metric": "phase_energy_j.prefill",
                "measurand": "gross_phase_energy_j",
                "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
                "ordered_bundle_ids": [
                    *p256_absolute_ids,
                    *[
                        member["bundle_id"]
                        for block in p256_blocks
                        for member in block["members"]
                    ],
                ],
            },
        ],
        "execution_mode": {
            "ordered_science_stage_ids": [
                stage["subcampaign_id"] for stage in stages
            ],
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
            "sha256": EXPECTED_EXTERNAL_SHA256[POLICY_REL.as_posix()],
        },
    }
    plan_bytes = render_json(plan)
    plan_sha = sha256_bytes(plan_bytes)
    plan_sidecar = sidecar_bytes(plan_sha, "calibration_plan.json")

    artifacts: dict[Path, bytes] = {
        PACK_REL / "README.md": readme(),
        PACK_REL / "generate_configs.py": embedded_generator_bytes(),
        PACK_REL / "calibration_plan.json": plan_bytes,
        PACK_REL / "calibration_plan.sha256": plan_sidecar,
        PACK_REL
        / "condition_families/condition_family_df_ph_decode_qwen25_7b.json": (
            REPO_ROOT / DECODE_TEMPLATE_REL
        ).read_bytes(),
        PACK_REL
        / "condition_families/condition_family_df_ph_prefill_p128_qwen25_7b.json": render_json(
            prefill
        ),
        PACK_REL
        / "condition_families/condition_family_df_ph_prefill_p256_qwen25_7b.json": render_json(
            p256
        ),
    }

    root_rows: list[dict[str, Any]] = []
    root_science: list[dict[str, Any]] = []
    stage_manifest_rows: list[dict[str, Any]] = []
    root_index = 1
    for stage in stages:
        stage_id = stage["subcampaign_id"]
        local_rows: list[dict[str, Any]] = []
        for local_index, run in enumerate(stage["runs"], start=1):
            config_plan_sha = (
                plan_sha
                if run.get("condition_family_id") == P256_FAMILY_ID
                else LEGACY_DECODE_PLAN_SHA256
            )
            config = config_for(run, config_plan_sha, p256_prompt_text)
            config_bytes = render_json(config)
            config_sha = sha256_bytes(config_bytes)
            config_rel = Path(stage_id) / run["filename"]
            artifacts[PACK_REL / config_rel] = config_bytes
            local = manifest_entry(run, local_index, run["filename"], config_sha)
            root = manifest_entry(
                run, root_index, config_rel.as_posix(), config_sha
            )
            local_rows.append(local)
            root_rows.append(root)
            root_science.append(
                {
                    "ordinal": root_index,
                    "stage_id": stage_id,
                    "config_path": (PACK_REL / config_rel).as_posix(),
                    "config_sha256": config_sha,
                    "run_id": run["run_id"],
                    "role": run["role"],
                    "block_id": run.get("block_id"),
                    "block_index": run["block_index"],
                    "position": run["position"],
                    "arm": run["label"],
                }
            )
            root_index += 1
        manifest_id = (
            f"d117-floor-qwen25-7b-v2-{stage_id.replace('_', '-')}-order-v1"
        )
        leaf_manifest = {
            "schema_version": ORDER_SCHEMA,
            # The frozen plan-tree manifest reference pins these bytes by SHA.
            "draft_status": emitted_draft_status(),
            "manifest_id": manifest_id,
            "plan_id": PLAN_ID,
            "calibration_plan_sha256": plan_sha,
            "ordering_note": stage["ordering_note"],
            "planned_n_bundles": len(local_rows),
            "executed_order": local_rows,
        }
        leaf_bytes = render_json(leaf_manifest)
        leaf_rel = Path(stage_id) / "order_manifest.json"
        artifacts[PACK_REL / leaf_rel] = leaf_bytes
        stage_manifest_rows.append(
            {
                "stage_id": stage_id,
                "kind": "manifest",
                "path": (PACK_REL / leaf_rel).as_posix(),
                "manifest_id": manifest_id,
                "sha256": sha256_bytes(leaf_bytes),
            }
        )

    root_manifest_id = "d117-floor-qwen25-7b-v2-order-v1"
    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        # The frozen producer contract pins the root manifest by SHA.
        "draft_status": emitted_draft_status(),
        "manifest_id": root_manifest_id,
        "plan_id": PLAN_ID,
        "calibration_plan_sha256": plan_sha,
        "planned_n_bundles": len(root_rows),
        "subcampaign_order": [
            {
                "index": index,
                "subcampaign_id": stage["subcampaign_id"],
                "role": stage["role"],
                "optional": False,
                "planned_n_bundles": len(stage["runs"]),
                "ordering_note": stage["ordering_note"],
                "manifest_path": stage_manifest_rows[index - 1]["path"],
                "manifest_id": stage_manifest_rows[index - 1]["manifest_id"],
                "manifest_sha256": stage_manifest_rows[index - 1]["sha256"],
            }
            for index, stage in enumerate(stages, start=1)
        ],
        "executed_order": root_rows,
    }
    root_bytes = render_json(root_manifest)
    root_sha = sha256_bytes(root_bytes)
    artifacts[PACK_REL / "order_manifest.json"] = root_bytes

    absolute_rows = root_science[:10]
    comparative_rows = root_science[10:50]
    p256_absolute_rows = root_science[50:60]
    p256_comparative_rows = root_science[60:100]
    spec = extraction_spec(
        decode=decode,
        prefill=prefill,
        p256=p256,
        decode_domain=decode_domain,
        prefill_domain=prefill_domain,
        p256_domain=p256_domain,
        absolute_rows=absolute_rows,
        comparative_rows=comparative_rows,
        p256_absolute_rows=p256_absolute_rows,
        p256_comparative_rows=p256_comparative_rows,
        root_manifest_id=root_manifest_id,
        root_manifest_sha256=root_sha,
    )
    spec_bytes = render_json(spec)
    spec_sha = sha256_bytes(spec_bytes)
    artifacts[extraction_spec_rel()] = spec_bytes

    config_rows = [
        {"bundle_id": row["run_id"], "config_sha256": row["config_sha256"]}
        for row in root_science
    ]
    config_set_sha = canonical_sha256(config_rows)
    producer = producer_contract(
        plan_sha256=plan_sha,
        plan_sidecar_sha256=sha256_bytes(plan_sidecar),
        spec_sha256=spec_sha,
        root_manifest_id=root_manifest_id,
        root_manifest_sha256=root_sha,
        config_set_sha256=config_set_sha,
        decode_domain=decode_domain,
        prefill_domain=prefill_domain,
        p256_domain=p256_domain,
        absolute_rows=absolute_rows,
        comparative_rows=comparative_rows,
        p256_absolute_rows=p256_absolute_rows,
        p256_comparative_rows=p256_comparative_rows,
        decode_identity_config_inventory=sorted(
            [
                {
                    "path": Path(row["config_path"])
                    .relative_to(PACK_REL)
                    .as_posix(),
                    "sha256": row["config_sha256"],
                }
                for row in root_science[:50]
            ],
            key=lambda row: row["path"],
        ),
        p256_identity_config_inventory=sorted(
            [
                {
                    "path": Path(row["config_path"])
                    .relative_to(PACK_REL)
                    .as_posix(),
                    "sha256": row["config_sha256"],
                }
                for row in root_science[50:]
            ],
            key=lambda row: row["path"],
        ),
        p256_prompt_text=p256_prompt_text,
    )
    producer_bytes = (
        (REPO_ROOT / PACK_REL / "producer_contract.json").read_bytes()
        if active_generation().preserve_current_frozen_bytes
        else render_json(producer)
    )
    if active_generation().preserve_current_frozen_bytes:
        producer = json.loads(producer_bytes)
    producer_sha = sha256_bytes(producer_bytes)
    artifacts[PACK_REL / "producer_contract.json"] = producer_bytes

    family_rows = [
        {
            "path": (
                f"{PACK_REL.as_posix()}/condition_families/"
                "condition_family_df_ph_decode_qwen25_7b.json"
            ),
            "byte_sha256": EXPECTED_EXTERNAL_SHA256[
                DECODE_TEMPLATE_REL.as_posix()
            ],
            "condition_family_id": DECODE_FAMILY_ID,
            "domain_sha256": decode_domain,
        },
        {
            "path": (
                f"{PACK_REL.as_posix()}/condition_families/"
                "condition_family_df_ph_prefill_p128_qwen25_7b.json"
            ),
            "byte_sha256": sha256_bytes(render_json(prefill)),
            "condition_family_id": PREFILL_FAMILY_ID,
            "domain_sha256": prefill_domain,
        },
        {
            "path": (
                f"{PACK_REL.as_posix()}/condition_families/"
                "condition_family_df_ph_prefill_p256_qwen25_7b.json"
            ),
            "byte_sha256": sha256_bytes(render_json(p256)),
            "condition_family_id": P256_FAMILY_ID,
            "domain_sha256": p256_domain,
            "prompt_artifact_path": P256_PROMPT_REL.as_posix(),
            "prompt_artifact_sha256": EXPECTED_EXTERNAL_SHA256[
                P256_PROMPT_REL.as_posix()
            ],
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
    ]
    stage_manifest_refs = {
        row["stage_id"]: {
            "kind": row["kind"],
            "path": row["path"],
            "manifest_id": row["manifest_id"],
            "sha256": row["sha256"],
        }
        for row in stage_manifest_rows
    }
    external_manifest_refs = external_inputs()
    tree = plan_tree(
        generator_sha256=(
            preserved_generator_sha256()
            if active_generation().preserve_current_frozen_bytes
            else sha256_bytes(artifacts[PACK_REL / "generate_configs.py"])
        ),
        plan_sha256=plan_sha,
        plan_sidecar_sha256=sha256_bytes(plan_sidecar),
        family_rows=family_rows,
        science_rows=root_science,
        spec_sha256=spec_sha,
        producer_sha256=producer_sha,
        config_set_sha256=config_set_sha,
        identity_pin_projection=producer["identity_pin_projection"],
        stage_manifest_refs=stage_manifest_refs,
        external_manifest_refs=external_manifest_refs,
    )
    tree_bytes = (
        (REPO_ROOT / PACK_REL / "plan_tree.json").read_bytes()
        if active_generation().preserve_current_frozen_bytes
        else render_json(tree)
    )
    tree_sha = sha256_bytes(tree_bytes)
    artifacts[PACK_REL / "plan_tree.json"] = tree_bytes
    artifacts[PACK_REL / "plan_tree.sha256"] = (
        (REPO_ROOT / PACK_REL / "plan_tree.sha256").read_bytes()
        if active_generation().preserve_current_frozen_bytes
        else sidecar_bytes(tree_sha, "plan_tree.json")
    )
    return {
        generated_relative_path(relative): content
        for relative, content in artifacts.items()
    }


def write_artifacts(output_root: Path, artifacts: Mapping[Path, bytes]) -> None:
    validate_generation_write_boundary(output_root, artifacts)
    for relative, content in artifacts.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def validate_generation_write_boundary(
    output_root: Path, outputs: Iterable[Path]
) -> None:
    """Refuse link traversal or anomalous existing nodes before any write."""

    # Registered residual (lead disposition; registration lives in
    # docs/risk_register.md -- this comment is not the registration). This
    # boundary is check-then-write: a concurrent process could substitute a
    # validated ancestor or write target with a symlink after this function
    # returns and before the bytes land.
    #
    # The disposition rests on DESK-TIME SINGLE-OPERATOR GENERATION, not on the
    # measurement threat model. Pack generation is hand-run by one operator at
    # the desk, outside any measurement window, against a repository checkout
    # the operator controls; nothing else is scheduled to write into the pack
    # path while it runs. The non-adversarial concurrency that genuinely occurs
    # here -- editors, backup and sync daemons, the parallel worktree fleet --
    # clobbers or duplicates files; none of it substitutes an ancestor
    # directory with a symlink in the microseconds after validation. Winning
    # this race requires a local program acting adversarially and with
    # knowledge of the boundary, which single-operator desk discipline
    # excludes. D-139 A1 ("no adversarial programs affecting the measurement
    # can be assumed") is cited BY ANALOGY only: its own scope is the
    # measurement environment, not this generator's desk-time write boundary.
    #
    # The accidental class IS closed: pre-existing links anywhere in the pack
    # path, spec, sidecar, or ancestors refuse before any write. The residual
    # reopens if the threat model is revised to admit concurrent adversarial
    # local processes, or if generation moves to multi-operator/shared-machine
    # use (cold-gate conditions C-B1a and C-B1b, 2026-08-18; C-B1b formally
    # supersedes delta-4's F2 dirfd remedy demand). No dirfd/O_NOFOLLOW
    # hardening is attempted here; the residual is registered, not closed.

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


def actual_pack_paths(pack_root: Path) -> set[Path]:
    return {
        path.relative_to(pack_root)
        for path in pack_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def compare_artifacts(output_root: Path, artifacts: Mapping[Path, bytes]) -> None:
    problems: list[str] = []
    for relative, expected in artifacts.items():
        path = output_root / relative
        try:
            observed = path.read_bytes()
        except OSError as exc:
            problems.append(f"{relative}: unreadable: {exc}")
            continue
        if observed != expected:
            problems.append(f"{relative}: bytes differ")
    if problems:
        raise ValueError("generated draft check failed: " + "; ".join(problems))


def check_inventory(
    output_root: Path,
    artifacts: Mapping[Path, bytes],
    identity: GenerationIdentity,
) -> None:
    pack_rel = identity.pack_rel
    pack_root = output_root / pack_rel
    expected = set(expected_pack_files())
    generated_tree = json.loads(
        artifacts[pack_rel / "plan_tree.json"].decode("utf-8")
    )
    freeze_reference = generated_tree["arm_attachments"]["arm_readiness"][
        "freeze_receipt"
    ]
    if freeze_reference is not None:
        freeze_path = Path(freeze_reference["path"])
        expected |= {
            freeze_path,
            freeze_path.with_name(f"{freeze_path.name}.sha256"),
        }
        freeze_receipt = json.loads(
            (output_root / pack_rel / freeze_path).read_text(encoding="utf-8")
        )
        for item in freeze_receipt["evidence"]:
            evidence_path = Path(item["path"])
            evidence_sidecar = (
                evidence_path.with_suffix(".sha256")
                if evidence_path.parent.name == "identity_pin_projection.receipts"
                else evidence_path.with_name(f"{evidence_path.name}.sha256")
            )
            expected |= {evidence_path, evidence_sidecar}
            evidence_receipt = json.loads(
                (output_root / pack_rel / evidence_path).read_text(
                    encoding="utf-8"
                )
            )
            expected.update(
                Path(fact["source_path"])
                for fact in evidence_receipt.get("facts", [])
                if "source_path" in fact
            )
    projection_reference = generated_tree["arm_attachments"][
        "identity_pin_projection"
    ]["projection_receipt"]
    if projection_reference is not None:
        projection_path = Path(projection_reference["path"])
        expected |= {
            projection_path,
            projection_path.with_suffix(".sha256"),
        }
    observed = actual_pack_paths(pack_root)
    missing = sorted(expected - observed)
    extras = sorted(observed - expected)
    if missing or extras:
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(path.as_posix() for path in missing))
        if extras:
            details.append("extras=" + ",".join(path.as_posix() for path in extras))
        raise ValueError("pack inventory differs: " + "; ".join(details))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-root", type=Path)
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
    artifacts = build_artifacts(identity)
    if args.check:
        check_root = args.output_root.resolve() if args.output_root else REPO_ROOT
        check_inventory(check_root, artifacts, identity)
        compare_artifacts(check_root, artifacts)
        status = identity.target_status
        identity_label = (
            "" if identity.target_ordinal == 1 else f"{identity.pack_id} "
        )
        print(
            f"{identity_label}{status.replace('_', ' ')} check passed: "
            "100 science configs, 6 floor cells, "
            "3 reporting cells"
        )
        return 0
    output_root = args.output_root.absolute() if args.output_root else REPO_ROOT
    write_artifacts(output_root, artifacts)
    pack_count = sum(1 for path in artifacts if identity.pack_rel in path.parents)
    print(
        f"generated {pack_count} pack files and "
        f"{extraction_spec_rel(identity).as_posix()}; "
        "science_configs=100"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
