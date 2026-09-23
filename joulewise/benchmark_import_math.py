"""Pinned, offline MATH rational-answer importer and deterministic scorer."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.benchmark_import import (
    EMPTY_THINK_PREFIX, PINNED_QWEN3_TOKENIZER_ID,
    REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256, REVIEWED_QWEN3_TOKENIZER_JSON_SHA256,
    _tokenizer_manifest,
)
from joulewise.gensuite import tokenizer_id_for
from joulewise.suite import (
    CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED, MARKER_DEFAULTS,
    OUTPUT_DEFAULTS, SUITE_SCHEMA_VERSION, SuiteManifest, suite_manifest_sha256,
)

REPO_URL = "https://github.com/openai/prm800k"
COMMIT = "7ecc794703b2877f63226f2477a49b34f9b25163"
LICENSE_BLOB_SHA1 = "4ccc7f8dba5cb9f5dc77f14778602ef4c0a585b2"
SOURCE_RECEIPTS = {
    "test.jsonl": {"sha256": "35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132", "bytes": 446564, "git_blob_sha1": "2376b9a194b46c0790e197c91b7249e5f88ac09b", "lfs_pointer_blob_sha1": "8837efbfa7fb7ad8a9a66b280a8cd86be3cd70bd", "line_count": 500, "license_blob_sha1": LICENSE_BLOB_SHA1},
    "train.jsonl": {"sha256": "90d96daeac3fe343ebb1e22ce93dd99690f75983e957f88de42f87cffe1e8076", "bytes": 10896985, "git_blob_sha1": "3a9d774ba092769cce4b93133bf3c97f2b8ea20c", "lfs_pointer_blob_sha1": "fabbf3962afc8d64618406adde7f012bf0ba3c20", "line_count": 12000, "license_blob_sha1": LICENSE_BLOB_SHA1},
}
PILOT_DOMAIN = "joulewise.benchmark_import.math.pilot.v1"
SELECTION_DOMAIN = "joulewise.benchmark_import.math.selection.v1"
SCORER_ID = "math_levels_v1/score_v1"
ANSWER_HASH_DOMAIN = "joulewise.math_answer.v1"
PROMPT_TEMPLATE = "{problem}\n\nPlease reason step by step, and put your final answer within \\boxed{}."
PROMPT_TEMPLATE_ID = "math_levels_v1/qwen3_chat_boxed_v1"
PROMPT_TEMPLATE_SHA256 = "1a0796c08f1175730c3dde6a9e7d38312904f985853cb2ad46d594a90dd2319d"
DIFFICULTY_QUARANTINE = "PENDING D-166 addendum/AP-5M: MATH author-assigned level (Hendrycks et al. 2021), fixed before any model output; stratifies comparisons and licenses no difficulty-causes-energy or intelligence-per-joule claim"
CONTAMINATION_NOTE = "PENDING AP-5M: MATH (2021) and PRM800K (2023) predate Qwen3 and are widely redistributed; pre-training contamination is UNMITIGABLE; accuracy is a property of this pinned subject-balanced rational-answer subset, never a capability claim"
CORRECTNESS_QUARANTINE = "quarantined annotation (C-004); malformed counts as incorrect (D-047.6); capped counts as truncated-incorrect (integration synthesis M2; AP-5M PENDING); no capability claim"
ELIGIBILITY_NOTE = "Rational-only reference subset: 2 duplicate rows, 954 non-rational references, and 5 ambiguous plain-comma references excluded; retained by level: 381/437, 733/894, 924/1130, 967/1214, 1035/1324."


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def authenticate_file(path: str | Path, name: str, *, pointer_path: str | Path | None = None, license_path: str | Path | None = None, expected: Mapping[str, Any] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Check every pinned receipt, including local pointer and license bytes."""
    if name not in SOURCE_RECEIPTS:
        raise ValueError(f"unknown source file: {name}")
    expected = SOURCE_RECEIPTS[name] if expected is None else expected
    if pointer_path is None:
        raise ValueError(f"{name} lfs_pointer_blob_sha1 receipt missing: pointer path required")
    if license_path is None:
        raise ValueError(f"{name} license_blob_sha1 receipt missing: license path required")
    payload = Path(path).read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{sha}\nsize {len(payload)}\n".encode("ascii")
    try:
        pointer_bytes = Path(pointer_path).read_bytes()
    except OSError as exc:
        raise ValueError(f"{name} lfs_pointer_blob_sha1 receipt missing") from exc
    try:
        license_bytes = Path(license_path).read_bytes()
    except OSError as exc:
        raise ValueError(f"{name} license_blob_sha1 receipt missing") from exc
    receipt = {"sha256": sha, "bytes": len(payload), "git_blob_sha1": git_blob_sha1(payload), "lfs_pointer_blob_sha1": git_blob_sha1(pointer_bytes), "line_count": len(payload.splitlines()), "license_blob_sha1": git_blob_sha1(license_bytes)}
    for field in ("sha256", "bytes", "git_blob_sha1", "lfs_pointer_blob_sha1", "line_count", "license_blob_sha1"):
        if receipt[field] != expected[field]:
            raise ValueError(f"{name} {field} receipt mismatch: got {receipt[field]}, expected {expected[field]}")
    if pointer_bytes != pointer:
        raise ValueError(f"{name} lfs_pointer_blob_sha1 receipt mismatch: committed pointer bytes mismatch")
    records = []
    for index, line in enumerate(payload.splitlines()):
        try:
            row = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{name} line {index + 1} invalid JSON") from exc
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) for k in ("problem", "solution", "answer", "subject", "unique_id")) or type(row.get("level")) is not int or row["level"] not in range(1, 6) or (row["unique_id"].startswith("test/") and any(not row[k] for k in ("problem", "solution", "answer", "subject"))):
            raise ValueError(f"{name} line {index + 1} invalid MATH row")
        records.append({**row, "source_file": name, "line_index": index})
    return records, receipt


