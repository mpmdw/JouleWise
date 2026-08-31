"""Pinned, offline benchmark import helpers for scored suite manifests.

The core importer is stdlib-only. ``transformers`` is imported lazily by
``render_prompts`` so ordinary CI imports do not acquire tokenizer or model
dependencies.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from joulewise.gensuite import tokenizer_id_for
from joulewise.model_panel import load_model_panel
from joulewise.suite import (
    CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED,
    MARKER_DEFAULTS,
    OUTPUT_DEFAULTS,
    SUITE_SCHEMA_VERSION,
    SuiteManifest,
    suite_manifest_sha256,
)


GSM8K_REPO_URL = "https://github.com/openai/grade-school-math"
GSM8K_COMMIT = "3101c7d5072418e28b9008a6636bde82a006892c"
GSM8K_TEST_PATH = "grade_school_math/data/test.jsonl"
GSM8K_TEST_SHA256 = "3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14"
GSM8K_TEST_GIT_BLOB_SHA1 = "e4c2ff4942b9a78bd74f04141224c11e28d12dc9"
GSM8K_TEST_LINE_COUNT = 1319
GSM8K_TEST_BYTES = 749738
GSM8K_LICENSE_SPDX = "MIT"
GSM8K_LICENSE_BLOB_SHA1 = "9e84fcbc4d81a1f433c90caf9f1cef373c12edae"
SELECTION_DOMAIN = "joulewise.benchmark_import.gsm8k.selection.v1"
ANSWER_HASH_DOMAIN = "joulewise.gsm8k_answer.v1"
SCORER_ID = "gsm8k_scored_v6/score_v1"
ANNOTATIONS_SCHEMA_VERSION = "gsm8k_scored_annotations.v1"
PROMPT_TEMPLATE_ID = "gsm8k_scored_v6/qwen3_chat_nothink_v1"
PROMPT_TEMPLATE = (
    "Solve the following grade-school math problem. Reason briefly in plain text, "
    "then give the final answer on its own last line in exactly the form `#### "
    "<number>` (a single integer or decimal, no units, no commas).\n\n"
    "Problem: {question}"
)
K_ITEMS = 8
OUTPUT_CAP = 384
OUTPUT_POLICY = "natural_eos"
GENERATOR_NAME = "gsm8k_scored_v6"
GENERATOR_VERSION = "1.0.0"
PINNED_CANONICAL_SUBSET_JSON_SHA256 = (
    "fcfc8ab8e8ce5ba2550d156d7a3242132b5216a89c7404053dae50105249231c"
)
PINNED_QWEN3_TOKENIZER_ID = (
    "tokfiles_3a482ed2a45359223fba1740c869449d91c0c5d6f82f5151a2514b5f0f2a7569"
)
REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256 = (
    "87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5"
)
REVIEWED_QWEN3_TOKENIZER_JSON_SHA256 = (
    "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
)
QWEN3_MODEL_IDS = ("qwen3-1p7b", "qwen3-8b")
QWEN3_RENDERING_PINSET_ID = "qwen3-real-prompts-v1-thinking-off"
QWEN3_PANEL_PATH = (
    Path(__file__).resolve().parents[1] / "configs" / "model_panels" / "qwen3_4bit.json"
)

PROMPT_TEMPLATE_SHA256 = hashlib.sha256(PROMPT_TEMPLATE.encode("utf-8")).hexdigest()
prompt_template_sha256 = PROMPT_TEMPLATE_SHA256
EMPTY_THINK_PREFIX = "<think>\n\n</think>\n\n"
SELECTION_RULE = "sha256-ordered first k by selection_key over source_sha256"
CORRECTNESS_QUARANTINE = (
    "quarantined annotation (C-004); malformed counts as incorrect (D-047.6); "
    "no capability claim"
)
CONTAMINATION_NOTE = (
    "D-166/C5-1.9/AP-5: Qwen3 pre-training contamination is UNMITIGABLE; "
    "accuracy is a property of the pinned set, never a capability claim"
)
DIFFICULTY_QUARANTINE = (
    "D-166/C5-1.9/AP-5: source difficulty is unlabelled; correctness remains "
    "quarantined and licenses no difficulty or capability claim"
)

OUTCOME_CORRECT = "correct"
OUTCOME_INCORRECT = "incorrect"
OUTCOME_TRUNCATED = "truncated"
OUTCOME_MALFORMED = "malformed"
OUTCOME_CLASSES = (
    OUTCOME_CORRECT,
    OUTCOME_INCORRECT,
    OUTCOME_TRUNCATED,
    OUTCOME_MALFORMED,
)
_SCORABLE_RUNTIME_STATUSES = frozenset(
    {"succeeded", "capped", "malformed", "runtime_failed"}
)
_ANSWER_LINE_RE = re.compile(
    r"#### (?P<answer>[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:/\d+)?)"
)

_TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "merges.txt",
    "vocab.json",
    "tokenizer.model",
    "spiece.model",
    "special_tokens_map.json",
    "added_tokens.json",
    "chat_template.jinja",
    "chat_template.json",
)


@dataclass(frozen=True)
class GSM8KScoreResult:
    item_id: str
    runtime_status: str
    outcome: str
    parsed_answer: str | None
    expected_answer: str
    correct: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuthenticatedGSM8KRecords(Sequence[Mapping[str, Any]]):
    """Immutable records plus the loader-verified source authentication chain."""

    records: tuple[Mapping[str, Any], ...]
    file_sha256: str
    file_bytes: int
    file_git_blob_sha1: str
    line_count: int
    source_payload: bytes

    def __getitem__(self, index: int) -> Mapping[str, Any]:
        return self.records[index]

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[Mapping[str, Any]]:
        return iter(self.records)


def _refuse(reason: str, detail: str) -> None:
    raise ValueError(f"{reason}: {detail}")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def load_gsm8k_test(path: str | Path) -> AuthenticatedGSM8KRecords:
    """Load and authenticate the pinned GSM8K test JSONL."""

    source_path = Path(path)
    payload = source_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != GSM8K_TEST_SHA256:
        raise ValueError(
            "GSM8K test.jsonl sha256 mismatch: "
            f"got {digest}, expected {GSM8K_TEST_SHA256}"
        )
    if len(payload) != GSM8K_TEST_BYTES:
        raise ValueError(
            f"GSM8K test.jsonl byte count mismatch: got {len(payload)}, "
            f"expected {GSM8K_TEST_BYTES}"
        )
    git_blob_payload = f"blob {len(payload)}\0".encode("ascii") + payload
    git_blob_sha1 = hashlib.sha1(git_blob_payload).hexdigest()
    if git_blob_sha1 != GSM8K_TEST_GIT_BLOB_SHA1:
        raise ValueError(
            "GSM8K test.jsonl git blob sha1 mismatch: "
            f"got {git_blob_sha1}, expected {GSM8K_TEST_GIT_BLOB_SHA1}"
        )
    lines = payload.decode("utf-8").splitlines()
    if len(lines) != GSM8K_TEST_LINE_COUNT:
        raise ValueError(
            f"GSM8K test.jsonl line count mismatch: got {len(lines)}, "
            f"expected {GSM8K_TEST_LINE_COUNT}"
        )

    records: list[dict[str, Any]] = []
    for line_index, line in enumerate(lines):
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"GSM8K test.jsonl line {line_index + 1} is invalid JSON"
            ) from exc
        if not isinstance(raw, dict):
            raise ValueError(f"GSM8K test.jsonl line {line_index + 1} must be an object")
        question = raw.get("question")
        answer = raw.get("answer")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                f"GSM8K test.jsonl line {line_index + 1} question must be non-empty"
            )
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError(
                f"GSM8K test.jsonl line {line_index + 1} answer must be non-empty"
            )
        records.append(
            {
                "line_index": line_index,
                "question": question,
                "answer": answer,
                "source_item_id": f"gsm8k_test_{line_index:04d}",
                "source_sha256": _canonical_json_sha256(
                    {"question": question, "answer": answer}
                ),
            }
        )
    return AuthenticatedGSM8KRecords(
        records=tuple(MappingProxyType(record) for record in records),
        file_sha256=digest,
        file_bytes=len(payload),
        file_git_blob_sha1=git_blob_sha1,
        line_count=len(lines),
        source_payload=payload,
    )


def canonical_answer(raw_answer: str) -> str:
    """Return a numeric string as a canonical lowest-terms rational."""

    if not isinstance(raw_answer, str) or not raw_answer.strip():
        raise ValueError("answer must be a non-empty string")
    normalized = raw_answer.strip().replace(",", "")
    try:
        return str(Fraction(normalized))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"unparsable numeric answer: {raw_answer!r}") from exc


def gold_answer(record: Mapping[str, Any]) -> str:
    """Return the final GSM8K answer as a canonical lowest-terms rational."""

    answer = record.get("answer")
    if not isinstance(answer, str):
        raise ValueError("GSM8K record answer must be a string")
    marker = "#### "
    if marker not in answer:
        raise ValueError("GSM8K answer has no final '#### ' marker")
    raw_gold = answer.rsplit(marker, 1)[1].strip()
    if not raw_gold:
        raise ValueError("GSM8K answer after final '#### ' marker is empty")
    return canonical_answer(raw_gold)


def selection_key(source_sha256: str) -> str:
    payload = f"{SELECTION_DOMAIN}\0{source_sha256}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def select_items(
    records: Sequence[Mapping[str, Any]], k: int = K_ITEMS
) -> list[dict[str, Any]]:
    if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer")
    if k > len(records):
        raise ValueError(f"k={k} exceeds record count {len(records)}")
    keyed: list[tuple[str, Mapping[str, Any]]] = []
    seen_keys: set[str] = set()
    for record in records:
        source_sha256 = record.get("source_sha256")
        if not isinstance(source_sha256, str):
            raise ValueError("every record must have a source_sha256 string")
        key = selection_key(source_sha256)
        if key in seen_keys:
            raise ValueError("duplicate GSM8K selection key")
        seen_keys.add(key)
        keyed.append((key, record))
    keyed.sort(key=lambda pair: pair[0])
    return [dict(record) for _, record in keyed[:k]]


def selected_item_ids_sha256(records: Sequence[Mapping[str, Any]]) -> str:
    return _canonical_json_sha256([record["source_item_id"] for record in records])


def canonical_subset_json_sha256(records: Sequence[Mapping[str, Any]]) -> str:
    subset = [
        {
            "source_item_id": record["source_item_id"],
            "question": record["question"],
            "answer": record["answer"],
        }
        for record in records
    ]
    return _canonical_json_sha256(subset)


def expected_answer_sha256(item_id: str, canonical_gold: str) -> str:
    payload = f"{ANSWER_HASH_DOMAIN}\0{item_id}\0{canonical_gold}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tokenizer_manifest(tokenizer_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for filename in _TOKENIZER_FILES:
        path = tokenizer_dir / filename
        if path.is_file():
            rows.append(
                {
                    "filename": filename,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        else:
            rows.append({"filename": filename, "status": "absent"})
    return rows


def _require_authenticated_source(
    records: Sequence[Mapping[str, Any]],
) -> AuthenticatedGSM8KRecords:
    if not isinstance(records, AuthenticatedGSM8KRecords):
        _refuse(
            "gsm8k_source_authentication_required",
            "records must come directly from load_gsm8k_test",
        )
    expected_receipt = (
        GSM8K_TEST_SHA256,
        GSM8K_TEST_BYTES,
        GSM8K_TEST_GIT_BLOB_SHA1,
        GSM8K_TEST_LINE_COUNT,
    )
    observed_receipt = (
        records.file_sha256,
        records.file_bytes,
        records.file_git_blob_sha1,
        records.line_count,
    )
    if observed_receipt != expected_receipt:
        _refuse(
            "gsm8k_source_authentication_receipt_mismatch",
            "loader receipt no longer matches the pinned source identity",
        )
    payload = records.source_payload
    payload_blob_sha1 = hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()
    if (
        hashlib.sha256(payload).hexdigest() != records.file_sha256
        or len(payload) != records.file_bytes
        or payload_blob_sha1 != records.file_git_blob_sha1
    ):
        _refuse(
            "gsm8k_source_authentication_receipt_mismatch",
            "receipt does not authenticate its retained source bytes",
        )
    lines = payload.decode("utf-8").splitlines()
    if len(lines) != records.line_count or len(lines) != len(records):
        _refuse(
            "gsm8k_source_authentication_records_mismatch",
            "authenticated line count does not match the retained records",
        )
    for line_index, (line, record) in enumerate(zip(lines, records, strict=True)):
        raw = json.loads(line)
        expected_record = {
            "line_index": line_index,
            "question": raw.get("question") if isinstance(raw, dict) else None,
            "answer": raw.get("answer") if isinstance(raw, dict) else None,
            "source_item_id": f"gsm8k_test_{line_index:04d}",
        }
        expected_record["source_sha256"] = _canonical_json_sha256(
            {
                "question": expected_record["question"],
                "answer": expected_record["answer"],
            }
        )
        if dict(record) != expected_record:
            _refuse(
                "gsm8k_source_authentication_records_mismatch",
                f"record {line_index} is not derived from the authenticated source bytes",
            )
    return records


def _reviewed_qwen3_pins(
    panel_path: str | Path | None = None,
) -> tuple[str, str]:
    panel = load_model_panel(QWEN3_PANEL_PATH if panel_path is None else panel_path)
    entries = [panel.get(model_id) for model_id in QWEN3_MODEL_IDS]
    if any(entry["admission"]["status"] != "admitted" for entry in entries):
        _refuse(
            "gsm8k_reviewed_panel_entry_not_admitted",
            "every D-166 Qwen3 panel entry must remain admitted",
        )
    if any(
        entry["rendering_pinset_id"] != QWEN3_RENDERING_PINSET_ID
        for entry in entries
    ):
        _refuse(
            "gsm8k_reviewed_panel_pinset_mismatch",
            "Qwen3 entries must bind the reviewed thinking-off rendering pinset",
        )
    pinset = panel.get_rendering_pinset(QWEN3_RENDERING_PINSET_ID)
    if (
        pinset["chat_template_sha256"] != REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256
        or pinset["tokenizer_json_sha256"]
        != REVIEWED_QWEN3_TOKENIZER_JSON_SHA256
    ):
        _refuse(
            "gsm8k_reviewed_panel_pin_drift",
            "Qwen3 panel prompt/tokenizer pins differ from the reviewed D-166 pinset",
        )
    return pinset["chat_template_sha256"], pinset["tokenizer_json_sha256"]


def _require_reviewed_qwen3_binding(
    rendered: Mapping[str, Any], *, panel_path: str | Path | None = None
) -> None:
    chat_template_sha256, tokenizer_json_sha256 = _reviewed_qwen3_pins(panel_path)
    if rendered.get("chat_template_sha256") != chat_template_sha256:
        _refuse(
            "gsm8k_reviewed_chat_template_mismatch",
            "rendered chat_template_sha256 does not match the reviewed Qwen3 panel",
        )
    if rendered.get("tokenizer_json_sha256") != tokenizer_json_sha256:
        _refuse(
            "gsm8k_reviewed_tokenizer_json_mismatch",
            "rendered tokenizer_json_sha256 does not match the reviewed Qwen3 panel",
        )
    if rendered.get("tokenizer_id") != PINNED_QWEN3_TOKENIZER_ID:
        _refuse(
            "gsm8k_reviewed_tokenizer_identity_mismatch",
            "rendered tokenizer file-manifest identity is not the reviewed Qwen3 identity",
        )


def render_prompts(
    records: Sequence[Mapping[str, Any]],
    tokenizer_dirs: Sequence[Path],
) -> dict[str, Any]:
    """Render selected records through every supplied local Qwen3 tokenizer."""

    if not tokenizer_dirs:
        raise ValueError("at least one tokenizer directory is required")
    try:
        from transformers import AutoTokenizer, __version__ as transformers_version
    except ImportError as exc:  # pragma: no cover - exercised only in bare CI
        raise RuntimeError("render_prompts requires transformers") from exc

    tokenizers: list[Any] = []
    chat_template_hashes: list[str] = []
    tokenizer_json_hashes: list[str] = []
    tokenizer_ids: list[str] = []
    for raw_dir in tokenizer_dirs:
        tokenizer_dir = Path(raw_dir)
        if not tokenizer_dir.is_dir():
            raise FileNotFoundError(f"tokenizer directory not found: {tokenizer_dir}")
        config_path = tokenizer_dir / "tokenizer_config.json"
        tokenizer_json_path = tokenizer_dir / "tokenizer.json"
        if not config_path.is_file() or not tokenizer_json_path.is_file():
            raise FileNotFoundError(
                f"tokenizer directory lacks tokenizer_config.json/tokenizer.json: {tokenizer_dir}"
            )
        config = json.loads(config_path.read_text(encoding="utf-8"))
        chat_template = config.get("chat_template")
        if not isinstance(chat_template, str) or not chat_template:
            raise ValueError(f"tokenizer chat_template is not a string: {tokenizer_dir}")
        chat_template_hashes.append(
            hashlib.sha256(chat_template.encode("utf-8")).hexdigest()
        )
        tokenizer_json_hashes.append(
            hashlib.sha256(tokenizer_json_path.read_bytes()).hexdigest()
        )
        tokenizer_ids.append(
            tokenizer_id_for(tokenizer_manifest=_tokenizer_manifest(tokenizer_dir))
        )
        tokenizers.append(
            AutoTokenizer.from_pretrained(
                str(tokenizer_dir),
                local_files_only=True,
            )
        )

    if len(set(chat_template_hashes)) != 1:
        raise AssertionError("chat_template sha256 differs across tokenizer directories")
    if len(set(tokenizer_json_hashes)) != 1:
        raise AssertionError("tokenizer.json sha256 differs across tokenizer directories")
    if len(set(tokenizer_ids)) != 1:
        raise AssertionError("tokenizer file-manifest identity differs across directories")

    rendered_items: list[dict[str, Any]] = []
    for record in records:
        prompt = PROMPT_TEMPLATE.format(question=record["question"])
        reference_text: str | None = None
        reference_ids: list[int] | None = None
        for tokenizer in tokenizers:
            messages = [{"role": "user", "content": prompt}]
            rendered_text = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                enable_thinking=False,
                tokenize=False,
            )
            tokenized = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                enable_thinking=False,
                tokenize=True,
            )
            raw_input_ids = getattr(tokenized, "input_ids", tokenized)
            prompt_token_ids = list(raw_input_ids)
            if not isinstance(rendered_text, str):
                raise AssertionError("apply_chat_template(tokenize=False) did not return text")
            reencoded_ids = list(
                tokenizer.encode(rendered_text, add_special_tokens=True)
            )
            if reencoded_ids != prompt_token_ids:
                raise AssertionError(
                    "rendered prompt text does not re-encode to the pinned token ids"
                )
            if not rendered_text.endswith(EMPTY_THINK_PREFIX):
                raise AssertionError(
                    "enable_thinking=False rendering lacks the empty <think> prefix"
                )
            think_prefix_ids = list(
                tokenizer.encode(EMPTY_THINK_PREFIX, add_special_tokens=False)
            )
            if not think_prefix_ids or prompt_token_ids[-len(think_prefix_ids) :] != think_prefix_ids:
                raise AssertionError(
                    "empty <think> prefix token ids are not present at the rendered tail"
                )
            if reference_text is None:
                reference_text = rendered_text
                reference_ids = prompt_token_ids
            elif rendered_text != reference_text or prompt_token_ids != reference_ids:
                raise AssertionError(
                    "rendered prompt text/token ids differ across tokenizer directories"
                )
        assert reference_text is not None and reference_ids is not None
        rendered_items.append(
            {
                "source_item_id": record["source_item_id"],
                "prompt_token_ids": reference_ids,
                "rendered_prompt_text": reference_text,
                "rendered_prompt_sha256": hashlib.sha256(
                    reference_text.encode("utf-8")
                ).hexdigest(),
            }
        )

    rendered = {
        "items": rendered_items,
        "chat_template_sha256": chat_template_hashes[0],
        "tokenizer_json_sha256": tokenizer_json_hashes[0],
        "tokenizer_id": tokenizer_ids[0],
        "rendered_with": {
            "library": "transformers",
            "version": transformers_version,
        },
    }
    _require_reviewed_qwen3_binding(rendered)
    return rendered


def build_gsm8k_scored_manifest(
    records: Sequence[Mapping[str, Any]],
    rendered: Mapping[str, Any],
    *,
    k: int = K_ITEMS,
    output_cap: int = OUTPUT_CAP,
) -> dict[str, Any]:
    """Build the materialized suite_manifest.v2 GSM8K scored profile."""

    if isinstance(output_cap, bool) or not isinstance(output_cap, int) or output_cap <= 0:
        raise ValueError("output_cap must be a positive integer")
    authenticated_records = _require_authenticated_source(records)
    _require_reviewed_qwen3_binding(rendered)
    selected = select_items(authenticated_records, k)
    rendered_items = rendered.get("items")
    if not isinstance(rendered_items, list):
        raise ValueError("rendered.items must be a list")
    if [row.get("source_item_id") for row in rendered_items] != [
        row["source_item_id"] for row in selected
    ]:
        raise ValueError("rendered items do not match the selected GSM8K order")

    subset_hash = canonical_subset_json_sha256(selected)
    ids_hash = selected_item_ids_sha256(selected)
    parameters_hash = _canonical_json_sha256(
        {
            "k": k,
            "output_cap": output_cap,
            "output_policy": OUTPUT_POLICY,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
            "prompt_template_sha256": PROMPT_TEMPLATE_SHA256,
            "selection_domain": SELECTION_DOMAIN,
        }
    )

    items: list[dict[str, Any]] = []
    for record, rendered_item in zip(selected, rendered_items, strict=True):
        canonical_gold = gold_answer(record)
        item_id = record["source_item_id"]
        prompt_token_ids = rendered_item["prompt_token_ids"]
        items.append(
            {
                "item_id": item_id,
                "item_type": "text_prompt",
                "category": "gsm8k",
                "difficulty": {
                    "axis": "none",
                    "value": 0.0,
                    "scale": "nominal",
                    "label": "unlabelled",
                    "source": GENERATOR_NAME,
                    "quarantine_note": DIFFICULTY_QUARANTINE,
                },
                "shape": {
                    "planned_prompt_tokens": len(prompt_token_ids),
                    "planned_output_tokens": output_cap,
                    "prompt_level": f"{len(prompt_token_ids)}_tokens",
                    "decode_level": f"{output_cap}_cap",
                },
                "source": {
                    "source_item_id": record["source_item_id"],
                    "source_sha256": record["source_sha256"],
                    "prompt_template_id": PROMPT_TEMPLATE_ID,
                    "license": GSM8K_LICENSE_SPDX,
                    "contamination_note": CONTAMINATION_NOTE,
                    "prompt_text": rendered_item["rendered_prompt_text"],
                    "prompt_token_ids": prompt_token_ids,
                },
                "grouping": {
                    "condition_id": f"gsm8k_k{k}_c{output_cap}",
                    "block_id": "gsm8k",
                    "level_id": f"c{output_cap}",
                    "prefix_group_id": None,
                },
                "output_policy": OUTPUT_POLICY,
                "tags": ["gsm8k", "scored", "nothink"],
                "scoring": {
                    "scorer_id": SCORER_ID,
                    "expected_answer_hash": expected_answer_sha256(
                        item_id, canonical_gold
                    ),
                    "correctness_quarantine": CORRECTNESS_QUARANTINE,
                },
            }
        )

    selection_note = (
        f"{CONTAMINATION_NOTE}; selection is SHA-ordered, not seeded"
    )
    manifest = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "suite_id": "gsm8k_scored_v6",
        "suite_profile": f"gsm8k_scored_v6_k{k}_c{output_cap}_qwen3",
        "suite_revision": "2026-08-28.d166-r3",
        "suite_seed": SELECTION_DOMAIN,
        "generator": {
            "name": GENERATOR_NAME,
            "version": GENERATOR_VERSION,
            "parameters_hash": parameters_hash,
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
            "declared_cache_policy": "warm_cache",
            "cache_policy_verification": (
                CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED
            ),
            "warmup_policy": "adapter_default",
            "default_output_policy": OUTPUT_POLICY,
        },
        "source_manifest": {
            "source_kind": "benchmark_import",
            "source_id": (
                "openai/grade-school-math@3101c7d5:"
                "grade_school_math/data/test.jsonl"
            ),
            "license": GSM8K_LICENSE_SPDX,
            "contamination_note": selection_note,
            "subset_id": f"gsm8k_test_sha256_k{k}_v1",
            "subset_sha256": subset_hash,
            "revision": GSM8K_COMMIT,
        },
        "benchmark_import": {
            "dataset": "gsm8k",
            "split": "test",
            "repo_url": GSM8K_REPO_URL,
            "commit": GSM8K_COMMIT,
            "file_path": GSM8K_TEST_PATH,
            "file_sha256": GSM8K_TEST_SHA256,
            "file_git_blob_sha1": GSM8K_TEST_GIT_BLOB_SHA1,
            "license_spdx": GSM8K_LICENSE_SPDX,
            "license_blob_sha1": GSM8K_LICENSE_BLOB_SHA1,
            "selection_rule": SELECTION_RULE,
            "selection_domain": SELECTION_DOMAIN,
            "k": k,
            "selected_item_ids": [record["source_item_id"] for record in selected],
            "selected_item_ids_sha256": ids_hash,
            "canonical_subset_json_sha256": subset_hash,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
            "prompt_template_sha256": PROMPT_TEMPLATE_SHA256,
            "chat_template_sha256": rendered["chat_template_sha256"],
            "enable_thinking": False,
            "tokenizer_json_sha256": rendered["tokenizer_json_sha256"],
            "tokenizer_id": rendered["tokenizer_id"],
            "rendered_with": rendered["rendered_with"],
        },
        "items": items,
        "markers": dict(MARKER_DEFAULTS),
        "outputs": dict(OUTPUT_DEFAULTS),
    }
    SuiteManifest.from_mapping(manifest)
    return manifest


def build_gsm8k_scored_annotations(
    manifest: Mapping[str, Any], records: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Build the correctness-quarantined scorer sidecar for a manifest."""

    manifest_dict = dict(manifest)
    validated = SuiteManifest.from_mapping(manifest_dict)
    records_by_id = {record["source_item_id"]: record for record in records}
    annotations: list[dict[str, Any]] = []
    for execution_index, item in enumerate(validated.items):
        record = records_by_id.get(item.source.source_item_id)
        if record is None:
            raise ValueError(f"source record not found for {item.source.source_item_id}")
        canonical_gold = gold_answer(record)
        answer_hash = expected_answer_sha256(item.item_id, canonical_gold)
        if item.scoring is None or item.scoring.expected_answer_hash != answer_hash:
            raise ValueError(f"manifest scoring hash mismatch for {item.item_id}")
        annotations.append(
            {
                "item_id": item.item_id,
                "execution_index": execution_index,
                "source_item_id": record["source_item_id"],
                "line_index": record["line_index"],
                "source_sha256": record["source_sha256"],
                "source_answer": record["answer"],
                "expected_answer": canonical_gold,
                "expected_answer_sha256": answer_hash,
                "scorer_id": SCORER_ID,
            }
        )
    sidecar = {
        "schema_version": ANNOTATIONS_SCHEMA_VERSION,
        "suite_id": validated.suite_id,
        "manifest_sha256": suite_manifest_sha256(manifest_dict),
        "quarantine": "expected answers are scorer inputs, not manifest fields",
        "consumer_note": (
            "Use this sidecar as the gsm8k_scored_v6 scorer input; expected "
            "answers and raw source answers remain quarantined from the suite manifest."
        ),
        "scorer": {
            "answer_hash_domain": ANSWER_HASH_DOMAIN,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
            "scorer_id": SCORER_ID,
        },
        "annotations": annotations,
    }
    validate_gsm8k_annotations(manifest_dict, sidecar)
    return sidecar


