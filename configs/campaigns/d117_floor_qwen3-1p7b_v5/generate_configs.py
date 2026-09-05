#!/usr/bin/env python3
"""Generate the D-117 Qwen3-1.7B floor campaign draft deterministically."""

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
PACK_REL = Path("configs/campaigns/d117_floor_qwen3-1p7b_v5")
CALIBRATION_PLAN_REFERENCE = "calibration_plan.json"
CURRENT_FAMILY_SUFFIX = "_v5"
SPEC_REL = PACK_REL / "extraction_spec.json"
SOURCE_PATH = Path(__file__).resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.campaign_generator_core import (  # noqa: E402
    actual_pack_paths,
    make_render_json,
    sha256_bytes,
    sidecar_bytes,
    validate_generation_write_boundary,
)
from joulewise.detection_floor import (  # noqa: E402
    COMMON_MODE_ESTIMATOR_ID,
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    two_shared_edge_common_mode_registration,
)
from joulewise.dominance_closeout import (  # noqa: E402
    COMMON_MODE_INPUT_FIELDS,
    COMMON_MODE_REPLAY_RULE_ID,
    DOMINANCE_COMPARISON,
    DOMINANCE_RATIO_ID,
    DOMINANCE_THRESHOLD,
    DOMINANCE_ZERO_DENOMINATOR_REASON,
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
from joulewise.calibration_bracketing import (  # noqa: E402
    acceptance_allowance_rule,
)
from joulewise.receipt_oracle import (  # noqa: E402
    derive_bracket_session_receipt_oracle,
)
from joulewise.provenance import prompt_token_ids_sha256  # noqa: E402
from joulewise.reduce import MIN_PHASE_SAMPLES as REDUCER_MIN_PHASE_SAMPLES  # noqa: E402
from joulewise.suite import (  # noqa: E402
    SUITE_SCHEMA_VERSION,
    SuiteManifest,
    suite_manifest_sha256,
)


N = 10
PREFILL_LENGTH = 512
PREFILL_LADDER_PROMPT_TOKENS = [512, 1024, 2048, 4096]
PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG = 5
PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5
PREFILL_MIN_PHASE_SAMPLES_PINNED = 3
PREFILL_SAMPLE_COUNT_MARGIN_FLOOR = 2
PREFILL_SELECTION_EXPRESSION = (
    "first r in ladder_prompt_tokens where small_model_member_count[r] >= "
    "min_small_model_members_per_rung and min(reducer_written_summary_metrics[r]"
    "[small_model_members].overlapping_power_interval_count) >= "
    "min_overlapping_power_interval_count; large-model probes recorded, "
    "non-gating; otherwise 4096"
)
PREFILL_RULING_TRACE_PATHS = (
    "docs/process_traces/2026-08-30-prefill-margin-coldgate/"
    "03-MAGISTRATE-RATIFICATION.md",
    "docs/process_traces/2026-09-01-fresh-model-review/"
    "16b-RULING-g2a-producers.md",
)
PREFILL_EXHAUSTED_LADDER_BRANCH = {
    "condition": "no_rung_clears_pre_registered_count_floor",
    "collection_prompt_tokens": 4096,
    "holm_family_m": 2,
    "reducer_refusal": {
        "condition": "overlapping_power_interval_count < min_phase_samples_pinned",
        "reason_code": "not_resolvable_sample_count",
        "printed_result": "reducer_refusal_as_emitted",
    },
    "pre_registration_refusal": {
        "condition": (
            "min_phase_samples_pinned <= overlapping_power_interval_count < "
            "min_overlapping_power_interval_count"
        ),
        "printed_result": "below the pre-registered count floor of 5",
        "disclose_reducer_resolvable_result": True,
        "print_reducer_refusal_code": False,
    },
}
PROMPT_SENTENCE = "The plan remains easy to audit."
PLAN_ID = "plan-d117-floor-qwen3-1p7b-decode-prefill-p512-v5"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen3-1p7b-v5"
CLAIM_ROOT_LEAF = "runs_d117_floor_qwen3-1p7b_v5"
BOUND_ROOT_LEAF = "runs_d117_floor_qwen3-1p7b_v5_bound"
CAMPAIGN_TAG = "d117-floor-qwen3-1p7b-v5"
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
    ""
)
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
TREE_SCHEMA = "joulewise.d117_plan_tree.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
DECODE_FAMILY_ID = "df-ph-decode-qwen3-1p7b"
PREFILL_FAMILY_ID = "df-ph-prefill-p42-qwen3-1p7b"
P512_FAMILY_ID = "df-ph-prefill-p512-qwen3-1p7b"
DECODE_FAMILY_REL = PACK_REL / "condition_families/condition_family_df_ph_decode.json"
PREFILL_FAMILY_REL = (
    PACK_REL
    / "condition_families/condition_family_df_ph_prefill_p42_qwen3_1p7b.json"
)
P512_FAMILY_REL = (
    PACK_REL
    / "condition_families/condition_family_df_ph_prefill_p512_qwen3_1p7b.json"
)
PANEL_REL = Path("configs/model_panels/qwen3_4bit.json")
DECODE_WORKLOAD_REL = Path("configs/workloads/real_prompts_v1.json")
PANEL_SHA256 = "78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a"
DECODE_WORKLOAD_SHA256 = "52ad0a4092b540426376edf19b717ba64552b34d9d2ee737d49dac7786c7616b"
MODEL_ID = "qwen3-1p7b"
MODEL_TAG = "qwen3-1p7b-mlx"
PLAN_PROFILE = "ALPHA"
PRODUCER_INDEX = 1
CONSUMER_ARM = "A"
DECODE_SUITE_REL = PACK_REL / "decode_prompt_manifest.json"
DECODE_WORKLOAD_CANDIDATE_REL = PACK_REL / "decode_workload_candidate.json"
PREFILL_PIN_REL = PACK_REL / "prefill_pin/prefill_prompt_pin.json"
P512_PROMPT_UTF8_SHA256 = ""
P512_SHARED_TOKENIZER_JSON_SHA256 = ""
P512_PROMPT_TOKEN_IDS_SHA256 = ""
P512_PROMPT_TEXT = ""
PREFILL_PIN_SOURCE_PATH: Path | None = None
PREFILL_PIN_SOURCE_RAW = b""
PREFILL_LADDER_SOURCE_PATH: Path | None = None
PREFILL_LADDER_SOURCE_REL: Path | None = None
PREFILL_LADDER_SOURCE_RAW = b""
PREFILL_SELECTION_SOURCE_PATH: Path | None = None
PREFILL_SELECTION_SOURCE_REL: Path | None = None
PREFILL_SELECTION_SOURCE_RAW = b""
DECODE_PROFILE: dict[str, Any] = {}
DECODE_RENDERING: dict[str, Any] = {}
POLICY_REL = Path("configs/campaign_policies/quiet_mac_p2_production.json")
ACCEPTANCE_REL = Path("configs/calibration/calibration_acceptance_d079_v2.json")
LEDGER_HEAD_REL = Path("configs/calibration/calibration_ledger_head.json")
POLICY_SHA256 = "b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd"
DECODE_FAMILY_DOMAIN_SHA256 = ""
PREFILL_FAMILY_DOMAIN_SHA256 = ""
P512_FAMILY_DOMAIN_SHA256 = ""
ACCEPTANCE_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)
ACCEPTANCE_DERIVATION_SHA256 = (
    "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
)
ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n19"
# D-138 dual-generation acceptance. The frozen `_v1` identity is permanently
# bound to the D-116 initial issuance; successor generations bind the reissue
# derived at the integrated estimator head.
SUCCESSOR_ACCEPTANCE_REL = Path(
    "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
)
SUCCESSOR_ACCEPTANCE_SHA256 = (
    "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"
)
SUCCESSOR_ACCEPTANCE_DERIVATION_SHA256 = (
    "18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3"
)
SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"
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
    PLAN_PROFILE,
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
    "plan-d117-floor-qwen3-1p7b-decode-prefill-p512-v5",
    "evidence-d117-floor-qwen3-1p7b-v5",
    "plan-set-d117-qwen3-1p7b-8b-phase-floor-v5",
    "d117-qwen3-phase-floor-set-v5",
    "d117-qwen3-1p7b-phase-floor-component-v5",
    "d117-qwen3-1p7b-prefill-p512-floor-v5",
    "d117-qwen3-1p7b-prefill-p42-floor-v5",
    "d117-qwen3-1p7b-decode-floor-v5",
    "tg-d117-qwen3-1p7b-prefill-p512-v5",
    "tg-d117-qwen3-1p7b-prefill-p42-v5",
    "tg-d117-qwen3-1p7b-decode-v5",
    # NOTE (round 6, 2026-08-18 cold-gate verdict holding 6): the gamma pack
    # name is deliberately NOT a threaded successor-identity token here. The
    # only thing this generator references inside that pack is the D-122
    # Q1-ratified p512 prompt ARTIFACT, an external ratified input pinned by
    # byte SHA -- the same treatment DECODE_TEMPLATE_REL/POLICY_REL get, and
    # they keep their committed v1 paths in successor generations too.
    # Threading it would point a successor floor pack at a sibling artifact
    # whose bytes this generator cannot read or pin: successor gamma packs now
    # carry a generation-specific freeze-neutral status value, so the threaded
    # reference and the pinned SHA would disagree, and the emitted
    # prompt_artifact_sha256 would be a false claim.
    "d117_floor_qwen3-1p7b_v5",
    "d117-floor-qwen3-1p7b-v5",
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


