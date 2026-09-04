#!/usr/bin/env python3
"""Generate a model-panel-parameterized D-117 CONTRAST v5 pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_REL = Path("configs/campaigns/d117_contrast_v5")
PACK_REL = GENERATOR_REL
CALIBRATION_PLAN_REFERENCE = "calibration_plan.json"
CURRENT_FAMILY_SUFFIX = "_v5"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.detection_floor import (  # noqa: E402
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
    dominance_ratio,
    replay_common_mode_dominance,
    split_common_mode_block_width,
)
from joulewise.provenance import prompt_token_ids_sha256  # noqa: E402
from joulewise.reduce import MIN_PHASE_SAMPLES as REDUCER_MIN_PHASE_SAMPLES  # noqa: E402
from joulewise.floor_extraction import (  # noqa: E402
    _common_mode_window_is_strictly_noncollapsed,
    validate_condition_family_definition,
)
from joulewise.identity_pins import (  # noqa: E402
    IDENTITY_PIN_DERIVATION_CONTRACT,
    IDENTITY_PIN_PROJECTION_WORK_ORDER,
    validate_identity_pin_projection,
)
from joulewise.arm_readiness import (  # noqa: E402
    plan_arm_readiness_attachment,
)
from joulewise.analysis_manifest_v3 import (  # noqa: E402
    DOMINANCE_REPLAY_SIDECAR_ROLE,
    EXACT_STACK_RULE_ID,
    FINALIZATION_CONTRACT_ID,
    FINALIZED_BASENAME_SUFFIX,
    FINALIZED_NAMESPACE_RULE_ID,
    GOVERNED_TRANSPORT_RULE_ID,
    SEMANTICS_PROJECTION_RULE_ID,
    analysis_semantics_projection_v1,
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    prospective_finalization_required_attachments,
    validate_prospective_analysis_manifest_v3,
)
from joulewise.model_panel import ModelPanelError, load_model_panel  # noqa: E402
from joulewise.suite import (  # noqa: E402
    SUITE_SCHEMA_VERSION,
    SuiteManifest,
    suite_manifest_sha256,
)
from joulewise.workload_profile import (  # noqa: E402
    WorkloadProfileError,
    load_workload_profile,
)
from joulewise.receipt_oracle import (  # noqa: E402
    derive_bracket_session_receipt_oracle,
)


DETECTION_FLOOR_ARTIFACT_SCHEMA = "joulewise.detection_floor_artifact.v2"
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
PREFILL_RULING_TRACE_PATH = (
    "docs/process_traces/2026-08-30-prefill-margin-coldgate/"
    "03-MAGISTRATE-RATIFICATION.md"
)
PREFILL_RULING_TRACE_PATHS = (
    PREFILL_RULING_TRACE_PATH,
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
# The reference-cadence ratification field has the same freeze-variance defect
# the option-(d) treatment cures for ``draft_status``: the 2026-08-13 literal
# below asserts that ratification has NOT happened yet, and the event that
# makes it false is precisely the minting of this pack's own D-134 freeze
# receipt -- which pins calibration_plan.json (and, through the plan-tree
# sidecar, the tree and order manifest carrying it) by SHA, so the byte can
# never transition. Successor packs therefore serialize the ratification
# AUTHORITY, which is true on both sides of the receipt, instead of a
# ratification STATE that flips at it.
LEGACY_FREEZE_RATIFICATION = "PENDING-LEAD-RATIFICATION"
SUCCESSOR_FREEZE_RATIFICATION = (
    "as_generated_pre_d134_freeze; the committed D-134 freeze receipt and its "
    "plan-tree attachment are the ratification authority for this "
    "reference-cadence declaration"
)
CURRENT_FROZEN_RECEIPT_SHA256 = ""
CURRENT_FROZEN_GENERATOR_SHA256 = ""
PROMPT_STATUS = "PROPOSED-PENDING-LEAD-RATIFICATION"
EMPTY_STATUS = "EMPTY"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
TREE_SCHEMA = "joulewise.d117_plan_tree.v1"
PLAN_ID = ""
EVIDENCE_ROOT_ID = ""
CLAIM_ROOT_LEAF = ""
BOUND_ROOT_LEAF = ""
N_BLOCKS = 10
MEMBERS_PER_BLOCK = 4
MEMBERS_PER_ARM = N_BLOCKS * MEMBERS_PER_BLOCK
TOTAL_SCIENCE_MEMBERS = MEMBERS_PER_ARM * 2
ABBA_POSITIONS = (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2"))


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
    # preserve-mode replay reproduces those committed bytes verbatim. In an
    # EMITTED successor generator this branch is unreachable by design: its own
    # family ordinal is >= 2 and the downgrade guard in GenerationIdentity
    # refuses every target below it before any write.
    return DRAFT_STATUS


def emitted_freeze_ratification() -> str:
    """Return the reference-cadence ratification byte for the target generation.

    Same contract as ``emitted_draft_status``: the ordinal-1 literal is the one
    the 2026-08-13 freeze receipt pins and is never repaired, and successors get
    wording whose truth does not turn on their own D-134 receipt. Nothing in
    production reads this field -- it is advisor-visible description only (the
    only in-tree readers are this generator and
    ``tests/test_d117_decode_contrast_plan.py``) -- which is exactly why a
    stale-on-mint literal would survive unnoticed.
    """

    if active_generation().target_is_successor_family:
        return SUCCESSOR_FREEZE_RATIFICATION
    return LEGACY_FREEZE_RATIFICATION


PRESERVE_CURRENT_FROZEN_BYTES = False
PACK_STATUS = DRAFT_STATUS


class GenerationIdentity:
    def __init__(
        self,
        pack_id: str | None = None,
        family_suffix: str = CURRENT_FAMILY_SUFFIX,
        preserve_current_frozen_bytes: bool = PRESERVE_CURRENT_FROZEN_BYTES,
    ) -> None:
        self.pack_id = pack_id or PACK_REL.name
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
        attachment = plan_arm_readiness_attachment(
            REPO_ROOT / self.pack_rel, "GAMMA", REPO_ROOT
        )
        return freeze_aware_status(attachment["freeze_receipt"])


_ACTIVE_GENERATION: GenerationIdentity | None = None
_SUCCESSOR_IDENTITY_TOKENS: tuple[str, ...] = ()


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
    source = (REPO_ROOT / GENERATOR_REL / "generate_configs.py").read_text(
        encoding="utf-8"
    )
    identity = active_generation()
    if identity.target_is_current:
        return source.encode("utf-8")
    source = thread_generation_identity(source)
    current_declaration = f'CURRENT_FAMILY_SUFFIX = "{CURRENT_FAMILY_SUFFIX}"'
    successor_declaration = f'CURRENT_FAMILY_SUFFIX = "{identity.family_suffix}"'
    if source.count(current_declaration) != 1:
        raise ValueError("generator family-suffix declaration is not unique")
    return source.replace(current_declaration, successor_declaration).encode("utf-8")


def generation_arm_readiness_attachment() -> dict[str, Any]:
    return plan_arm_readiness_attachment(
        REPO_ROOT / active_generation().pack_rel,
        "GAMMA",
        REPO_ROOT,
    )


def preserved_generator_sha256() -> str:
    tree = json.loads(
        (REPO_ROOT / active_generation().pack_rel / "plan_tree.json").read_text(
            encoding="utf-8"
        )
    )
    return tree["generator"]["sha256"]


# D-138 dual-generation acceptance. The frozen `_v1` identity is permanently
# bound to the D-116 initial issuance; successor generations bind the reissue
# derived at the integrated estimator head.
PREDECESSOR_ACCEPTANCE = {
    "acceptance_id": "d079_calibration_acceptance_v2_n19",
    "rel": "configs/calibration/calibration_acceptance_d079_v2.json",
    "artifact_sha256": (
        "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
    ),
    "derivation_sha256": (
        "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
    ),
}
SUCCESSOR_ACCEPTANCE = {
    "acceptance_id": "d079_calibration_acceptance_v2_n17_r6",
    "rel": "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json",
    "artifact_sha256": (
        "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d"
    ),
    "derivation_sha256": (
        "18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3"
    ),
}


def acceptance_pin() -> dict[str, str]:
    """Return the acceptance generation this pack binds.

    Preserve mode replays the frozen `_v1` bytes, which are permanently bound
    to the D-116 initial issuance. Any successor generation binds the D-138
    reissue instead, so the two generations never share a pin.
    """

    return (
        PREDECESSOR_ACCEPTANCE
        if active_generation().preserve_current_frozen_bytes
        else SUCCESSOR_ACCEPTANCE
    )


MODEL_A: dict[str, Any] = {}
MODEL_B: dict[str, Any] = {}
MODEL_ENTRIES: dict[str, dict[str, Any]] = {}
MODEL_IDS: dict[str, str] = {}
MODEL_ID_TOKENS: dict[str, str] = {}
MODELS: dict[str, dict[str, Any]] = {}
MODEL_TAGS: dict[str, str] = {}
DECODE_FAMILIES: dict[str, dict[str, str]] = {}
PREFILL_FAMILY_IDS: dict[str, str] = {}
FLOOR_PACKS: dict[str, Path] = {}
QUANTIZATION: dict[str, Any] = {}
PAIR_TOKEN = ""
RUN_PREFIX = ""
CONSUMER_FAMILY_ID = ""
PANEL_FILE_ARGUMENT = ""
PREFILL_PIN_FILE_ARGUMENT = ""
PREFILL_PROMPT_TEXT = ""
PREFILL_PROMPT_SHA256 = ""
PREFILL_REPEAT_COUNT = 0
PREFILL_CLOSING_SENTENCE = ""
PREFILL_SELECTION_AUTHORITY: dict[str, Any] = {}
PREFILL_GENERATION_METHOD = ""
PREFILL_TOKEN_IDS: dict[str, list[int]] = {}
PREFILL_TOKEN_IDS_SHA256: dict[str, str] = {}
SHARED_TOKENIZER_JSON_SHA256 = ""
PREFILL_LENGTH: int | None = None
PREFILL_ARM = "prefill_unresolved"
DECODE_WORKLOAD_FILE_ARGUMENT = ""
DECODE_PROFILE: dict[str, Any] = {}
DECODE_RENDERINGS: dict[str, list[dict[str, Any]]] = {}
DECODE_PROMPT_TOKENS: dict[str, int] = {}
CHAT_TEMPLATE_SHA256: dict[str, str] = {}

HARDWARE = {
    "id": "macbook_m3_max",
    "transport": "local",
    "runtime_backend": "mlx",
    "telemetry_backend": "powermetrics",
    "device_kind": "apple_silicon_unified_memory",
    "notes": "D-117 gamma panel-selected contrast; normal powermetrics sampler set only",
}


def generation_hardware() -> dict[str, Any]:
    return {
        **HARDWARE,
        "notes": f"{HARDWARE['notes']}; pack status {emitted_draft_status()}.",
    }
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}


def dominance_criterion_registration() -> dict[str, Any]:
    """Return the frozen D-165 ratio and common-mode replay contract."""

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


def contrast_floor_estimator_registration() -> dict[str, Any]:
    """Return the v5 contrast-only D-165 extension of the issued registration."""

    return {
        **two_shared_edge_common_mode_registration(),
        "dominance_criterion": dominance_criterion_registration(),
    }

PROMPT_SENTENCE = "The plan remains easy to audit."
PROMPT_FINAL_SENTENCE = "The plan remains easy to audit and simple to review."


def _identifier_token(model_id: str) -> str:
    return model_id.replace("_", "-")


def _model_config(entry: dict[str, Any]) -> dict[str, Any]:
    for key in ("tokenizer_json_sha256", "chat_template_sha256"):
        if key not in entry or entry[key] is None:
            raise ValueError(f"v5_member_model_identity_pin_missing: {key}")
        value = entry[key]
        if (
            not isinstance(value, str)
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
        ):
            raise ValueError(f"v5_member_model_identity_pin_invalid: {key}")
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


def _token_ids_sha256(token_ids: list[int]) -> str:
    return prompt_token_ids_sha256(token_ids)


def _load_prefill_prompt_pin(
    path: Path, *, prefill_length: int, tokenizer_json_sha256: str, panel_sha256: str
) -> dict[str, Any]:
    """Load the post-G2 prompt pin without consulting a tokenizer or model."""

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = item
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"prefill_prompt_pin_invalid: {exc}") from exc
    keys = {
        "schema_version",
        "selection_authority",
        "ladder_prompt_tokens",
        "min_small_model_members_per_rung",
        "min_overlapping_power_interval_count",
        "min_phase_samples_pinned",
        "sample_count_margin_floor",
        "selection_expression",
        "g2a_record_sha256",
        "selection_record",
        "prompt_ladder",
        "panel_sha256",
        "exhausted_ladder_branch",
        "prefill_length",
        "tokenizer_json_sha256",
        "special_token_policy",
        "prompt_text",
        "prompt_text_utf8_sha256",
        "prompt_token_ids",
        "prompt_token_ids_sha256",
        "prompt_tokens",
        "repeat_count",
        "closing_sentence",
        "generation_method",
    }
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("prefill_prompt_pin_invalid: closed schema mismatch")
    if value["schema_version"] != "joulewise.prefill_prompt_pin.v2":
        raise ValueError("prefill_prompt_pin_invalid: unknown schema_version")
    if value["special_token_policy"] != "add_special_tokens=true":
        raise ValueError("prefill_prompt_pin_invalid: special_token_policy")
    if value["ladder_prompt_tokens"] != PREFILL_LADDER_PROMPT_TOKENS:
        raise ValueError("prefill_prompt_pin_invalid: ladder_prompt_tokens")
    if (
        value["min_small_model_members_per_rung"]
        != PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG
    ):
        raise ValueError(
            "prefill_prompt_pin_invalid: min_small_model_members_per_rung"
        )
    if (
        value["min_overlapping_power_interval_count"]
        != PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT
    ):
        raise ValueError(
            "prefill_prompt_pin_invalid: min_overlapping_power_interval_count"
        )
    if value["min_phase_samples_pinned"] != PREFILL_MIN_PHASE_SAMPLES_PINNED:
        raise ValueError("prefill_prompt_pin_invalid: min_phase_samples_pinned")
    if value["min_phase_samples_pinned"] != REDUCER_MIN_PHASE_SAMPLES:
        raise ValueError("prefill_prompt_pin_reducer_min_phase_samples_mismatch")
    if value["sample_count_margin_floor"] != PREFILL_SAMPLE_COUNT_MARGIN_FLOOR:
        raise ValueError("prefill_prompt_pin_invalid: sample_count_margin_floor")
    if (
        value["min_overlapping_power_interval_count"]
        - value["min_phase_samples_pinned"]
        != value["sample_count_margin_floor"]
    ):
        raise ValueError("prefill_prompt_pin_count_floor_inconsistent")
    if value["selection_expression"] != PREFILL_SELECTION_EXPRESSION:
        raise ValueError("prefill_prompt_pin_invalid: selection_expression")
    if value["exhausted_ladder_branch"] != PREFILL_EXHAUSTED_LADDER_BRANCH:
        raise ValueError("prefill_prompt_pin_invalid: exhausted_ladder_branch")
    selection_authority = value["selection_authority"]
    if (
        not isinstance(selection_authority, dict)
        or set(selection_authority) != {"g2a_record", "ruling_trace_paths"}
        or not isinstance(selection_authority["g2a_record"], dict)
        or set(selection_authority["g2a_record"]) != {"record_id", "path"}
        or any(
            not isinstance(selection_authority["g2a_record"][key], str)
            or not selection_authority["g2a_record"][key].strip()
            for key in ("record_id", "path")
        )
        or selection_authority["ruling_trace_paths"] != list(PREFILL_RULING_TRACE_PATHS)
    ):
        raise ValueError("prefill_prompt_pin_invalid: selection_authority")
    if not isinstance(value["g2a_record_sha256"], str) or not value[
        "g2a_record_sha256"
    ].strip():
        raise ValueError(
            "prefill_g2a_record_hash_unresolved: D-166 requires the selected "
            "G2-a record hash; no default or placeholder hash is permitted"
        )
    if len(value["g2a_record_sha256"]) != 64 or any(
        character not in "0123456789abcdef"
        for character in value["g2a_record_sha256"]
    ):
        raise ValueError("prefill_prompt_pin_invalid: g2a_record_sha256")
    if (
        selection_authority["g2a_record"]["record_id"]
        != f"sha256:{value['g2a_record_sha256']}"
    ):
        raise ValueError("selection_authority_mismatch")

    def bundle_bytes(field: str) -> bytes:
        reference = value[field]
        if (
            not isinstance(reference, dict)
            or set(reference) != {"path", "sha256"}
            or not isinstance(reference["path"], str)
            or not reference["path"].strip()
            or not isinstance(reference["sha256"], str)
        ):
            raise ValueError(f"prefill_prompt_pin_invalid: {field}")
        relative = Path(reference["path"])
        if relative.is_absolute():
            raise ValueError(f"prefill_prompt_pin_invalid: {field}.path")
        target = (path.parent / relative).resolve()
        try:
            target.relative_to(path.parent.resolve())
        except ValueError as exc:
            raise ValueError(f"prefill_prompt_pin_invalid: {field}.path") from exc
        try:
            raw = target.read_bytes()
        except OSError as exc:
            raise ValueError(f"{field}_missing") from exc
        if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
            raise ValueError(f"{field}_sha256_mismatch")
        return raw

    selection_raw = bundle_bytes("selection_record")
    if hashlib.sha256(selection_raw).hexdigest() != value["g2a_record_sha256"]:
        raise ValueError("selection_record_sha256_mismatch")
    ladder_raw = bundle_bytes("prompt_ladder")
    try:
        ladder = json.loads(
            ladder_raw,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"prefill_prompt_pin_invalid: prompt_ladder: {exc}") from exc
    if not isinstance(ladder, dict) or not isinstance(ladder.get("rungs"), list):
        raise ValueError("prefill_prompt_pin_invalid: prompt_ladder")
    if ladder.get("tokenizer_json_sha256") != tokenizer_json_sha256:
        raise ValueError("prompt_ladder_tokenizer_sha256_mismatch")
    ladder_policy = ladder.get("panel_thinking_policy")
    ladder_panel_sha = (
        ladder_policy.get("panel_sha256") if isinstance(ladder_policy, dict) else None
    )
    if value["panel_sha256"] != ladder_panel_sha or ladder_panel_sha != panel_sha256:
        raise ValueError(
            "prefill_prompt_pin_panel_sha256_mismatch: "
            f"pin={value['panel_sha256']} ladder={ladder_panel_sha} panel={panel_sha256}"
        )
    rung = next(
        (
            item
            for item in ladder["rungs"]
            if isinstance(item, dict) and item.get("prefill_tokens") == prefill_length
        ),
        None,
    )
    if rung is None:
        raise ValueError("prompt_ladder_rung_missing")
    if (
        value["prefill_length"] != prefill_length
        or value["prompt_tokens"] != prefill_length
    ):
        raise ValueError("prefill_prompt_pin_length_mismatch")
    if value["tokenizer_json_sha256"] != tokenizer_json_sha256:
        raise ValueError("prefill_prompt_pin_tokenizer_sha256_mismatch")
    text = value["prompt_text"]
    if not isinstance(text, str) or not text:
        raise ValueError("prefill_prompt_pin_invalid: prompt_text")
    if (
        hashlib.sha256(text.encode("utf-8")).hexdigest()
        != value["prompt_text_utf8_sha256"]
    ):
        raise ValueError("prefill_prompt_pin_text_sha256_mismatch")
    ids = value["prompt_token_ids"]
    if (
        not isinstance(ids, list)
        or len(ids) != prefill_length
        or any(
            isinstance(item, bool) or not isinstance(item, int) or item < 0
            for item in ids
        )
    ):
        raise ValueError("prefill_prompt_pin_token_ids_invalid")
    if prompt_token_ids_sha256(ids) != value["prompt_token_ids_sha256"]:
        raise ValueError("prefill_prompt_pin_token_ids_sha256_mismatch")
    if not isinstance(value["repeat_count"], int) or value["repeat_count"] <= 0:
        raise ValueError("prefill_prompt_pin_invalid: repeat_count")
    if not isinstance(value["closing_sentence"], str) or not value["closing_sentence"].strip():
        raise ValueError("prefill_prompt_pin_invalid: closing_sentence")
    if (
        not isinstance(value["generation_method"], str)
        or not value["generation_method"].strip()
    ):
        raise ValueError("prefill_prompt_pin_invalid: generation_method")
    rung_fields = {
        "prompt_text": "prompt_text",
        "prompt_text_utf8_sha256": "prompt_text_utf8_sha256",
        "prompt_token_ids": "prompt_token_ids",
        "prompt_token_ids_sha256": "prompt_token_ids_sha256",
        "prompt_tokens": "prefill_tokens",
        "repeat_count": "repeat_count",
        "closing_sentence": "closing_sentence",
        "generation_method": "generation_method",
    }
    for pin_field, ladder_field in rung_fields.items():
        if value[pin_field] != rung.get(ladder_field):
            raise ValueError(f"prefill_prompt_pin_ladder_rung_mismatch: {pin_field}")
    if value["tokenizer_json_sha256"] != ladder.get("tokenizer_json_sha256"):
        raise ValueError("prefill_prompt_pin_ladder_rung_mismatch: tokenizer_json_sha256")
    expected_text = " ".join(
        [PROMPT_SENTENCE] * value["repeat_count"] + [value["closing_sentence"]]
    )
    if text != expected_text:
        raise ValueError("prefill_prompt_pin_prompt_construction_mismatch")
    expected_method = (
        f"{value['repeat_count']} x '{PROMPT_SENTENCE}' + "
        f"'{value['closing_sentence']}' under tokenizer "
        f"sha256:{value['tokenizer_json_sha256']}"
    )
    if value["generation_method"] != expected_method:
        raise ValueError("prefill_prompt_pin_generation_method_construction_mismatch")
    return value


def configure_model_pair(
    panel_path: Path,
    model_a_id: str,
    model_b_id: str,
    *,
    decode_workload_path: Path,
    prefill_length: int | None,
    prefill_prompt_pin_path: Path | None = None,
) -> None:
    """Load the selected admitted pair and derive every model-bearing identity."""

    global PACK_REL, PLAN_ID, EVIDENCE_ROOT_ID, CLAIM_ROOT_LEAF, BOUND_ROOT_LEAF
    global MODEL_A, MODEL_B, MODEL_ENTRIES, MODEL_IDS, MODEL_ID_TOKENS
    global MODELS, MODEL_TAGS, DECODE_FAMILIES, PREFILL_FAMILY_IDS, FLOOR_PACKS
    global QUANTIZATION, PAIR_TOKEN, RUN_PREFIX, CONSUMER_FAMILY_ID
    global PANEL_FILE_ARGUMENT, PREFILL_PIN_FILE_ARGUMENT
    global PREFILL_PROMPT_TEXT, PREFILL_PROMPT_SHA256, PREFILL_REPEAT_COUNT
    global PREFILL_CLOSING_SENTENCE
    global PREFILL_SELECTION_AUTHORITY, PREFILL_GENERATION_METHOD
    global PREFILL_TOKEN_IDS, PREFILL_TOKEN_IDS_SHA256
    global SHARED_TOKENIZER_JSON_SHA256
    global PREFILL_LENGTH, PREFILL_ARM, DECODE_WORKLOAD_FILE_ARGUMENT
    global DECODE_PROFILE, DECODE_RENDERINGS, DECODE_PROMPT_TOKENS
    global CHAT_TEMPLATE_SHA256, STAGE_SPECS, REFERENCE_AFTER_STAGE

    if prefill_length is None:
        raise ValueError(
            "prefill_length_unresolved: D-166 as amended requires the G2-a "
            "prefill sweep result; no default or placeholder length is permitted"
        )
    if prefill_length not in set(PREFILL_LADDER_PROMPT_TOKENS):
        raise ValueError(
            "prefill_length_unknown: expected one of 512, 1024, 2048, 4096"
        )
    if prefill_prompt_pin_path is None:
        raise ValueError(
            "prefill_prompt_pin_unresolved: the selected G2-a length needs an "
            "explicit hash-bound prompt pin"
        )
    try:
        panel = load_model_panel(panel_path)
        selected = {"A": dict(panel.get(model_a_id)), "B": dict(panel.get(model_b_id))}
    except ModelPanelError as exc:
        raise ValueError(f"model_panel_refused: {exc}") from exc
    try:
        panel_sha256 = hashlib.sha256(panel_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError(f"model_panel_unreadable: {exc}") from exc
    if model_a_id == model_b_id:
        raise ValueError("model_pair_duplicate: model A and model B must differ")
    for arm, entry in selected.items():
        if entry["admission"]["status"] != "admitted":
            raise ValueError(
                f"model_not_admitted: arm {arm} model {entry['model_id']!r} "
                f"has status {entry['admission']['status']!r}"
            )
    if selected["A"]["quantization"] != selected["B"]["quantization"]:
        raise ValueError("pair_quantization_mismatch: frozen contrast requires one quantization")
    if selected["A"]["weight_format"] != selected["B"]["weight_format"]:
        raise ValueError("pair_weight_format_mismatch: frozen contrast requires one format")
    if selected["A"]["weight_format"] != "mlx":
        raise ValueError("weight_format_runtime_mismatch: frozen runtime backend is mlx")
    try:
        decode_profile = load_workload_profile(decode_workload_path)
    except WorkloadProfileError as exc:
        raise ValueError(f"decode_workload_refused: {exc}") from exc

    tokenizer_hashes = {
        arm: entry["tokenizer_json_sha256"] for arm, entry in selected.items()
    }
    if tokenizer_hashes["A"] != tokenizer_hashes["B"]:
        raise ValueError(
            "pair_tokenizer_identity_mismatch: model tokenizer.json SHA-256 values differ"
        )
    template_hashes = {
        arm: entry["chat_template_sha256"] for arm, entry in selected.items()
    }
    if template_hashes["A"] != template_hashes["B"]:
        raise ValueError(
            "pair_chat_template_mismatch: model chat_template SHA-256 values differ"
        )

    pinset_ids = {selected[arm]["rendering_pinset_id"] for arm in ("A", "B")}
    if None in pinset_ids or len(pinset_ids) != 1:
        raise ValueError("pair_rendering_pinset_mismatch")
    try:
        pinset = panel.get_rendering_pinset(pinset_ids.pop())
    except ModelPanelError as exc:
        raise ValueError(f"decode_rendering_pinset_refused: {exc}") from exc
    if (
        pinset["workload_profile_id"] != decode_profile.profile_id
        or pinset["prompt_set_sha256"] != decode_profile.prompt_set_sha256
    ):
        raise ValueError("decode_rendering_workload_binding_mismatch")
    profile_projection = [
        (prompt["prompt_id"], prompt["text_utf8_sha256"])
        for prompt in decode_profile.prompts
    ]
    pin_projection = [
        (prompt["prompt_id"], prompt["text_utf8_sha256"])
        for prompt in pinset["prompts"]
    ]
    if pin_projection != profile_projection:
        raise ValueError("decode_rendering_prompt_projection_mismatch")
    if pinset["tokenizer_json_sha256"] != tokenizer_hashes["A"]:
        raise ValueError("decode_rendering_tokenizer_sha256_mismatch")
    if pinset["chat_template_sha256"] != template_hashes["A"]:
        raise ValueError("decode_rendering_chat_template_sha256_mismatch")
    if pinset["enable_thinking"] != "false" or pinset["chat_template_applied"] is not True:
        raise ValueError("decode_rendering_policy_mismatch")
    renderings: dict[str, list[dict[str, Any]]] = {
        arm: [
            {**dict(prompt), "prompt_token_ids": list(prompt["prompt_token_ids"]), "enable_thinking": "false"}
            for prompt in pinset["prompts"]
        ]
        for arm in ("A", "B")
    }
    prompt_token_counts: dict[str, int] = {}
    for arm, entry in selected.items():
        if entry["chat_template_applied"] is not True:
            raise ValueError(
                f"chat_template_policy_mismatch: {entry['model_id']} must apply its template"
            )
        if entry["enable_thinking"] != "false":
            raise ValueError(
                f"thinking_policy_mismatch: {entry['model_id']} expected 'false'"
            )
        counts = {row["prompt_tokens"] for row in renderings[arm]}
        if len(counts) != 1:
            raise ValueError(
                "decode_prompt_shape_mismatch: condition-family schema requires one "
                f"positive prompt_tokens value; {entry['model_id']} rendered {sorted(counts)}"
            )
        prompt_token_counts[arm] = counts.pop()

    prefill_pin = _load_prefill_prompt_pin(
        prefill_prompt_pin_path,
        prefill_length=prefill_length,
        tokenizer_json_sha256=tokenizer_hashes["A"],
        panel_sha256=panel_sha256,
    )
    prompt_text = prefill_pin["prompt_text"]
    repeat_count = prefill_pin["repeat_count"]
    token_ids = {arm: list(prefill_pin["prompt_token_ids"]) for arm in ("A", "B")}

    MODEL_ENTRIES = selected
    MODEL_IDS = {arm: entry["model_id"] for arm, entry in selected.items()}
    MODEL_ID_TOKENS = {
        arm: _identifier_token(model_id) for arm, model_id in MODEL_IDS.items()
    }
    MODEL_A = _model_config(selected["A"])
    MODEL_B = _model_config(selected["B"])
    MODELS = {"A": MODEL_A, "B": MODEL_B}
    MODEL_TAGS = {arm: selected[arm]["tag"] for arm in ("A", "B")}
    QUANTIZATION = dict(selected["A"]["quantization"])
    PAIR_TOKEN = f"{MODEL_ID_TOKENS['A']}-vs-{MODEL_ID_TOKENS['B']}"
    pack_id = f"d117_contrast_{MODEL_IDS['A']}_vs_{MODEL_IDS['B']}_v5"
    PACK_REL = Path("configs/campaigns") / pack_id
    PLAN_ID = (
        f"plan-d117-contrast-{PAIR_TOKEN}-decode-prefill-p{prefill_length}-v5"
    )
    EVIDENCE_ROOT_ID = f"evidence-d117-contrast-{PAIR_TOKEN}-v5"
    CLAIM_ROOT_LEAF = f"runs_{pack_id}"
    BOUND_ROOT_LEAF = f"{CLAIM_ROOT_LEAF}_bound"
    RUN_PREFIX = f"d117c-{PAIR_TOKEN}-v5"
    CONSUMER_FAMILY_ID = f"d117-{PAIR_TOKEN}-gamma-consumer-v5"
    DECODE_FAMILIES = {
        arm: {"condition_family_id": f"sw-decode-{arm.lower()}-{MODEL_ID_TOKENS[arm]}"}
        for arm in ("A", "B")
    }
    PREFILL_FAMILY_IDS = {
        arm: f"sw-prefill-p{prefill_length}-{arm.lower()}-{MODEL_ID_TOKENS[arm]}"
        for arm in ("A", "B")
    }
    FLOOR_PACKS = {
        arm: Path("configs/campaigns") / f"d117_floor_{MODEL_IDS[arm]}_v5"
        for arm in ("A", "B")
    }
    PREFILL_PROMPT_TEXT = prompt_text
    PREFILL_PROMPT_SHA256 = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    PREFILL_REPEAT_COUNT = repeat_count
    PREFILL_CLOSING_SENTENCE = prefill_pin["closing_sentence"]
    PREFILL_SELECTION_AUTHORITY = prefill_pin["selection_authority"]
    PREFILL_GENERATION_METHOD = prefill_pin["generation_method"]
    PREFILL_TOKEN_IDS = token_ids
    PREFILL_TOKEN_IDS_SHA256 = {
        arm: _token_ids_sha256(token_ids[arm]) for arm in ("A", "B")
    }
    SHARED_TOKENIZER_JSON_SHA256 = tokenizer_hashes["A"]
    PANEL_FILE_ARGUMENT = panel_path.as_posix()
    PREFILL_PIN_FILE_ARGUMENT = prefill_prompt_pin_path.as_posix()
    PREFILL_LENGTH = prefill_length
    PREFILL_ARM = f"prefill_p{prefill_length}"
    DECODE_WORKLOAD_FILE_ARGUMENT = decode_workload_path.as_posix()
    DECODE_PROFILE = {
        "schema_version": decode_profile.schema_version,
        "profile_id": decode_profile.profile_id,
        "license": decode_profile.license,
        "prompt_set_sha256": decode_profile.prompt_set_sha256,
        "prompts": [dict(prompt) for prompt in decode_profile.prompts],
    }
    DECODE_RENDERINGS = renderings
    DECODE_PROMPT_TOKENS = prompt_token_counts
    CHAT_TEMPLATE_SHA256 = template_hashes
    STAGE_SPECS = (
        {
            "subcampaign_id": "01_decode_contrast_blocks_01_05",
            "measurement_arm": "decode",
            "role": "decode_contrast_first_half",
            "first_block": 1,
            "last_block": 5,
        },
        {
            "subcampaign_id": "02_decode_contrast_blocks_06_10",
            "measurement_arm": "decode",
            "role": "decode_contrast_second_half",
            "first_block": 6,
            "last_block": 10,
        },
        {
            "subcampaign_id": f"03_prefill_p{prefill_length}_contrast_blocks_01_05",
            "measurement_arm": PREFILL_ARM,
            "role": f"prefill_p{prefill_length}_contrast_first_half",
            "first_block": 1,
            "last_block": 5,
        },
        {
            "subcampaign_id": f"04_prefill_p{prefill_length}_contrast_blocks_06_10",
            "measurement_arm": PREFILL_ARM,
            "role": f"prefill_p{prefill_length}_contrast_second_half",
            "first_block": 6,
            "last_block": 10,
        },
    )
    REFERENCE_AFTER_STAGE = {
        STAGE_SPECS[0]["subcampaign_id"]: "gamma-reference-decode-midpoint",
        STAGE_SPECS[1]["subcampaign_id"]: "gamma-reference-arm-boundary",
        STAGE_SPECS[2]["subcampaign_id"]: "gamma-reference-prefill-midpoint",
        STAGE_SPECS[3]["subcampaign_id"]: "gamma-reference-end",
    }
REFERENCE_CADENCE_AUTHORITY = (
    "docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md "
    "§6 U7 gamma implementation session"
)
STAGE_SPECS: tuple[dict[str, Any], ...] = ()
REFERENCE_AFTER_STAGE: dict[str, str] = {}

POLICY_PATH = Path("configs/campaign_policies/quiet_mac_p2_production.json")
NEG8_MANIFEST_PATH = Path("configs/campaigns/neg8_reference_corpus/order_manifest.json")
NEG8_CORPUS_PATH = Path(
    "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json"
)
START_REF_MANIFEST_PATH = Path(
    "configs/campaigns/window_references/start_triplet/order_manifest.json"
)
MID_REF_MANIFEST_PATH = Path(
    "configs/campaigns/window_references/midpoint/order_manifest.json"
)
END_REF_MANIFEST_PATH = Path(
    "configs/campaigns/window_references/end_triplet/order_manifest.json"
)


def render_json(value: Any) -> bytes:
    return (
        json.dumps(thread_generation_identity(value), indent=2, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def render_suite_manifest_bytes(value: dict[str, Any]) -> bytes:
    """Render exactly the effective bytes named by suite_manifest_sha256."""

    effective = SuiteManifest.from_mapping(value).to_dict()
    return (json.dumps(effective, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def target_versioned_id(stem: str, *, separator: str = "-") -> str:
    """Return an identifier carrying the selected family generation."""

    version = active_generation().family_suffix.removeprefix("_")
    return f"{stem}{separator}{version}"


def producer_floor_artifact_id(measurement_arm: str, arm: str) -> str:
    """Derive the producer floor identity the corresponding v5 pack must mint."""

    role = "decode" if measurement_arm == "decode" else f"prefill-p{PREFILL_LENGTH}"
    return f"d117-{MODEL_ID_TOKENS[arm]}-{role}-floor-v5"


def producer_transport_group_id(measurement_arm: str, arm: str) -> str:
    """Derive the governed exact-stack transport group for one producer."""

    role = "decode" if measurement_arm == "decode" else f"prefill-p{PREFILL_LENGTH}"
    return f"tg-d117-{MODEL_ID_TOKENS[arm]}-{role}-v5"


def write_bytes(path: Path, data: bytes) -> None:
    allowed = validate_generation_output_inventory(active_generation())
    if not any(
        len(path.parts) >= len(relative.parts)
        and path.parts[-len(relative.parts):] == relative.parts
        for relative in allowed
    ):
        raise ValueError(f"output path is outside the closed inventory: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


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


def sidecar_bytes(digest: str, filename: str) -> bytes:
    return f"{digest}  {filename}\n".encode("utf-8")


def repo_sha(path: Path) -> str:
    return file_sha256(REPO_ROOT / path)


def empty_slot(
    todo: str, *, branch: str | None = None, value: Any = ""
) -> dict[str, Any]:
    row: dict[str, Any] = {"status": EMPTY_STATUS, "value": value, "todo": todo}
    if branch is not None:
        row["branch"] = branch
    return row


def run_id(measurement_arm: str, block: int, position: str) -> str:
    if measurement_arm == "decode":
        prefix = f"{RUN_PREFIX}-decode-contrast"
    elif measurement_arm == PREFILL_ARM:
        prefix = f"{RUN_PREFIX}-prefill-p{PREFILL_LENGTH}-contrast"
    else:
        raise ValueError(f"unknown measurement arm: {measurement_arm}")
    return f"{prefix}-b{block:02d}-{position}"


def expected_pack_paths(*, include_generator: bool = True) -> tuple[Path, ...]:
    paths = [
        Path("README.md"),
        Path("calibration_plan.json"),
        Path("calibration_plan.sha256"),
        Path("order_manifest.json"),
        Path("plan_tree.json"),
        Path("plan_tree.sha256"),
        Path("analysis_manifest_v3.json"),
        Path("consumer_family_declaration.json"),
        Path("decode_workload_candidate.json"),
        Path("prefill_prompt_candidate.json"),
        family_relpath("decode", "A"),
        family_relpath("decode", "B"),
        family_relpath(PREFILL_ARM, "A"),
        family_relpath(PREFILL_ARM, "B"),
    ]
    if include_generator:
        paths.append(Path("generate_configs.py"))
    for arm in ("A", "B"):
        for prompt_index in range(len(DECODE_PROFILE["prompts"])):
            paths.append(decode_suite_relpath(arm, prompt_index))
    for stage in STAGE_SPECS:
        stage_id = stage["subcampaign_id"]
        paths.append(Path(stage_id) / "order_manifest.json")
        for block in range(stage["first_block"], stage["last_block"] + 1):
            for position in ("a1", "b1", "b2", "a2"):
                paths.append(Path(stage_id) / f"{run_id(stage['measurement_arm'], block, position)}.json")
    return tuple(paths)


def validate_generation_output_inventory(identity: GenerationIdentity) -> set[Path]:
    outputs = {identity.pack_rel / path for path in expected_pack_paths()}
    if len(outputs) != len(expected_pack_paths()) or any(
        identity.pack_rel not in path.parents for path in outputs
    ):
        raise ValueError("generation output inventory escapes the target pack")
    return outputs


def block_id(measurement_arm: str, block: int) -> str:
    prefix = (
        "d117-decode"
        if measurement_arm == "decode"
        else f"d117-prefill-p{PREFILL_LENGTH}"
    )
    return f"{prefix}-contrast-b{block:02d}"


def family_id(measurement_arm: str, arm: str) -> str:
    if measurement_arm == "decode":
        return DECODE_FAMILIES[arm]["condition_family_id"]
    return PREFILL_FAMILY_IDS[arm]


def metric_for(measurement_arm: str) -> str:
    return "phase_energy_j.decode" if measurement_arm == "decode" else "phase_energy_j.prefill"


def workload_for(
    measurement_arm: str, arm: str | None = None
) -> dict[str, Any]:
    if measurement_arm == "decode":
        return {
            "name": f"{DECODE_PROFILE['profile_id']}_chat_rendered",
            "repetitions": 1,
            "warmup_runs": 1,
            "output_tokens": 512,
        }
    if arm not in {"A", "B"}:
        raise ValueError("prompt_realization_registration_missing: prefill arm")
    return {
        "name": f"df_ph_prefill_p{PREFILL_LENGTH}_candidate",
        "repetitions": 1,
        "warmup_runs": 1,
        "output_tokens": 512,
        "prompt_text": PREFILL_PROMPT_TEXT,
        "prompt_token_expectation": {
            "schema_version": "joulewise.prompt_token_expectation.v1",
            "token_hash_domain": "joulewise.prompt_token_ids.v1",
            "token_count": len(PREFILL_TOKEN_IDS[arm]),
            "token_ids_sha256": PREFILL_TOKEN_IDS_SHA256[arm],
        },
    }


def prefill_family_definition(arm: str) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": PREFILL_FAMILY_IDS[arm],
        "workload_profile": {
            "name": f"df_ph_prefill_p{PREFILL_LENGTH}_candidate",
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


def decode_family_definition(arm: str) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": DECODE_FAMILIES[arm]["condition_family_id"],
        "workload_profile": {
            "name": f"{DECODE_PROFILE['profile_id']}_chat_rendered",
            "prompt_tokens": DECODE_PROMPT_TOKENS[arm],
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "measurement_target": {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        },
        "comparison_policy": "same_condition_repeat_and_null_abba_alias",
        "abba_alias_relation": "A_equals_B",
    }


def decode_prompt_index(block: int) -> int:
    return (block - 1) % len(DECODE_PROFILE["prompts"])


def decode_suite_relpath(arm: str, prompt_index: int) -> Path:
    prompt_id = DECODE_PROFILE["prompts"][prompt_index]["prompt_id"]
    return Path(
        "decode_prompt_manifests"
    ) / MODEL_IDS[arm] / f"{prompt_index + 1:02d}_{prompt_id}.json"


def decode_suite_manifest(arm: str, prompt_index: int) -> dict[str, Any]:
    prompt = DECODE_PROFILE["prompts"][prompt_index]
    rendering = DECODE_RENDERINGS[arm][prompt_index]
    manifest = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "suite_id": (
            f"d117-{PAIR_TOKEN}-{MODEL_ID_TOKENS[arm]}-"
            f"{prompt['prompt_id']}-decode-v5"
        ),
        "suite_profile": DECODE_PROFILE["profile_id"],
        "suite_revision": DECODE_PROFILE["prompt_set_sha256"],
        "suite_seed": "d166-block-prompt-cycle-v1",
        "generator": {
            "name": "d117_v5_chat_template_renderer",
            "version": "1.0.0",
            "parameters_hash": CHAT_TEMPLATE_SHA256[arm],
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
                "item_id": f"{prompt['prompt_id']}-{MODEL_ID_TOKENS[arm]}-rendered",
                "item_type": "ids_prompt",
                "category": "real_question",
                "difficulty": {
                    "axis": "unscored_real_prompt",
                    "value": float(prompt_index + 1),
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
                        f"chat_template_sha256:{CHAT_TEMPLATE_SHA256[arm]}"
                    ),
                    "license": DECODE_PROFILE["license"],
                    "contamination_note": "original prompt; rendered IDs are the run input",
                    "prompt_token_ids": rendering["prompt_token_ids"],
                },
                "grouping": {
                    "condition_id": family_id("decode", arm),
                    "block_id": "single_prompt",
                    "level_id": prompt["prompt_id"],
                    "prefix_group_id": None,
                },
                "output_policy": "fixed_budget_exact",
                "tags": [
                    "d166-real-prompt",
                    f"enable-thinking={rendering['enable_thinking']}",
                ],
            }
        ],
    }
    SuiteManifest.from_mapping(manifest)
    return manifest


def decode_declared_suite_manifest_set(arm: str) -> list[dict[str, Any]]:
    """Declare the closed manifest census from the registered block rotation."""

    counts = [0] * len(DECODE_PROFILE["prompts"])
    members_per_block = sum(label == arm for label, _position in ABBA_POSITIONS)
    for stage in STAGE_SPECS:
        if stage["measurement_arm"] != "decode":
            continue
        for block in range(stage["first_block"], stage["last_block"] + 1):
            counts[decode_prompt_index(block)] += members_per_block
    return [
        {
            "suite_manifest_ref": (
                active_generation().pack_rel / decode_suite_relpath(arm, prompt_index)
            ).as_posix(),
            "suite_manifest_sha256": suite_manifest_sha256(
                decode_suite_manifest(arm, prompt_index)
            ),
            "declared_member_count": counts[prompt_index],
        }
        for prompt_index in range(len(DECODE_PROFILE["prompts"]))
    ]


def declared_identity_workload_profile(
    measurement_arm: str, arm: str
) -> dict[str, Any]:
    if measurement_arm == "decode":
        return {
            "name": f"{DECODE_PROFILE['profile_id']}_chat_rendered",
            "repetitions": 1,
            "warmup_runs": 1,
            "prompt_tokens": None,
            "output_tokens": 512,
            "prompt_text": None,
            "dataset_ref": None,
            "suite_manifest_set": decode_declared_suite_manifest_set(arm),
        }
    workload = workload_for(measurement_arm, arm)
    return {
        **workload,
        "prompt_tokens": workload.get("prompt_tokens"),
        "prompt_text": workload.get("prompt_text"),
        "dataset_ref": None,
    }


def decode_workload_candidate() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.d117_decode_workload_candidate.v1",
        "draft_status": emitted_draft_status(),
        "profile": {
            "path": DECODE_WORKLOAD_FILE_ARGUMENT,
            "profile_id": DECODE_PROFILE["profile_id"],
            "prompt_set_sha256": DECODE_PROFILE["prompt_set_sha256"],
            "license": DECODE_PROFILE["license"],
        },
        "rendering_policy": {
            "messages": [{"role": "user", "content": "<profile prompt text>"}],
            "add_generation_prompt": True,
            "chat_template_applied": True,
            "output_policy": "greedy_forced_512_suppress_eos",
        },
        "assignment": {
            "rule_id": "d166_block_prompt_cycle.v1",
            "rule": "prompt_index = (block_number - 1) mod prompt_count",
            "same_prompt_for_all_a_and_b_members_in_block": True,
            "prompt_count": len(DECODE_PROFILE["prompts"]),
        },
        "per_model": [
            {
                "model_id": MODEL_IDS[arm],
                "chat_template_sha256": CHAT_TEMPLATE_SHA256[arm],
                "prompt_tokens": DECODE_PROMPT_TOKENS[arm],
                "prompts": DECODE_RENDERINGS[arm],
            }
            for arm in ("A", "B")
        ],
    }


def build_condition_families() -> tuple[dict[tuple[str, str], bytes], dict[tuple[str, str], str]]:
    family_bytes: dict[tuple[str, str], bytes] = {}
    domain_hashes: dict[tuple[str, str], str] = {}
    for arm in ("A", "B"):
        definition = decode_family_definition(arm)
        errors = validate_condition_family_definition(definition)
        if errors:
            raise ValueError(f"decode family {arm} is invalid: {'; '.join(errors)}")
        family_bytes[("decode", arm)] = render_json(definition)
        domain_hashes[("decode", arm)] = canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, definition
        )

        prefill_definition = prefill_family_definition(arm)
        errors = validate_condition_family_definition(prefill_definition)
        if errors:
            raise ValueError(f"prefill family {arm} is invalid: {'; '.join(errors)}")
        family_bytes[(PREFILL_ARM, arm)] = render_json(prefill_definition)
        domain_hashes[(PREFILL_ARM, arm)] = canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, prefill_definition
        )
    return family_bytes, domain_hashes


def family_relpath(measurement_arm: str, arm: str) -> Path:
    arm_name = "decode" if measurement_arm == "decode" else PREFILL_ARM
    return Path(
        f"condition_families/condition_family_sw_{arm_name}_{arm.lower()}_"
        f"{MODEL_IDS[arm]}.json"
    )


def prompt_candidate() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.d117_prompt_candidate.v1",
        # The prompt artifact pins the chosen D-166 prefill length and token IDs.
        "draft_status": emitted_draft_status(),
        "candidate_status": PROMPT_STATUS,
        "authority": {
            "prompt_length": "D-166 R-2 with the D-122 exact-token-count rule",
            "prompt_text": PREFILL_SELECTION_AUTHORITY,
        },
        "prompt_text": PREFILL_PROMPT_TEXT,
        "prompt_text_utf8_sha256": PREFILL_PROMPT_SHA256,
        "planned_token_count": PREFILL_LENGTH,
        "token_count_basis": {
            "status": "PANEL-AND-G2A-PIN-VERIFIED-CANDIDATE",
            "shared_tokenizer_json_sha256": SHARED_TOKENIZER_JSON_SHA256,
            "repeat_count": PREFILL_REPEAT_COUNT,
            "repeated_sentence": PROMPT_SENTENCE,
            "final_sentence": PREFILL_CLOSING_SENTENCE,
            "model_panel_entries_bound": [MODEL_A["name"], MODEL_B["name"]],
            "per_model": [
                {
                    "model_id": MODEL_IDS[arm],
                    "vocab_size": MODEL_ENTRIES[arm]["vocab_size"],
                    "tokenizer_json_sha256": MODEL_ENTRIES[arm][
                        "tokenizer_json_sha256"
                    ],
                    "token_count": len(PREFILL_TOKEN_IDS[arm]),
                    "token_ids": PREFILL_TOKEN_IDS[arm],
                    "token_ids_sha256": PREFILL_TOKEN_IDS_SHA256[arm],
                }
                for arm in ("A", "B")
            ],
            "construction": PREFILL_GENERATION_METHOD,
            "lead_rerun_required_before_ratification": True,
        },
    }


def consumer_declaration() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.d117_consumer_family_declaration.v1",
        # The frozen gamma plan test pins this declaration's exact SHA.
        "draft_status": emitted_draft_status(),
        "declaration_kind": "consumer_family_declaration",
        "binding_mode": "declaration_only",
        "byte_binding_pinset": False,
        "authority": (
            "plan-factory frozen cross-pack vocabulary, amended by D-122 and D-166"
        ),
        "consumer_family_id": CONSUMER_FAMILY_ID,
        "decode_floor_cells": {
            "condition_a": producer_floor_artifact_id("decode", "A"),
            "condition_b": producer_floor_artifact_id("decode", "B"),
            "derivation": "deterministic plan-factory floor artifact vocabulary",
            "floor_rule": "cross_stack_armwise_max.v1",
        },
        f"prefill_p{PREFILL_LENGTH}_floor_dependency": {
            "cell_ids": [
                producer_floor_artifact_id(PREFILL_ARM, arm)
                for arm in ("A", "B")
            ],
            "transport_rule": {
                "mode": "exact_stack_only",
                "rule_id": EXACT_STACK_RULE_ID,
            },
        },
        "forbidden_content": [
            "aggregate artifact byte SHA",
            "floor artifact pinset",
            "postcollection receipt or verdict bytes",
        ],
    }


def arm_plan(
    measurement_arm: str,
    arm: str,
    family_bytes: dict[tuple[str, str], bytes],
    domain_hashes: dict[tuple[str, str], str],
) -> dict[str, Any]:
    model = MODELS[arm]
    return {
        "condition_family_id": family_id(measurement_arm, arm),
        "condition_family_byte_sha256": sha256_bytes(family_bytes[(measurement_arm, arm)]),
        "condition_family_domain_sha256": domain_hashes[(measurement_arm, arm)],
        "model_name": model["name"],
        "model_family": model["family"],
        "model_revision": model["revision"],
        "model_source": model["source"],
        "weight_format": model["weight_format"],
        "model_tag": MODEL_TAGS[arm],
    }


def build_runs() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    all_runs: list[dict[str, Any]] = []
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for stage in STAGE_SPECS:
        stage_runs: list[dict[str, Any]] = []
        measurement_arm = stage["measurement_arm"]
        for block in range(stage["first_block"], stage["last_block"] + 1):
            prompt_index = decode_prompt_index(block) if measurement_arm == "decode" else None
            for sequence_index, (arm, position) in enumerate(ABBA_POSITIONS, start=1):
                member_id = run_id(measurement_arm, block, position.lower())
                row = {
                    "run_id": member_id,
                    "filename": f"{member_id}.json",
                    "stage_id": stage["subcampaign_id"],
                    "measurement_arm": measurement_arm,
                    "metric": metric_for(measurement_arm),
                    "arm": arm,
                    "position": position,
                    "position_in_block": sequence_index,
                    "block_index": block,
                    "block_id": block_id(measurement_arm, block),
                    "condition_family_id": family_id(measurement_arm, arm),
                    "decode_prompt_index": prompt_index,
                    "decode_prompt_id": (
                        DECODE_PROFILE["prompts"][prompt_index]["prompt_id"]
                        if prompt_index is not None
                        else None
                    ),
                }
                stage_runs.append(row)
                all_runs.append(row)
        by_stage[stage["subcampaign_id"]] = stage_runs
    return all_runs, by_stage


def ordered_blocks(runs: Iterable[dict[str, Any]], measurement_arm: str) -> list[dict[str, Any]]:
    selected = [run for run in runs if run["measurement_arm"] == measurement_arm]
    blocks: list[dict[str, Any]] = []
    for block in range(1, N_BLOCKS + 1):
        members = [run for run in selected if run["block_index"] == block]
        blocks.append(
            {
                "block_id": block_id(measurement_arm, block),
                "block_number": block,
                "executed_labels": ["A", "B", "B", "A"],
                "prompt_assignment": (
                    {
                        "rule_id": "d166_block_prompt_cycle.v1",
                        "prompt_index": decode_prompt_index(block),
                        "prompt_id": DECODE_PROFILE["prompts"][
                            decode_prompt_index(block)
                        ]["prompt_id"],
                        "same_for_all_members": True,
                    }
                    if measurement_arm == "decode"
                    else None
                ),
                "members": [
                    {
                        "position": run["position"],
                        "plan_label": run["arm"],
                        "plan_sequence_index": run["position_in_block"],
                        "bundle_id": run["run_id"],
                    }
                    for run in members
                ],
            }
        )
    return blocks


def build_plan(
    runs: list[dict[str, Any]],
    family_bytes: dict[tuple[str, str], bytes],
    domain_hashes: dict[tuple[str, str], str],
    prompt_sha: str,
    declaration_sha: str,
) -> dict[str, Any]:
    return {
        "schema_version": PLAN_SCHEMA,
        # The D-134 freeze receipt pins calibration_plan.json by SHA, so this
        # serialized status can never transition after the receipt is minted --
        # the committed receipt IS the freeze state (cold-gate verdict
        # 2026-08-18, holdings 1 and 6). Do not make this field freeze-reactive.
        "draft_status": emitted_draft_status(),
        "plan_id": PLAN_ID,
        "calibration_scope": "production_window",
        "fixed_n": N_BLOCKS,
        "authorities": [
            "D-117",
            "D-122",
            "D-123",
            "D-124",
            "D-125",
            "D-139",
            "D-157",
            "D-165",
            "D-166",
        ],
        "stack_scope": {
            "hardware_target": "macbook_m3_max",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "quantization": "int4",
            "sampling": SAMPLING,
            "measurement_arms": {
                measurement_arm: {
                    "arms": {
                        arm: arm_plan(measurement_arm, arm, family_bytes, domain_hashes)
                        for arm in ("A", "B")
                    },
                    "workload": workload_for(measurement_arm, "A"),
                }
                for measurement_arm in ("decode", PREFILL_ARM)
            },
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
                "cell_id": f"d117-sw-decode-contrast-{PAIR_TOKEN}",
                "measurement_arm": "decode",
                "kind": "comparative_contrast",
                "minimum_claim_n_blocks": N_BLOCKS,
                "metric": "phase_energy_j.decode",
                "target_precheck_path": ["phase", "decode"],
                "difference_orientation": "condition_b_minus_condition_a",
                "point_estimator": "abba_block_arm_mean_difference_t_v1",
                "floor_estimator_registration": contrast_floor_estimator_registration(),
                "test": "two_sided",
                "scientific_hypothesis_direction": "positive",
                "family_alpha": 0.05,
                "multiplicity": "Holm",
                "family_m": 2,
                "equivalence_margin": None,
                "mde": None,
                "ordered_blocks": ordered_blocks(runs, "decode"),
            },
            {
                "cell_id": f"d117-sw-prefill-p{PREFILL_LENGTH}-contrast-{PAIR_TOKEN}",
                "measurement_arm": PREFILL_ARM,
                "kind": "comparative_contrast",
                "minimum_claim_n_blocks": N_BLOCKS,
                "metric": "phase_energy_j.prefill",
                "target_precheck_path": ["phase", "prefill"],
                "difference_orientation": "condition_b_minus_condition_a",
                "point_estimator": "abba_block_arm_mean_difference_t_v1",
                "floor_estimator_registration": contrast_floor_estimator_registration(),
                "prompt_candidate": {
                    "path": "prefill_prompt_candidate.json",
                    "sha256": prompt_sha,
                    "status": PROMPT_STATUS,
                },
                "test": "two_sided",
                "scientific_hypothesis_direction": "positive",
                "family_alpha": 0.05,
                "multiplicity": "Holm",
                "family_m": 2,
                "equivalence_margin": None,
                "mde": None,
                "ordered_blocks": ordered_blocks(runs, PREFILL_ARM),
            },
        ],
        "reported_energy_cells": [],
        "execution_mode": {
            "ordered_science_stage_ids": [
                stage["subcampaign_id"] for stage in STAGE_SPECS
            ],
            "planned_science_bundles": TOTAL_SCIENCE_MEMBERS,
            "planned_bound_bundles": 12,
            "planned_reference_bundles": 9,
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
            "path": POLICY_PATH.as_posix(),
            "sha256": repo_sha(POLICY_PATH),
        },
    }


def config_for(run: dict[str, Any], plan_sha256: str) -> dict[str, Any]:
    prefill_tags = (
        [
            f"prompt-tokens={PREFILL_LENGTH}",
            f"prompt-text-sha256={PREFILL_PROMPT_SHA256}",
            f"prompt-status={PROMPT_STATUS}",
        ]
        if run["measurement_arm"] == PREFILL_ARM
        else []
    )
    decode_tags = (
        [
            f"decode-workload={DECODE_PROFILE['profile_id']}",
            f"decode-prompt={run['decode_prompt_id']}",
            f"chat-template-sha256={CHAT_TEMPLATE_SHA256[run['arm']]}",
        ]
        if run["measurement_arm"] == "decode"
        else []
    )
    tags = [
        "phase2",
        f"d117-contrast-{PAIR_TOKEN}-v5",
        "production-window",
        "comparative-contrast",
        f"measurement-arm={run['measurement_arm']}",
        f"df-condition={run['condition_family_id']}",
        f"calibration-plan-sha256={plan_sha256}",
        f"calibration-abba-block-id={run['block_id']}",
        f"calibration-abba-label={run['arm']}",
        f"calibration-abba-sequence-index={run['position_in_block']}",
        *prefill_tags,
        *decode_tags,
    ]
    if active_generation().target_is_successor_family:
        tags.append("launch_lineage_required")
    if run["measurement_arm"] == "decode":
        prompt_index = run["decode_prompt_index"]
        suite = decode_suite_manifest(run["arm"], prompt_index)
        workload = {
            "name": f"{DECODE_PROFILE['profile_id']}_chat_rendered",
            "repetitions": 1,
            "warmup_runs": 1,
            "output_tokens": 512,
            "suite_manifest_ref": (
                active_generation().pack_rel
                / decode_suite_relpath(run["arm"], prompt_index)
            ).as_posix(),
            "suite_manifest_sha256": suite_manifest_sha256(suite),
        }
    else:
        workload = workload_for(run["measurement_arm"], run["arm"])
    return {
        "schema_version": "0.1",
        "run_id": run["run_id"],
        "model": MODELS[run["arm"]],
        "quantization": QUANTIZATION,
        "hardware_target": generation_hardware(),
        "workload_profile": workload,
        "interconnect": {"name": "local"},
        "sampling": SAMPLING,
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "lead",
            "tags": tags,
        },
    }


def manifest_entry(run: dict[str, Any], index: int, config_path: str, config_sha: str) -> dict[str, Any]:
    return {
        "index": index,
        "config": config_path,
        "config_sha256": config_sha,
        "run_id": run["run_id"],
        "model_tag": MODEL_TAGS[run["arm"]],
        "role": "comparative_contrast_member",
        "measurement_arm": run["measurement_arm"],
        "metric": run["metric"],
        "arm": run["arm"],
        "condition_family_id": run["condition_family_id"],
        "block_id": run["block_id"],
        "block_index": run["block_index"],
        "position": run["position"],
        "position_in_block": run["position_in_block"],
    }


def build_external_manifest(label: str, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads((REPO_ROOT / manifest_path).read_text(encoding="utf-8"))
    base = manifest_path.parent
    members = []
    for row in manifest["executed_order"]:
        member_path = base / row["config"]
        members.append(
            {
                "run_id": row["run_id"],
                "path": member_path.as_posix(),
                "sha256": repo_sha(member_path),
            }
        )
    return {
        "input_id": label,
        "manifest_path": manifest_path.as_posix(),
        "manifest_sha256": repo_sha(manifest_path),
        "manifest_id": manifest["manifest_id"],
        "expected_count": manifest["planned_n_bundles"],
        "members": members,
    }


def token(kind: str, value: str, *, relative: str | None = None) -> dict[str, Any]:
    row = {"kind": kind, "value": value}
    if relative is not None:
        row["relative"] = relative
    return row


def literal(value: str) -> dict[str, Any]:
    return token("literal", value)


def repo_path(value: str) -> dict[str, Any]:
    return token("repo_path", value)


def binding(value: str) -> dict[str, Any]:
    return token("binding", value)


def binding_path(value: str, relative: str) -> dict[str, Any]:
    return token("binding_path", value, relative=relative)


def tree_pointer(value: str) -> dict[str, Any]:
    return token("tree_pointer", value)


def command(command_id: str, command_kind: str, tool_id: str, interface_id: str, arguments: list[dict[str, Any]]) -> dict[str, Any]:
    return {
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


def launch(commands: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema_version": "joulewise.stage_launch.v1", "commands": commands}


def campaign_command(stage_id: str, config_dir: str, root_binding: str) -> dict[str, Any]:
    return command(
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
            repo_path(POLICY_PATH.as_posix()),
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


def stage_row(
    stage_id: str,
    ordinal: int,
    kind: str,
    expected_count: int,
    predecessor: str | None,
    successor: str | None,
    input_ref: dict[str, Any],
    commands: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "ordinal": ordinal,
        "kind": kind,
        "expected_count": expected_count,
        "predecessor": predecessor,
        "successor": successor,
        "input_ref": input_ref,
        "launch": launch(commands),
    }


def freeze_aware_reservation_plan_arguments(
    identity: GenerationIdentity | None = None,
    *,
    pack_rel: Path | None = None,
    plan_reference: str = CALIBRATION_PLAN_REFERENCE,
) -> list[dict[str, Any]]:
    selected = identity or active_generation()
    if selected.target_ordinal == 1:
        return []
    if plan_reference != CALIBRATION_PLAN_REFERENCE:
        raise ValueError("reservation plan must use the canonical pack-relative reference")
    resolved_pack_rel = pack_rel or selected.pack_rel
    return [
        literal("--plan"),
        repo_path((resolved_pack_rel / plan_reference).as_posix()),
    ]


def build_stage_graph(stage_manifests: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    stages: list[tuple[str, str, int, dict[str, Any], list[dict[str, Any]]]] = []
    stages.append(
        (
            "gamma-bracket-reservation",
            "bracket_reservation",
            0,
            {"kind": "plan_tree"},
            [
                command(
                    "gamma-bracket-reservation.reserve",
                    "bracket_reservation",
                    "bracket_reserver",
                    "joulewise.calibration_window_bracket_reservation.cli.v1",
                    [
                        literal("--ledger"), binding("ledger_path"),
                        literal("--head-pin"), repo_path("configs/calibration/calibration_ledger_head.json"),
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
                    ],
                )
            ],
        )
    )
    stages.append(
        (
            "gamma-calibration-pre",
            "calibration_capture",
            1,
            {"kind": "arm_attachment", "slot": "pre_attempt_id"},
            [
                command(
                    "gamma-calibration-pre.capture",
                    "calibration_capture",
                    "fiducial_capture",
                    "joulewise.powermetrics_fiducial.cli.v1",
                    [
                        literal("--allow-live"), literal("--output-root"),
                        binding_path("claim_runs_root", "instrument_validation"),
                        literal("--session-id"), binding("bracket_session_id"),
                        literal("--slot"), literal("pre"),
                        literal("--attempt-id"), binding("pre_attempt_id"),
                        literal("--power-policy"), literal("ac_high_power"),
                    ],
                )
            ],
        )
    )
    stages.append(
        (
            "gamma-bound-collection",
            "campaign_collection",
            12,
            {"kind": "external_input", "input_id": "neg8_bound_corpus"},
            [campaign_command("gamma-bound-collection", NEG8_MANIFEST_PATH.parent.as_posix(), "bound_runs_root")],
        )
    )
    stages.append(
        (
            "gamma-bound-derivation",
            "bound_derivation",
            0,
            {"kind": "external_input", "input_id": "neg8_settled_corpus"},
            [
                command(
                    "gamma-bound-derivation.derive",
                    "bound_derivation",
                    "campaign_runner",
                    "joulewise.run_campaign.cli.v1",
                    [
                        literal("--derive-neg8-drift-bound"), repo_path(NEG8_CORPUS_PATH.as_posix()),
                        literal("--neg8-drift-bound-output"), binding_path("bound_runs_root", "neg8-drift-bound.json"),
                        literal("--runs-dir"), binding("bound_runs_root"),
                    ],
                )
            ],
        )
    )
    stages.append(
        (
            "gamma-reference-start",
            "campaign_collection",
            3,
            {"kind": "external_input", "input_id": "start_references"},
            [campaign_command("gamma-reference-start", START_REF_MANIFEST_PATH.parent.as_posix(), "claim_runs_root")],
        )
    )
    for stage in STAGE_SPECS[:2]:
        stage_id = f"gamma-science-{stage['subcampaign_id'].replace('_', '-')}"
        stages.append(
            (
                stage_id,
                "campaign_collection",
                20,
                {"kind": "pack_manifest", **stage_manifests[stage["subcampaign_id"]]},
                [campaign_command(stage_id, (PACK_REL / stage["subcampaign_id"]).as_posix(), "claim_runs_root")],
            )
        )
        if stage["last_block"] == 5:
            stages.append(
                (
                    "gamma-reference-decode-midpoint",
                    "campaign_collection",
                    1,
                    {"kind": "external_input", "input_id": "midpoint_reference"},
                    [campaign_command("gamma-reference-decode-midpoint", MID_REF_MANIFEST_PATH.parent.as_posix(), "claim_runs_root")],
                )
            )
        else:
            stages.append(
                (
                    "gamma-reference-arm-boundary",
                    "campaign_collection",
                    1,
                    {"kind": "external_input", "input_id": "midpoint_reference"},
                    [campaign_command("gamma-reference-arm-boundary", MID_REF_MANIFEST_PATH.parent.as_posix(), "claim_runs_root")],
                )
            )
    for stage in STAGE_SPECS[2:]:
        stage_id = f"gamma-science-{stage['subcampaign_id'].replace('_', '-')}"
        stages.append(
            (
                stage_id,
                "campaign_collection",
                20,
                {"kind": "pack_manifest", **stage_manifests[stage["subcampaign_id"]]},
                [campaign_command(stage_id, (PACK_REL / stage["subcampaign_id"]).as_posix(), "claim_runs_root")],
            )
        )
        if stage["last_block"] == 5:
            stages.append(
                (
                    "gamma-reference-prefill-midpoint",
                    "campaign_collection",
                    1,
                    {"kind": "external_input", "input_id": "midpoint_reference"},
                    [campaign_command("gamma-reference-prefill-midpoint", MID_REF_MANIFEST_PATH.parent.as_posix(), "claim_runs_root")],
                )
            )
    stages.append(
        (
            "gamma-reference-end",
            "campaign_collection",
            3,
            {"kind": "external_input", "input_id": "end_references"},
            [campaign_command("gamma-reference-end", END_REF_MANIFEST_PATH.parent.as_posix(), "claim_runs_root")],
        )
    )
    stages.append(
        (
            "gamma-calibration-post",
            "calibration_capture",
            1,
            {"kind": "arm_attachment", "slot": "post_attempt_id"},
            [
                command(
                    "gamma-calibration-post.capture",
                    "calibration_capture",
                    "fiducial_capture",
                    "joulewise.powermetrics_fiducial.cli.v1",
                    [
                        literal("--allow-live"), literal("--output-root"),
                        binding_path("claim_runs_root", "instrument_validation"),
                        literal("--session-id"), binding("bracket_session_id"),
                        literal("--slot"), literal("post"),
                        literal("--attempt-id"), binding("post_attempt_id"),
                        literal("--power-policy"), literal("ac_high_power"),
                    ],
                )
            ],
        )
    )
    stages.append(
        (
            "gamma-whole-window-verdict",
            "whole_window_verdict",
            0,
            {"kind": "derived", "from": "claim_runs_root"},
            [
                command(
                    "gamma-whole-window-verdict.issue",
                    "whole_window_verdict",
                    "campaign_runner",
                    "joulewise.run_campaign.cli.v1",
                    [
                        literal("--whole-window-verdict"), literal("--runs-dir"), binding("claim_runs_root"),
                        literal("--log"), binding_path("claim_runs_root", "campaign_log.jsonl"),
                        literal("--campaign-policy"), repo_path(POLICY_PATH.as_posix()),
                        literal("--neg8-drift-bound"), binding_path("bound_runs_root", "neg8-drift-bound.json"),
                    ],
                )
            ],
        )
    )
    stages.append(
        (
            "gamma-backup",
            "backup",
            0,
            {"kind": "arm_attachment", "slot": "backup_destinations"},
            [
                command(
                    "gamma-backup.claim",
                    "backup",
                    "backup_runs",
                    "joulewise.backup_runs.cli.v1",
                    [binding("claim_runs_root"), binding("claim_backup_destination")],
                ),
                command(
                    "gamma-backup.bound",
                    "backup",
                    "backup_runs",
                    "joulewise.backup_runs.cli.v1",
                    [binding("bound_runs_root"), binding("bound_backup_destination")],
                ),
            ],
        )
    )

    rows: list[dict[str, Any]] = []
    for index, (stage_id, kind, count, input_ref, commands) in enumerate(stages, start=1):
        predecessor = stages[index - 2][0] if index > 1 else None
        successor = stages[index][0] if index < len(stages) else None
        rows.append(
            stage_row(stage_id, index, kind, count, predecessor, successor, input_ref, commands)
        )
    return rows


def family_tree_rows(
    family_bytes: dict[tuple[str, str], bytes],
    domain_hashes: dict[tuple[str, str], str],
) -> list[dict[str, Any]]:
    rows = []
    for measurement_arm in ("decode", PREFILL_ARM):
        for arm in ("A", "B"):
            rows.append(
                {
                    "measurement_arm": measurement_arm,
                    "arm": arm,
                    "path": family_relpath(measurement_arm, arm).as_posix(),
                    "sha256": sha256_bytes(family_bytes[(measurement_arm, arm)]),
                    "condition_family_id": family_id(measurement_arm, arm),
                    "canonical_domain_sha256": domain_hashes[(measurement_arm, arm)],
                }
            )
    return rows


def build_analysis_manifest(
    plan_sha: str,
    root_manifest: dict[str, Any],
    root_manifest_sha: str,
    stage_manifest_rows: list[dict[str, Any]],
    all_entries: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    prompt_sha: str,
    declaration_sha: str,
) -> dict[str, Any]:
    del declaration_sha  # The prospective floor contract replaces the draft pin.

    analysis_family_id = target_versioned_id(
        f"d117-gamma-decode-prefill-p{PREFILL_LENGTH}-primary-holm"
    )
    family_instance_id = target_versioned_id(
        f"fam-d117-gamma-decode-prefill-p{PREFILL_LENGTH}-primary-holm"
    )
    family_metric_tag = f"phase_decode_prefill_p{PREFILL_LENGTH}_energy"

    def contrast_id(measurement_arm: str) -> str:
        return f"ctr-d117-{measurement_arm.replace('_', '-')}-{PAIR_TOKEN}"

    def floor_dependency(measurement_arm: str) -> dict[str, Any]:
        condition_ids = [
            family_id_for_arm
            for family_id_for_arm in (
                family_id(measurement_arm, "A"),
                family_id(measurement_arm, "B"),
            )
        ]
        domain_sha_by_id = {
            row["condition_family_id"]: row["canonical_domain_sha256"]
            for row in family_rows
        }
        return {
            "required_artifact_schema": DETECTION_FLOOR_ARTIFACT_SCHEMA,
            "floor_selector": {
                "backend": "powermetrics",
                "metric": metric_for(measurement_arm),
                "window_class": "phase",
                "condition_family_ids": condition_ids,
                "floor_field": "floor_gate_j",
                "transport_rule_id": EXACT_STACK_RULE_ID,
                "claim_floor_rule": "cross_stack_armwise_max.v1",
            },
            "transport": {
                "mode": "exact_stack_only",
                "rule_id": EXACT_STACK_RULE_ID,
                "transport_groups": [
                    {
                        "transport_group_id": producer_transport_group_id(
                            measurement_arm, arm
                        ),
                        "condition_family_id": condition_id,
                        "condition_domain_sha256": domain_sha_by_id[condition_id],
                        "group_rule_id": GOVERNED_TRANSPORT_RULE_ID,
                    }
                    for arm, condition_id in zip(
                        ("A", "B"), condition_ids, strict=True
                    )
                ],
            },
        }

    def contrast(measurement_arm: str) -> dict[str, Any]:
        entries = [entry for entry in all_entries if entry["measurement_arm"] == measurement_arm]
        common: dict[str, Any] = {
            "contrast_id": contrast_id(measurement_arm),
            "measurement_arm": measurement_arm,
            "metric": metric_for(measurement_arm),
            "metric_tag": (
                "phase_decode_energy"
                if measurement_arm == "decode"
                else f"phase_prefill_p{PREFILL_LENGTH}_energy"
            ),
            "target_precheck_path": ["phase", "decode" if measurement_arm == "decode" else "prefill"],
            "condition_a_id": family_id(measurement_arm, "A"),
            "condition_b_id": family_id(measurement_arm, "B"),
            "difference_orientation": "condition_b_minus_condition_a",
            "point_estimator": "abba_block_arm_mean_difference_t_v1",
            "floor_estimator_registration": contrast_floor_estimator_registration(),
            "block_ids": [block_id(measurement_arm, block) for block in range(1, N_BLOCKS + 1)],
            "members": [
                {
                    "run_id": entry["run_id"],
                    "config": entry["config"],
                    "config_sha256": entry["config_sha256"],
                    "arm": entry["arm"],
                    "block_id": entry["block_id"],
                    "block_number": entry["block_index"],
                    "position": entry["position"],
                    "order_index": entry["index"],
                }
                for entry in entries
            ],
            "family_instance_id": family_instance_id,
            "claim_role": "primary",
            "test": "two_sided",
            "scientific_hypothesis_direction": "positive",
            "equivalence": None,
            "mde": None,
            "floor_dependency": floor_dependency(measurement_arm),
        }
        if measurement_arm == "decode":
            common["prompt"] = None
        else:
            common["prompt"] = {
                "path": "prefill_prompt_candidate.json",
                "sha256": prompt_sha,
                "status": PROMPT_STATUS,
            }
        return common

    # The attachment roles and their schema versions come from the supported
    # accessor rather than a local copy, so this generator -- which is
    # committed into the frozen successor pack -- cannot drift from the
    # validator it must satisfy.  This pack registers the dominance
    # criterion on every contrast, so it declares the D-165 replay-sidecar
    # role as well (five rows; clause 7e).
    required_attachments = prospective_finalization_required_attachments(
        optional_roles=(DOMINANCE_REPLAY_SIDECAR_ROLE,),
    )

    manifest = {
        "schema_version": "joulewise.analysis_manifest.v3.prospective",
        "manifest_id": "",
        # D-139 A2 freezes analysis semantics at production generation; the
        # D-134 pack receipt remains the separate dynamic pack-freeze state.
        "freeze_status": "frozen",
        "plan": {
            "plan_id": PLAN_ID,
            "path": "calibration_plan.json",
            "sha256": plan_sha,
        },
        "evidence_root_id": EVIDENCE_ROOT_ID,
        "root_order_manifest": {
            "path": "order_manifest.json",
            "manifest_id": root_manifest["manifest_id"],
            "sha256": root_manifest_sha,
        },
        "stage_manifests": stage_manifest_rows,
        "condition_families": family_rows,
        "design": {
            "design_id": target_versioned_id("d117-gamma-two-arm-abba-design"),
            "analysis_type": "comparative_contrast",
            "null_alias": False,
            "unit_of_analysis": "abba_block_arm_mean_difference",
            "difference_orientation": "condition_b_minus_condition_a",
            "sampling_plan": {
                "design": "fixed_n",
                "planned_n_blocks": N_BLOCKS,
                "freeze_basis": "frozen_before_measurement",
                "allowed_replacement_reasons": [],
            },
            "randomization": {
                # The ABBA arm order is deterministic: assignment is fixed by
                # position, not drawn. No randomization reference distribution
                # exists, so the licensed production result is "not required";
                # label-swap schemes would assert unratified exchangeability.
                "scheme": "deterministic_rotation",
                "exchangeability": "none",
                "seed": None,
            },
        },
        "replacement_policy": {
            "outcome_dependent_top_up": "forbidden",
            "science_member_replacements": 0,
            "allowed_replacement_reasons": [],
        },
        "families": [
            {
                "family_id": analysis_family_id,
                "family_instance_id": family_instance_id,
                "plan_id": PLAN_ID,
                "claim_role": "primary",
                "metric_tag": family_metric_tag,
                "multiplicity": {
                    "method": "holm",
                    "alpha": 0.05,
                    "q": None,
                    "m": 2,
                },
                "contrast_ids": [
                    contrast_id("decode"),
                    contrast_id(PREFILL_ARM),
                ],
            }
        ],
        "contrasts": [contrast("decode"), contrast(PREFILL_ARM)],
        "finalization_contract": {
            "contract_id": FINALIZATION_CONTRACT_ID,
            "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
            "namespace_rule_id": FINALIZED_NAMESPACE_RULE_ID,
            "output_basename_suffix": FINALIZED_BASENAME_SUFFIX,
            "required_attachments": required_attachments,
        },
        "frozen_semantics_sha256": "",
    }
    manifest = thread_generation_identity(manifest)
    projection = analysis_semantics_projection_v1(manifest)
    if projection.get("projection_rule_id") != SEMANTICS_PROJECTION_RULE_ID:
        raise ValueError("analysis semantics projection rule drifted")
    manifest["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(manifest)
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    return manifest


def build_tree(
    plan_sha: str,
    generator_sha: str,
    family_rows: list[dict[str, Any]],
    science_rows: list[dict[str, Any]],
    stage_graph: list[dict[str, Any]],
    external_inputs: list[dict[str, Any]],
    analysis_sha: str,
    declaration_sha: str,
    decode_workload_sha: str,
) -> dict[str, Any]:
    identity_units = []
    producer_plans = {
        "A": {
            "plan_id": (
                f"plan-d117-floor-{MODEL_ID_TOKENS['A']}-"
                f"decode-prefill-p{PREFILL_LENGTH}-v5"
            ),
            "path": f"../{FLOOR_PACKS['A'].name}/calibration_plan.json",
        },
        "B": {
            "plan_id": (
                f"plan-d117-floor-{MODEL_ID_TOKENS['B']}-"
                f"decode-prefill-p{PREFILL_LENGTH}-v5"
            ),
            "path": f"../{FLOOR_PACKS['B'].name}/calibration_plan.json",
        },
    }
    for arm, measurement_arm in (
        ("A", "decode"),
        ("A", PREFILL_ARM),
        ("B", "decode"),
        ("B", PREFILL_ARM),
    ):
        family = (
            DECODE_FAMILIES[arm]["condition_family_id"]
            if measurement_arm == "decode"
            else PREFILL_FAMILY_IDS[arm]
        )
        identity_units.append(
            {
                "identity_unit_id": f"{arm}/{measurement_arm}",
                "producer_plan_reference": producer_plans[arm],
                "consumer_bindings": [
                    {
                        "arm": arm,
                        "family": family,
                        "measurement_arm": measurement_arm,
                    }
                ],
                "declared_identity": {
                    "hardware_target": HARDWARE["id"],
                    "runtime_backend": HARDWARE["runtime_backend"],
                    "telemetry_backend": HARDWARE["telemetry_backend"],
                    "model_name": MODELS[arm]["name"],
                    "model_source": MODELS[arm]["source"],
                    "model_revision": MODELS[arm]["revision"],
                    "quantization": dict(QUANTIZATION),
                    "workload_profile": declared_identity_workload_profile(
                        measurement_arm, arm
                    ),
                },
                "config_inventory": [
                    {
                        "path": Path(row["config_path"]).as_posix(),
                        "sha256": row["config_sha256"],
                    }
                    for row in science_rows
                    if row["arm"] == arm and row["measurement_arm"] == measurement_arm
                ],
                "model_runtime_config": {
                    "model_artifact_sha256": None,
                    "runtime_identity_sha256": None,
                    "config_set_sha256": None,
                },
            }
        )
    identity_pin_projection = validate_identity_pin_projection(
        {
            "work_order": IDENTITY_PIN_PROJECTION_WORK_ORDER,
            "mode": "derive_never_operator_enter",
            "state": "unprojected",
            "required_before_arm": True,
            "derivation_contract": IDENTITY_PIN_DERIVATION_CONTRACT,
            "identity_units": identity_units,
            "projection_receipt": None,
            "supersedes": [],
        }
    )
    return {
        "schema_version": TREE_SCHEMA,
        # The D-134 plan-tree sidecar pins this artifact by SHA.
        "draft_status": emitted_draft_status(),
        "plan": {
            "path": "calibration_plan.json",
            "plan_id": PLAN_ID,
            "actual_sha256": plan_sha,
            "declared_sha256": plan_sha,
            "sidecar_path": "calibration_plan.sha256",
            "sidecar_sha256": sha256_bytes(sidecar_bytes(plan_sha, "calibration_plan.json")),
        },
        "generator": {
            "path": (PACK_REL / "generate_configs.py").as_posix(),
            "sha256": generator_sha,
        },
        "window_identity": {"window_id": PLAN_ID, "evidence_root_id": EVIDENCE_ROOT_ID},
        "roots": {"claim_leaf": CLAIM_ROOT_LEAF, "bound_leaf": BOUND_ROOT_LEAF},
        "reference_cadence": {
            "authority": REFERENCE_CADENCE_AUTHORITY,
            "binding_40_member_rule": (
                "one midpoint reference between two 20-member halves of each ABBA arm"
            ),
            "two_arm_interpretation": "arm_midpoints_plus_arm_boundary",
            "freeze_ratification": emitted_freeze_ratification(),
        },
        "campaign_policy": {
            "path": POLICY_PATH.as_posix(),
            "sha256": repo_sha(POLICY_PATH),
        },
        "acceptance_policy": {
            "selection": "issued_d116_artifact_only",
            "issued_artifact_id": acceptance_pin()["acceptance_id"],
            "issued_artifact_sha256": acceptance_pin()["artifact_sha256"],
            "issued_derivation_sha256": acceptance_pin()["derivation_sha256"],
            "issued_artifact_reopened": False,
            "arming_dependencies": [
                "impl/d117-postcollection-trust landed and mint bar lifted",
                "U2 successor registry available",
                "reason-code unit resolved",
                "U11 identity-pin projection receipt available",
                "U8 readiness validation passed",
                "U10 aggregate floor artifact available for decode declaration binding",
            ],
        },
        "condition_families": family_rows,
        "science": science_rows,
        "stage_graph": stage_graph,
        "external_inputs": external_inputs,
        "attempt_policy": {
            "calibration_retries": 0,
            "science_member_replacements": 0,
            "outcome_dependent_top_up": "forbidden",
            "failure_semantics": "abort_window_and_demote_to_non_claim_bearing",
            "retry_commands_present": False,
        },
        "arm_attachments": {
            "arm_readiness": generation_arm_readiness_attachment(),
            "launch": {
                "schema_version": "joulewise.stage_launch_bindings.v1",
                "closed_bindings": {
                    "repo_root": "existing_absolute_directory",
                    "ledger_path": "existing_absolute_file",
                    "claim_runs_root": "fresh_absolute_directory_with_declared_leaf",
                    "bound_runs_root": "fresh_absolute_directory_with_declared_leaf",
                    "operator_log_root": "absolute_directory",
                    "pre_calibration_dir": "absolute_directory",
                    "post_calibration_dir": "absolute_directory",
                    "claim_backup_destination": "absolute_path",
                    "bound_backup_destination": "absolute_path",
                    "bracket_session_id": "non_path_string",
                    "pre_attempt_id": "non_path_string",
                    "post_attempt_id": "non_path_string",
                    "identity_epoch_json": "authenticated_absolute_file",
                    "t1_bindings_json": "authenticated_absolute_file",
                },
                "calibration_directory_relation": {
                    "pre": "claim_runs_root/instrument_validation/pre_attempt_id",
                    "post": "claim_runs_root/instrument_validation/post_attempt_id",
                },
            },
            "absolute_roots": empty_slot("TODO(U8): materialize fresh absolute roots at arm"),
            "selected_acceptance": empty_slot("TODO(U2/U8): select authenticated acceptance at arm"),
            "identity_pin_projection": identity_pin_projection,
            "aggregate_floor_artifact_sha256": empty_slot(
                "TODO(U10/U8): validate and attach exact aggregate artifact bytes at arm"
            ),
            "receipt_oracle": derive_bracket_session_receipt_oracle(),
            "prefill_phase_recording_proof": empty_slot(
                "TODO(lead): re-run the plan-factory amendment-5 desk proof from custodied "
                f"{MODEL_A['name']} and {MODEL_B['name']} bundles before ratification"
            ),
            "readiness_record": empty_slot("TODO(U8): validate the exact draft after all gates land"),
        },
        "closeout_attachments": {
            "bracket_binding_sha256": empty_slot(
                "TODO(postcollection): populate from the completed bracket session"
            ),
            "terminal_committed_head": empty_slot(
                "TODO(postcollection): populate from the committed terminal head"
            ),
            "whole_window_verdict_sha256": empty_slot("TODO(postcollection): issue only after collection"),
            "evaluation_basis_sha256": empty_slot("TODO(postcollection): derive exact 80-member basis"),
            "claim_backup_receipt": empty_slot("TODO(postcollection): verified backup receipt"),
            "bound_backup_receipt": empty_slot("TODO(postcollection): verified backup receipt"),
        },
        "downstream_contract": {
            "analysis_manifest_path": "analysis_manifest_v3.json",
            "analysis_manifest_sha256": analysis_sha,
            "consumer_family_declaration_path": "consumer_family_declaration.json",
            "consumer_family_declaration_sha256": declaration_sha,
            "binding_mode": "declaration_only",
        },
        "decode_workload": {
            "path": "decode_workload_candidate.json",
            "sha256": decode_workload_sha,
            "assignment_rule_id": "d166_block_prompt_cycle.v1",
        },
        "runtime_budget": {
            # The D-134 plan-tree sidecar pins this nested field by SHA.
            "draft_status": emitted_draft_status(),
            "decode": {
                "members": MEMBERS_PER_ARM,
                "minutes_with_margin": 168.0,
                "authority": REFERENCE_CADENCE_AUTHORITY,
                "prompt_assignment": {
                    "rule_id": "d166_block_prompt_cycle.v1",
                    "rule": "prompt_index = (block_number - 1) mod prompt_count",
                    "same_prompt_for_all_a_and_b_members_in_block": True,
                    "prompt_count": len(DECODE_PROFILE["prompts"]),
                },
            },
            PREFILL_ARM: {
                "members": MEMBERS_PER_ARM,
                "core_minutes_before_margin": None,
                "minutes_with_20_percent_margin": None,
                "budget_status": "EMPTY-PENDING-D162-G2-SHAKEDOWN",
                "authority": (
                    "D-166 as amended selects length and budget from the G2-a record"
                ),
            },
            "interior_reference_augmentation": {
                "additional_references": 2,
                "core_minutes_before_margin": 10.0,
                "minutes_with_20_percent_margin": 12.0,
                "placement": [
                    "after_decode_member_40_arm_boundary",
                    "after_prefill_member_20_arm_midpoint",
                ],
                "authority": REFERENCE_CADENCE_AUTHORITY,
                "freeze_ratification": emitted_freeze_ratification(),
            },
            "combined_minutes_with_margin": None,
            "combined_derivation": (
                "EMPTY until the D-166 G2-a sweep supplies the selected prefill budget"
            ),
            "member_replacement_authority": False,
        },
    }


def validate_gamma_identity_unit_roster(tree: Mapping[str, Any]) -> None:
    """Enforce R-7's exact ordered GAMMA roster and producer-plan mapping."""

    expected = [
        (
            f"{arm}/{measurement_arm}",
            {
                "plan_id": (
                    f"plan-d117-floor-{MODEL_ID_TOKENS[arm]}-"
                    f"decode-prefill-p{PREFILL_LENGTH}-v5"
                ),
                "path": f"../{FLOOR_PACKS[arm].name}/calibration_plan.json",
            },
        )
        for arm, measurement_arm in (
            ("A", "decode"),
            ("A", PREFILL_ARM),
            ("B", "decode"),
            ("B", PREFILL_ARM),
        )
    ]
    try:
        units = tree["arm_attachments"]["identity_pin_projection"]["identity_units"]
    except (KeyError, TypeError) as exc:
        raise ValueError("gamma_identity_unit_roster_invalid: roster is absent") from exc
    observed = [
        (unit.get("identity_unit_id"), unit.get("producer_plan_reference"))
        for unit in units
        if isinstance(unit, Mapping)
    ]
    if observed != expected:
        raise ValueError(
            "gamma_identity_unit_roster_invalid: expected ordered "
            + ", ".join(unit_id for unit_id, _producer in expected)
        )


