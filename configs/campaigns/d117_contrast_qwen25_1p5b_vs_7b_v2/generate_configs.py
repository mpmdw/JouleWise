#!/usr/bin/env python3
"""Generate the unfrozen D-117 gamma contrast campaign draft."""

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
PACK_REL = Path("configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2")
CALIBRATION_PLAN_REFERENCE = "calibration_plan.json"
CURRENT_FAMILY_SUFFIX = "_v2"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.detection_floor import (  # noqa: E402
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    two_shared_edge_common_mode_registration,
)
from joulewise.floor_extraction import (  # noqa: E402
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
from joulewise.receipt_oracle import (  # noqa: E402
    derive_bracket_session_receipt_oracle,
)


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
CURRENT_FROZEN_RECEIPT_SHA256 = (
    "2ef73bf042f2f0e43d4e65fa4658f82c242269478cf68de05494456ba3d3106f"
)
CURRENT_FROZEN_GENERATOR_SHA256 = (
    "550035ae92199185e9ad21ae0277593e4821c1788f645ee5345bd6d3268a1c09"
)
PROMPT_STATUS = "PROPOSED-PENDING-LEAD-RATIFICATION"
EMPTY_STATUS = "EMPTY"
PLAN_SCHEMA = "joulewise.detection_floor_calibration_plan.v1"
ORDER_SCHEMA = "joulewise.order_manifest.v1"
TREE_SCHEMA = "joulewise.d117_plan_tree.v1"
PLAN_ID = "plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v2"
EVIDENCE_ROOT_ID = "evidence-d117-contrast-qwen25-1p5b-vs-7b-v2"
CLAIM_ROOT_LEAF = "runs_d117_contrast_qwen25_1p5b_vs_7b_v2"
BOUND_ROOT_LEAF = "runs_d117_contrast_qwen25_1p5b_vs_7b_v2_bound"
N_BLOCKS = 10
MEMBERS_PER_BLOCK = 4
MEMBERS_PER_ARM = N_BLOCKS * MEMBERS_PER_BLOCK
TOTAL_SCIENCE_MEMBERS = MEMBERS_PER_ARM * 2


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


ARM_READINESS_ATTACHMENT = plan_arm_readiness_attachment(
    REPO_ROOT / PACK_REL,
    "GAMMA",
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
    "plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v2",
    "evidence-d117-contrast-qwen25-1p5b-vs-7b-v2",
    "d117-qwen25-1p5b-vs-7b-gamma-consumer-v2",
    "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2",
    "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v2",
    "d117-qwen25-1p5b-decode-floor-v2",
    "d117-qwen25-7b-decode-floor-v2",
    "d117_floor_qwen25_1p5b_v2",
    "d117_floor_qwen25_7b_v2",
    "d117_contrast_qwen25_1p5b_vs_7b_v2",
    "d117-contrast-qwen25-1p5b-vs-7b-v2",
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
    source = (REPO_ROOT / PACK_REL / "generate_configs.py").read_text(
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
    identity = active_generation()
    return plan_arm_readiness_attachment(
        REPO_ROOT / identity.pack_rel,
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

MODEL_A = {
    "name": "Qwen2.5-1.5B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
    "weight_format": "mlx",
    "context_window": 32768,
}
MODEL_B = {
    "name": "Qwen2.5-7B-Instruct-4bit",
    "family": "qwen2.5",
    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
    "revision": "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
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
        "D-117 gamma Qwen2.5 1.5B-versus-7B contrast on the current M3 Max; "
        "normal powermetrics sampler set only"
    ),
}


def generation_hardware() -> dict[str, Any]:
    return {
        **HARDWARE,
        "notes": f"{HARDWARE['notes']}; pack status {emitted_draft_status()}.",
    }
SAMPLING = {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0}

DECODE_FAMILIES = {
    "A": {
        "condition_family_id": "sw-decode-a-qwen25-1p5b",
        "source": Path(
            "configs/campaigns/splitwise_decode_v1/condition_families/"
            "condition_family_sw_decode_a_qwen25_1p5b.json"
        ),
        "target_byte_sha256": (
            "3ff3a801d7f74ca3d3bd74d961aadde304e7fd1adc7940a39cf47ff0c40943cf"
        ),
        "target_domain_sha256": (
            "c13a3ebf5461ed9a442a8e67555f70301848d56a55ab766570d46ca067934f12"
        ),
    },
    "B": {
        "condition_family_id": "sw-decode-b-qwen25-7b",
        "source": Path(
            "configs/campaigns/splitwise_decode_v1/condition_families/"
            "condition_family_sw_decode_b_qwen25_7b.json"
        ),
        "target_byte_sha256": (
            "c153b8dcbae5761e1d39404e55415d0ed95072151fb98fe75bce3e2740d54b9e"
        ),
        "target_domain_sha256": (
            "5149a8552600341883439a73fa135caa0e6ba292544c7c6fe2e69674318df4e3"
        ),
    },
}
PREFILL_FAMILY_IDS = {
    "A": "sw-prefill-p256-a-qwen25-1p5b",
    "B": "sw-prefill-p256-b-qwen25-7b",
}
MODELS = {"A": MODEL_A, "B": MODEL_B}
MODEL_TAGS = {"A": "qwen25-1p5b-mlx", "B": "qwen25-7b-mlx"}

PROMPT_SENTENCE = "The plan remains easy to audit."
PROMPT_FINAL_SENTENCE = "The plan remains easy to audit and simple to review."
PREFILL_PROMPT_TEXT = " ".join([PROMPT_SENTENCE] * 35 + [PROMPT_FINAL_SENTENCE])
PREFILL_PROMPT_SHA256 = hashlib.sha256(PREFILL_PROMPT_TEXT.encode("utf-8")).hexdigest()
SHARED_TOKENIZER_JSON_SHA256 = (
    "a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf"
)
REFERENCE_CADENCE_AUTHORITY = (
    "docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md "
    "§6 U7 gamma implementation session"
)
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
        "subcampaign_id": "03_prefill_p256_contrast_blocks_01_05",
        "measurement_arm": "prefill_p256",
        "role": "prefill_p256_contrast_first_half",
        "first_block": 1,
        "last_block": 5,
    },
    {
        "subcampaign_id": "04_prefill_p256_contrast_blocks_06_10",
        "measurement_arm": "prefill_p256",
        "role": "prefill_p256_contrast_second_half",
        "first_block": 6,
        "last_block": 10,
    },
)

REFERENCE_AFTER_STAGE = {
    "01_decode_contrast_blocks_01_05": "gamma-reference-decode-midpoint",
    "02_decode_contrast_blocks_06_10": "gamma-reference-arm-boundary",
    "03_prefill_p256_contrast_blocks_01_05": "gamma-reference-prefill-midpoint",
    "04_prefill_p256_contrast_blocks_06_10": "gamma-reference-end",
}

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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
        prefix = "d117c15v7-decode-contrast"
    elif measurement_arm == "prefill_p256":
        prefix = "d117c15v7-prefill-p256-contrast"
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
        Path("prefill_prompt_candidate.json"),
        Path("condition_families/condition_family_sw_decode_a_qwen25_1p5b.json"),
        Path("condition_families/condition_family_sw_decode_b_qwen25_7b.json"),
        Path("condition_families/condition_family_sw_prefill_p256_a_qwen25_1p5b.json"),
        Path("condition_families/condition_family_sw_prefill_p256_b_qwen25_7b.json"),
    ]
    if include_generator:
        paths.append(Path("generate_configs.py"))
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
    prefix = "d117-decode" if measurement_arm == "decode" else "d117-prefill-p256"
    return f"{prefix}-contrast-b{block:02d}"