def load_math_test(test_path: str | Path, train_path: str | Path, *, pointer_test: str | Path | None = None, pointer_train: str | Path | None = None, license_path: str | Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    test, test_receipt = authenticate_file(test_path, "test.jsonl", pointer_path=pointer_test, license_path=license_path)
    train, train_receipt = authenticate_file(train_path, "train.jsonl", pointer_path=pointer_train, license_path=license_path)
    if any(not row["unique_id"].startswith("test/") for row in test):
        raise ValueError("test.jsonl contains non-test unique_id")
    return test + [row for row in train if row["unique_id"].startswith("test/")], {"test.jsonl": test_receipt, "train.jsonl": train_receipt}


_INT = re.compile(r"[+-]?\d+")
_DEC = re.compile(r"[+-]?(?:\d+\.\d*|\.\d+)")
_GROUPED = re.compile(r"[+-]?\d{1,3}(?:,\d{3})+")
_SLASH = re.compile(r"([+-]?\d+)/(\d+)")
_ARG = r"(?:\{([+-]?\d+)\}|(\d))"
_FRAC = re.compile(r"([+-]?)\\frac" + _ARG + _ARG)
_UNIT = re.compile(r"(.*?)(?:\\(?:text|mbox|textrm|mathrm)\{[^{}0-9]*\})+")
_LHS = re.compile(r"[A-Za-z]=(.+)")


def canonical_reference_v1(raw: str) -> str | None:
    """Frozen reference parser: eligibility must not follow scorer revisions."""
    if not isinstance(raw, str):
        return None
    s = raw.replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
    s = s.replace(r"\$", "").replace("$", "")
    for token in (r"\!", r"\,", r"\;", r"\:", r"\ ", "~"):
        s = s.replace(token, "")
    s = "".join(s.split())
    for suffix in (r"^\circ", r"^{\circ}", r"\%", "%", r"\degree"):
        if s.endswith(suffix):
            s = s[:-len(suffix)]
            break
    match = _UNIT.fullmatch(s)
    if match and match.group(1):
        s = match.group(1)
    s = s.replace("{,}", ",")
    match = _LHS.fullmatch(s)
    if match:
        s = match.group(1)
    try:
        if _INT.fullmatch(s) or _DEC.fullmatch(s):
            return str(Fraction(s))
        if _GROUPED.fullmatch(s):
            return str(Fraction(s.replace(",", "")))
        match = _SLASH.fullmatch(s)
        if match:
            return str(Fraction(int(match.group(1)), int(match.group(2))))
        match = _FRAC.fullmatch(s)
        if match:
            sign, n1, n2, d1, d2 = match.groups()
            value = Fraction(int(n1 if n1 is not None else n2), int(d1 if d1 is not None else d2))
            return str(-value if sign == "-" else value)
    except (ValueError, ZeroDivisionError):
        pass
    return None


def canonical_math_rational(raw: str) -> str | None:
    """Response parser; deliberately duplicated from pinned reference v1."""
    if not isinstance(raw, str):
        return None
    s = raw.replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
    s = s.replace(r"\$", "").replace("$", "")
    for token in (r"\!", r"\,", r"\;", r"\:", r"\ ", "~"):
        s = s.replace(token, "")
    s = "".join(s.split())
    for suffix in (r"^\circ", r"^{\circ}", r"\%", "%", r"\degree"):
        if s.endswith(suffix):
            s = s[:-len(suffix)]
            break
    match = _UNIT.fullmatch(s)
    if match and match.group(1):
        s = match.group(1)
    s = s.replace("{,}", ",")
    match = _LHS.fullmatch(s)
    if match:
        s = match.group(1)
    try:
        if _INT.fullmatch(s) or _DEC.fullmatch(s):
            return str(Fraction(s))
        if _GROUPED.fullmatch(s):
            return str(Fraction(s.replace(",", "")))
        match = _SLASH.fullmatch(s)
        if match:
            return str(Fraction(int(match.group(1)), int(match.group(2))))
        match = _FRAC.fullmatch(s)
        if match:
            sign, n1, n2, d1, d2 = match.groups()
            value = Fraction(int(n1 if n1 is not None else n2), int(d1 if d1 is not None else d2))
            return str(-value if sign == "-" else value)
    except (ValueError, ZeroDivisionError):
        pass
    return None


def last_boxed(text: str) -> str | None:
    matches = list(re.finditer(r"\\(?:boxed|fbox)(?=\{|\s+[^\s{}])", text))
    if not matches:
        return None
    match = matches[-1]
    index = match.end()
    if text[index] != "{":
        token = re.match(r"\s+([^\s{}])", text[index:])
        return token.group(1) if token else None
    start = index
    depth = 0
    for cursor in range(start, len(text)):
        if text[cursor] == "{":
            depth += 1
        elif text[cursor] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:cursor]
    return None