def readme_bytes() -> bytes:
    oracle = derive_bracket_session_receipt_oracle()
    identity = active_generation()
    version = identity.family_suffix.removeprefix("_")
    regeneration_command = (
        "python configs/campaigns/d117_contrast_v5/generate_configs.py "
        f"--panel {PANEL_FILE_ARGUMENT} --model-a {MODEL_IDS['A']} "
        f"--model-b {MODEL_IDS['B']} --decode-workload "
        f"{DECODE_WORKLOAD_FILE_ARGUMENT} --prefill-length {PREFILL_LENGTH} "
        f"--prefill-prompt-pin {PREFILL_PIN_FILE_ARGUMENT}"
    )
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
        prefill_floor_ids = [
            producer_floor_artifact_id(PREFILL_ARM, arm) for arm in ("A", "B")
        ]
        content = f"""# D-117 gamma contrast pack {version} — status governed by the D-134 freeze receipt

{identity_statement}This description does not carry freeze status. The committed D-134 freeze
receipt and its plan-tree attachment are authoritative for this pack's frozen
state; the receipt pins `calibration_plan.json` by SHA, so this text and every
serialized status field stay exactly as generated on both sides of the freeze.
The generated `calibration_plan.json` and `plan_tree.json` carry
`draft_status = {SUCCESSOR_EMITTED_STATUS}`; the prospective
`analysis_manifest_v3.json` instead carries `freeze_status = frozen`.
An external unexpired PASS/GO arm receipt is required before launch.

This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast over the D-166 pinned real-prompt profile and the 40-member
{PREFILL_LENGTH}-token prefill ABBA contrast. It makes
no data, verdict, receipt, or artifact-byte claim.

Authority order is D-117, D-122, D-123, D-124, D-125, D-139, D-157, D-165,
then D-166. D-166 supersedes the synthetic decode prompt and p256 prefill text. The
plan tree uses the shared `joulewise.d117_plan_tree.v1` schema family.

The binding 40-member cadence is
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` §6, “U7 — gamma
implementation session”: one midpoint between two 20-member ABBA halves. It
does not settle a mixed two-arm 80-member interpretation. This pack therefore
places references after science members 20, 40, and 60: both arm midpoints
plus the decode/prefill boundary; the committed D-134 freeze receipt and its
plan-tree attachment are the ratification authority for that reading.

The prefill prompt text is a labelled
`PROPOSED-PENDING-LEAD-RATIFICATION` candidate. The pack records the exact
generated hashes so regeneration can be tested; the D-134 freeze receipt, not
this text, is what pins them.

The consumer-family artifact is declaration-only. It names the deterministic
alpha/beta decode cell IDs but contains no aggregate-artifact SHA and is not a
pinset. Its dedicated {PREFILL_LENGTH}-token prefill floor dependencies are
`{prefill_floor_ids[0]}` and `{prefill_floor_ids[1]}`. Both use
`exact_stack_only` under `{EXACT_STACK_RULE_ID}`; no cross-length transport is
licensed or needed.

The receipt oracle is replay-derived from `{oracle['source']['module']}` and
records {oracle['receipt_count']} physical receipts for
{oracle['logical_operation_count']} logical operations per finalized pre/post
bracket session. Actual receipt bytes and the absolute terminal sequence remain
empty until arm and collection. Identity pins remain unpopulated pending U11.
Both shared-edge ABBA contrast cells register the canonical D-124 common-mode
floor estimator treatment required to match their floor-calibration cells.

Regenerate or check:

```text
{regeneration_command}
{regeneration_command} --check
```
"""
        return thread_generation_identity(content).encode("utf-8")
    content = f"""# D-117 gamma contrast pack {version} — unfrozen draft

{identity_statement}This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast and the D-166 40-member {PREFILL_LENGTH}-token prefill ABBA contrast. It is
not armable and makes no data, verdict, receipt, or artifact-byte claim.

Authority order is D-117, D-122, D-123, D-124, then D-125. D-122 supersedes
the older design-memo and plan-factory decode-only text. The plan tree uses
the shared `joulewise.d117_plan_tree.v1` schema family and every top-level
artifact declares `draft_status = unfrozen_draft`.

The binding 40-member cadence is
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` §6, “U7 — gamma
implementation session”: one midpoint between two 20-member ABBA halves. It
does not settle a mixed two-arm 80-member interpretation. This draft therefore
places references after science members 20, 40, and 60: both arm midpoints
plus the decode/prefill boundary, pending lead ratification at freeze.

The prefill prompt text is a labelled
`PROPOSED-PENDING-LEAD-RATIFICATION` candidate. The pack records exact draft
hashes so regeneration can be tested, not as a hash-freeze claim.

The consumer-family artifact is declaration-only. It names the deterministic
alpha/beta decode cell IDs but contains no aggregate-artifact SHA and is not a
pinset. A {PREFILL_LENGTH}-token prefill floor or a ruled transport rule remains
an explicit EMPTY slot.

The receipt oracle is replay-derived from `{oracle['source']['module']}` and
records {oracle['receipt_count']} physical receipts for
{oracle['logical_operation_count']} logical operations per finalized pre/post
bracket session. Actual receipt bytes and the absolute terminal sequence remain
empty until arm and collection. Identity pins remain EMPTY pending U11.
Both shared-edge ABBA contrast cells register the canonical D-124 common-mode
floor estimator treatment required to match their floor-calibration cells.

Regenerate or check:

```text
{regeneration_command}
{regeneration_command} --check
```
"""
    return thread_generation_identity(content).encode("utf-8")