def family_id(measurement_arm: str, arm: str) -> str:
    if measurement_arm == "decode":
        return DECODE_FAMILIES[arm]["condition_family_id"]
    return PREFILL_FAMILY_IDS[arm]


def metric_for(measurement_arm: str) -> str:
    return "phase_energy_j.decode" if measurement_arm == "decode" else "phase_energy_j.prefill"


def workload_for(measurement_arm: str) -> dict[str, Any]:
    if measurement_arm == "decode":
        return {
            "name": "df_ph_decode",
            "repetitions": 1,
            "warmup_runs": 1,
            "prompt_tokens": 128,
            "output_tokens": 512,
        }
    return {
        "name": "df_ph_prefill_p256_candidate",
        "repetitions": 1,
        "warmup_runs": 1,
        "output_tokens": 512,
        "prompt_text": PREFILL_PROMPT_TEXT,
    }


def prefill_family_definition(arm: str) -> dict[str, Any]:
    return {
        "schema_version": "joulewise.condition_family_definition.v1",
        "condition_family_id": PREFILL_FAMILY_IDS[arm],
        "workload_profile": {
            "name": "df_ph_prefill_p256_candidate",
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


def build_condition_families() -> tuple[dict[tuple[str, str], bytes], dict[tuple[str, str], str]]:
    family_bytes: dict[tuple[str, str], bytes] = {}
    domain_hashes: dict[tuple[str, str], str] = {}
    for arm in ("A", "B"):
        source_bytes = (REPO_ROOT / DECODE_FAMILIES[arm]["source"]).read_bytes()
        if sha256_bytes(source_bytes) != DECODE_FAMILIES[arm]["target_byte_sha256"]:
            raise ValueError(f"decode family {arm} source byte SHA drifted")
        definition = json.loads(source_bytes.decode("utf-8"))
        domain_sha = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition)
        if domain_sha != DECODE_FAMILIES[arm]["target_domain_sha256"]:
            raise ValueError(f"decode family {arm} domain SHA drifted")
        family_bytes[("decode", arm)] = source_bytes
        domain_hashes[("decode", arm)] = domain_sha

        prefill_definition = prefill_family_definition(arm)
        errors = validate_condition_family_definition(prefill_definition)
        if errors:
            raise ValueError(f"prefill family {arm} is invalid: {'; '.join(errors)}")
        family_bytes[("prefill_p256", arm)] = render_json(prefill_definition)
        domain_hashes[("prefill_p256", arm)] = canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, prefill_definition
        )
    return family_bytes, domain_hashes