def plain_comma_ambiguous(answer: str) -> bool:
    s = "".join(answer.split())
    for token in (r"\,", r"\;", r"\:"):
        s = s.replace(token, "")
    return "," in s.replace(r",\!", "").replace("{,}", "")


def eligible_records(rows: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ids = Counter(row["unique_id"] for row in rows)
    excluded = Counter()
    nonduplicate = Counter()
    eligible = []
    for row in rows:
        uid = row["unique_id"]
        level = row["level"]
        if ids[uid] > 1:
            excluded["duplicate_unique_id"] += 1
            continue
        nonduplicate[level] += 1
        gold = canonical_reference_v1(row["answer"])
        if gold is None:
            excluded["gold_not_rational"] += 1
            continue
        if plain_comma_ambiguous(row["answer"]):
            excluded["plain_comma_gold"] += 1
            continue
        box = last_boxed(row["solution"])
        if box is None or canonical_reference_v1(box) != gold:
            raise ValueError(f"reference answer/last box mismatch: {uid}")
        source_fields = {field: row[field] for field in ("problem", "answer", "level", "subject", "unique_id")}
        eligible.append({**row, "source_item_id": "math_" + uid.removesuffix(".json").replace("/", "_"), "source_sha256": canonical_json_sha256(source_fields), "expected_answer": gold, "in_math500": row["source_file"] == "test.jsonl"})
    levels = {str(level): {"nonduplicate": nonduplicate[level], "eligible": sum(row["level"] == level for row in eligible), "retention": sum(row["level"] == level for row in eligible) / nonduplicate[level] if nonduplicate[level] else None} for level in range(1, 6)}
    cells = {str(level): dict(sorted(Counter(row["subject"] for row in eligible if row["level"] == level).items())) for level in range(1, 6)}
    return eligible, {"rows": len(rows), "raw_distinct_ids": len(ids), "unique_ids": sum(count == 1 for count in ids.values()), "excluded": dict(excluded), "eligible": len(eligible), "levels": levels, "cells": cells, "reference_self_check": f"{len(eligible)}/{len(eligible)}"}


def selection_key(domain: str, source_sha256: str) -> str:
    return hashlib.sha256(f"{domain}\0{source_sha256}".encode("utf-8")).hexdigest()


def _keyed(rows: Sequence[Mapping[str, Any]], domain: str) -> list[dict[str, Any]]:
    result = [dict(row) for row in rows]
    keys = [selection_key(domain, row["source_sha256"]) for row in result]
    if len(keys) != len(set(keys)) or len({row["source_item_id"] for row in result}) != len(result):
        raise ValueError("duplicate selection key or source_item_id")
    return sorted(result, key=lambda row: selection_key(domain, row["source_sha256"]))


def _subject_interleaved(rows: Sequence[Mapping[str, Any]], domain: str) -> list[dict[str, Any]]:
    subjects = sorted({row["subject"] for row in rows})
    queues = {subject: [row for row in rows if row["subject"] == subject] for subject in subjects}
    ordered = []
    for round_index in range(max((len(queue) for queue in queues.values()), default=0)):
        round_rows = [queue[round_index] for queue in queues.values() if round_index < len(queue)]
        ordered.extend(sorted(round_rows, key=lambda row: selection_key(domain, row["source_sha256"])))
    return ordered


def select_pilot(rows: Sequence[Mapping[str, Any]], per_level: int = 16) -> list[dict[str, Any]]:
    if type(per_level) is not int or per_level <= 0:
        raise ValueError("per_level must be positive")
    queues = {level: _subject_interleaved(_keyed([r for r in rows if r["level"] == level], PILOT_DOMAIN), PILOT_DOMAIN) for level in range(1, 6)}
    if any(len(queue) < per_level for queue in queues.values()):
        raise ValueError("short pilot level")
    # Round-robin, hardest first; 16 complete rounds gives 16 in every level.
    return [queues[level][round_index] for round_index in range(per_level) for level in (5, 4, 3, 2, 1)]


def select_items(rows: Sequence[Mapping[str, Any]], pilot: Sequence[Mapping[str, Any]], n: int) -> list[dict[str, Any]]:
    if n not in (64, 128) or type(n) is not int:
        raise ValueError("n must be 64 or 128")
    pilot_ids = {row["source_item_id"] for row in pilot}
    if len(pilot_ids) != len(pilot):
        raise ValueError("duplicate pilot id")
    remaining = _keyed([row for row in rows if row["source_item_id"] not in pilot_ids], SELECTION_DOMAIN)
    selected = []
    for level in range(1, 6):
        ordered = _subject_interleaved([row for row in remaining if row["level"] == level], SELECTION_DOMAIN)
        if len(ordered) < n:
            raise ValueError(f"short level {level}: {len(ordered)} < {n}")
        selected.extend(ordered[:n])
    return selected


def score_response(response_text: str, expected_answer: str, *, runtime_status: str = "succeeded", enable_thinking: bool = False) -> dict[str, Any]:
    if runtime_status not in {"succeeded", "capped", "malformed", "runtime_failed"} or not isinstance(response_text, str):
        raise ValueError("invalid response or runtime status")
    reference = canonical_math_rational(expected_answer)
    if reference is None:
        raise ValueError("expected answer is not rational")
    section = response_text.rsplit("</think>", 1)[1] if enable_thinking and "</think>" in response_text else (None if enable_thinking else response_text)
    box = last_boxed(section) if section is not None else None
    parsed = canonical_math_rational(box) if box is not None else None
    # A stripped unit or percent can change the value; keep the parsed value
    # for audit, but never award correctness for these response-only hazards.
    unsafe_response = bool(box is not None and (
        re.search(r"\\(?:text|mathrm)\{\s*(?:thousand|million|billion|trillion|hundred|dozen|i)\s*\}", box, re.IGNORECASE)
        or re.search(r"i\s*$", box)
        or ("%" in box) != ("%" in expected_answer)
    ))
    parse_status = "missing_think_close" if section is None else "no_box_or_unbalanced" if box is None else "boxed_noncanonical" if parsed is None else "parsed"
    if runtime_status in {"runtime_failed", "malformed"}:
        outcome = "malformed"
    elif runtime_status == "capped":
        outcome = "truncated"
    elif section is None or box is None:
        outcome = "malformed"
    elif parsed == reference and not unsafe_response:
        outcome = "correct"
    else:
        outcome = "incorrect"
    return {"outcome": outcome, "correct": outcome == "correct", "parsed_answer": parsed, "expected_answer": reference, "parse_status": parse_status, "runtime_status": runtime_status}


def score_math_outcome_table(response_rows: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any], sidecar: Mapping[str, Any] | None = None) -> dict[str, Any]:
    native = manifest.get("schema_version") == SUITE_SCHEMA_VERSION
    if native:
        if sidecar is None:
            raise ValueError("MATH annotations required for native suite")
        validate_math_annotations(manifest, sidecar)
        items = manifest["items"]
        annotations = sidecar["annotations"]
        expected_ids_hash = manifest["benchmark_import"]["selected_item_ids_sha256"]
        enable_thinking = manifest["benchmark_import"]["enable_thinking"]
    else:
        items = manifest["items"]
        annotations = items
        expected_ids_hash = manifest["selected_item_ids_sha256"]
        enable_thinking = manifest["enable_thinking"]
    expected_ids = [item["item_id"] for item in items]
    observed = [row.get("item_id") for row in response_rows]
    if observed != expected_ids:
        raise ValueError("response exact-set/order mismatch")
    if canonical_json_sha256(expected_ids) != expected_ids_hash:
        raise ValueError("manifest id-list hash mismatch")
    results = []
    counts = {str(level): Counter() for level in range(1, 6)}
    for row, item, annotation in zip(response_rows, items, annotations, strict=True):
        level = annotation["level"]
        result = score_response(row["response_text"], annotation["expected_answer"], runtime_status=row["status"], enable_thinking=enable_thinking)
        result.update(item_id=item["item_id"], level=level)
        results.append(result)
        counts[str(level)][result["outcome"]] += 1
    return {"scorer_id": SCORER_ID, "correct_count": sum(r["correct"] for r in results), "item_count": len(results), "outcome_counts_by_level": {k: dict(v) for k, v in counts.items()}, "items": results, "quarantine": CORRECTNESS_QUARANTINE}