def generate(
    output_repo_root: Path,
    identity: GenerationIdentity | None = None,
) -> dict[str, str]:
    with generation_context(identity or GenerationIdentity()):
        output_repo_root.mkdir(parents=True, exist_ok=True)
        outputs = validate_generation_output_inventory(active_generation())
        validate_generation_write_boundary(output_repo_root, outputs)
        with tempfile.TemporaryDirectory(
            prefix=".d117-v5-stage-", dir=output_repo_root
        ) as temporary:
            staging_root = Path(temporary)
            hashes = _generate(staging_root)
            for relative in sorted(
                outputs,
                key=lambda path: path.as_posix(),
            ):
                write_bytes(
                    output_repo_root / relative,
                    (staging_root / relative).read_bytes(),
                )
            return hashes


def _generate(output_repo_root: Path) -> dict[str, str]:
    outputs = validate_generation_output_inventory(active_generation())
    validate_generation_write_boundary(output_repo_root, outputs)
    if active_generation().preserve_current_frozen_bytes:
        for relative in sorted(outputs, key=lambda path: path.as_posix()):
            write_bytes(
                output_repo_root / relative,
                (REPO_ROOT / relative).read_bytes(),
            )
        pack_root = REPO_ROOT / active_generation().pack_rel
        return {
            "plan_sha256": file_sha256(pack_root / "calibration_plan.json"),
            "tree_sha256": file_sha256(pack_root / "plan_tree.json"),
            "analysis_sha256": file_sha256(pack_root / "analysis_manifest_v3.json"),
            "prompt_sha256": file_sha256(pack_root / "prefill_prompt_candidate.json"),
            "consumer_declaration_sha256": file_sha256(
                pack_root / "consumer_family_declaration.json"
            ),
        }
    out = output_repo_root / active_generation().pack_rel
    out.mkdir(parents=True, exist_ok=True)
    generator_bytes = embedded_generator_bytes()
    generator_sha = (
        preserved_generator_sha256()
        if active_generation().preserve_current_frozen_bytes
        else sha256_bytes(generator_bytes)
    )
    if not active_generation().preserve_current_frozen_bytes:
        write_bytes(out / "generate_configs.py", generator_bytes)

    family_bytes, domain_hashes = build_condition_families()
    for key, data in family_bytes.items():
        write_bytes(out / family_relpath(*key), data)

    prompt_bytes = render_json(prompt_candidate())
    prompt_sha = sha256_bytes(prompt_bytes)
    write_bytes(out / "prefill_prompt_candidate.json", prompt_bytes)

    decode_workload_bytes = render_json(decode_workload_candidate())
    decode_workload_sha = sha256_bytes(decode_workload_bytes)
    write_bytes(out / "decode_workload_candidate.json", decode_workload_bytes)
    for arm in ("A", "B"):
        for prompt_index in range(len(DECODE_PROFILE["prompts"])):
            suite_bytes = render_suite_manifest_bytes(
                decode_suite_manifest(arm, prompt_index)
            )
            write_bytes(out / decode_suite_relpath(arm, prompt_index), suite_bytes)

    declaration_bytes = render_json(consumer_declaration())
    declaration_sha = sha256_bytes(declaration_bytes)
    write_bytes(out / "consumer_family_declaration.json", declaration_bytes)

    runs, by_stage = build_runs()
    plan = build_plan(runs, family_bytes, domain_hashes, prompt_sha, declaration_sha)
    plan_bytes = render_json(plan)
    plan_sha = sha256_bytes(plan_bytes)
    write_bytes(out / "calibration_plan.json", plan_bytes)
    write_bytes(out / "calibration_plan.sha256", sidecar_bytes(plan_sha, "calibration_plan.json"))

    root_entries: list[dict[str, Any]] = []
    stage_manifest_rows: list[dict[str, Any]] = []
    stage_manifest_refs: dict[str, dict[str, Any]] = {}
    root_index = 1
    for stage_number, stage in enumerate(STAGE_SPECS, start=1):
        stage_id = stage["subcampaign_id"]
        local_entries: list[dict[str, Any]] = []
        for local_index, run in enumerate(by_stage[stage_id], start=1):
            config_bytes = render_json(config_for(run, plan_sha))
            config_sha = sha256_bytes(config_bytes)
            write_bytes(out / stage_id / run["filename"], config_bytes)
            local_entries.append(manifest_entry(run, local_index, run["filename"], config_sha))
            root_entries.append(
                manifest_entry(run, root_index, f"{stage_id}/{run['filename']}", config_sha)
            )
            root_index += 1
        stage_manifest = {
            "schema_version": ORDER_SCHEMA,
            # The frozen plan-tree manifest reference pins these bytes by SHA.
            "draft_status": emitted_draft_status(),
            "manifest_id": f"d117-gamma-{stage_id.replace('_', '-')}-order-v1",
            "plan_id": PLAN_ID,
            "calibration_plan_sha256": plan_sha,
            "successor_stage_id": REFERENCE_AFTER_STAGE[stage_id],
            "ordering_note": (
                f"Fixed contiguous A/B/B/A blocks {stage['first_block']}-"
                f"{stage['last_block']} for {stage['measurement_arm']}; numbering "
                "does not reset across the split."
            ),
            "planned_n_bundles": len(local_entries),
            "executed_order": local_entries,
        }
        stage_manifest_bytes = render_json(stage_manifest)
        stage_manifest_sha = sha256_bytes(stage_manifest_bytes)
        stage_manifest_path = Path(stage_id) / "order_manifest.json"
        write_bytes(out / stage_manifest_path, stage_manifest_bytes)
        manifest_row = {
            "index": stage_number,
            "subcampaign_id": stage_id,
            "role": stage["role"],
            "optional": False,
            "planned_n_bundles": len(local_entries),
            "manifest_path": stage_manifest_path.as_posix(),
            "manifest_id": stage_manifest["manifest_id"],
            "manifest_sha256": stage_manifest_sha,
            "successor_stage_id": REFERENCE_AFTER_STAGE[stage_id],
        }
        stage_manifest_rows.append(manifest_row)
        stage_manifest_refs[stage_id] = {
            "path": stage_manifest_path.as_posix(),
            "manifest_id": stage_manifest["manifest_id"],
            "sha256": stage_manifest_sha,
        }

    root_manifest = {
        "schema_version": ORDER_SCHEMA,
        # The frozen gamma analysis manifest pins the root manifest by SHA.
        "draft_status": emitted_draft_status(),
        "manifest_id": f"d117-gamma-{PAIR_TOKEN}-order-v1",
        "plan_id": PLAN_ID,
        "calibration_plan_sha256": plan_sha,
        "planned_n_bundles": len(root_entries),
        "subcampaign_order": stage_manifest_rows,
        "reference_cadence": {
            "authority": REFERENCE_CADENCE_AUTHORITY,
            "binding_40_member_rule": (
                "one midpoint reference between two 20-member halves of each ABBA arm"
            ),
            "two_arm_interpretation": "arm_midpoints_plus_arm_boundary",
            "freeze_ratification": emitted_freeze_ratification(),
        },
        "interior_reference_stages": [
            {
                "after_science_member": 20,
                "stage_id": "gamma-reference-decode-midpoint",
                "purpose": "decode_arm_midpoint",
            },
            {
                "after_science_member": 40,
                "stage_id": "gamma-reference-arm-boundary",
                "purpose": "decode_prefill_arm_boundary",
            },
            {
                "after_science_member": 60,
                "stage_id": "gamma-reference-prefill-midpoint",
                "purpose": "prefill_arm_midpoint",
            },
        ],
        "executed_order": root_entries,
    }
    root_manifest_bytes = render_json(root_manifest)
    root_manifest_sha = sha256_bytes(root_manifest_bytes)
    write_bytes(out / "order_manifest.json", root_manifest_bytes)

    family_rows = family_tree_rows(family_bytes, domain_hashes)
    analysis = build_analysis_manifest(
        plan_sha,
        root_manifest,
        root_manifest_sha,
        stage_manifest_rows,
        root_entries,
        family_rows,
        prompt_sha,
        declaration_sha,
    )
    analysis_bytes = render_json(analysis)
    analysis_sha = sha256_bytes(analysis_bytes)
    write_bytes(out / "analysis_manifest_v3.json", analysis_bytes)

    external_inputs = [
        build_external_manifest("neg8_bound_corpus", NEG8_MANIFEST_PATH),
        {
            "input_id": "neg8_settled_corpus",
            "path": NEG8_CORPUS_PATH.as_posix(),
            "sha256": repo_sha(NEG8_CORPUS_PATH),
        },
        build_external_manifest("start_references", START_REF_MANIFEST_PATH),
        build_external_manifest("midpoint_reference", MID_REF_MANIFEST_PATH),
        build_external_manifest("end_references", END_REF_MANIFEST_PATH),
    ]
    stage_graph = build_stage_graph(stage_manifest_refs)
    science_rows = [
        {
            "ordinal": entry["index"],
            "stage_id": "gamma-science-" + next(
                stage["subcampaign_id"].replace("_", "-")
                for stage in STAGE_SPECS
                if entry["config"].startswith(stage["subcampaign_id"] + "/")
            ),
            "config_path": entry["config"],
            "config_sha256": entry["config_sha256"],
            "run_id": entry["run_id"],
            "role": entry["role"],
            "measurement_arm": entry["measurement_arm"],
            "block_id": entry["block_id"],
            "block_index": entry["block_index"],
            "position": entry["position"],
            "arm": entry["arm"],
        }
        for entry in root_entries
    ]
    tree = build_tree(
        plan_sha,
        generator_sha,
        family_rows,
        science_rows,
        stage_graph,
        external_inputs,
        analysis_sha,
        declaration_sha,
        decode_workload_sha,
    )
    validate_gamma_identity_unit_roster(tree)
    tree_bytes = (
        (REPO_ROOT / PACK_REL / "plan_tree.json").read_bytes()
        if active_generation().preserve_current_frozen_bytes
        else render_json(tree)
    )
    tree_sha = sha256_bytes(tree_bytes)
    write_bytes(out / "plan_tree.json", tree_bytes)
    write_bytes(
        out / "plan_tree.sha256",
        (
            (REPO_ROOT / PACK_REL / "plan_tree.sha256").read_bytes()
            if active_generation().preserve_current_frozen_bytes
            else sidecar_bytes(tree_sha, "plan_tree.json")
        ),
    )
    write_bytes(out / "README.md", readme_bytes())

    validate_prompt_realization_registration(out)

    analysis_value = json.loads(
        (out / "analysis_manifest_v3.json").read_text(encoding="utf-8")
    )
    refusals = validate_prospective_analysis_manifest_v3(
        analysis_value,
        manifest_dir=out,
        plan_tree_path=out / "plan_tree.json",
    )
    if refusals:
        raise ValueError(
            "analysis_manifest_v3_refused: "
            + "; ".join(
                f"{refusal.reason_code}: {refusal.detail}" for refusal in refusals
            )
        )

    return {
        "plan_sha256": plan_sha,
        "tree_sha256": tree_sha,
        "analysis_sha256": analysis_sha,
        "prompt_sha256": prompt_sha,
        "consumer_declaration_sha256": declaration_sha,
    }