def family_relpath(measurement_arm: str, arm: str) -> Path:
    if measurement_arm == "decode":
        suffix = "1p5b" if arm == "A" else "7b"
        return Path(
            f"condition_families/condition_family_sw_decode_{arm.lower()}_qwen25_{suffix}.json"
        )
    suffix = "1p5b" if arm == "A" else "7b"
    return Path(
        f"condition_families/condition_family_sw_prefill_p256_{arm.lower()}_qwen25_{suffix}.json"
    )


def prompt_candidate() -> dict[str, Any]:
    return {
        "schema_version": "joulewise.d117_prompt_candidate.v1",
        # Q1 pins the p256 prompt artifact bytes and token-ID identity.
        "draft_status": emitted_draft_status(),
        "candidate_status": PROMPT_STATUS,
        "authority": {
            "prompt_length": "D-122 clause 1",
            "prompt_text": "TODO(lead): no named authority pins text",
        },
        "prompt_text": PREFILL_PROMPT_TEXT,
        "prompt_text_utf8_sha256": PREFILL_PROMPT_SHA256,
        "planned_token_count": 256,
        "token_count_basis": {
            "status": "LOCAL-TOKENIZER-ARTIFACT-VERIFIED-CANDIDATE",
            "shared_tokenizer_json_sha256": SHARED_TOKENIZER_JSON_SHA256,
            "model_artifacts_checked": [MODEL_A["name"], MODEL_B["name"]],
            "construction": (
                "35 seven-token repo-idiom sentences plus one eleven-token "
                "sentence under the shared Qwen2.5 tokenizer"
            ),
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
            "plan-factory frozen cross-pack vocabulary, amended in scope by D-122"
        ),
        "consumer_family_id": "d117-qwen25-1p5b-vs-7b-gamma-consumer-v2",
        "decode_floor_cells": {
            "condition_a": "d117-qwen25-1p5b-decode-floor-v2",
            "condition_b": "d117-qwen25-7b-decode-floor-v2",
            "derivation": "deterministic plan-factory floor artifact vocabulary",
            "floor_rule": "cross_stack_armwise_max.v1",
        },
        "prefill_p256_floor_dependency": {
            "cell_ids": empty_slot(
                "TODO(lead authority): D-122 does not identify ruled 256-token "
                "prefill floor cells",
                value=[],
            ),
            "transport_rule": empty_slot(
                "TODO(lead authority): D-122 does not ratify transport from the "
                "alpha/beta 128-token prefill floor cells to this 256-token estimand"
            ),
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
    positions = (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2"))
    for stage in STAGE_SPECS:
        stage_runs: list[dict[str, Any]] = []
        measurement_arm = stage["measurement_arm"]
        for block in range(stage["first_block"], stage["last_block"] + 1):
            for sequence_index, (arm, position) in enumerate(positions, start=1):
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
        "authorities": ["D-117", "D-122", "D-123", "D-124", "D-125"],
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
                    "workload": workload_for(measurement_arm),
                }
                for measurement_arm in ("decode", "prefill_p256")
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
                "cell_id": "d117-sw-decode-contrast-qwen25-1p5b-vs-7b",
                "measurement_arm": "decode",
                "kind": "comparative_contrast",
                "minimum_claim_n_blocks": N_BLOCKS,
                "metric": "phase_energy_j.decode",
                "target_precheck_path": ["phase", "decode"],
                "difference_orientation": "condition_b_minus_condition_a",
                "point_estimator": "abba_block_arm_mean_difference_t_v1",
                "floor_estimator_registration": two_shared_edge_common_mode_registration(),
                "test": "two_sided",
                "scientific_hypothesis_direction": "positive",
                "family_alpha": 0.05,
                "multiplicity": "Holm",
                "family_m": 1,
                "multiplicity_note": (
                    "family_m=1 is contingent on unresolved decode/prefill "
                    "family-cardinality ratification; see the prefill_p256 cell's "
                    "multiplicity TODO."
                ),
                "equivalence_margin": None,
                "mde": None,
                "ordered_blocks": ordered_blocks(runs, "decode"),
            },
            {
                "cell_id": "d117-sw-prefill-p256-contrast-qwen25-1p5b-vs-7b",
                "measurement_arm": "prefill_p256",
                "kind": "comparative_contrast",
                "minimum_claim_n_blocks": N_BLOCKS,
                "metric": "phase_energy_j.prefill",
                "target_precheck_path": ["phase", "prefill"],
                "difference_orientation": "condition_b_minus_condition_a",
                "point_estimator": "abba_block_arm_mean_difference_t_v1",
                "floor_estimator_registration": two_shared_edge_common_mode_registration(),
                "prompt_candidate": {
                    "path": "prefill_prompt_candidate.json",
                    "sha256": prompt_sha,
                    "status": PROMPT_STATUS,
                },
                "test": empty_slot(
                    "TODO(lead authority): D-122 requires the arm but does not pin "
                    "the prefill inferential test"
                ),
                "family_alpha": empty_slot(
                    "TODO(lead authority): ratify the prefill contrast family alpha"
                ),
                "multiplicity": empty_slot(
                    "TODO(lead authority): ratify whether decode and prefill share a family"
                ),
                "family_m": empty_slot(
                    "TODO(lead authority): ratify multiplicity cardinality"
                ),
                "equivalence_margin": None,
                "mde": None,
                "ordered_blocks": ordered_blocks(runs, "prefill_p256"),
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
    prompt_tags = (
        [
            "prompt-tokens=256",
            f"prompt-text-sha256={PREFILL_PROMPT_SHA256}",
            f"prompt-status={PROMPT_STATUS}",
        ]
        if run["measurement_arm"] == "prefill_p256"
        else []
    )
    tags = [
        "phase2",
        "d117-contrast-qwen25-1p5b-vs-7b-v2",
        "production-window",
        "comparative-contrast",
        f"measurement-arm={run['measurement_arm']}",
        f"df-condition={run['condition_family_id']}",
        f"calibration-plan-sha256={plan_sha256}",
        f"calibration-abba-block-id={run['block_id']}",
        f"calibration-abba-label={run['arm']}",
        f"calibration-abba-sequence-index={run['position_in_block']}",
        *prompt_tags,
    ]
    if active_generation().target_is_successor_family:
        tags.append("launch_lineage_required")
    return {
        "schema_version": "0.1",
        "run_id": run["run_id"],
        "model": MODELS[run["arm"]],
        "quantization": QUANTIZATION,
        "hardware_target": generation_hardware(),
        "workload_profile": workload_for(run["measurement_arm"]),
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
    for measurement_arm in ("decode", "prefill_p256"):
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
    def contrast(measurement_arm: str) -> dict[str, Any]:
        entries = [entry for entry in all_entries if entry["measurement_arm"] == measurement_arm]
        common: dict[str, Any] = {
            "contrast_id": (
                f"ctr-d117-{measurement_arm.replace('_', '-')}-qwen25-1p5b-vs-7b"
            ),
            "measurement_arm": measurement_arm,
            "metric": metric_for(measurement_arm),
            "target_precheck_path": ["phase", "decode" if measurement_arm == "decode" else "prefill"],
            "condition_a_id": family_id(measurement_arm, "A"),
            "condition_b_id": family_id(measurement_arm, "B"),
            "difference_orientation": "condition_b_minus_condition_a",
            "point_estimator": "abba_block_arm_mean_difference_t_v1",
            "floor_estimator_registration": two_shared_edge_common_mode_registration(),
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
        }
        if measurement_arm == "decode":
            common.update(
                {
                    "test": "two_sided",
                    "scientific_hypothesis_direction": "positive",
                    "multiplicity": {
                        "method": "Holm",
                        "alpha": 0.05,
                        "m": 1,
                        "note": (
                            "family_m=1 is contingent on unresolved decode/prefill "
                            "family-cardinality ratification; see the prefill_p256 "
                            "contrast multiplicity TODO."
                        ),
                    },
                    "equivalence_margin": None,
                    "mde": None,
                    "floor_dependency": {
                        "consumer_family_declaration_path": "consumer_family_declaration.json",
                        "consumer_family_declaration_sha256": declaration_sha,
                        "binding_mode": "declaration_only",
                    },
                }
            )
        else:
            common.update(
                {
                    "prompt_candidate": {
                        "path": "prefill_prompt_candidate.json",
                        "sha256": prompt_sha,
                        "status": PROMPT_STATUS,
                    },
                    "test": empty_slot(
                        "TODO(lead authority): ratify prefill inferential test"
                    ),
                    "multiplicity": empty_slot(
                        "TODO(lead authority): ratify prefill multiplicity family"
                    ),
                    "equivalence_margin": None,
                    "mde": None,
                    "floor_dependency": empty_slot(
                        "TODO(lead authority): ratify a 256-token prefill floor or transport rule"
                    ),
                }
            )
        return common

    return {
        "schema_version": "joulewise.analysis_manifest.v3.prospective",
        # The frozen gamma plan tree pins this analysis manifest by SHA.
        "draft_status": emitted_draft_status(),
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
        "contrasts": [contrast("decode"), contrast("prefill_p256")],
        "postcollection_attachments": {
            "whole_window_verdict_sha256": empty_slot(
                "TODO(postcollection): passed whole-window verdict does not exist before collection"
            ),
            "evaluation_basis_sha256": empty_slot(
                "TODO(postcollection): derive exact 80-member basis after collection"
            ),
            "bracket_binding_sha256": empty_slot(
                "TODO(postcollection): populate from the completed bracket session",
            ),
            "committed_terminal_ledger_head": empty_slot(
                "TODO(postcollection): populate from the committed terminal head",
            ),
            "aggregate_floor_artifact_sha256": empty_slot(
                "TODO(U10): declaration-only pack cannot bind postcollection artifact bytes"
            ),
        },
    }


def build_tree(
    plan_sha: str,
    generator_sha: str,
    family_rows: list[dict[str, Any]],
    science_rows: list[dict[str, Any]],
    stage_graph: list[dict[str, Any]],
    external_inputs: list[dict[str, Any]],
    analysis_sha: str,
    declaration_sha: str,
) -> dict[str, Any]:
    identity_units = []
    producer_plans = {
        "A": {
            "plan_id": "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2",
            "path": "../d117_floor_qwen25_1p5b_v2/calibration_plan.json",
        },
        "B": {
            "plan_id": "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v2",
            "path": "../d117_floor_qwen25_7b_v2/calibration_plan.json",
        },
    }
    for arm, measurement_arm in (
        ("A", "decode"),
        ("A", "prefill_p256"),
        ("B", "decode"),
        ("B", "prefill_p256"),
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
                    "quantization": {**QUANTIZATION, "group_size": None},
                    "workload_profile": {
                        **workload_for(measurement_arm),
                        "prompt_tokens": (
                            workload_for(measurement_arm).get("prompt_tokens")
                        ),
                        "prompt_text": (
                            workload_for(measurement_arm).get("prompt_text")
                        ),
                        "dataset_ref": None,
                    },
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
            "issued_artifact_id": "d079_calibration_acceptance_v2_n19",
            "issued_artifact_sha256": (
                "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
            ),
            "issued_derivation_sha256": (
                "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
            ),
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
                "1.5B and 7B bundles before ratification"
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
        "runtime_budget": {
            # The D-134 plan-tree sidecar pins this nested field by SHA.
            "draft_status": emitted_draft_status(),
            "decode": {
                "members": MEMBERS_PER_ARM,
                "minutes_with_margin": 168.0,
                "authority": REFERENCE_CADENCE_AUTHORITY,
            },
            "prefill_p256": {
                "members": MEMBERS_PER_ARM,
                "core_minutes_before_margin": 110.0,
                "minutes_with_20_percent_margin": 130.0,
                "authority": "D-122 sizing scout rough ABBA arm and runtime",
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
            "combined_minutes_with_margin": 310.0,
            "combined_derivation": "168.0 + 130.0 + 12.0",
            "member_replacement_authority": False,
        },
    }


def readme_bytes() -> bytes:
    oracle = derive_bracket_session_receipt_oracle()
    identity = active_generation()
    version = identity.family_suffix.removeprefix("_")
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
        content = f"""# D-117 gamma contrast pack {version} — status governed by the D-134 freeze receipt

{identity_statement}This description does not carry freeze status. The committed D-134 freeze
receipt and its plan-tree attachment are authoritative for this pack's frozen
state; the receipt pins `calibration_plan.json` by SHA, so this text and every
serialized `draft_status` field stay exactly as generated on both sides of the
freeze. An external unexpired PASS/GO arm receipt is required before launch.

This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast and the D-122 40-member 256-token prefill ABBA contrast. It makes
no data, verdict, receipt, or artifact-byte claim.

Authority order is D-117, D-122, D-123, D-124, then D-125. D-122 supersedes
the older design-memo and plan-factory decode-only text. The plan tree uses
the shared `joulewise.d117_plan_tree.v1` schema family and every top-level
artifact declares `draft_status = {SUCCESSOR_EMITTED_STATUS}`.

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
pinset. A 256-token prefill floor or a ruled 128-to-256 transport rule remains
an explicit EMPTY slot.

The receipt oracle is replay-derived from `{oracle['source']['module']}` and
records {oracle['receipt_count']} physical receipts for
{oracle['logical_operation_count']} logical operations per finalized pre/post
bracket session. Actual receipt bytes and the absolute terminal sequence remain
empty until arm and collection. Identity pins remain EMPTY pending U11. The
Both shared-edge ABBA contrast cells register the canonical D-124 common-mode
floor estimator treatment required to match their floor-calibration cells.

Regenerate or check:

```text
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py --check
python3 -m unittest tests.test_d117_decode_contrast_plan
```
"""
        return thread_generation_identity(content).encode("utf-8")
    content = f"""# D-117 gamma contrast pack {version} — unfrozen draft

{identity_statement}This pack stages both prospectively required gamma arms: a 40-member decode
ABBA contrast and the D-122 40-member 256-token prefill ABBA contrast. It is
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
pinset. A 256-token prefill floor or a ruled 128-to-256 transport rule remains
an explicit EMPTY slot.

The receipt oracle is replay-derived from `{oracle['source']['module']}` and
records {oracle['receipt_count']} physical receipts for
{oracle['logical_operation_count']} logical operations per finalized pre/post
bracket session. Actual receipt bytes and the absolute terminal sequence remain
empty until arm and collection. Identity pins remain EMPTY pending U11. The
Both shared-edge ABBA contrast cells register the canonical D-124 common-mode
floor estimator treatment required to match their floor-calibration cells.

Regenerate or check:

```text
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py
python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py --check
python3 -m unittest tests.test_d117_decode_contrast_plan
```
"""
    return thread_generation_identity(content).encode("utf-8")


def generate(
    output_repo_root: Path,
    identity: GenerationIdentity | None = None,
) -> dict[str, str]:
    with generation_context(identity or GenerationIdentity()):
        return _generate(output_repo_root)


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
        "manifest_id": "d117-gamma-qwen25-1p5b-vs-7b-order-v1",
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
    )
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

    return {
        "plan_sha256": plan_sha,
        "tree_sha256": tree_sha,
        "analysis_sha256": analysis_sha,
        "prompt_sha256": prompt_sha,
        "consumer_declaration_sha256": declaration_sha,
    }


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
    parser.add_argument("--pack-id", default=PACK_REL.name)
    parser.add_argument("--family-suffix", default=CURRENT_FAMILY_SUFFIX)
    parser.add_argument(
        "--preserve-current-frozen-bytes",
        action=argparse.BooleanOptionalAction,
        default=PRESERVE_CURRENT_FROZEN_BYTES,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    identity = GenerationIdentity(
        pack_id=args.pack_id,
        family_suffix=args.family_suffix,
        preserve_current_frozen_bytes=args.preserve_current_frozen_bytes,
    )
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
        f"decode_members={MEMBERS_PER_ARM} prefill_p256_members={MEMBERS_PER_ARM} "
        f"plan_sha256={hashes['plan_sha256']} tree_sha256={hashes['tree_sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"generation failed: {exc}") from exc