def render_prompts(rows: Sequence[Mapping[str, Any]], tokenizer_dirs: Sequence[str | Path], *, enable_thinking: bool) -> dict[str, Any]:
    """Lazy, local-only Qwen3 rendering; both mirrors must agree byte for byte."""
    if not tokenizer_dirs:
        raise ValueError("at least one tokenizer directory required")
    try:
        from transformers import AutoTokenizer, __version__ as version
    except ImportError as exc:
        raise RuntimeError("render_prompts requires transformers") from exc
    rendered = []
    pinsets = []
    for raw_dir in tokenizer_dirs:
        directory = Path(raw_dir)
        config = json.loads((directory / "tokenizer_config.json").read_text())
        chat_sha = hashlib.sha256(config["chat_template"].encode()).hexdigest()
        tokenizer_sha = hashlib.sha256((directory / "tokenizer.json").read_bytes()).hexdigest()
        tokenizer_id = tokenizer_id_for(tokenizer_manifest=_tokenizer_manifest(directory))
        pins = (chat_sha, tokenizer_sha, tokenizer_id)
        if pins != (REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256, REVIEWED_QWEN3_TOKENIZER_JSON_SHA256, PINNED_QWEN3_TOKENIZER_ID):
            raise ValueError("reviewed Qwen3 tokenizer pin mismatch")
        pinsets.append(pins)
        tokenizer = AutoTokenizer.from_pretrained(str(directory), local_files_only=True)
        current = []
        for row in rows:
            prompt = PROMPT_TEMPLATE.replace("{problem}", row["problem"])
            messages = [{"role": "user", "content": prompt}]
            kwargs = {"add_generation_prompt": True, "enable_thinking": enable_thinking}
            text = tokenizer.apply_chat_template(messages, tokenize=False, **kwargs)
            ids = list(tokenizer.apply_chat_template(messages, tokenize=True, **kwargs))
            if list(tokenizer.encode(text, add_special_tokens=True)) != ids:
                raise ValueError("prompt text/token ids mismatch")
            if text != _expected_rendered_prompt(row["problem"], enable_thinking):
                raise ValueError("rendered prompt shape mismatch")
            current.append({"source_item_id": row["source_item_id"], "rendered_prompt_text": text, "prompt_token_ids": ids})
        if rendered and current != rendered:
            raise ValueError("tokenizer mirrors render differently")
        rendered = current
    return {"items": rendered, "chat_template_sha256": pinsets[0][0], "tokenizer_json_sha256": pinsets[0][1], "tokenizer_id": pinsets[0][2], "rendered_with": {"library": "transformers", "version": version}}


