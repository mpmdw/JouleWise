import copy
import hashlib
import json
import unittest
from pathlib import Path

from joulewise.analysis_engine.artifact import (
    SCHEMA_VERSION_V2,
    calculate_claim_verdicts_id,
    claim_side_bound_from_terms,
    render_claim_verdicts,
    validate_claim_verdicts,
)
from joulewise.analysis_engine.claims import evaluate_claim
from joulewise.provenance import prompt_token_ids_sha256
from joulewise.results_fill_gamma import (
    DECODE_TOKEN_NAMES,
    OUTCOME_PLACEMENT_IDS,
    PREFILL_TOKEN_TEMPLATES,
    STOP_FILL,
    render_gamma_contract,
)
from tests.test_analysis_claims import minimal_artifact


ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixtures" / "results_fill_gamma" / "symbolic-2048-cases.json"
DECODE_ID = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b"
PREFILL_ID = "ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b"
HEX = "a" * 64
SELECTION_EXPRESSION = (
    "first r in ladder_prompt_tokens where small_model_member_count[r] >= "
    "min_small_model_members_per_rung and min(reducer_written_summary_metrics[r]"
    "[small_model_members].overlapping_power_interval_count) >= "
    "min_overlapping_power_interval_count; large-model probes recorded, "
    "non-gating; otherwise 4096"
)
EXHAUSTED_BRANCH = {
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


def _with_content_id(artifact):
    artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
    return artifact


def _base_gamma_artifact(parameters):
    artifact = minimal_artifact()
    artifact["schema_version"] = SCHEMA_VERSION_V2
    contrast = artifact["contrasts"][0]
    contrast["contrast_id"] = DECODE_ID
    contrast["metric"]["metric_tag"] = "phase_decode_energy"
    contrast["metric"]["name"] = "phase_energy_j.decode"
    contrast["estimator"]["name"] = "abba_block_arm_mean_difference_t_v1"
    contrast["deterministic_bounds"]["terms"][0]["name"] = (
        "E_clock_anchor_shift_bound_j"
    )
    self_bound = parameters["claim_side_bound_j"]
    contrast["deterministic_bounds"]["terms"][0]["bound"] = self_bound
    contrast["deterministic_bounds"]["total"] = self_bound
    contrast["deterministic_bounds"]["decision_interval"] = {
        "lower": parameters["estimate_j"] - self_bound,
        "upper": parameters["estimate_j"] + self_bound,
    }
    contrast["claim_side_bound"] = claim_side_bound_from_terms(
        contrast["deterministic_bounds"]["terms"]
    )

    first_resolution = contrast["floor"]["resolutions"][0]
    first_resolution.update(
        {
            "status": "exact",
            "source_cell_ids": ["cell-a"],
            "transport_group_id": None,
            "transport_rule_id": None,
        }
    )
    second_resolution = copy.deepcopy(first_resolution)
    second_resolution.update(
        {
            "source_cell_ids": ["cell-b"],
            "floor_abs_j": parameters["arm_floor_j"][1],
            "floor_cmp_j": parameters["arm_floor_j"][1],
            "floor_gate_j": parameters["arm_floor_j"][1],
        }
    )
    contrast["floor"].update(
        {
            "floor_row_ids": ["cell-a", "cell-b"],
            "floor_abs_j": max(
                first_resolution["floor_abs_j"], second_resolution["floor_abs_j"]
            ),
            "floor_cmp_j": max(
                first_resolution["floor_cmp_j"], second_resolution["floor_cmp_j"]
            ),
            "active_floor_j": max(parameters["arm_floor_j"]),
            "transport_verdict": "exact",
            "resolutions": [first_resolution, second_resolution],
            "claim_floor_rule": "cross_stack_armwise_max.v1",
            "aggregation": "max_never_sum",
            "arm_gates": [
                {
                    "arm_id": "A",
                    "condition_family_id": "cond-a",
                    "status": "exact",
                    "floor_gate_j": parameters["arm_floor_j"][0],
                },
                {
                    "arm_id": "B",
                    "condition_family_id": "cond-b",
                    "status": "exact",
                    "floor_gate_j": parameters["arm_floor_j"][1],
                },
            ],
        }
    )

    audit_by_slot = {
        (audit["block_id"], audit["condition_id"]): audit
        for audit in artifact["bundle_audit"]
    }
    second_positions = []
    for block_number in (1, 2):
        for side in ("a", "b"):
            row = copy.deepcopy(
                audit_by_slot[(f"block-{block_number}", f"cond-{side}")]
            )
            row["bundle_id"] += "-second"
            row["entry_id"] += "-second"
            row["relative_path"] += "-second"
            second_positions.append(row)
    artifact["bundle_audit"].extend(second_positions)
    for block_number, block in enumerate(
        contrast["bundle_blocks"]["blocks"], start=1
    ):
        block["bundle_a_id"] = None
        block["bundle_b_id"] = None
        block["position_bundle_ids"] = {
            "A1": f"a-{block_number}",
            "B1": f"b-{block_number}",
            "B2": f"b-{block_number}-second",
            "A2": f"a-{block_number}-second",
        }
    contrast["bundle_blocks"]["included_bundle_ids"] = sorted(
        audit["bundle_id"] for audit in artifact["bundle_audit"]
    )

    prefill = copy.deepcopy(contrast)
    prefill["contrast_id"] = PREFILL_ID
    prefill["metric"]["metric_tag"] = "phase_prefill_energy"
    prefill["metric"]["name"] = "phase_energy_j.prefill"
    artifact["contrasts"] = [contrast, prefill]
    family = artifact["families"][0]
    family.update(
        {
            "m": 2,
            "contrast_ids": [DECODE_ID, PREFILL_ID],
            "finite_test_count": 2,
            "raw_ordering": [DECODE_ID, PREFILL_ID],
            "adjusted_p_values": {DECODE_ID: 0.0, PREFILL_ID: 0.0},
        }
    )
    _set_overlap_count(artifact, parameters["overlap_count"])
    _with_content_id(artifact)
    assert validate_claim_verdicts(artifact) == []
    return artifact


def _set_overlap_count(artifact, count):
    eligible = count >= 3
    reasons = [] if eligible else ["insufficient_in_window_samples"]
    for audit in artifact["bundle_audit"]:
        audit["window_prechecks"]["phase_prefill_energy"] = {
            "status": "eligible" if eligible else "ineligible",
            "eligible": eligible,
            "reasons": reasons,
            "source_field": "window_evidence_precheck",
            "legacy_precheck_not_claim_evaluator": False,
            "evidence": {
                "eligible": eligible,
                "reasons": reasons,
                "window_count": 1,
                "windows": [{"in_window_sample_count": count}],
            },
        }


def _reevaluate(contrast):
    contrast["claim_evaluation"] = evaluate_claim(
        estimate=contrast["estimator"]["estimate"],
        metrology_aware_ci95=contrast["estimator"]["metrology_aware_CI95"],
        decision_interval=contrast["deterministic_bounds"]["decision_interval"],
        floor_gate_j=contrast["floor"]["active_floor_j"],
        adjusted_rejected=contrast["multiplicity"]["rejected"],
        base_reason_codes=[],
        equivalence=None,
        claim_role=contrast["claim_role"],
        confirmatory_status=contrast["sampling"]["confirmatory_status"],
        evidence_class="current",
        hypothesized_direction="positive",
    )


def _floor_failure(artifact, parameters):
    for contrast in artifact["contrasts"]:
        floor = contrast["floor"]
        floor["resolutions"][0].update(
            {
                "floor_abs_j": parameters["arm_floor_j"][0],
                "floor_cmp_j": parameters["arm_floor_j"][0],
                "floor_gate_j": parameters["arm_floor_j"][0],
            }
        )
        floor["resolutions"][1].update(
            {
                "floor_abs_j": parameters["arm_floor_j"][1],
                "floor_cmp_j": parameters["arm_floor_j"][1],
                "floor_gate_j": parameters["arm_floor_j"][1],
            }
        )
        floor.update(
            {
                "floor_abs_j": max(parameters["arm_floor_j"]),
                "floor_cmp_j": max(parameters["arm_floor_j"]),
                "active_floor_j": max(parameters["arm_floor_j"]),
            }
        )
        floor["arm_gates"][0]["floor_gate_j"] = parameters["arm_floor_j"][0]
        floor["arm_gates"][1]["floor_gate_j"] = parameters["arm_floor_j"][1]
        _reevaluate(contrast)
    return _with_content_id(artifact)


def _direction_failure(artifact, parameters):
    for contrast in artifact["contrasts"]:
        deterministic = contrast["deterministic_bounds"]
        bound = parameters["claim_side_bound_j"]
        estimate = contrast["estimator"]["estimate"]
        deterministic["terms"][0]["bound"] = bound
        deterministic["total"] = bound
        deterministic["decision_interval"] = {
            "lower": estimate - bound,
            "upper": estimate + bound,
        }
        contrast["claim_side_bound"]["value_j"] = bound
        _reevaluate(contrast)
    return _with_content_id(artifact)


def _remove_contrast(artifact, contrast_id):
    artifact["contrasts"] = [
        contrast
        for contrast in artifact["contrasts"]
        if contrast["contrast_id"] != contrast_id
    ]
    family = artifact["families"][0]
    remaining = [contrast["contrast_id"] for contrast in artifact["contrasts"]]
    family["m"] = len(remaining)
    family["contrast_ids"] = remaining
    family["finite_test_count"] = len(remaining)
    family["raw_ordering"] = remaining
    family["adjusted_p_values"] = {contrast_id: 0.0 for contrast_id in remaining}
    return _with_content_id(artifact)


def _source_bytes(artifact):
    selection = {
        "collection_prefill_tokens": 2048,
        "qualifying_prefill_tokens": [2048, 4096],
        "refusal": None,
        "rule": {
            "all_small_count_ge_5_required": True,
            "ladder_prefill_tokens": [512, 1024, 2048, 4096],
            "minimum_overlapping_power_interval_count": 5,
            "minimum_small_members_per_rung": 5,
            "reducer_min_phase_samples": 3,
            "selection": "shortest_qualifying_rung",
        },
        "schema_version": "joulewise.g2a_prefill_selection.v1",
        "selected_prefill_tokens": 2048,
        "status": "selected",
        "summary_sha256": HEX,
    }
    selection_raw = json.dumps(selection, sort_keys=True).encode("utf-8")
    selection_sha = hashlib.sha256(selection_raw).hexdigest()
    prompt_text = "synthetic fixture prompt"
    token_ids = [0] * 2048
    prompt_pin = {
        "schema_version": "joulewise.prefill_prompt_pin.v2",
        "selection_authority": {
            "g2a_record": {
                "record_id": f"sha256:{selection_sha}",
                "path": "fixture/g2a-selection.json",
            },
            "ruling_trace_paths": [
                "docs/process_traces/2026-08-30-prefill-margin-coldgate/"
                "03-MAGISTRATE-RATIFICATION.md",
                "docs/process_traces/2026-09-01-fresh-model-review/"
                "16b-RULING-g2a-producers.md",
            ],
        },
        "ladder_prompt_tokens": [512, 1024, 2048, 4096],
        "min_small_model_members_per_rung": 5,
        "min_overlapping_power_interval_count": 5,
        "min_phase_samples_pinned": 3,
        "sample_count_margin_floor": 2,
        "selection_expression": SELECTION_EXPRESSION,
        "g2a_record_sha256": selection_sha,
        "selection_record": {
            "path": "fixture/g2a-selection.json",
            "sha256": selection_sha,
        },
        "prompt_ladder": {"path": "fixture/prompt-ladder.json", "sha256": HEX},
        "panel_sha256": HEX,
        "exhausted_ladder_branch": EXHAUSTED_BRANCH,
        "prefill_length": 2048,
        "tokenizer_json_sha256": HEX,
        "special_token_policy": "add_special_tokens=true",
        "prompt_text": prompt_text,
        "prompt_text_utf8_sha256": hashlib.sha256(
            prompt_text.encode("utf-8")
        ).hexdigest(),
        "prompt_token_ids": token_ids,
        "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
        "prompt_tokens": 2048,
        "repeat_count": 1,
        "closing_sentence": "synthetic fixture close",
        "generation_method": "synthetic fixture only",
    }
    prompt_pin_raw = json.dumps(prompt_pin, sort_keys=True).encode("utf-8")
    return {
        "claim_verdicts_bytes": render_claim_verdicts(artifact),
        "expected_claim_verdicts_id": artifact["claim_verdicts_id"],
        "g2a_selection_bytes": selection_raw,
        "expected_g2a_selection_sha256": selection_sha,
        "prompt_pin_bytes": prompt_pin_raw,
        "expected_prompt_pin_sha256": hashlib.sha256(prompt_pin_raw).hexdigest(),
    }


def _render(artifact):
    return render_gamma_contract(**_source_bytes(artifact))


def _field_paths(value, predicate, path=()):
    paths = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if predicate(key):
                paths.append(child_path)
            paths.extend(_field_paths(child, predicate, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_field_paths(child, predicate, (*path, index)))
    return paths


def _mutate_path(value, path):
    parent = value
    for part in path[:-1]:
        parent = parent[part]
    key = path[-1]
    current = parent[key]
    if isinstance(current, bool):
        parent[key] = not current
    elif isinstance(current, int):
        parent[key] = current + 1
    elif isinstance(current, float):
        parent[key] = current + 1.0
    elif isinstance(current, str):
        parent[key] = "mutated"
    elif current is None:
        parent[key] = "mutated"
    elif isinstance(current, list):
        parent[key] = [*current, "mutated"]
    elif isinstance(current, dict):
        parent[key] = {**current, "mutated": True}
    else:
        raise AssertionError(f"no mutation for {path!r}")


class GammaResultContractTests(unittest.TestCase):
    def test_gamma_result_contract_table(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        expected = fixture["expected"]
        cases = fixture["synthetic_cases"]
        self.assertTrue(fixture["fixture_only"])
        self.assertFalse(fixture["measurement_values"])
        self.assertFalse(fixture["claim_bearing"])
        self.assertEqual(len(DECODE_TOKEN_NAMES), 14)
        self.assertEqual(len(PREFILL_TOKEN_TEMPLATES), 14)

        supported_artifact = _base_gamma_artifact(cases["supported"])
        supported = _render(supported_artifact)
        self.assertNotEqual(supported, STOP_FILL)
        self.assertEqual(supported["prefill_length"], 2048)
        self.assertEqual(len(supported["tokens"]), 28)
        self.assertEqual(supported["rows"]["DS-30"], expected["floor_pass"])
        self.assertEqual(supported["rows"]["DS-31"], expected["direction_pass"])
        self.assertEqual(supported["rows"]["DS-32"], expected["decode_supported"])
        self.assertEqual(supported["rows"]["PG-06"], expected["floor_pass"])
        self.assertEqual(supported["rows"]["PG-07"], expected["direction_pass"])
        self.assertEqual(supported["rows"]["PG-08"], expected["prefill_supported"])
        self.assertEqual(supported["rows"]["DS-28"], "F+B = 1.25 J; signed clearance = 0.75 J")
        self.assertEqual(supported["rows"]["PG-04"], "F+B = 1.25 J; signed clearance = 0.75 J")
        self.assertEqual(supported["rows"]["DS-29"], "0.25")
        self.assertEqual(supported["rows"]["PG-05"], "0.25")
        for row in ("DS-32", "PG-08"):
            self.assertEqual(tuple(supported["placements"][row]), OUTCOME_PLACEMENT_IDS)
            self.assertEqual(
                set(supported["placements"][row].values()),
                {supported["rows"][row]},
            )
        serialized = json.dumps(supported, ensure_ascii=False)
        for pseudotoken in ("[PENDING]", "[FILL:", "[VALUE]", "[PREFILL_LENGTH]"):
            self.assertNotIn(pseudotoken, serialized)

        floor_failed = _render(
            _floor_failure(copy.deepcopy(supported_artifact), cases["floor_failure"])
        )
        self.assertEqual(floor_failed["rows"]["DS-30"], expected["floor_fail"])
        self.assertEqual(floor_failed["rows"]["PG-06"], expected["floor_fail"])
        self.assertIn("not supported — not resolvable", floor_failed["rows"]["DS-32"])

        direction_failed = _render(
            _direction_failure(
                copy.deepcopy(supported_artifact), cases["direction_failure"]
            )
        )
        self.assertEqual(direction_failed["rows"]["DS-31"], expected["direction_fail"])
        self.assertEqual(direction_failed["rows"]["PG-07"], expected["direction_fail"])

        decode_absent = _render(
            _remove_contrast(copy.deepcopy(supported_artifact), DECODE_ID)
        )
        self.assertEqual(decode_absent["rows"]["DS-32"], expected["decode_absent"])
        prefill_absent = _render(
            _remove_contrast(copy.deepcopy(supported_artifact), PREFILL_ID)
        )
        self.assertEqual(prefill_absent["rows"]["PG-08"], expected["prefill_absent"])

        count_four_artifact = copy.deepcopy(supported_artifact)
        _set_overlap_count(
            count_four_artifact,
            cases["pre_registration_refusal"]["overlap_count"],
        )
        self.assertEqual(
            _render(_with_content_id(count_four_artifact))["rows"]["PG-08"],
            expected["count_four"],
        )
        count_two_artifact = copy.deepcopy(supported_artifact)
        _set_overlap_count(
            count_two_artifact, cases["reducer_refusal"]["overlap_count"]
        )
        self.assertEqual(
            _render(_with_content_id(count_two_artifact))["rows"]["PG-08"],
            expected["count_two"],
        )

        equivalent = copy.deepcopy(supported_artifact)
        equivalent["contrasts"][0]["claim_evaluation"]["outcome"] = "equivalent"
        _with_content_id(equivalent)
        self.assertEqual(_render(equivalent), STOP_FILL)
        wrong_id = copy.deepcopy(supported_artifact)
        wrong_id["contrasts"][0]["contrast_id"] = "wrong"
        _with_content_id(wrong_id)
        self.assertEqual(_render(wrong_id), STOP_FILL)

        for mutation in fixture["pinned_source_mutations"]:
            with self.subTest(mutation=mutation["label"]):
                sources = _source_bytes(supported_artifact)
                raw_key = mutation["raw_key"]
                mutated = bytearray(sources[raw_key])
                mutated[mutation["byte_index"]] ^= 1
                sources[raw_key] = bytes(mutated)
                self.assertEqual(render_gamma_contract(**sources), STOP_FILL)

        classes = fixture["mutation_field_classes"]
        predicates = {
            "digest": lambda key: key in classes["digest_exact"]
            or classes["digest_substring"] in key,
            "census": lambda key: key in classes["census_exact"],
            "outcome": lambda key: key in classes["outcome_exact"],
        }
        raw_sources = {
            "claim_verdicts_bytes": json.loads(
                _source_bytes(supported_artifact)["claim_verdicts_bytes"]
            ),
            "g2a_selection_bytes": json.loads(
                _source_bytes(supported_artifact)["g2a_selection_bytes"]
            ),
            "prompt_pin_bytes": json.loads(
                _source_bytes(supported_artifact)["prompt_pin_bytes"]
            ),
        }
        observed = {label: 0 for label in predicates}
        for raw_key, structured in raw_sources.items():
            for label, predicate in predicates.items():
                for path in _field_paths(structured, predicate):
                    with self.subTest(source=raw_key, field_class=label, path=path):
                        attacked = copy.deepcopy(structured)
                        _mutate_path(attacked, path)
                        sources = _source_bytes(supported_artifact)
                        sources[raw_key] = json.dumps(
                            attacked, sort_keys=True
                        ).encode("utf-8")
                        self.assertEqual(render_gamma_contract(**sources), STOP_FILL)
                        observed[label] += 1
        self.assertEqual(observed, {"digest": 46, "census": 41, "outcome": 53})


if __name__ == "__main__":
    unittest.main()