render_json = make_render_json(thread_generation_identity)


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
    return selected.pack_rel / "extraction_spec.json"


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
        PLAN_PROFILE,
        REPO_ROOT,
    )


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
            "artifact_sha256": ACCEPTANCE_SHA256,
            "derivation_sha256": ACCEPTANCE_DERIVATION_SHA256,
        }
    return {
        "acceptance_id": SUCCESSOR_ACCEPTANCE_ID,
        "rel": SUCCESSOR_ACCEPTANCE_REL,
        "artifact_sha256": SUCCESSOR_ACCEPTANCE_SHA256,
        "derivation_sha256": SUCCESSOR_ACCEPTANCE_DERIVATION_SHA256,
    }


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


LEGACY_SUCCESSOR_REGENERATION_RULE = (
    "A successor acceptance artifact issuing before arm REQUIRES pack regeneration "
    "(packs are unfrozen drafts; the D-125 lineage-envelope alternative is recorded "
    "as a freeze-time lead decision)."
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

MODEL = {
    "name": "Qwen3-1.7B-4bit",
    "family": "qwen3",
    "source": "/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit",
    "revision": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
    "weight_format": "mlx",
    "context_window": 40960,
    "tokenizer_json_sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4",
    "chat_template_sha256": "87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5",
}
QUANTIZATION = {"name": "int4", "bits": 4, "group_size": 64}
HARDWARE = {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": (
        "D-117 alpha Qwen3-1.7B production floor campaign on the current "
        "M3 Max; normal powermetrics sampler set only."
    ),
}
WORKLOAD = {
    "name": "real_prompts_v1_chat_rendered",
    "repetitions": 1,
    "warmup_runs": 1,
    "prompt_tokens": 42,
    "output_tokens": 512,
}
P512_WORKLOAD_NAME = "df_ph_prefill_p512_candidate"
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
        "stage_id": "04_phase_prefill_p512_absolute",
        "role": "absolute_phase_prefill_p512",
        "ordering_note": "Ten fixed absolute p512 prefill repeats in repetition order.",
    },
    {
        "stage_id": "05_phase_prefill_p512_abba_blocks_01_05",
        "role": "comparative_phase_prefill_p512_first_half",
        "ordering_note": "Fixed contiguous null A/B/B/A p512 prefill blocks 1-5.",
    },
    {
        "stage_id": "06_phase_prefill_p512_abba_blocks_06_10",
        "role": "comparative_phase_prefill_p512_second_half",
        "ordering_note": "Fixed contiguous null A/B/B/A p512 prefill blocks 6-10.",
    },
)


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        thread_generation_identity(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
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


def write_json(output_root: Path, relative: Path, value: Any) -> bytes:
    raw = render_json(value)
    write_bytes(output_root, relative, raw)
    return raw


def dominance_criterion_registration() -> dict[str, Any]:
    return {
        "kind": "comparative",
        "ratio_id": DOMINANCE_RATIO_ID,
        "numerator": "corner_widened_unguarded_floor_j",
        "denominator": "point_unguarded_floor_j",
        "threshold": DOMINANCE_THRESHOLD,
        "comparison": DOMINANCE_COMPARISON,
        "exact_equality_policy": "R == 2.0 passes",
        "per_component": True,
        "all_must_pass": True,
        "mixed_outcome_policy": "report_per_component_and_use_null_framing",
        "zero_denominator_policy": {
            "action": "refuse",
            "reason": DOMINANCE_ZERO_DENOMINATOR_REASON,
            "never_emit": ["Infinity", "NaN"],
        },
        "component_dispositions": {
            "absolute_independent_corner": {
                "status": "reportable",
                "part_of_ratio_gate": True,
            },
            "absolute_common_mode": {
                "status": "not_applicable",
                "reason": (
                    "the absolute estimator uses deviations from the mean, so a "
                    "uniform shared fiducial shift cancels exactly; the replay is "
                    "registered only for comparative ABBA block inputs"
                ),
            },
            "comparative_common_mode": {
                "status": "mandatory",
                "withdrawal_comparison": "R_cm < 2.0",
                "withdrawal_consequence": "withdraw_dominance_sentence",
            },
            "absolute_local_only_diagnostic": {
                "status": "not_registered",
                "reason": "deferred; requires a distinct versioned name",
            },
        },
        "common_mode": {
            "disclosure": "mandatory",
            "applies_to": "comparative_abba",
            "ratio_id": "attribution_dominance_ratio_common_mode.v1",
            "threshold": DOMINANCE_THRESHOLD,
            "withdrawal_comparison": "R_cm < 2.0",
            "withdrawal_consequence": "withdraw_dominance_sentence",
            "replay_rule": {
                "rule_id": COMMON_MODE_REPLAY_RULE_ID,
                "replay_fence": "authenticated_custodied_block_inputs_only",
                "input_fields": list(COMMON_MODE_INPUT_FIELDS),
                "formula_reference": [
                    "joulewise.floor_extraction._common_mode_block_half_width.v1",
                    "joulewise.detection_floor.comparative_false_effect_floor.v1",
                ],
                "formula": (
                    "split each registered block width into its shared excursion "
                    "and local residual terms; enumerate one common shared sign "
                    "across all blocks and every independent local sign; take the "
                    "maximum comparative unguarded floor"
                ),
            },
        },
    }


def floor_estimator_registration() -> dict[str, Any]:
    return {
        **two_shared_edge_common_mode_registration(),
        "dominance_criterion": dominance_criterion_registration(),
    }


def decode_family_definition() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": DECODE_FAMILY_ID,
        "workload_profile": dict(WORKLOAD),
        "measurement_target": {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def prefill_family_definition() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": PREFILL_FAMILY_ID,
        "workload_profile": {
            "name": WORKLOAD["name"],
            "prompt_tokens": WORKLOAD["prompt_tokens"],
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


def p512_family_definition() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": P512_FAMILY_ID,
        "workload_profile": {
            "name": P512_WORKLOAD_NAME,
            "prompt_tokens": PREFILL_LENGTH,
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


def load_model_inputs(
    panel_path: Path = REPO_ROOT / PANEL_REL,
    decode_workload_path: Path = REPO_ROOT / DECODE_WORKLOAD_REL,
) -> None:
    global DECODE_PROFILE, DECODE_RENDERING
    if sha256_file(panel_path) != PANEL_SHA256:
        raise ValueError("model_panel_sha256_mismatch")
    if sha256_file(decode_workload_path) != DECODE_WORKLOAD_SHA256:
        raise ValueError("decode_workload_sha256_mismatch")
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    entries = panel.get("entries") if isinstance(panel, dict) else None
    entry = next(
        (
            item
            for item in entries or []
            if isinstance(item, dict) and item.get("model_id") == MODEL_ID
        ),
        None,
    )
    if entry is None or entry.get("admission", {}).get("status") != "admitted":
        raise ValueError("model_panel_admission_mismatch")
    expected_model = {
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
    if expected_model != MODEL or entry.get("quantization") != QUANTIZATION:
        raise ValueError("model_panel_identity_mismatch")
    if (
        entry.get("enable_thinking") != "false"
        or entry.get("chat_template_applied") is not True
    ):
        raise ValueError("thinking_policy_mismatch")
    pinsets = panel.get("rendering_pinsets")
    pinset = next(
        (
            item
            for item in pinsets or []
            if isinstance(item, dict)
            and item.get("pinset_id") == entry.get("rendering_pinset_id")
        ),
        None,
    )
    profile = json.loads(decode_workload_path.read_text(encoding="utf-8"))
    prompts = profile.get("prompts") if isinstance(profile, dict) else None
    renderings = pinset.get("prompts") if isinstance(pinset, dict) else None
    if (
        pinset is None
        or pinset.get("workload_profile_id") != profile.get("profile_id")
        or pinset.get("prompt_set_sha256") != profile.get("prompt_set_sha256")
        or pinset.get("tokenizer_json_sha256") != MODEL["tokenizer_json_sha256"]
        or pinset.get("chat_template_sha256") != MODEL["chat_template_sha256"]
        or pinset.get("enable_thinking") != "false"
        or pinset.get("chat_template_applied") is not True
        or not isinstance(prompts, list)
        or not isinstance(renderings, list)
        or len(prompts) != len(renderings)
    ):
        raise ValueError("decode_rendering_policy_mismatch")
    prompt = prompts[0]
    rendering = renderings[0]
    if (
        prompt.get("prompt_id") != "sky_color"
        or rendering.get("prompt_id") != prompt.get("prompt_id")
        or rendering.get("text_utf8_sha256") != prompt.get("text_utf8_sha256")
        or rendering.get("prompt_tokens") != WORKLOAD["prompt_tokens"]
        or rendering.get("prompt_token_ids", [])[-4:]
        != [151667, 271, 151668, 271]
        or prompt_token_ids_sha256(rendering.get("prompt_token_ids", []))
        != rendering.get("prompt_token_ids_sha256")
    ):
        raise ValueError("decode_index_zero_rendering_mismatch")
    DECODE_PROFILE = profile
    DECODE_RENDERING = dict(rendering)


def decode_suite_manifest() -> dict[str, Any]:
    prompt = DECODE_PROFILE["prompts"][0]
    rendering = DECODE_RENDERING
    manifest = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "suite_id": f"d117-{MODEL_ID}-sky-color-decode-floor-v5",
        "suite_profile": DECODE_PROFILE["profile_id"],
        "suite_revision": DECODE_PROFILE["prompt_set_sha256"],
        "suite_seed": "d166-floor-index-zero-v1",
        "generator": {
            "name": "d117_v5_chat_template_renderer",
            "version": "1.0.0",
            "parameters_hash": MODEL["chat_template_sha256"],
        },
        "analysis_contract": {
            "independent_unit": "bundle",
            "primary_window_class": "suite",
            "allowed_aggregation_levels": ["suite", "block", "level"],
        },
        "execution_policy": {
            "order_policy": "manifest_order",
            "within_bundle_repeats": 1,
            "cooldown_policy": "bundle_only",
            "declared_cache_policy": "cold_between_bundles",
            "cache_policy_verification": "declared_not_verified",
            "warmup_policy": "adapter_default",
            "default_output_policy": "fixed_budget_exact",
        },
        "source_manifest": {
            "source_id": DECODE_PROFILE["profile_id"],
            "source_kind": "original_real_prompts",
            "revision": DECODE_PROFILE["prompt_set_sha256"],
            "subset_id": prompt["prompt_id"],
            "subset_sha256": prompt["text_utf8_sha256"],
            "license": DECODE_PROFILE["license"],
            "contamination_note": "original prompts; no benchmark capability claim",
        },
        "items": [
            {
                "item_id": f"{prompt['prompt_id']}-{MODEL_ID}-rendered",
                "item_type": "ids_prompt",
                "category": "real_question",
                "difficulty": {
                    "axis": "unscored_real_prompt",
                    "value": 1.0,
                    "scale": "nominal",
                    "label": prompt["prompt_id"],
                    "source": DECODE_PROFILE["profile_id"],
                    "quarantine_note": "content variety only; no accuracy inference",
                },
                "shape": {
                    "planned_prompt_tokens": rendering["prompt_tokens"],
                    "planned_output_tokens": 512,
                    "prompt_level": f"rendered_{rendering['prompt_tokens']}_tokens",
                    "decode_level": "forced_512_tokens",
                },
                "source": {
                    "source_item_id": prompt["prompt_id"],
                    "source_sha256": rendering["prompt_token_ids_sha256"],
                    "prompt_template_id": (
                        f"chat_template_sha256:{MODEL['chat_template_sha256']}"
                    ),
                    "license": DECODE_PROFILE["license"],
                    "contamination_note": (
                        "original prompt; rendered IDs are the run input"
                    ),
                    "prompt_token_ids": list(rendering["prompt_token_ids"]),
                },
                "grouping": {
                    "condition_id": DECODE_FAMILY_ID,
                    "block_id": "single_prompt",
                    "level_id": prompt["prompt_id"],
                    "prefix_group_id": None,
                },
                "output_policy": "fixed_budget_exact",
                "tags": ["d166-real-prompt", "enable-thinking=false"],
            }
        ],
    }
    SuiteManifest.from_mapping(manifest)
    return manifest


def decode_workload_candidate() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.d117_decode_workload_candidate.v1",
        "draft_status": emitted_draft_status(),
        "profile": {
            "path": DECODE_WORKLOAD_REL.as_posix(),
            "profile_id": DECODE_PROFILE["profile_id"],
            "prompt_set_sha256": DECODE_PROFILE["prompt_set_sha256"],
            "license": DECODE_PROFILE["license"],
        },
        "rendering_policy": {
            "messages": [{"role": "user", "content": "<profile prompt text>"}],
            "add_generation_prompt": True,
            "chat_template_applied": True,
            "enable_thinking": "false",
            "output_policy": "greedy_forced_512_suppress_eos",
        },
        "assignment": {
            "rule_id": "ruling-171a-floor-index-zero.v1",
            "rule": "prompt_index = 0",
            "same_prompt_for_all_floor_members": True,
            "prompt_count": 1,
        },
        "per_model": [
            {
                "model_id": MODEL_ID,
                "tokenizer_json_sha256": MODEL["tokenizer_json_sha256"],
                "chat_template_sha256": MODEL["chat_template_sha256"],
                "prompt_tokens": DECODE_RENDERING["prompt_tokens"],
                "prompts": [dict(DECODE_RENDERING)],
            }
        ],
    }


def configure_prefill_pin(path: Path) -> None:
    global P512_PROMPT_UTF8_SHA256, P512_SHARED_TOKENIZER_JSON_SHA256
    global P512_PROMPT_TOKEN_IDS_SHA256, P512_PROMPT_TEXT
    global PREFILL_PIN_SOURCE_PATH, PREFILL_PIN_SOURCE_RAW
    global PREFILL_LADDER_SOURCE_PATH, PREFILL_LADDER_SOURCE_REL
    global PREFILL_LADDER_SOURCE_RAW, PREFILL_SELECTION_SOURCE_PATH
    global PREFILL_SELECTION_SOURCE_REL, PREFILL_SELECTION_SOURCE_RAW

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"prefill_prompt_pin_invalid: duplicate key {key!r}")
            result[key] = value
        return result

    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"prefill_prompt_pin_invalid: {exc}") from exc
    required = {
        "schema_version", "selection_authority", "ladder_prompt_tokens",
        "min_small_model_members_per_rung", "min_overlapping_power_interval_count",
        "min_phase_samples_pinned", "sample_count_margin_floor",
        "selection_expression", "g2a_record_sha256", "selection_record",
        "prompt_ladder", "panel_sha256", "exhausted_ladder_branch",
        "prefill_length", "tokenizer_json_sha256", "special_token_policy",
        "prompt_text", "prompt_text_utf8_sha256", "prompt_token_ids",
        "prompt_token_ids_sha256", "prompt_tokens", "repeat_count",
        "closing_sentence", "generation_method",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("prefill_prompt_pin_invalid: closed schema mismatch")
    if (
        value["schema_version"] != "joulewise.prefill_prompt_pin.v2"
        or value["ladder_prompt_tokens"] != PREFILL_LADDER_PROMPT_TOKENS
        or value["min_small_model_members_per_rung"]
        != PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG
        or value["min_overlapping_power_interval_count"]
        != PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT
        or value["min_phase_samples_pinned"] != PREFILL_MIN_PHASE_SAMPLES_PINNED
        or value["min_phase_samples_pinned"] != REDUCER_MIN_PHASE_SAMPLES
        or value["sample_count_margin_floor"] != PREFILL_SAMPLE_COUNT_MARGIN_FLOOR
        or value["min_overlapping_power_interval_count"]
        - value["min_phase_samples_pinned"]
        != value["sample_count_margin_floor"]
        or value["selection_expression"] != PREFILL_SELECTION_EXPRESSION
        or value["exhausted_ladder_branch"] != PREFILL_EXHAUSTED_LADDER_BRANCH
        or value["prefill_length"] != PREFILL_LENGTH
        or value["prompt_tokens"] != PREFILL_LENGTH
        or value["tokenizer_json_sha256"] != MODEL["tokenizer_json_sha256"]
        or value["panel_sha256"] != PANEL_SHA256
        or value["special_token_policy"] != "add_special_tokens=true"
    ):
        raise ValueError("prefill_prompt_pin_invalid: ruled constants mismatch")
    authority = value["selection_authority"]
    if (
        not isinstance(authority, dict)
        or set(authority) != {"g2a_record", "ruling_trace_paths"}
        or authority.get("ruling_trace_paths") != list(PREFILL_RULING_TRACE_PATHS)
        or not isinstance(authority.get("g2a_record"), dict)
        or set(authority["g2a_record"]) != {"record_id", "path"}
        or any(
            not isinstance(authority["g2a_record"][key], str)
            or not authority["g2a_record"][key].strip()
            for key in ("record_id", "path")
        )
        or authority["g2a_record"].get("record_id")
        != f"sha256:{value['g2a_record_sha256']}"
    ):
        raise ValueError("prefill_prompt_pin_invalid: selection_authority")
    if (
        not isinstance(value["g2a_record_sha256"], str)
        or len(value["g2a_record_sha256"]) != 64
        or any(
            character not in "0123456789abcdef"
            for character in value["g2a_record_sha256"]
        )
    ):
        raise ValueError("prefill_prompt_pin_invalid: g2a_record_sha256")

    def bound_file(field: str) -> tuple[Path, Path, bytes]:
        ref = value[field]
        if (
            not isinstance(ref, dict)
            or set(ref) != {"path", "sha256"}
            or not isinstance(ref["path"], str)
            or not ref["path"].strip()
            or not isinstance(ref["sha256"], str)
        ):
            raise ValueError(f"prefill_prompt_pin_invalid: {field}")
        relative = Path(ref["path"])
        if relative.is_absolute():
            raise ValueError(f"prefill_prompt_pin_invalid: {field}.path")
        target = (path.parent / relative).resolve()
        try:
            target.relative_to(path.parent.resolve())
        except ValueError as exc:
            raise ValueError(f"prefill_prompt_pin_invalid: {field}.path") from exc
        try:
            bound_raw = target.read_bytes()
        except OSError as exc:
            raise ValueError(f"{field}_missing") from exc
        if sha256_bytes(bound_raw) != ref["sha256"]:
            raise ValueError(f"{field}_sha256_mismatch")
        return relative, target, bound_raw

    selection_rel, selection_path, selection_raw = bound_file("selection_record")
    ladder_rel, ladder_path, ladder_raw = bound_file("prompt_ladder")
    if sha256_bytes(selection_raw) != value["g2a_record_sha256"]:
        raise ValueError("selection_record_sha256_mismatch")
    try:
        selection = json.loads(
            selection_raw,
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(
            f"prefill_prompt_pin_invalid: selection_record: {exc}"
        ) from exc
    selection_keys = {
        "collection_prefill_tokens",
        "qualifying_prefill_tokens",
        "refusal",
        "rule",
        "schema_version",
        "selected_prefill_tokens",
        "status",
        "summary_sha256",
    }
    if not isinstance(selection, dict) or set(selection) != selection_keys:
        raise ValueError("selection_record_closed_schema_mismatch")
    if selection.get("schema_version") != "joulewise.g2a_prefill_selection.v1":
        raise ValueError("selection_record_schema_version_invalid")
    if selection.get("status") == "refused":
        raise ValueError("selection_record_refused_not_supported")
    if selection.get("status") != "selected":
        raise ValueError("selection_record_status_invalid")
    if selection.get("collection_prefill_tokens") != PREFILL_LENGTH:
        raise ValueError("selection_record_collection_prefill_tokens_mismatch")
    if (
        selection.get("selected_prefill_tokens") != PREFILL_LENGTH
        or selection.get("refusal") is not None
    ):
        raise ValueError("selection_record_selected_branch_malformed")
    ladder = json.loads(
        ladder_raw,
        object_pairs_hook=reject_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if (
        not isinstance(ladder, dict)
        or set(ladder)
        != {
            "schema_version",
            "prompt_sentence",
            "tokenizer_json_sha256",
            "panel_thinking_policy",
            "rendering_mode",
            "chat_template_applied",
            "thinking_policy",
            "rungs",
        }
        or ladder.get("schema_version")
        != "joulewise.g2a_prefill_prompt_ladder.v1"
        or ladder.get("prompt_sentence") != PROMPT_SENTENCE
        or ladder.get("tokenizer_json_sha256") != MODEL["tokenizer_json_sha256"]
        or ladder.get("panel_thinking_policy")
        != {"enable_thinking": "false", "panel_sha256": PANEL_SHA256}
        or not isinstance(ladder.get("rungs"), list)
    ):
        raise ValueError("prefill_prompt_pin_invalid: prompt_ladder")
    rungs = ladder["rungs"]
    if len(rungs) != len(PREFILL_LADDER_PROMPT_TOKENS):
        raise ValueError("prompt_ladder_expected_four_rungs")
    rungs_by_length: dict[int, dict[str, Any]] = {}
    for row in rungs:
        length = row.get("prefill_tokens") if isinstance(row, dict) else None
        if (
            isinstance(length, bool)
            or not isinstance(length, int)
            or length not in PREFILL_LADDER_PROMPT_TOKENS
            or length in rungs_by_length
        ):
            raise ValueError("prompt_ladder_rung_length_invalid_or_duplicate")
        rungs_by_length[length] = row
    if tuple(sorted(rungs_by_length)) != tuple(PREFILL_LADDER_PROMPT_TOKENS):
        raise ValueError("prompt_ladder_lengths_mismatch")
    rung = rungs_by_length[PREFILL_LENGTH]
    ids = value["prompt_token_ids"]
    text = value["prompt_text"]
    if (
        rung is None
        or isinstance(rung.get("prefill_tokens"), bool)
        or not isinstance(rung.get("prefill_tokens"), int)
        or isinstance(rung.get("repeat_count"), bool)
        or not isinstance(rung.get("repeat_count"), int)
        or rung["repeat_count"] <= 0
        or not isinstance(text, str)
        or not isinstance(ids, list)
        or len(ids) != PREFILL_LENGTH
        or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in ids)
        or sha256_bytes(text.encode("utf-8")) != value["prompt_text_utf8_sha256"]
        or prompt_token_ids_sha256(ids) != value["prompt_token_ids_sha256"]
    ):
        raise ValueError("prefill_prompt_pin_invalid: prompt realization")
    rung_map = {
        "prompt_text": "prompt_text",
        "prompt_text_utf8_sha256": "prompt_text_utf8_sha256",
        "prompt_token_ids": "prompt_token_ids",
        "prompt_token_ids_sha256": "prompt_token_ids_sha256",
        "prompt_tokens": "prefill_tokens",
        "repeat_count": "repeat_count",
        "closing_sentence": "closing_sentence",
        "generation_method": "generation_method",
    }
    if any(value[left] != rung.get(right) for left, right in rung_map.items()):
        raise ValueError("prefill_prompt_pin_ladder_rung_mismatch")
    expected_text = " ".join(
        [PROMPT_SENTENCE] * value["repeat_count"] + [value["closing_sentence"]]
    )
    expected_method = (
        f"{value['repeat_count']} x '{PROMPT_SENTENCE}' + "
        f"'{value['closing_sentence']}' under tokenizer "
        f"sha256:{value['tokenizer_json_sha256']}"
    )
    if text != expected_text or value["generation_method"] != expected_method:
        raise ValueError("prefill_prompt_pin_prompt_construction_mismatch")
    PREFILL_PIN_SOURCE_PATH = path
    PREFILL_PIN_SOURCE_RAW = raw
    PREFILL_LADDER_SOURCE_PATH = ladder_path
    PREFILL_LADDER_SOURCE_REL = ladder_rel
    PREFILL_LADDER_SOURCE_RAW = ladder_raw
    PREFILL_SELECTION_SOURCE_PATH = selection_path
    PREFILL_SELECTION_SOURCE_REL = selection_rel
    PREFILL_SELECTION_SOURCE_RAW = selection_raw
    P512_PROMPT_UTF8_SHA256 = value["prompt_text_utf8_sha256"]
    P512_SHARED_TOKENIZER_JSON_SHA256 = value["tokenizer_json_sha256"]
    P512_PROMPT_TOKEN_IDS_SHA256 = value["prompt_token_ids_sha256"]
    P512_PROMPT_TEXT = text


def load_and_verify_families() -> tuple[
    dict[str, Any], bytes, dict[str, Any], bytes, dict[str, Any], bytes
]:
    global DECODE_FAMILY_DOMAIN_SHA256
    global PREFILL_FAMILY_DOMAIN_SHA256
    global P512_FAMILY_DOMAIN_SHA256

    decode = decode_family_definition()
    errors = validate_condition_family_definition(decode)
    if errors:
        raise ValueError(f"decode condition-family definition is invalid: {errors[0]}")
    decode_raw = render_json(decode)
    DECODE_FAMILY_DOMAIN_SHA256 = canonical_domain_sha256(
        CONDITION_FAMILY_DOMAIN, decode
    )

    prefill = prefill_family_definition()
    errors = validate_condition_family_definition(prefill)
    if errors:
        raise ValueError(f"prefill condition-family definition is invalid: {errors[0]}")
    prefill_raw = render_json(prefill)
    PREFILL_FAMILY_DOMAIN_SHA256 = canonical_domain_sha256(
        CONDITION_FAMILY_DOMAIN, prefill
    )
    p512 = p512_family_definition()
    errors = validate_condition_family_definition(p512)
    if errors:
        raise ValueError(f"p512 condition-family definition is invalid: {errors[0]}")
    p512_raw = render_json(p512)
    P512_FAMILY_DOMAIN_SHA256 = canonical_domain_sha256(
        CONDITION_FAMILY_DOMAIN, p512
    )
    return decode, decode_raw, prefill, prefill_raw, p512, p512_raw


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
        run_id = f"d117fq31p7-df-ph-decode-abs-r{rep:02d}"
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
        block_id = f"d117-df-cmp-abba-ph-decode-qwen3-1p7b-b{block:02d}"
        members: dict[str, str] = {}
        for sequence_index, (label, position) in enumerate(positions, start=1):
            run_id = (
                f"d117fq31p7-df-cmp-abba-ph-decode-b{block:02d}-"
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

    p512_absolute_ids: list[str] = []
    for rep in range(1, N + 1):
        run_id = f"d117fq31p7-df-ph-prefill-p512-abs-r{rep:02d}"
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
            "condition_family_id": P512_FAMILY_ID,
            "collection_tags": [f"rep{rep}"],
        }
        stages[3]["runs"].append(run)
        p512_absolute_ids.append(run_id)

    p512_blocks: list[dict[str, Any]] = []
    for block in range(1, N + 1):
        block_id = (
            f"d117-df-cmp-abba-ph-prefill-p512-qwen3-1p7b-b{block:02d}"
        )
        members: dict[str, str] = {}
        for sequence_index, (label, position) in enumerate(positions, start=1):
            run_id = (
                f"d117fq31p7-df-cmp-abba-ph-prefill-p512-b{block:02d}-"
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
                "condition_family_id": P512_FAMILY_ID,
                "collection_tags": [
                    f"rep{block}",
                    f"calibration-abba-block-id={block_id}",
                    f"calibration-abba-label={label}",
                    f"calibration-abba-sequence-index={sequence_index}",
                ],
            }
            stages[4 if block <= 5 else 5]["runs"].append(run)
            members[position] = run_id
        p512_blocks.append(
            {
                "block_id": block_id,
                "executed_labels": ["A", "B", "B", "A"],
                "members": members,
            }
        )
    return stages, absolute_ids, blocks, p512_absolute_ids, p512_blocks


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
    run: dict[str, Any], plan_sha256: str, p512_prompt_text: str
) -> dict[str, Any]:
    family_id = run.get("condition_family_id", DECODE_FAMILY_ID)
    workload = (
        {
            "name": P512_WORKLOAD_NAME,
            "repetitions": 1,
            "warmup_runs": 1,
            "output_tokens": 512,
            "prompt_text": p512_prompt_text,
            "prompt_token_expectation": {
                "schema_version": "joulewise.prompt_token_expectation.v1",
                "token_hash_domain": "joulewise.prompt_token_ids.v1",
                "token_count": PREFILL_LENGTH,
                "token_ids_sha256": P512_PROMPT_TOKEN_IDS_SHA256,
            },
        }
        if family_id == P512_FAMILY_ID
        else {
            "name": WORKLOAD["name"],
            "repetitions": 1,
            "warmup_runs": 1,
            "output_tokens": 512,
            "suite_manifest_ref": DECODE_SUITE_REL.as_posix(),
            "suite_manifest_sha256": suite_manifest_sha256(
                decode_suite_manifest()
            ),
        }
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
        "model_tag": MODEL_TAG,
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
            "stage_id": "alpha-science-prefill-p512-absolute",
            "kind": "campaign_collection",
            "expected_count": 10,
            "input": stage_manifest_refs["04_phase_prefill_p512_absolute"],
            "launch": campaign_launch(
                "alpha-science-prefill-p512-absolute",
                PACK_REL / "04_phase_prefill_p512_absolute",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-science-prefill-p512-abba-01-05",
            "kind": "campaign_collection",
            "expected_count": 20,
            "input": stage_manifest_refs["05_phase_prefill_p512_abba_blocks_01_05"],
            "launch": campaign_launch(
                "alpha-science-prefill-p512-abba-01-05",
                PACK_REL / "05_phase_prefill_p512_abba_blocks_01_05",
                "claim_runs_root",
            ),
        },
        {
            "stage_id": "alpha-science-prefill-p512-abba-06-10",
            "kind": "campaign_collection",
            "expected_count": 20,
            "input": stage_manifest_refs["06_phase_prefill_p512_abba_blocks_06_10"],
            "launch": campaign_launch(
                "alpha-science-prefill-p512-abba-06-10",
                PACK_REL / "06_phase_prefill_p512_abba_blocks_06_10",
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
            "acceptance_id": acceptance_pin()["acceptance_id"],
            "path": acceptance_pin()["rel"].as_posix(),
            "artifact_sha256": acceptance_pin()["artifact_sha256"],
            "derivation_sha256": acceptance_pin()["derivation_sha256"],
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
        },
        "allowance_rule": acceptance_allowance_rule(
            acceptance_pin()["acceptance_id"]
        ),
        "allowance_embedding_count": 1,
        "component_composition": "componentwise_max_never_sum.v1",
    }


def build_extraction_spec(
    decode_definition: dict[str, Any],
    prefill_definition: dict[str, Any],
    p512_definition: dict[str, Any],
    absolute_ids: list[str],
    blocks: list[dict[str, Any]],
    p512_absolute_ids: list[str],
    p512_blocks: list[dict[str, Any]],
    config_rows: list[dict[str, str]],
    order_manifest_sha256: str,
) -> dict[str, Any]:
    config_by_id = {row["bundle_id"]: row["config_sha256"] for row in config_rows}
    comparative_ids = [
        block["members"][position]
        for block in blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    p512_comparative_ids = [
        block["members"][position]
        for block in p512_blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    order_binding = {
        "path": (PACK_REL / "order_manifest.json").as_posix(),
        "manifest_id": "d117-floor-qwen3-1p7b-v5-order-v1",
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
            "d117-df-ph-decode-qwen3-1p7b-absolute",
            "phase_energy_j.decode",
            ["phase", "decode"],
            DECODE_FAMILY_ID,
            decode_definition,
            DECODE_FAMILY_DOMAIN_SHA256,
        ),
        comparative_cell(
            "d117-df-cmp-abba-ph-decode-qwen3-1p7b",
            "phase_energy_j.decode",
            ["phase", "decode"],
            DECODE_FAMILY_ID,
            decode_definition,
            DECODE_FAMILY_DOMAIN_SHA256,
        ),
        absolute_cell(
            "d117-df-ph-prefill-p42-qwen3-1p7b-absolute",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            PREFILL_FAMILY_ID,
            prefill_definition,
            PREFILL_FAMILY_DOMAIN_SHA256,
        ),
        comparative_cell(
            "d117-df-cmp-abba-ph-prefill-p42-qwen3-1p7b",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            PREFILL_FAMILY_ID,
            prefill_definition,
            PREFILL_FAMILY_DOMAIN_SHA256,
        ),
        absolute_cell(
            "d117-df-ph-prefill-p512-qwen3-1p7b-absolute",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            P512_FAMILY_ID,
            p512_definition,
            P512_FAMILY_DOMAIN_SHA256,
            p512_absolute_ids,
        ),
        comparative_cell(
            "d117-df-cmp-abba-ph-prefill-p512-qwen3-1p7b",
            "phase_energy_j.prefill",
            ["phase", "prefill"],
            P512_FAMILY_ID,
            p512_definition,
            P512_FAMILY_DOMAIN_SHA256,
            p512_blocks,
            p512_comparative_ids,
        ),
    ]
    decode_ids = [*absolute_ids, *comparative_ids]
    p512_ids = [*p512_absolute_ids, *p512_comparative_ids]

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
            "cell_id": "d117-reported-mean-ph-decode-qwen3-1p7b",
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
            "cell_id": "d117-reported-mean-ph-prefill-p42-qwen3-1p7b",
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
            "cell_id": "d117-reported-mean-ph-prefill-p512-qwen3-1p7b",
            "metric": "phase_energy_j.prefill",
            "window_class": "phase",
            "target_precheck_path": ["phase", "prefill"],
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "expected_n": 50,
            "members": reported_members(p512_ids),
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
    p512_config_rows: list[dict[str, str]],
    decode_identity_config_inventory: list[dict[str, str]],
    p512_identity_config_inventory: list[dict[str, str]],
    p512_prompt_text: str,
) -> dict[str, Any]:
    config_rows = [*decode_config_rows, *p512_config_rows]
    config_set_sha256 = canonical_sha256(config_rows)
    decode_identity_workload = {
        "name": WORKLOAD["name"],
        "repetitions": 1,
        "warmup_runs": 1,
        "output_tokens": 512,
        "suite_manifest_ref": DECODE_SUITE_REL.as_posix(),
        "suite_manifest_sha256": suite_manifest_sha256(decode_suite_manifest()),
    }
    prefill_identity_workload = {
        "name": P512_WORKLOAD_NAME,
        "repetitions": 1,
        "warmup_runs": 1,
        "output_tokens": 512,
        "prompt_text": p512_prompt_text,
        "prompt_token_expectation": {
            "schema_version": "joulewise.prompt_token_expectation.v1",
            "token_hash_domain": "joulewise.prompt_token_ids.v1",
            "token_count": PREFILL_LENGTH,
            "token_ids_sha256": P512_PROMPT_TOKEN_IDS_SHA256,
        },
    }
    roles = [
        {
            "role": "decode",
            "artifact_cell_id": "d117-qwen3-1p7b-decode-floor-v5",
            "transport_group_id": "tg-d117-qwen3-1p7b-decode-v5",
            "metric": "phase_energy_j.decode",
            "target_precheck_path": ["phase", "decode"],
            "condition_family_id": DECODE_FAMILY_ID,
            "absolute_calibration_cell_id": "d117-df-ph-decode-qwen3-1p7b-absolute",
            "comparative_calibration_cell_id": "d117-df-cmp-abba-ph-decode-qwen3-1p7b",
            "allowed_consumer_families": ["sw-decode-a-qwen3-1p7b"],
            "members": decode_config_rows,
        },
        {
            "role": "prefill",
            "artifact_cell_id": "d117-qwen3-1p7b-prefill-p42-floor-v5",
            "transport_group_id": "tg-d117-qwen3-1p7b-prefill-p42-v5",
            "metric": "phase_energy_j.prefill",
            "target_precheck_path": ["phase", "prefill"],
            "condition_family_id": PREFILL_FAMILY_ID,
            "absolute_calibration_cell_id": "d117-df-ph-prefill-p42-qwen3-1p7b-absolute",
            "comparative_calibration_cell_id": "d117-df-cmp-abba-ph-prefill-p42-qwen3-1p7b",
            "allowed_consumer_families": ["df-ph-prefill-p42-qwen3-1p7b"],
            "members": decode_config_rows,
        },
        {
            "role": "prefill_p512",
            "artifact_cell_id": "d117-qwen3-1p7b-prefill-p512-floor-v5",
            "transport_group_id": "tg-d117-qwen3-1p7b-prefill-p512-v5",
            "metric": "phase_energy_j.prefill",
            "target_precheck_path": ["phase", "prefill"],
            "condition_family_id": P512_FAMILY_ID,
            "absolute_calibration_cell_id": "d117-df-ph-prefill-p512-qwen3-1p7b-absolute",
            "comparative_calibration_cell_id": "d117-df-cmp-abba-ph-prefill-p512-qwen3-1p7b",
            "allowed_consumer_families": ["sw-prefill-p512-a-qwen3-1p7b"],
            "members": p512_config_rows,
        },
    ]
    return {
        "schema_version": "joulewise.d117_floor_producer_contract.v1",
        # The frozen plan test pins the producer-contract artifact SHA.
        "draft_status": emitted_draft_status(),
        "plan_set_id": "plan-set-d117-qwen3-1p7b-8b-phase-floor-v5",
        "aggregate_artifact_id": "d117-qwen3-phase-floor-set-v5",
        "producer_index": PRODUCER_INDEX,
        "component_artifact_id": "d117-qwen3-1p7b-phase-floor-component-v5",
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
            "workload_profile": decode_identity_workload,
            "workload_profiles": {
                "decode_and_prefill_p42": decode_identity_workload,
                "prefill_p512": {
                    "name": P512_WORKLOAD_NAME,
                    "repetitions": 1,
                    "warmup_runs": 1,
                    "output_tokens": 512,
                    "prompt_text_utf8_sha256": P512_PROMPT_UTF8_SHA256,
                },
            },
        },
        "order_manifest": {
            "path": (PACK_REL / "order_manifest.json").as_posix(),
            "manifest_id": "d117-floor-qwen3-1p7b-v5-order-v1",
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
                            "arm": CONSUMER_ARM,
                            "family": "sw-decode-a-qwen3-1p7b",
                            "measurement_arm": "decode",
                        },
                        {
                            "arm": CONSUMER_ARM,
                            "family": PREFILL_FAMILY_ID,
                            "measurement_arm": "prefill_p42",
                        },
                    ],
                    "declared_identity": {
                        "hardware_target": HARDWARE["id"],
                        "runtime_backend": HARDWARE["runtime_backend"],
                        "telemetry_backend": HARDWARE["telemetry_backend"],
                        "model_name": MODEL["name"],
                        "model_source": MODEL["source"],
                        "model_revision": MODEL["revision"],
                        "quantization": dict(QUANTIZATION),
                        "workload_profile": {
                            **decode_identity_workload,
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
                    "identity_unit_id": "alpha/prefill_p512",
                    "producer_plan_reference": {
                        "plan_id": PLAN_ID,
                        "path": emitted_plan_reference(),
                    },
                    "consumer_bindings": [
                        {
                            "arm": CONSUMER_ARM,
                            "family": "sw-prefill-p512-a-qwen3-1p7b",
                            "measurement_arm": "prefill_p512",
                        }
                    ],
                    "declared_identity": {
                        "hardware_target": HARDWARE["id"],
                        "runtime_backend": HARDWARE["runtime_backend"],
                        "telemetry_backend": HARDWARE["telemetry_backend"],
                        "model_name": MODEL["name"],
                        "model_source": MODEL["source"],
                        "model_revision": MODEL["revision"],
                        "quantization": dict(QUANTIZATION),
                        "workload_profile": {
                            **prefill_identity_workload,
                            "prompt_tokens": None,
                            "dataset_ref": None,
                        },
                    },
                    "config_inventory": p512_identity_config_inventory,
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
            "# D-117 Qwen3-1.7B floor campaign — status governed by the "
            "D-134 freeze receipt\n\n"
            f"{identity_statement}"
            "This description does not carry freeze status. The committed D-134 "
            "freeze receipt and its plan-tree attachment are authoritative for "
            "this pack's frozen state; the receipt pins `calibration_plan.json` "
            "by SHA, so this text and every serialized `draft_status` field stay "
            "exactly as generated on both sides of the freeze. An external "
            "unexpired PASS/GO arm receipt is required before launch.\n\n"
            "This pack pre-registers the alpha window's 10 absolute decode members, "
            "ten null A/B/B/A blocks (40 members), and a zero-member prefill metric "
            "rider over the same 50 physical bundles. It also carries a dedicated "
            "D-166 p512 prefill domain with 10 absolute members and ten null A/B/B/A "
            "blocks (50 additional members), plus three D-123 reported phase-energy "
            "means. The p512 workload name remains `df_ph_prefill_p512_candidate` "
            "for byte identity with the gamma consumer even though Q1 has frozen its "
            "prompt.\n\n"
            "Its receipt oracle is replay-derived from "
            f"`{oracle['source']['module']}`: {oracle['receipt_count']} physical "
            f"receipts for {oracle['logical_operation_count']} logical operations per "
            "finalized pre/post bracket session. Actual receipt bytes and the absolute "
            "terminal sequence remain arm-time evidence. Arm-time identities require "
            "U11 projection, "
            "and lead review must complete before any later release step.\n\n"
            f"{successor_regeneration_rule()}\n\n"
            "Generate or verify with:\n\n"
            "```text\n"
            "python3 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py "
            "--prefill-prompt-pin /path/to/issued/prefill-prompt-pin.json\n"
            "python3 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check\n"
            "```\n\n"
            "Integrity SHA-256 values in this pack detect drift; they do not mark "
            "release.\n"
        )
        return thread_generation_identity(content).encode("utf-8")
    content = (
        "# D-117 Qwen3-1.7B floor campaign — unfrozen draft\n\n"
        f"{identity_statement}"
        "This pack pre-registers the alpha window's 10 absolute decode members, "
        "ten null A/B/B/A blocks (40 members), and a zero-member prefill metric "
        "rider over the same 50 physical bundles. It also carries a dedicated "
        "D-166 p512 prefill domain with 10 absolute members and ten null A/B/B/A "
        "blocks (50 additional members), plus three D-123 reported phase-energy "
        "means. The p512 workload name remains `df_ph_prefill_p512_candidate` "
        "for byte identity with the gamma consumer even though Q1 has frozen its "
        "prompt.\n\n"
        "The pack is not armable. Its receipt oracle is replay-derived from "
        f"`{oracle['source']['module']}`: {oracle['receipt_count']} physical "
        f"receipts for {oracle['logical_operation_count']} logical operations per "
        "finalized pre/post bracket session. Actual receipt bytes and the absolute "
        "terminal sequence remain arm-time evidence. Arm-time identities require "
        "U11 projection, "
        "and lead review must complete before any later release step.\n\n"
        f"{successor_regeneration_rule()}\n\n"
        "Generate or verify with:\n\n"
        "```text\n"
        "python3 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py "
        "--prefill-prompt-pin /path/to/issued/prefill-prompt-pin.json\n"
        "python3 configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check\n"
        "```\n\n"
            "Integrity SHA-256 values in this draft detect drift; they do not mark release.\n"
    )
    return thread_generation_identity(content).encode("utf-8")


def generate(
    output_root: Path,
    identity: GenerationIdentity | None = None,
) -> tuple[int, str, str]:
    load_model_inputs()
    if PREFILL_PIN_SOURCE_PATH is None:
        raise ValueError(
            "prefill_prompt_pin_unresolved: supply the issued G2-a pin; "
            "no selection evidence is synthesized by this generator"
        )
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
        p512_definition,
        p512_raw,
    ) = load_and_verify_families()
    p512_prompt_text = P512_PROMPT_TEXT
    for path, expected in (
        (POLICY_REL, POLICY_SHA256),
        (acceptance_pin()["rel"], acceptance_pin()["artifact_sha256"]),
        (LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256),
        (NEG8_SETTLED_REL, NEG8_SETTLED_SHA256),
    ):
        if sha256_file(REPO_ROOT / path) != expected:
            raise ValueError(f"pinned input drifted: {path.as_posix()}")

    write_bytes(output_root, PACK_REL / "generate_configs.py", source_raw)
    write_bytes(output_root, PACK_REL / "README.md", readme_bytes())
    decode_suite_raw = render_json(decode_suite_manifest())
    write_bytes(output_root, DECODE_SUITE_REL, decode_suite_raw)
    decode_workload_candidate_raw = render_json(decode_workload_candidate())
    write_bytes(
        output_root,
        DECODE_WORKLOAD_CANDIDATE_REL,
        decode_workload_candidate_raw,
    )
    write_bytes(output_root, PREFILL_PIN_REL, PREFILL_PIN_SOURCE_RAW)
    assert PREFILL_LADDER_SOURCE_PATH is not None
    assert PREFILL_LADDER_SOURCE_REL is not None
    assert PREFILL_SELECTION_SOURCE_PATH is not None
    assert PREFILL_SELECTION_SOURCE_REL is not None
    write_bytes(
        output_root,
        PREFILL_PIN_REL.parent / PREFILL_LADDER_SOURCE_REL,
        PREFILL_LADDER_SOURCE_RAW,
    )
    write_bytes(
        output_root,
        PREFILL_PIN_REL.parent / PREFILL_SELECTION_SOURCE_REL,
        PREFILL_SELECTION_SOURCE_RAW,
    )
    write_bytes(output_root, DECODE_FAMILY_REL, decode_raw)
    write_bytes(output_root, PREFILL_FAMILY_REL, prefill_raw)
    write_bytes(output_root, P512_FAMILY_REL, p512_raw)

    stages, absolute_ids, blocks, p512_absolute_ids, p512_blocks = build_assembly()
    decode_ids = absolute_ids + [
        block["members"][position]
        for block in blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    p512_ids = p512_absolute_ids + [
        block["members"][position]
        for block in p512_blocks
        for position in ("A1", "B1", "B2", "A2")
    ]
    reported_cells = [
        {
            "cell_id": "d117-reported-mean-ph-decode-qwen3-1p7b",
            "metric": "phase_energy_j.decode",
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "ordered_bundle_ids": decode_ids,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p42-qwen3-1p7b",
            "metric": "phase_energy_j.prefill",
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "ordered_bundle_ids": decode_ids,
        },
        {
            "cell_id": "d117-reported-mean-ph-prefill-p512-qwen3-1p7b",
            "metric": "phase_energy_j.prefill",
            "measurand": "gross_phase_energy_j",
            "reducer": "arithmetic_mean_over_fixed_member_universe.v1",
            "ordered_bundle_ids": p512_ids,
        },
    ]
    canonical_blocks = calibration_plan_blocks(blocks)
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
        "authorities": [
            "D-116", "D-117", "D-123", "D-124", "D-139",
            "D-164", "D-165", "D-166", "ruling-171a",
        ],
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
            "prefill_p512_condition_family_id": P512_FAMILY_ID,
            "prefill_p512_condition_family_sha256": P512_FAMILY_DOMAIN_SHA256,
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
                "cell_id": "d117-df-ph-decode-qwen3-1p7b-absolute",
                "kind": "absolute",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": "d117-df-cmp-abba-ph-decode-qwen3-1p7b",
                "kind": "comparative_abba",
                "metric": "phase_energy_j.decode",
                "condition_family_id": DECODE_FAMILY_ID,
                "ordered_blocks": canonical_blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
                "floor_estimator_registration": floor_estimator_registration(),
            },
            {
                "cell_id": "d117-df-ph-prefill-p42-qwen3-1p7b-absolute",
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_bundle_ids": absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": "d117-df-cmp-abba-ph-prefill-p42-qwen3-1p7b",
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": PREFILL_FAMILY_ID,
                "ordered_blocks": canonical_blocks,
                "estimator": COMMON_MODE_ESTIMATOR_ID,
                "floor_estimator_registration": floor_estimator_registration(),
            },
            {
                "cell_id": "d117-df-ph-prefill-p512-qwen3-1p7b-absolute",
                "kind": "absolute",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": P512_FAMILY_ID,
                "ordered_bundle_ids": p512_absolute_ids,
                "estimator": "d054_false_effect_guard.v1",
            },
            {
                "cell_id": "d117-df-cmp-abba-ph-prefill-p512-qwen3-1p7b",
                "kind": "comparative_abba",
                "metric": "phase_energy_j.prefill",
                "condition_family_id": P512_FAMILY_ID,
                "ordered_blocks": calibration_plan_blocks(p512_blocks),
                "estimator": COMMON_MODE_ESTIMATOR_ID,
                "floor_estimator_registration": floor_estimator_registration(),
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
            config_raw = write_json(
                output_root,
                config_rel,
                config_for(run, plan_sha256, p512_prompt_text),
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
        manifest_id = f"d117-floor-qwen3-1p7b-v5-{stage_id.replace('_', '-')}-order-v1"
        stage_manifest = {
            "schema_version": ORDER_SCHEMA,
            # The frozen plan-tree manifest reference pins these bytes by SHA.
            "draft_status": emitted_draft_status(),
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
        "draft_status": emitted_draft_status(),
        "manifest_id": "d117-floor-qwen3-1p7b-v5-order-v1",
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
        p512_definition,
        absolute_ids,
        blocks,
        p512_absolute_ids,
        p512_blocks,
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
        p512_prompt_text,
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
        "draft_status": emitted_draft_status(),
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
                "acceptance_id": acceptance_pin()["acceptance_id"],
                "path": acceptance_pin()["rel"].as_posix(),
                "artifact_sha256": acceptance_pin()["artifact_sha256"],
                "derivation_sha256": acceptance_pin()["derivation_sha256"],
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
                "byte_sha256": sha256_bytes(decode_raw),
                "condition_family_id": DECODE_FAMILY_ID,
                "domain_sha256": DECODE_FAMILY_DOMAIN_SHA256,
            },
            {
                "path": PREFILL_FAMILY_REL.as_posix(),
                "byte_sha256": sha256_bytes(prefill_raw),
                "condition_family_id": PREFILL_FAMILY_ID,
                "domain_sha256": PREFILL_FAMILY_DOMAIN_SHA256,
            },
            {
                "path": P512_FAMILY_REL.as_posix(),
                "byte_sha256": sha256_bytes(p512_raw),
                "condition_family_id": P512_FAMILY_ID,
                "domain_sha256": P512_FAMILY_DOMAIN_SHA256,
                "prompt_artifact_path": PREFILL_PIN_REL.as_posix(),
                "prompt_artifact_sha256": sha256_bytes(PREFILL_PIN_SOURCE_RAW),
                "prompt_text_utf8_sha256": P512_PROMPT_UTF8_SHA256,
                "shared_tokenizer_json_sha256": P512_SHARED_TOKENIZER_JSON_SHA256,
                "prompt_token_ids_sha256": P512_PROMPT_TOKEN_IDS_SHA256,
                "prompt_identity_ruling": "D-166 as amended; ruling 171a R-6",
                "token_id_sha256_pin_status": "full_sha256",
            },
        ],
        "science": science_rows,
        "stage_graph": graph,
        "external_inputs": {
            "manifests": list(external_inputs.values()),
            "artifacts": [
                {"path": NEG8_SETTLED_REL.as_posix(), "sha256": NEG8_SETTLED_SHA256},
                {
                    "path": PREFILL_PIN_REL.as_posix(),
                    "sha256": sha256_bytes(PREFILL_PIN_SOURCE_RAW),
                },
                {"path": PANEL_REL.as_posix(), "sha256": PANEL_SHA256},
                {"path": DECODE_WORKLOAD_REL.as_posix(), "sha256": DECODE_WORKLOAD_SHA256},
                {
                    "path": DECODE_SUITE_REL.as_posix(),
                    "sha256": sha256_bytes(decode_suite_raw),
                },
                {
                    "path": DECODE_WORKLOAD_CANDIDATE_REL.as_posix(),
                    "sha256": sha256_bytes(decode_workload_candidate_raw),
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
        "decode_workload": {
            "path": DECODE_WORKLOAD_CANDIDATE_REL.name,
            "sha256": sha256_bytes(decode_workload_candidate_raw),
            "assignment_rule_id": "ruling-171a-floor-index-zero.v1",
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
        Path("extraction_spec.json"),
        Path("decode_prompt_manifest.json"),
        Path("decode_workload_candidate.json"),
        Path("prefill_pin/prefill_prompt_pin.json"),
        Path("condition_families/condition_family_df_ph_decode.json"),
        Path("condition_families/condition_family_df_ph_prefill_p42_qwen3_1p7b.json"),
        Path("condition_families/condition_family_df_ph_prefill_p512_qwen3_1p7b.json"),
        Path("01_phase_decode_absolute/order_manifest.json"),
        Path("02_phase_decode_abba_blocks_01_05/order_manifest.json"),
        Path("03_phase_decode_abba_blocks_06_10/order_manifest.json"),
        Path("04_phase_prefill_p512_absolute/order_manifest.json"),
        Path("05_phase_prefill_p512_abba_blocks_01_05/order_manifest.json"),
        Path("06_phase_prefill_p512_abba_blocks_06_10/order_manifest.json"),
    ]
    if PREFILL_LADDER_SOURCE_REL is None or PREFILL_SELECTION_SOURCE_REL is None:
        raise ValueError("prefill_prompt_pin_unresolved")
    paths.extend(
        [
            Path("prefill_pin") / PREFILL_LADDER_SOURCE_REL,
            Path("prefill_pin") / PREFILL_SELECTION_SOURCE_REL,
        ]
    )
    paths.extend(
        Path(f"01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r{rep:02d}.json")
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
                f"{stage}/d117fq31p7-df-cmp-abba-ph-decode-b{block:02d}-{position}.json"
            )
            for position in ("a1", "b1", "b2", "a2")
        )
    paths.extend(
        Path(
            f"04_phase_prefill_p512_absolute/"
            f"d117fq31p7-df-ph-prefill-p512-abs-r{rep:02d}.json"
        )
        for rep in range(1, 11)
    )
    for block in range(1, 11):
        stage = (
            "05_phase_prefill_p512_abba_blocks_01_05"
            if block <= 5
            else "06_phase_prefill_p512_abba_blocks_06_10"
        )
        paths.extend(
            Path(
                f"{stage}/d117fq31p7-df-cmp-abba-ph-prefill-p512-"
                f"b{block:02d}-{position}.json"
            )
            for position in ("a1", "b1", "b2", "a2")
        )
    return paths


def validate_generation_output_inventory(identity: GenerationIdentity) -> set[Path]:
    pack_outputs = {identity.pack_rel / path for path in expected_pack_paths()}
    outputs = pack_outputs
    if len(pack_outputs) != len(expected_pack_paths()):
        raise ValueError("generation output inventory is not exactly contained")
    if any(
        identity.pack_rel not in path.parents
        for path in outputs
    ):
        raise ValueError("generation output inventory escapes the target allowlist")
    return outputs


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
        "--prefill-prompt-pin",
        type=Path,
        help=(
            "issued G2-a joulewise.prefill_prompt_pin.v2; defaults to the "
            "custodied copy inside an already-generated pack"
        ),
    )
    parser.add_argument(
        "--preserve-current-frozen-bytes",
        action=argparse.BooleanOptionalAction,
        default=PRESERVE_CURRENT_FROZEN_BYTES,
    )
    args = parser.parse_args()
    return args


def main() -> int:
    args = parse_args()
    pin_path = args.prefill_prompt_pin
    if pin_path is None:
        candidate_root = args.output_root.resolve() if args.output_root else REPO_ROOT
        candidate = candidate_root / PREFILL_PIN_REL
        if candidate.is_file():
            pin_path = candidate
    if pin_path is None:
        raise ValueError(
            "prefill_prompt_pin_unresolved: pass --prefill-prompt-pin with "
            "the issued G2-a pin"
        )
    configure_prefill_pin(pin_path.resolve())
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