def validate_gsm8k_annotations(
    manifest: Mapping[str, Any], sidecar: Mapping[str, Any]
) -> None:
    """Authenticate the exact scorer sidecar against its suite manifest."""

    manifest_dict = dict(manifest)
    validated = SuiteManifest.from_mapping(manifest_dict)
    expected_top_keys = {
        "schema_version",
        "suite_id",
        "manifest_sha256",
        "quarantine",
        "consumer_note",
        "scorer",
        "annotations",
    }
    if set(sidecar) != expected_top_keys:
        raise ValueError("GSM8K annotations top-level key set mismatch")
    if sidecar.get("schema_version") != ANNOTATIONS_SCHEMA_VERSION:
        raise ValueError("GSM8K annotations schema_version mismatch")
    if sidecar.get("suite_id") != validated.suite_id:
        raise ValueError("GSM8K annotations suite_id mismatch")
    if sidecar.get("manifest_sha256") != suite_manifest_sha256(manifest_dict):
        raise ValueError("GSM8K annotations manifest_sha256 mismatch")
    if sidecar.get("scorer") != {
        "answer_hash_domain": ANSWER_HASH_DOMAIN,
        "prompt_template_id": PROMPT_TEMPLATE_ID,
        "scorer_id": SCORER_ID,
    }:
        raise ValueError("GSM8K annotations scorer identity mismatch")

    annotations = sidecar.get("annotations")
    if not isinstance(annotations, list) or len(annotations) != len(validated.items):
        raise ValueError("GSM8K annotations item count mismatch")
    expected_annotation_keys = {
        "item_id",
        "execution_index",
        "source_item_id",
        "line_index",
        "source_sha256",
        "source_answer",
        "expected_answer",
        "expected_answer_sha256",
        "scorer_id",
    }
    subset: list[dict[str, Any]] = []
    question_prefix = PROMPT_TEMPLATE.split("{question}", 1)[0]
    for index, (item, annotation) in enumerate(
        zip(validated.items, annotations, strict=True)
    ):
        if not isinstance(annotation, Mapping) or set(annotation) != expected_annotation_keys:
            raise ValueError(f"GSM8K annotation {index} key set mismatch")
        if annotation.get("execution_index") != index:
            raise ValueError(f"GSM8K annotation {index} execution_index mismatch")
        if annotation.get("item_id") != item.item_id:
            raise ValueError(f"GSM8K annotation {index} item_id mismatch")
        if annotation.get("source_item_id") != item.source.source_item_id:
            raise ValueError(f"GSM8K annotation {index} source_item_id mismatch")
        if annotation.get("source_sha256") != item.source.source_sha256:
            raise ValueError(f"GSM8K annotation {index} source_sha256 mismatch")
        expected_answer = annotation.get("expected_answer")
        if not isinstance(expected_answer, str):
            raise ValueError(f"GSM8K annotation {index} expected_answer malformed")
        expected_hash = expected_answer_sha256(
            item.item_id, canonical_answer(expected_answer)
        )
        if annotation.get("expected_answer_sha256") != expected_hash:
            raise ValueError(f"GSM8K annotation {index} answer hash mismatch")
        if item.scoring is None or item.scoring.expected_answer_hash != expected_hash:
            raise ValueError(f"GSM8K annotation {index} manifest answer hash mismatch")
        if annotation.get("scorer_id") != SCORER_ID:
            raise ValueError(f"GSM8K annotation {index} scorer_id mismatch")
        source_answer = annotation.get("source_answer")
        if not isinstance(source_answer, str):
            raise ValueError(f"GSM8K annotation {index} source_answer malformed")
        if gold_answer({"answer": source_answer}) != canonical_answer(expected_answer):
            raise ValueError(f"GSM8K annotation {index} source gold mismatch")
        rendered_prompt = item.source.prompt_text
        if not isinstance(rendered_prompt, str):
            raise ValueError(f"GSM8K annotation {index} rendered prompt missing")
        try:
            question_start = (
                rendered_prompt.index(question_prefix) + len(question_prefix)
            )
            question_end = rendered_prompt.index("<|im_end|>", question_start)
        except ValueError as exc:
            raise ValueError(
                f"GSM8K annotation {index} rendered prompt shape mismatch"
            ) from exc
        question = rendered_prompt[question_start:question_end]
        source_record = {"question": question, "answer": source_answer}
        if _canonical_json_sha256(source_record) != item.source.source_sha256:
            raise ValueError(f"GSM8K annotation {index} source hash mismatch")
        subset.append(
            {"source_item_id": item.source.source_item_id, **source_record}
        )

    benchmark_import = validated.benchmark_import
    if benchmark_import is None:
        raise ValueError("GSM8K manifest benchmark_import is missing")
    if (
        canonical_subset_json_sha256(subset)
        != benchmark_import.canonical_subset_json_sha256
    ):
        raise ValueError("GSM8K annotations canonical subset hash mismatch")