def validate_prompt_realization_registration(pack_root: Path) -> None:
    """Refuse a closed pack whose realized-prompt registration is not joined."""

    def refuse(code: str, detail: str) -> None:
        raise ValueError(f"{code}: {detail}")

    try:
        candidate = json.loads(
            (pack_root / "prefill_prompt_candidate.json").read_text(
                encoding="utf-8"
            )
        )
        per_model = candidate["token_count_basis"]["per_model"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        refuse("prompt_realization_registration_invalid", f"prompt candidate: {exc}")
    if not isinstance(per_model, list):
        refuse(
            "prompt_realization_registration_invalid",
            "prompt candidate per_model must be a list",
        )

    candidate_by_model: dict[str, dict[str, Any]] = {}
    for row in per_model:
        if not isinstance(row, dict) or not isinstance(row.get("model_id"), str):
            refuse(
                "prompt_realization_registration_invalid",
                "prompt candidate per_model row is malformed",
            )
        model_id = row["model_id"]
        token_ids = row.get("token_ids")
        token_count = row.get("token_count")
        token_ids_sha256 = row.get("token_ids_sha256")
        if (
            model_id in candidate_by_model
            or not isinstance(token_ids, list)
            or isinstance(token_count, bool)
            or not isinstance(token_count, int)
            or token_count <= 0
            or token_count != len(token_ids)
            or not isinstance(token_ids_sha256, str)
            or len(token_ids_sha256) != 64
            or any(character not in "0123456789abcdef" for character in token_ids_sha256)
            or token_ids_sha256 != _token_ids_sha256(token_ids)
        ):
            refuse(
                "prompt_realization_registration_invalid",
                f"prompt candidate row for {model_id!r} is invalid",
            )
        candidate_by_model[model_id] = row

    family_counts: dict[str, int] = {}
    for arm in ("A", "B"):
        try:
            family = json.loads(
                (pack_root / family_relpath(PREFILL_ARM, arm)).read_text(
                    encoding="utf-8"
                )
            )
            family_count = family["workload_profile"]["prompt_tokens"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            refuse(
                "prompt_realization_registration_invalid",
                f"prefill family {arm}: {exc}",
            )
        if (
            isinstance(family_count, bool)
            or not isinstance(family_count, int)
            or family_count <= 0
        ):
            refuse(
                "prompt_realization_registration_invalid",
                f"prefill family {arm} prompt_tokens is invalid",
            )
        family_counts[arm] = family_count

    expected_keys = {
        "schema_version",
        "token_hash_domain",
        "token_count",
        "token_ids_sha256",
    }
    config_paths = sorted(
        path
        for path in pack_root.glob("[0-9][0-9]_*/*.json")
        if path.name != "order_manifest.json"
    )
    if not config_paths:
        refuse(
            "prompt_realization_registration_missing", "no generated configs"
        )
    for config_path in config_paths:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            workload = config["workload_profile"]
            model_name = config["model"]["name"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            refuse(
                "prompt_realization_registration_invalid",
                f"{config_path.relative_to(pack_root)}: {exc}",
            )
        is_prefill = isinstance(workload.get("prompt_text"), str)
        if not is_prefill:
            if "prompt_token_expectation" in workload:
                refuse(
                    "prompt_realization_registration_invalid",
                    f"{config_path.relative_to(pack_root)}: decode config carries expectation",
                )
            continue
        if "prompt_token_expectation" not in workload:
            refuse(
                "prompt_realization_registration_missing",
                f"{config_path.relative_to(pack_root)}",
            )
        expectation = workload.get("prompt_token_expectation")
        if not isinstance(expectation, dict) or set(expectation) != expected_keys:
            refuse(
                "prompt_realization_registration_invalid",
                f"{config_path.relative_to(pack_root)}: expectation schema",
            )
        count = expectation.get("token_count")
        token_hash = expectation.get("token_ids_sha256")
        if (
            expectation.get("schema_version")
            != "joulewise.prompt_token_expectation.v1"
            or expectation.get("token_hash_domain")
            != "joulewise.prompt_token_ids.v1"
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count <= 0
            or not isinstance(token_hash, str)
            or len(token_hash) != 64
            or any(character not in "0123456789abcdef" for character in token_hash)
        ):
            refuse(
                "prompt_realization_registration_invalid",
                f"{config_path.relative_to(pack_root)}: expectation value",
            )
        matching_arms = [
            arm for arm in ("A", "B") if MODELS[arm]["name"] == model_name
        ]
        if len(matching_arms) != 1:
            refuse(
                "prompt_realization_registration_invalid",
                f"{config_path.relative_to(pack_root)}: model arm is unresolved",
            )
        arm = matching_arms[0]
        candidate_row = candidate_by_model.get(MODEL_IDS[arm])
        if not isinstance(candidate_row, dict):
            refuse(
                "prompt_realization_registration_invalid",
                f"{config_path.relative_to(pack_root)}: candidate row is missing",
            )
        if (
            count != candidate_row["token_count"]
            or token_hash != candidate_row["token_ids_sha256"]
            or count != family_counts[arm]
        ):
            refuse(
                "prompt_realization_registration_inconsistent",
                f"{config_path.relative_to(pack_root)}: config/candidate/family disagree",
            )


def actual_pack_paths(pack_root: Path) -> set[Path]:
    return {
        path.relative_to(pack_root)
        for path in pack_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def check(
    check_root: Path = REPO_ROOT,
    identity: GenerationIdentity | None = None,
) -> dict[str, str]:
    selected_identity = identity or GenerationIdentity()
    with tempfile.TemporaryDirectory(prefix="d117-gamma-check-") as temporary:
        temp_root = Path(temporary)
        hashes = generate(temp_root, selected_identity)
        generated = temp_root / selected_identity.pack_rel
        pack_root = check_root / selected_identity.pack_rel
        expected_paths = set(expected_pack_paths())
        generated_tree = json.loads(
            (generated / "plan_tree.json").read_text(encoding="utf-8")
        )
        freeze_reference = generated_tree["arm_attachments"]["arm_readiness"][
            "freeze_receipt"
        ]
        if freeze_reference is not None:
            freeze_path = Path(freeze_reference["path"])
            expected_paths |= {
                freeze_path,
                freeze_path.with_name(f"{freeze_path.name}.sha256"),
            }
            freeze_receipt = json.loads(
                (pack_root / freeze_path).read_text(encoding="utf-8")
            )
            for item in freeze_receipt["evidence"]:
                evidence_path = Path(item["path"])
                evidence_sidecar = (
                    evidence_path.with_suffix(".sha256")
                    if evidence_path.parent.name
                    == "identity_pin_projection.receipts"
                    else evidence_path.with_name(f"{evidence_path.name}.sha256")
                )
                expected_paths |= {evidence_path, evidence_sidecar}
                evidence_receipt = json.loads(
                    (pack_root / evidence_path).read_text(encoding="utf-8")
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
        observed_paths = actual_pack_paths(pack_root)
        missing = sorted(expected_paths - observed_paths)
        extras = sorted(observed_paths - expected_paths)
        if missing or extras:
            detail: list[str] = []
            if missing:
                detail.append("missing=" + ",".join(path.as_posix() for path in missing))
            if extras:
                detail.append("extras=" + ",".join(path.as_posix() for path in extras))
            raise ValueError("pack inventory differs: " + "; ".join(detail))
        for relative in expected_pack_paths(include_generator=False):
            expected_path = generated / relative
            actual_path = pack_root / relative
            if not expected_path.is_file():
                raise ValueError(f"generated expected path missing: {relative}")
            if not actual_path.is_file():
                raise ValueError(f"production expected path missing: {relative}")
            if expected_path.read_bytes() != actual_path.read_bytes():
                raise ValueError(f"production bytes differ from regeneration: {relative}")
        # The generator is source input, not generated output. Its SHA is embedded in
        # plan_tree.json; comparing the repository path to itself would prove nothing.
        return hashes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--panel", required=True, type=Path)
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument(
        "--decode-workload",
        type=Path,
        default=Path("configs/workloads/real_prompts_v1.json"),
    )
    parser.add_argument(
        "--prefill-length",
        type=int,
        choices=(512, 1024, 2048, 4096),
    )
    parser.add_argument("--prefill-prompt-pin", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_model_pair(
        args.panel,
        args.model_a,
        args.model_b,
        decode_workload_path=args.decode_workload,
        prefill_length=args.prefill_length,
        prefill_prompt_pin_path=args.prefill_prompt_pin,
    )
    identity = GenerationIdentity()
    hashes = (
        check(
            args.output_root.resolve() if args.output_root else REPO_ROOT,
            identity,
        )
        if args.check
        else generate(
            args.output_root.absolute() if args.output_root else REPO_ROOT,
            identity,
        )
    )
    mode = "checked" if args.check else "generated"
    status = identity.target_status
    identity_label = (
        status.replace("_", " ")
        if identity.target_ordinal == 1
        else identity.pack_id
    )
    print(
        f"{mode} D-117 gamma {identity_label}: "
        f"decode_members={MEMBERS_PER_ARM} {PREFILL_ARM}_members={MEMBERS_PER_ARM} "
        f"plan_sha256={hashes['plan_sha256']} tree_sha256={hashes['tree_sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