def _expected_rendered_prompt(problem: str, enable_thinking: bool) -> str:
    user = PROMPT_TEMPLATE.replace("{problem}", problem)
    tail = "" if enable_thinking else EMPTY_THINK_PREFIX
    return f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n{tail}"


def build_math_manifest(rows: Sequence[Mapping[str, Any]], receipts: Mapping[str, Any], *, set_name: str, n: int | None = None, enable_thinking: bool = False, rendered: Mapping[str, Any] | None = None) -> dict[str, Any]:
    eligible, population = eligible_records(rows)
    pilot = select_pilot(eligible)
    if set_name == "pilot":
        selected = pilot
    elif set_name == "test" and n in (64, 128):
        selected = select_items(eligible, pilot, n)
    else:
        raise ValueError("set must be pilot or test with n=64/128")
    if rendered is not None and [r["source_item_id"] for r in rendered["items"]] != [r["source_item_id"] for r in selected]:
        raise ValueError("rendered item order mismatch")
    items = []
    for index, row in enumerate(selected):
        rendered_row = rendered["items"][index] if rendered is not None else None
        item = {key: row[key] for key in ("source_item_id", "source_sha256", "source_file", "line_index", "unique_id", "level", "subject", "in_math500", "problem", "expected_answer")}
        item["item_id"] = item["source_item_id"]
        item["difficulty"] = {"axis": "math_author_level", "value": row["level"], "scale": "ordinal", "label": f"Level {row['level']}", "source": "hendrycks_math_2021", "quarantine_note": DIFFICULTY_QUARANTINE}
        if rendered_row is not None:
            item["prompt_text"] = rendered_row["rendered_prompt_text"]
            item["prompt_token_ids"] = rendered_row["prompt_token_ids"]
        else:
            item["prompt_text"] = PROMPT_TEMPLATE.replace("{problem}", row["problem"])
        items.append(item)
    ids = [row["item_id"] for row in items]
    return {"schema_version": "math_scored_manifest.v1", "dataset": "math", "repo_url": REPO_URL, "commit": COMMIT, "set": set_name, "n_per_level": n if set_name == "test" else 16, "enable_thinking": enable_thinking, "scorer_id": SCORER_ID, "prompt_template_id": PROMPT_TEMPLATE_ID, "prompt_template_sha256": PROMPT_TEMPLATE_SHA256, "source_files": receipts, "population": population, "eligibility_note": ELIGIBILITY_NOTE, "contamination_note": CONTAMINATION_NOTE, "correctness_quarantine": CORRECTNESS_QUARANTINE, "pilot_item_ids_sha256": canonical_json_sha256([row["source_item_id"] for row in pilot]), "selected_item_ids_sha256": canonical_json_sha256(ids), "items": items, "rendering": {k: v for k, v in rendered.items() if k != "items"} if rendered else None}


