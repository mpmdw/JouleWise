"""Affine smoke envelope-gate analysis (P2-010b).

The gate consumes strict-valid suite bundles and emits a D-036-style verdict
computed from recorded per-item evidence. D-047.3 is load-bearing here:
deterministic smoke repetitions replicate energy only, so token, stop-reason,
and advisory correctness denominators are distinct non-sentinel items.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from joulewise.bundle_read import BundleReadError, BundleReader

STRICT_PROBLEMS = Callable[[Path], list[str]]

VERDICT_VALIDATED = "envelope_validated"
VERDICT_FAILED = "envelope_failed"
VERDICT_REFUSED = "bundle_refused"

REASON_BUNDLE_NOT_STRICT_VALID = "bundle_not_strict_valid"
REASON_SUITE_MANIFEST_MISSING = "suite_manifest_missing"
REASON_SUMMARY_SUITE_METRICS_MISSING = "summary_suite_metrics_missing"
REASON_SUITE_SEED_MISMATCH = "suite_seed_mismatch"
REASON_SUITE_ID_MISMATCH = "suite_id_mismatch"
REASON_SUITE_PROFILE_MISMATCH = "suite_profile_mismatch"
REASON_SUITE_MANIFEST_IDENTITY_MISMATCH = "suite_manifest_identity_mismatch"
REASON_LEVEL_SET_MISMATCH = "level_set_mismatch"
REASON_ITEM_EVIDENCE_MALFORMED = "item_evidence_malformed"
REASON_DENOMINATOR_NOT_8 = "denominator_not_8_distinct_non_sentinel_items"
REASON_DISTINCT_ITEM_EVIDENCE_CONFLICT = "distinct_item_evidence_conflict"
REASON_E1 = "E1_stop_reason_invariance_failed"
REASON_E2 = "E2_emitted_token_mean_invariance_failed"
REASON_E3 = "E3_emitted_token_distribution_homogeneity_failed"
REASON_E4 = "E4_prompt_token_invariance_failed"

# Out-of-domain suite shape is a D-036 input refusal, not a failed science
# gate: E1-E4 are only meaningful for the P2-010b affine smoke profile.
EXPECTED_SUITE_ID = "affine_smoke_v1"
EXPECTED_WORKLOAD_PROFILE = "affine_smoke_v1"
EXPECTED_MANIFEST_SUITE_PROFILE = "affine_mod_ladder_v1_smoke"
EXPECTED_LEVEL_IDS = ("L01", "L08", "L64")
EXPECTED_LEVEL_DENOMINATOR = 8
E1_MAX_NON_EOS_RATE = 0.05
E1_MAX_RATE_SPREAD = 0.05
E2_MAX_MEAN_SPREAD_TOKENS = 1.0
E3_PERMUTATIONS = 10_000
E3_MIN_PERMUTATION_P = 0.01
E4_MAX_GLOBAL_PROMPT_TOKEN_RANGE = 4
E4_MAX_LEVEL_MEAN_SPREAD_TOKENS = 2.0
E5_MIN_DISTINCT_PARSED_PER_CLASS = 10


@dataclass(frozen=True)
class _ItemEvidence:
    item_id: str
    level_id: str
    prompt_tokens: int
    emitted_tokens: int
    stop_reason: str
    status: str
    parse_status: str | None
    correct: bool | None


def analyze_envelope_gate(
    bundle_dirs: list[Path],
    strict_problems: STRICT_PROBLEMS,
) -> dict[str, Any]:
    """Return the JSON-serializable envelope-gate verdict artifact."""
    paths = [Path(path) for path in bundle_dirs]
    if not paths:
        return _refused([], [REASON_BUNDLE_NOT_STRICT_VALID], "no bundle directories provided")

    bundle_records: list[dict[str, Any]] = []
    readers: list[BundleReader] = []
    refusal_reasons: list[str] = []
    for path in paths:
        problems = strict_problems(path)
        record = {
            "path": str(path),
            "hashes": _bundle_hashes(path),
            "strict_valid": not problems,
            "strict_problems": problems,
        }
        bundle_records.append(record)
        if problems:
            refusal_reasons.append(REASON_BUNDLE_NOT_STRICT_VALID)
        else:
            readers.append(BundleReader(path))
    if refusal_reasons:
        return _refused(bundle_records, sorted(set(refusal_reasons)), "all inputs must be strict-valid bundles")

    try:
        manifest_records = [_manifest_record(reader) for reader in readers]
    except BundleReadError as exc:
        return _refused(bundle_records, [REASON_SUITE_MANIFEST_MISSING], str(exc))
    if any(record is None for record in manifest_records):
        return _refused(
            bundle_records,
            [REASON_SUITE_MANIFEST_MISSING],
            "each bundle must carry suite_manifest.json",
        )
    manifests = [record for record in manifest_records if record is not None]
    domain_problem = _suite_domain_problem(manifests)
    if domain_problem is not None:
        reason, message, extra = domain_problem
        return _refused(bundle_records, [reason], message, extra=extra)
    suite_seeds = {record["suite_seed"] for record in manifests}
    if len(suite_seeds) != 1:
        return _refused(
            bundle_records,
            [REASON_SUITE_SEED_MISMATCH],
            "all bundles must use the same suite_seed for the E3 permutation seed",
        )
    identity_problem = _suite_identity_problem(manifests)
    if identity_problem is not None:
        return _refused(
            bundle_records,
            [REASON_SUITE_MANIFEST_IDENTITY_MISMATCH],
            "all bundles must be repetitions of the same affine smoke suite manifest",
            extra={"suite_identities": identity_problem},
        )

    summary_missing = [
        str(reader.path)
        for reader in readers
        if not isinstance(reader.raw_summary().get("suite_metrics"), dict)
    ]
    if summary_missing:
        return _refused(
            bundle_records,
            [REASON_SUMMARY_SUITE_METRICS_MISSING],
            "each strict-valid suite bundle must have summary_metrics.suite_metrics",
            extra={"missing_suite_metrics": summary_missing},
        )

    try:
        evidence, evidence_conflicts = _distinct_item_evidence(readers)
    except BundleReadError as exc:
        return _refused(bundle_records, [REASON_ITEM_EVIDENCE_MALFORMED], str(exc))
    levels = _sorted_levels(evidence)
    if tuple(levels) != EXPECTED_LEVEL_IDS:
        return _refused(
            bundle_records,
            [REASON_LEVEL_SET_MISMATCH],
            "affine smoke gate requires exactly the D-047.2 levels L01, L08, and L64",
            extra={
                "expected_levels": list(EXPECTED_LEVEL_IDS),
                "observed_levels": levels,
            },
        )
    denominators = {
        level: len([item for item in evidence.values() if item.level_id == level])
        for level in EXPECTED_LEVEL_IDS
    }
    reason_codes: list[str] = []
    if any(value != EXPECTED_LEVEL_DENOMINATOR for value in denominators.values()):
        reason_codes.append(REASON_DENOMINATOR_NOT_8)
    if evidence_conflicts:
        reason_codes.append(REASON_DISTINCT_ITEM_EVIDENCE_CONFLICT)

    e1 = _gate_e1(evidence, levels)
    e2 = _gate_e2(evidence, levels)
    e3 = _gate_e3(evidence, levels, next(iter(suite_seeds)))
    e4 = _gate_e4(evidence, levels)
    e5 = _advisory_e5(evidence, levels)

    for gate, code in ((e1, REASON_E1), (e2, REASON_E2), (e3, REASON_E3), (e4, REASON_E4)):
        if not gate["pass"]:
            reason_codes.append(code)

    reason_codes = sorted(set(reason_codes))
    verdict = VERDICT_VALIDATED if not reason_codes else VERDICT_FAILED
    return {
        "schema_version": "envelope_gate.v1",
        "verdict": verdict,
        "reason_codes": reason_codes,
        "bundle_count": len(readers),
        "bundle_hashes": bundle_records,
        "suite": {
            "suite_id": manifests[0]["suite_id"],
            "suite_profile": manifests[0]["suite_profile"],
            "suite_revision": manifests[0]["suite_revision"],
            "suite_seed": manifests[0]["suite_seed"],
            "manifest_sha256": sorted({record["manifest_sha256"] for record in manifests}),
        },
        "denominators": {
            "rule": "8 distinct non-sentinel items per level; repeated bundles replicate energy only",
            "expected_per_level": EXPECTED_LEVEL_DENOMINATOR,
            "observed_distinct_non_sentinel_items_per_level": denominators,
            "sentinel_exclusion": "items tagged 'sentinel' are excluded from all gate level statistics",
        },
        "gates": {"E1": e1, "E2": e2, "E3": e3, "E4": e4, "E5": e5},
        "evidence_conflicts": evidence_conflicts,
        "calibration_evidence_only": {
            "label": "measured level-window gross energies from suite_metrics; not gate statistics",
            "level_window_gross_energies_j": _level_window_energy_records(readers),
        },
    }


def _refused(
    bundle_records: list[dict[str, Any]],
    reason_codes: list[str],
    message: str,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "envelope_gate.v1",
        "verdict": VERDICT_REFUSED,
        "reason_codes": sorted(set(reason_codes)),
        "bundle_count": len(bundle_records),
        "bundle_hashes": bundle_records,
        "refusal_message": message,
    }
    if extra:
        result.update(extra)
    return result


def _manifest_record(reader: BundleReader) -> dict[str, Any] | None:
    manifest = reader.suite_manifest()
    if manifest is None:
        return None
    config = reader.config()
    metadata = reader.metadata()
    suite_metadata = metadata.get("suite") if isinstance(metadata.get("suite"), dict) else {}
    manifest_sha256 = suite_metadata.get("manifest_sha256")
    return {
        "suite_id": manifest.suite_id,
        "suite_profile": manifest.suite_profile,
        "suite_revision": manifest.suite_revision,
        "suite_seed": manifest.suite_seed,
        "workload_profile": config.workload_profile.name,
        "manifest_sha256": manifest_sha256 if isinstance(manifest_sha256, str) else "",
        "manifest_levels": _sorted_manifest_levels(manifest),
    }


def _sorted_manifest_levels(manifest: Any) -> list[str]:
    levels = {
        item.grouping.level_id
        for item in manifest.items
        if "sentinel" not in item.tags
    }
    return sorted(levels, key=_level_sort_key)


def _suite_domain_problem(
    manifests: list[dict[str, str]],
) -> tuple[str, str, dict[str, Any]] | None:
    bad_suite_ids = sorted(
        {
            record["suite_id"]
            for record in manifests
            if record["suite_id"] != EXPECTED_SUITE_ID
        }
    )
    if bad_suite_ids:
        return (
            REASON_SUITE_ID_MISMATCH,
            "affine smoke gate only accepts suite_id affine_smoke_v1",
            {"expected_suite_id": EXPECTED_SUITE_ID, "observed_suite_ids": bad_suite_ids},
        )
    bad_workload_profiles = sorted(
        {
            record["workload_profile"]
            for record in manifests
            if record["workload_profile"] != EXPECTED_WORKLOAD_PROFILE
        }
    )
    bad_manifest_profiles = sorted(
        {
            record["suite_profile"]
            for record in manifests
            if record["suite_profile"] != EXPECTED_MANIFEST_SUITE_PROFILE
        }
    )
    if bad_workload_profiles or bad_manifest_profiles:
        return (
            REASON_SUITE_PROFILE_MISMATCH,
            "affine smoke gate only accepts the affine_smoke_v1 profile",
            {
                "expected_workload_profile": EXPECTED_WORKLOAD_PROFILE,
                "observed_workload_profiles": bad_workload_profiles,
                "expected_manifest_suite_profile": EXPECTED_MANIFEST_SUITE_PROFILE,
                "observed_manifest_suite_profiles": bad_manifest_profiles,
            },
        )
    manifest_level_sets = sorted(
        {
            tuple(record["manifest_levels"])
            for record in manifests
            if tuple(record["manifest_levels"]) != EXPECTED_LEVEL_IDS
        }
    )
    if manifest_level_sets:
        return (
            REASON_LEVEL_SET_MISMATCH,
            "affine smoke gate requires exactly the D-047.2 levels L01, L08, and L64",
            {
                "expected_levels": list(EXPECTED_LEVEL_IDS),
                "observed_manifest_level_sets": [list(levels) for levels in manifest_level_sets],
            },
        )
    return None


def _suite_identity_problem(manifests: list[dict[str, str]]) -> list[dict[str, str]] | None:
    identities = [
        {
            "suite_id": record["suite_id"],
            "suite_profile": record["suite_profile"],
            "suite_revision": record["suite_revision"],
            "suite_seed": record["suite_seed"],
            "manifest_sha256": record["manifest_sha256"],
        }
        for record in manifests
    ]
    unique = {tuple(sorted(identity.items())) for identity in identities}
    if len(unique) <= 1:
        return None
    return identities


def _distinct_item_evidence(
    readers: list[BundleReader],
) -> tuple[dict[str, _ItemEvidence], list[dict[str, Any]]]:
    by_id: dict[str, _ItemEvidence] = {}
    conflicts: list[dict[str, Any]] = []
    for reader in readers:
        manifest = reader.suite_manifest()
        if manifest is None:
            continue
        outputs = _suite_outputs_by_index(reader.path)
        manifest_items = list(manifest.items)
        for window in reader.item_windows():
            if window.item_index < 0 or window.item_index >= len(manifest_items):
                continue
            manifest_item = manifest_items[window.item_index]
            if "sentinel" in manifest_item.tags:
                continue
            evidence = _item_evidence(window, manifest_item.grouping.level_id, outputs)
            existing = by_id.get(evidence.item_id)
            if existing is None:
                by_id[evidence.item_id] = evidence
            elif existing != evidence:
                conflicts.append(
                    {
                        "item_id": evidence.item_id,
                        "bundle_path": str(reader.path),
                        "first": _evidence_dict(existing),
                        "conflicting": _evidence_dict(evidence),
                    }
                )
    return by_id, conflicts


def _item_evidence(window: Any, level_id: str, outputs: dict[int, dict[str, Any]]) -> _ItemEvidence:
    output = outputs.get(window.item_index, {})
    return _ItemEvidence(
        item_id=window.item_id,
        level_id=level_id,
        prompt_tokens=_required_int(window.end_metadata.get("prompt_tokens"), "prompt_tokens"),
        emitted_tokens=_required_int(window.end_metadata.get("emitted_tokens"), "emitted_tokens"),
        stop_reason=_required_str(window.end_metadata.get("stop_reason"), "stop_reason"),
        status=window.status,
        parse_status=_optional_parse_status(output),
        correct=_optional_correct(output),
    )


def _required_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BundleReadError(
            f"item evidence {field_name} is not a non-negative integer: {value!r}"
        )
    return value


def _required_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise BundleReadError(f"item evidence {field_name} is not a string: {value!r}")
    return value


def _optional_parse_status(output: dict[str, Any]) -> str | None:
    value = output.get("parse_status")
    if isinstance(value, str):
        return value
    scoring = output.get("scoring")
    if isinstance(scoring, dict) and isinstance(scoring.get("parse_status"), str):
        return scoring["parse_status"]
    return None


def _optional_correct(output: dict[str, Any]) -> bool | None:
    value = output.get("correct")
    if isinstance(value, bool):
        return value
    scoring = output.get("scoring")
    if isinstance(scoring, dict) and isinstance(scoring.get("correct"), bool):
        return scoring["correct"]
    return None


def _suite_outputs_by_index(path: Path) -> dict[int, dict[str, Any]]:
    output_path = path / "outputs" / "suite_items.jsonl"
    records: dict[int, dict[str, Any]] = {}
    try:
        text = output_path.read_text()
    except OSError:
        return records
    for line in text.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            continue
        index = record.get("item_index")
        if isinstance(index, int) and not isinstance(index, bool):
            records[index] = record
    return records


def _sorted_levels(evidence: dict[str, _ItemEvidence]) -> list[str]:
    levels = sorted({item.level_id for item in evidence.values()}, key=_level_sort_key)
    return levels


def _level_sort_key(level_id: str) -> tuple[int, str]:
    digits = "".join(ch for ch in level_id if ch.isdigit())
    if digits:
        return (int(digits), level_id)
    return (10**9, level_id)


def _by_level(evidence: dict[str, _ItemEvidence], level: str) -> list[_ItemEvidence]:
    return sorted(
        [item for item in evidence.values() if item.level_id == level],
        key=lambda item: item.item_id,
    )


def _gate_e1(evidence: dict[str, _ItemEvidence], levels: list[str]) -> dict[str, Any]:
    rates: dict[str, float] = {}
    counts: dict[str, dict[str, int]] = {}
    for level in levels:
        items = _by_level(evidence, level)
        non_eos = sum(1 for item in items if item.stop_reason != "eos")
        denom = len(items)
        rates[level] = non_eos / denom if denom else 0.0
        counts[level] = {"non_eos": non_eos, "denominator": denom}
    max_rate = max(rates.values()) if rates else 0.0
    min_rate = min(rates.values()) if rates else 0.0
    spread = max_rate - min_rate
    return {
        "pass": max_rate <= E1_MAX_NON_EOS_RATE and spread <= E1_MAX_RATE_SPREAD,
        "metric": "fraction stop_reason != 'eos' per level",
        "counts": counts,
        "rates": rates,
        "max_rate": max_rate,
        "spread": spread,
        "thresholds": {
            "max_rate_lte": E1_MAX_NON_EOS_RATE,
            "spread_lte": E1_MAX_RATE_SPREAD,
            "zero_tolerance_note": "at n=8 distinct items, the 5% threshold means zero tolerated non-EOS items per level",
        },
    }


def _gate_e2(evidence: dict[str, _ItemEvidence], levels: list[str]) -> dict[str, Any]:
    means = {
        level: _mean([item.emitted_tokens for item in _by_level(evidence, level)])
        for level in levels
    }
    spread = (max(means.values()) - min(means.values())) if means else 0.0
    return {
        "pass": spread <= E2_MAX_MEAN_SPREAD_TOKENS,
        "metric": "per-level mean emitted_tokens spread",
        "level_means": means,
        "spread_tokens": spread,
        "thresholds": {"spread_tokens_lte": E2_MAX_MEAN_SPREAD_TOKENS},
    }


def _gate_e3(evidence: dict[str, _ItemEvidence], levels: list[str], suite_seed: str) -> dict[str, Any]:
    labels: list[str] = []
    bins: list[str] = []
    table = _empty_bin_table(levels)
    for level in levels:
        for item in _by_level(evidence, level):
            labels.append(level)
            bucket = _emitted_bin(item.emitted_tokens)
            bins.append(bucket)
            table[level][bucket] += 1
    observed = _chi_square(table)
    seed_bytes = hashlib.sha256((suite_seed + "envelope_gate").encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(seed_bytes, "big"))
    ge = 0
    shuffled_labels = list(labels)
    for _ in range(E3_PERMUTATIONS):
        rng.shuffle(shuffled_labels)
        permuted = _empty_bin_table(levels)
        for level, bucket in zip(shuffled_labels, bins, strict=True):
            permuted[level][bucket] += 1
        if _chi_square(permuted) >= observed - 1e-12:
            ge += 1
    p_value = (ge + 1) / (E3_PERMUTATIONS + 1)
    return {
        "pass": p_value >= E3_MIN_PERMUTATION_P,
        "metric": "chi-square level x emitted-token-count bins {1,2,3,4,5+}",
        "bins": ["1", "2", "3", "4", "5+"],
        "contingency": table,
        "chi_square": observed,
        "permutation_p": p_value,
        "permutations": E3_PERMUTATIONS,
        "rng_seed_sha256": hashlib.sha256((suite_seed + "envelope_gate").encode("utf-8")).hexdigest(),
        "thresholds": {"permutation_p_gte": E3_MIN_PERMUTATION_P},
    }


def _empty_bin_table(levels: list[str]) -> dict[str, dict[str, int]]:
    return {level: {"1": 0, "2": 0, "3": 0, "4": 0, "5+": 0} for level in levels}


def _emitted_bin(value: int) -> str:
    if value <= 1:
        return "1"
    if value == 2:
        return "2"
    if value == 3:
        return "3"
    if value == 4:
        return "4"
    return "5+"


def _chi_square(table: dict[str, dict[str, int]]) -> float:
    levels = list(table)
    bins = ["1", "2", "3", "4", "5+"]
    row_totals = {level: sum(table[level].values()) for level in levels}
    col_totals = {bucket: sum(table[level][bucket] for level in levels) for bucket in bins}
    total = sum(row_totals.values())
    if total == 0:
        return 0.0
    statistic = 0.0
    for level in levels:
        for bucket in bins:
            expected = row_totals[level] * col_totals[bucket] / total
            if expected > 0:
                observed = table[level][bucket]
                statistic += (observed - expected) ** 2 / expected
    return statistic


def _gate_e4(evidence: dict[str, _ItemEvidence], levels: list[str]) -> dict[str, Any]:
    all_prompt_tokens = [item.prompt_tokens for item in evidence.values()]
    means = {
        level: _mean([item.prompt_tokens for item in _by_level(evidence, level)])
        for level in levels
    }
    global_range = max(all_prompt_tokens) - min(all_prompt_tokens) if all_prompt_tokens else 0
    mean_spread = max(means.values()) - min(means.values()) if means else 0.0
    return {
        "pass": (
            global_range <= E4_MAX_GLOBAL_PROMPT_TOKEN_RANGE
            and mean_spread <= E4_MAX_LEVEL_MEAN_SPREAD_TOKENS
        ),
        "metric": "realized prompt_tokens invariance",
        "global_range_tokens": global_range,
        "level_means": means,
        "level_mean_spread_tokens": mean_spread,
        "thresholds": {
            "global_range_lte": E4_MAX_GLOBAL_PROMPT_TOKEN_RANGE,
            "level_mean_spread_lte": E4_MAX_LEVEL_MEAN_SPREAD_TOKENS,
        },
    }


def _advisory_e5(evidence: dict[str, _ItemEvidence], levels: list[str]) -> dict[str, Any]:
    per_level: dict[str, Any] = {}
    evaluable_levels: dict[str, float] = {}
    for level in levels:
        parsed_correct: list[_ItemEvidence] = []
        parsed_incorrect: list[_ItemEvidence] = []
        for item in _by_level(evidence, level):
            if item.parse_status != "parsed" or item.correct is None:
                continue
            if item.correct:
                parsed_correct.append(item)
            else:
                parsed_incorrect.append(item)
        correct_count = len(parsed_correct)
        incorrect_count = len(parsed_incorrect)
        record: dict[str, Any] = {
            "parsed_correct_distinct_items": correct_count,
            "parsed_incorrect_distinct_items": incorrect_count,
            "min_required_per_class": E5_MIN_DISTINCT_PARSED_PER_CLASS,
        }
        if (
            correct_count >= E5_MIN_DISTINCT_PARSED_PER_CLASS
            and incorrect_count >= E5_MIN_DISTINCT_PARSED_PER_CLASS
        ):
            delta = abs(
                _mean([item.emitted_tokens for item in parsed_incorrect])
                - _mean([item.emitted_tokens for item in parsed_correct])
            )
            record.update({"status": "evaluable", "abs_mean_delta_tokens": delta})
            evaluable_levels[level] = delta
        else:
            record["status"] = "expected_not_evaluable"
        per_level[level] = record
    return {
        "advisory": True,
        "gates_envelope": False,
        "status": "expected_not_evaluable" if not evaluable_levels else "evaluable",
        "metric": "early-EOS bias by correctness class",
        "thresholds": {
            "min_distinct_parsed_items_per_class": E5_MIN_DISTINCT_PARSED_PER_CLASS,
            "abs_mean_delta_tokens_lte_when_evaluable": E2_MAX_MEAN_SPREAD_TOKENS,
        },
        "per_level": per_level,
    }


def _mean(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def _evidence_dict(evidence: _ItemEvidence) -> dict[str, Any]:
    return {
        "item_id": evidence.item_id,
        "level_id": evidence.level_id,
        "prompt_tokens": evidence.prompt_tokens,
        "emitted_tokens": evidence.emitted_tokens,
        "stop_reason": evidence.stop_reason,
        "status": evidence.status,
        "parse_status": evidence.parse_status,
        "correct": evidence.correct,
    }


def _level_window_energy_records(readers: list[BundleReader]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for reader in readers:
        summary = reader.raw_summary()
        suite_metrics = summary.get("suite_metrics") if isinstance(summary, dict) else None
        levels = suite_metrics.get("levels") if isinstance(suite_metrics, dict) else None
        if not isinstance(levels, list):
            continue
        for level in levels:
            if not isinstance(level, dict):
                continue
            records.append(
                {
                    "bundle_path": str(reader.path),
                    "group_id": level.get("group_id"),
                    "energy_gross_j": level.get("energy_gross_j"),
                    "item_count": level.get("item_count"),
                    "status_counts": level.get("status_counts"),
                    "identifiability": level.get("identifiability"),
                }
            )
    return records


def _bundle_hashes(path: Path) -> dict[str, Any]:
    artifacts = [
        "config.json",
        "metadata.json",
        "events.jsonl",
        "power_trace.csv",
        "summary_metrics.json",
        "suite_manifest.json",
        "outputs/suite_items.jsonl",
    ]
    hashes: dict[str, str | None] = {}
    aggregate = hashlib.sha256()
    for name in artifacts:
        artifact_path = path / name
        if not artifact_path.is_file():
            hashes[name] = None
            continue
        data = artifact_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        hashes[name] = digest
        aggregate.update(name.encode("utf-8") + b"\0" + digest.encode("ascii") + b"\0")
    return {"path": str(path), "artifact_sha256": hashes, "bundle_evidence_sha256": aggregate.hexdigest()}