def parse_response_answer(response_text: str) -> str | None:
    """Parse only an exact ``#### N`` final non-empty line."""

    if not isinstance(response_text, str):
        raise TypeError("response_text must be a string")
    stripped = response_text.strip()
    if not stripped:
        return None
    match = _ANSWER_LINE_RE.fullmatch(stripped.splitlines()[-1].strip())
    if match is None:
        return None
    try:
        return canonical_answer(match.group("answer"))
    except ValueError:
        return None


def score_gsm8k_response(
    response_text: str,
    annotation: Mapping[str, Any],
    *,
    runtime_status: str,
) -> GSM8KScoreResult:
    """Apply D-166's pinned four-way outcome rule to one response."""

    if runtime_status not in _SCORABLE_RUNTIME_STATUSES:
        raise ValueError(f"unsupported GSM8K runtime status: {runtime_status!r}")
    item_id = annotation.get("item_id")
    expected = annotation.get("expected_answer")
    declared_hash = annotation.get("expected_answer_sha256")
    scorer_id = annotation.get("scorer_id")
    if not isinstance(item_id, str) or not item_id:
        raise ValueError("GSM8K annotation item_id must be non-empty")
    if not isinstance(expected, str):
        raise ValueError("GSM8K annotation expected_answer must be a string")
    canonical_expected = canonical_answer(expected)
    expected_hash = expected_answer_sha256(item_id, canonical_expected)
    if declared_hash != expected_hash:
        raise ValueError(f"GSM8K annotation answer hash mismatch for {item_id}")
    if scorer_id != SCORER_ID:
        raise ValueError(f"GSM8K annotation scorer mismatch for {item_id}")

    parsed = parse_response_answer(response_text)
    if runtime_status in {"runtime_failed", "malformed"}:
        outcome = OUTCOME_MALFORMED
    elif parsed is None and runtime_status == "capped":
        outcome = OUTCOME_TRUNCATED
    elif parsed is None:
        outcome = OUTCOME_MALFORMED
    elif parsed == canonical_expected:
        outcome = OUTCOME_CORRECT
    else:
        outcome = OUTCOME_INCORRECT
    return GSM8KScoreResult(
        item_id=item_id,
        runtime_status=runtime_status,
        outcome=outcome,
        parsed_answer=parsed,
        expected_answer=canonical_expected,
        correct=outcome == OUTCOME_CORRECT,
    )