def hash_only_manifest(full: Mapping[str, Any]) -> dict[str, Any]:
    return {"schema_version": "math_hash_only_manifest.v1", "dataset": full["dataset"], "commit": full["commit"], "set": full["set"], "n_per_level": full["n_per_level"], "enable_thinking": full["enable_thinking"], "source_files": full["source_files"], "population": full["population"], "pilot_item_ids_sha256": full["pilot_item_ids_sha256"], "selected_item_ids_sha256": full["selected_item_ids_sha256"], "prompt_template_sha256": full["prompt_template_sha256"], "items": [{"item_id": row["item_id"], "source_sha256": row["source_sha256"]} for row in full["items"]]}


def expected_answer_sha256(item_id: str, answer: str) -> str:
    return hashlib.sha256(f"{ANSWER_HASH_DOMAIN}\0{item_id}\0{answer}".encode("utf-8")).hexdigest()


def _selected_records(rows: Sequence[Mapping[str, Any]], set_name: str, n: int | None) -> list[dict[str, Any]]:
    eligible, _ = eligible_records(rows)
    pilot = select_pilot(eligible)
    if set_name == "pilot" and n is None:
        return pilot
    if set_name == "test" and n in (64, 128):
        return select_items(eligible, pilot, n)
    raise ValueError("set must be pilot or test with n=64/128")


def build_math_suite_manifest(
    rows: Sequence[Mapping[str, Any]], receipts: Mapping[str, Any],
    *, set_name: str, n: int | None, enable_thinking: bool,
    rendered: Mapping[str, Any], output_cap: int,
) -> dict[str, Any]:
    """Build a native suite_manifest.v2 once rendering and cap are pinned."""
    if type(output_cap) is not int or output_cap <= 0:
        raise ValueError("output_cap must be positive")
    selected = _selected_records(rows, set_name, n)
    rendered_items = rendered.get("items")
    if not isinstance(rendered_items, list) or [r.get("source_item_id") for r in rendered_items] != [r["source_item_id"] for r in selected]:
        raise ValueError("rendered item order mismatch")
    pins = (
        rendered.get("chat_template_sha256"),
        rendered.get("tokenizer_json_sha256"),
        rendered.get("tokenizer_id"),
    )
    if pins != (
        REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256,
        REVIEWED_QWEN3_TOKENIZER_JSON_SHA256,
        PINNED_QWEN3_TOKENIZER_ID,
    ):
        raise ValueError("reviewed Qwen3 rendering pin mismatch")
    source_files = []
    for name in ("test.jsonl", "train.jsonl"):
        if receipts.get(name) != SOURCE_RECEIPTS[name]:
            raise ValueError(f"{name} receipt mismatch")
        source_files.append({"path": f"prm800k/math_splits/{name}", **receipts[name]})
    ids = [row["source_item_id"] for row in selected]
    subset = [{"source_item_id": row["source_item_id"], "source_sha256": row["source_sha256"]} for row in selected]
    subset_hash = canonical_json_sha256(subset)
    ids_hash = canonical_json_sha256(ids)
    set_label = "pilot" if set_name == "pilot" else f"n{n}"
    arm = "think" if enable_thinking else "nothink"
    items = []
    for row, rendered_row in zip(selected, rendered_items, strict=True):
        item_id = row["source_item_id"]
        token_ids = rendered_row.get("prompt_token_ids")
        prompt_text = rendered_row.get("rendered_prompt_text")
        if not isinstance(token_ids, list) or not token_ids or not isinstance(prompt_text, str):
            raise ValueError(f"rendered prompt missing for {item_id}")
        if prompt_text != _expected_rendered_prompt(row["problem"], enable_thinking):
            raise ValueError(f"rendered prompt shape mismatch for {item_id}")
        items.append({
            "item_id": item_id, "item_type": "text_prompt", "category": "math",
            "difficulty": {"axis": "math_author_level", "value": row["level"], "scale": "ordinal", "label": f"Level {row['level']}", "source": "hendrycks_math_2021", "quarantine_note": DIFFICULTY_QUARANTINE},
            "shape": {"planned_prompt_tokens": len(token_ids), "planned_output_tokens": output_cap, "prompt_level": f"{len(token_ids)}_tokens", "decode_level": f"{output_cap}_cap"},
            "source": {"source_item_id": item_id, "source_sha256": row["source_sha256"], "prompt_template_id": PROMPT_TEMPLATE_ID, "license": "MIT", "contamination_note": CONTAMINATION_NOTE, "prompt_text": prompt_text, "prompt_token_ids": token_ids},
            "grouping": {"condition_id": f"math_{set_label}_{arm}_c{output_cap}", "block_id": "math_pilot" if set_name == "pilot" else f"math_level_{row['level']}", "level_id": "pilot" if set_name == "pilot" else f"level_{row['level']}", "prefix_group_id": None},
            "output_policy": "natural_eos", "tags": ["math", "scored", set_name, arm],
            "scoring": {"scorer_id": SCORER_ID, "expected_answer_hash": expected_answer_sha256(item_id, row["expected_answer"]), "correctness_quarantine": CORRECTNESS_QUARANTINE},
        })
    manifest = {
        "schema_version": SUITE_SCHEMA_VERSION, "suite_id": "math_levels_v1",
        "suite_profile": f"math_levels_v1_{set_label}_{arm}_c{output_cap}",
        "suite_revision": "2026-09-23.pending-ap5m", "suite_seed": SELECTION_DOMAIN,
        "generator": {"name": "math_levels_v1", "version": "1.0.0", "parameters_hash": canonical_json_sha256({"set": set_label, "arm": arm, "output_cap": output_cap, "prompt_template_sha256": PROMPT_TEMPLATE_SHA256, "selection_domain": PILOT_DOMAIN if set_name == "pilot" else SELECTION_DOMAIN})},
        "analysis_contract": {"independent_unit": "bundle", "primary_window_class": "suite", "allowed_aggregation_levels": ["suite", "block", "level"]},
        "execution_policy": {"order_policy": "manifest_order", "within_bundle_repeats": 1, "cooldown_policy": "bundle_only", "declared_cache_policy": "warm_cache", "cache_policy_verification": CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED, "warmup_policy": "adapter_default", "default_output_policy": "natural_eos"},
        "source_manifest": {"source_kind": "benchmark_import", "source_id": f"openai/prm800k@{COMMIT}:prm800k/math_splits/test+train", "revision": COMMIT, "subset_id": f"math_test_{set_label}_{arm}_v1", "subset_sha256": subset_hash, "license": "MIT", "contamination_note": CONTAMINATION_NOTE + "; " + ELIGIBILITY_NOTE},
        "benchmark_import": {"dataset": "math", "split": "test", "repo_url": REPO_URL, "commit": COMMIT, "file_path": "prm800k/math_splits/test.jsonl", "file_sha256": receipts["test.jsonl"]["sha256"], "file_git_blob_sha1": receipts["test.jsonl"]["git_blob_sha1"], "license_spdx": "MIT", "license_blob_sha1": receipts["test.jsonl"]["license_blob_sha1"], "source_files": source_files, "selection_rule": "domain-separated SHA-256; pilot and test subject-interleaved per level", "selection_domain": PILOT_DOMAIN if set_name == "pilot" else SELECTION_DOMAIN, "k": len(selected), "selected_item_ids": ids, "selected_item_ids_sha256": ids_hash, "canonical_subset_json_sha256": subset_hash, "prompt_template_id": PROMPT_TEMPLATE_ID, "prompt_template_sha256": PROMPT_TEMPLATE_SHA256, "chat_template_sha256": pins[0], "enable_thinking": enable_thinking, "tokenizer_json_sha256": pins[1], "tokenizer_id": pins[2], "rendered_with": rendered["rendered_with"]},
        "items": items, "markers": dict(MARKER_DEFAULTS), "outputs": dict(OUTPUT_DEFAULTS),
    }
    SuiteManifest.from_mapping(manifest)
    return manifest