def score_gsm8k_outcome_table(
    response_rows: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    sidecar: Mapping[str, Any],
) -> dict[str, Any]:
    """Score an exact k-item response set and emit the fixed four-way table."""

    manifest_dict = dict(manifest)
    raw_benchmark_import = manifest_dict.get("benchmark_import")
    if not isinstance(raw_benchmark_import, Mapping):
        _refuse("gsm8k_pinned_manifest_missing", "benchmark_import is required")
    raw_items = manifest_dict.get("items")
    if (
        raw_benchmark_import.get("k") != K_ITEMS
        or not isinstance(raw_items, list)
        or len(raw_items) != K_ITEMS
    ):
        _refuse(
            "gsm8k_pinned_set_count_mismatch",
            f"D-166 requires exactly k={K_ITEMS} items per member",
        )
    if (
        raw_benchmark_import.get("canonical_subset_json_sha256")
        != PINNED_CANONICAL_SUBSET_JSON_SHA256
    ):
        _refuse(
            "gsm8k_pinned_subset_hash_mismatch",
            "manifest canonical_subset_json_sha256 is not the D-166 pinned set",
        )
    validated = SuiteManifest.from_mapping(manifest_dict)
    validate_gsm8k_annotations(manifest_dict, sidecar)
    annotations = sidecar.get("annotations")
    assert isinstance(annotations, list)
    expected_ids = [item.item_id for item in validated.items]
    observed_ids = [
        row.get("item_id") if isinstance(row, Mapping) else None
        for row in response_rows
    ]
    if not observed_ids:
        _refuse("gsm8k_pinned_set_empty", "a member must contain all eight items")
    if len(observed_ids) < K_ITEMS:
        reason = (
            "gsm8k_pinned_set_subset"
            if set(observed_ids).issubset(expected_ids)
            else "gsm8k_pinned_set_foreign"
        )
        _refuse(reason, f"received {len(observed_ids)} of {K_ITEMS} required items")
    if len(observed_ids) > K_ITEMS:
        reason = (
            "gsm8k_pinned_set_superset"
            if set(expected_ids).issubset(observed_ids)
            else "gsm8k_pinned_set_foreign"
        )
        _refuse(reason, f"received {len(observed_ids)} items; exactly {K_ITEMS} are required")
    if set(observed_ids) != set(expected_ids):
        _refuse(
            "gsm8k_pinned_set_foreign",
            "response items do not equal the D-166 pinned item set",
        )
    if observed_ids != expected_ids:
        _refuse(
            "gsm8k_pinned_set_order_mismatch",
            "response items must follow the pinned manifest order",
        )
    results: list[GSM8KScoreResult] = []
    for index, (row, annotation) in enumerate(
        zip(response_rows, annotations, strict=True)
    ):
        if not isinstance(row, Mapping):
            raise ValueError(f"GSM8K response row {index} must be an object")
        if not isinstance(annotation, Mapping):
            raise ValueError(f"GSM8K annotation {index} must be an object")
        if row.get("item_id") != annotation.get("item_id"):
            raise ValueError(f"GSM8K response row {index} item_id mismatch")
        response_text = row.get("response_text")
        runtime_status = row.get("status")
        if not isinstance(response_text, str):
            raise ValueError(f"GSM8K response row {index} response_text must be a string")
        if not isinstance(runtime_status, str):
            raise ValueError(f"GSM8K response row {index} status must be a string")
        results.append(
            score_gsm8k_response(
                response_text,
                annotation,
                runtime_status=runtime_status,
            )
        )
    counts = {outcome: 0 for outcome in OUTCOME_CLASSES}
    for result in results:
        counts[result.outcome] += 1
    correct_count = counts[OUTCOME_CORRECT]
    return {
        "scorer_id": SCORER_ID,
        "quarantine": (
            "accuracy is a property of this pinned set, not a capability claim"
        ),
        "item_count": len(results),
        "correct_count": correct_count,
        "accuracy": correct_count / len(results) if results else None,
        "outcome_counts": counts,
        "items": [result.to_dict() for result in results],
    }