def build_math_annotations(manifest: Mapping[str, Any], selected: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Keep reference answers and source-row identity outside the runnable suite."""
    validated = SuiteManifest.from_mapping(manifest)
    if [r["source_item_id"] for r in selected] != [i.item_id for i in validated.items]:
        raise ValueError("annotation source order mismatch")
    annotations = []
    for index, (item, row) in enumerate(zip(validated.items, selected, strict=True)):
        annotation = {key: row[key] for key in ("source_item_id", "source_sha256", "source_file", "line_index", "unique_id", "level", "subject", "in_math500")}
        annotation.update(item_id=item.item_id, execution_index=index, source_answer=row["answer"], expected_answer=row["expected_answer"], expected_answer_sha256=expected_answer_sha256(item.item_id, row["expected_answer"]), scorer_id=SCORER_ID)
        annotations.append(annotation)
    sidecar = {"schema_version": "math_levels_annotations.v1", "suite_id": validated.suite_id, "manifest_sha256": suite_manifest_sha256(manifest), "quarantine": CORRECTNESS_QUARANTINE, "annotations": annotations}
    validate_math_annotations(manifest, sidecar)
    return sidecar


def validate_math_annotations(manifest: Mapping[str, Any], sidecar: Mapping[str, Any]) -> None:
    validated = SuiteManifest.from_mapping(manifest)
    benchmark = validated.benchmark_import
    if benchmark is None or benchmark.source_files is None:
        raise ValueError("MATH two-file benchmark receipts missing")
    files = {Path(entry["path"]).name: entry for entry in benchmark.source_files}
    if sidecar.get("schema_version") != "math_levels_annotations.v1" or sidecar.get("suite_id") != validated.suite_id or sidecar.get("manifest_sha256") != suite_manifest_sha256(manifest):
        raise ValueError("MATH annotation manifest binding mismatch")
    annotations = sidecar.get("annotations")
    if not isinstance(annotations, list) or len(annotations) != len(validated.items):
        raise ValueError("MATH annotation count mismatch")
    subset = []
    for index, (item, row) in enumerate(zip(validated.items, annotations, strict=True)):
        if not isinstance(row, Mapping) or row.get("execution_index") != index or row.get("item_id") != item.item_id or row.get("source_item_id") != item.source.source_item_id or row.get("source_sha256") != item.source.source_sha256:
            raise ValueError(f"MATH annotation {index} identity mismatch")
        if row.get("source_file") not in files or type(row.get("line_index")) is not int or not 0 <= row["line_index"] < files[row["source_file"]]["line_count"] or row.get("in_math500") != (row["source_file"] == "test.jsonl"):
            raise ValueError(f"MATH annotation {index} source location mismatch")
        uid = row.get("unique_id")
        if not isinstance(uid, str) or "math_" + uid.removesuffix(".json").replace("/", "_") != item.item_id:
            raise ValueError(f"MATH annotation {index} unique_id mismatch")
        if row.get("level") != item.difficulty.value or not isinstance(row.get("subject"), str):
            raise ValueError(f"MATH annotation {index} level/subject mismatch")
        answer = row.get("source_answer")
        expected = row.get("expected_answer")
        if not isinstance(answer, str) or not isinstance(expected, str) or canonical_math_rational(answer) != expected:
            raise ValueError(f"MATH annotation {index} answer mismatch")
        answer_hash = expected_answer_sha256(item.item_id, expected)
        if row.get("expected_answer_sha256") != answer_hash or item.scoring is None or item.scoring.expected_answer_hash != answer_hash or row.get("scorer_id") != SCORER_ID:
            raise ValueError(f"MATH annotation {index} answer hash mismatch")
        prompt = item.source.prompt_text
        prefix = "<|im_start|>user\n"
        suffix = PROMPT_TEMPLATE.replace("{problem}", "")
        full_suffix = suffix + "<|im_end|>\n<|im_start|>assistant\n" + ("" if benchmark.enable_thinking else EMPTY_THINK_PREFIX)
        if not isinstance(prompt, str) or not prompt.startswith(prefix) or not prompt.endswith(full_suffix):
            raise ValueError(f"MATH annotation {index} prompt shape mismatch")
        problem = prompt[len(prefix):-len(full_suffix)]
        if prompt != _expected_rendered_prompt(problem, benchmark.enable_thinking):
            raise ValueError(f"MATH annotation {index} prompt shape mismatch")
        source_fields = {"problem": problem, "answer": answer, "level": row["level"], "subject": row["subject"], "unique_id": uid}
        if canonical_json_sha256(source_fields) != item.source.source_sha256:
            raise ValueError(f"MATH annotation {index} source hash mismatch")
        subset.append({"source_item_id": item.item_id, "source_sha256": item.source.source_sha256})
    if canonical_json_sha256(subset) != benchmark.canonical_subset_json_sha256:
        raise ValueError("MATH annotation subset hash mismatch")
