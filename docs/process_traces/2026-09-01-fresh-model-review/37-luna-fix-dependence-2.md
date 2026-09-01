```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Round-2 dependence-sensitivity rulings implemented within the three-file scope.",
  "workspace": {
    "base_requested": "907f5877",
    "base_mode": "exact",
    "head_start": "907f5877",
    "head_end": "907f5877",
    "upstream_end": "907f5877",
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [
    "docs/paper/round7/dependence-sensitivity.md",
    "scripts/dependence_sensitivity.py",
    "tests/test_dependence_sensitivity.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_dependence_sensitivity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 11 tests in 3.033s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --example",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "  },",
          "  \"comparison\": {",
          "    \"direction_gate_outcomes_agree\": true",
          "  }",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"direction_gate_outcomes_agree\": true"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --block-deltas \"$(grep '^| Ordered block deltas' docs/paper/round7/dependence-sensitivity.md | cut -d'|' -f3 | tr -d ' \\t' | tr -d '\\140')\" --floor 3.5 --se-metrology 0.2 --deterministic-bound-total 3.5",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "        \"passes\": false",
          "      }",
          "    }",
          "  },",
          "  \"comparison\": {",
          "    \"direction_gate_outcomes_agree\": false",
          "  }",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"direction_gate_outcomes_agree\": false"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "An additional piped canonical-suite invocation exceeded 150 seconds and was interrupted with exit 130; an earlier exact canonical invocation completed with exit 0.",
      "needs": ""
    }
  ]
}
```

## Change

| Ruling | Cure | File:line | Test |
|---|---|---|---|
| R1, R8 | One-decimal example list and recomputed arithmetic | `scripts/dependence_sensitivity.py:42-55`; `docs/paper/round7/dependence-sensitivity.md:69-99` | Golden document/script test |
| R2 | Reason-keyed refusal table and AST completeness test | `tests/test_dependence_sensitivity.py:89-219,552-568` | Focused suite |
| R2 | Removed duplicate list guard; removed V positivity guard; added positive-SE refusal | `scripts/dependence_sensitivity.py:140,204-207,363-368` | Refusal rows |
| R3 | Catch `OverflowError` at both CLI boundaries | `scripts/dependence_sensitivity.py:438,450` | Overflow row |
| R4–R6 | Non-verdict fencing and seven-column DERIVE proposal rows | `docs/paper/round7/dependence-sensitivity.md:13,55,109-114` | Document assertions |
| R7 | Disagreement-path CLI example and false comparison outcome | `docs/paper/round7/dependence-sensitivity.md:95-99` | Golden test |
| R8 | Corrected standard-deviation wording, generator field citations, and floor gloss | `docs/paper/round7/dependence-sensitivity.md:9,11,47` | Document assertions |

## Refusal table

CLI rows assert exit 2, empty stdout, and matching stderr. Call rows assert `ValueError` with the listed regex. `BASE` is `--floor 1.0 --se-metrology 0.2 --deterministic-bound-total 0.1`.

| Name | argv-or-call | Expected reason regex |
|---|---|---|
| finite_boolean | CLI `[true,2,3,4,5,6,7,8,9,10]` + BASE | `must be a finite number` |
| finite_string | `_finite_number("1", "value")` | `must be a finite number` |
| dict_deltas | CLI `{"a":1}` + BASE | `must be a JSON list` |
| string_deltas | `analyze_deltas("0123456789")` | `must be a JSON list` |
| four_blocks | CLI `[1,2,3,4]` + BASE | `exactly ten complete block deltas are required` |
| eleven_blocks | CLI eleven values + BASE | `exactly ten complete block deltas are required` |
| invalid_json | CLI `[1,]` + BASE | `is not valid JSON` |
| missing_deltas_file | `--block-deltas-file tests/not-a-real-dependence-sensitivity-input.json` + BASE | `cannot read block-delta JSON` |
| nonfinite_delta | CLI `[1,2,3,4,5,6,7,8,9,NaN]` + BASE | `block_deltas_j\[9\] must be a finite number` |
| constant_sequence | CLI ten `1` values + BASE | `rho is undefined` |
| perfect_alternation | CLI `[1,-1,1,-1,1,-1,1,-1,1,-1]` + BASE | `abs\(rho\) < 1` |
| ar1_one_block | `ar1_variance_inflation_factor(1, 0.0)` | `at least two blocks` |
| ar1_nonfinite_rho | `ar1_variance_inflation_factor(10, math.nan)` | `must be a finite number` |
| ar1_out_of_range | `ar1_variance_inflation_factor(10, 1.0)` | `abs\(rho\) < 1` |
| estimated_rho_constant | `estimate_ar1_rho([1.0] * 10, 1.0)` | `rho is undefined` |
| estimated_rho_out_of_range | `estimate_ar1_rho([1.0, -1.0] * 5, 0.0)` | `abs\(rho\) < 1` |
| five_blocks | CLI five values + BASE | `exactly ten complete block deltas are required` |
| negative_floor | CLI ten values, `--floor -0.1` | `must be non-negative` |
| nonfinite_metrology_se | CLI ten values, `--se-metrology nan` | `se_metrology_j must be a finite number` |
| negative_metrology_se | CLI ten values, `--se-metrology -0.1` | `must be non-negative` |
| negative_deterministic_total | CLI ten values, `--deterministic-bound-total -0.1` | `must be non-negative` |
| infinite_interval | CLI ten values, `--se-metrology 1e308` | `interval is not finite` |
| infinite_decision_interval | CLI ten values, `--se-metrology 5e307 --deterministic-bound-total 1.7e308` | `decision interval is not finite` |
| effective_n_not_finite | `_degrees_of_freedom(10, math.inf)` | `not positive and finite` |
| too_few_effective_blocks | `_degrees_of_freedom(10, 1.9)` | `fewer than two usable blocks` |
| sample_stddev_not_finite | mocked nonfinite sample standard deviation | `sample standard deviation is not finite` |
| zero_total_standard_error | `_model_result(sample_stddev_j=0.0, se_metrology_j=0.0)` | `total standard error must be positive` |
| example_with_floor | `--example --floor 3.5` | `cannot be combined` |
| caller_alpha | `--example --alpha 0.10` | `unrecognized arguments: --alpha` |
| missing_source | metrology args without a source | `is required unless --example` |
| missing_metrology | source and floor without metrology args | `are required unless --example` |
| overflow | CLI `[1e308]*10` + BASE | `overflow` |

## Verification commands and tails

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_dependence_sensitivity`

  ```
  Ran 11 tests in 3.033s

  OK
  ```

- `python3 scripts/dependence_sensitivity.py --example` exited 0; its final output tail was:

  ```json
  {
    "comparison": {
      "direction_gate_outcomes_agree": true
    }
  }
  ```

- Disagreement-path command exited 0; its final output tail was:

  ```json
  {
    "comparison": {
      "direction_gate_outcomes_agree": false
    }
  }
  ```

- `git diff --check` exited 0 with no output.

## Full `--example` output

```json
{
  "schema_version": "joulewise.dependence_sensitivity.v1",
  "artifact_type": "registered_dependence_sensitivity",
  "input_authentication": {
    "canonical_json": "UTF-8 JSON with ensure_ascii=false and separators=(',', ':')",
    "block_deltas_json_sha256": "d491f10155812486e53031a9a812b3c799c73487eefaadab6a428527648c3c7a",
    "metrology_inputs": {
      "se_metrology_j": 0.2,
      "deterministic_bound_total_j": 4.0
    },
    "metrology_inputs_json_sha256": "580d1cdac250fb7616f9cbf404a0234b39b5abf37af7715c2f8fcfa9c5756732"
  },
  "input": {
    "block_deltas_j": [
      5.0,
      7.6,
      5.5,
      4.2,
      4.7,
      6.8,
      5.5,
      3.6,
      3.9,
      3.2
    ],
    "registered_floor_j": 3.5,
    "registered_alpha": 0.05,
    "se_metrology_j": 0.2,
    "deterministic_bound_total_j": 4.0
  },
  "summary": {
    "n_blocks": 10,
    "sum_j": 50.0,
    "mean_j": 5.0,
    "squared_deviations_sum_j2": 17.639999999999997,
    "sample_stddev_j": 1.4
  },
  "ar1_rho_estimator": {
    "method": "centred_conditional_least_squares_lag1_v1",
    "formula": "sum((d_i-mean)*(d_i_minus_1-mean), i=2..n) / sum((d_i_minus_1-mean)^2, i=2..n)",
    "numerator": 4.32,
    "denominator": 14.399999999999997,
    "rho_hat": 0.3000000000000001
  },
  "ar1_variance_terms": [
    {
      "lag": 1,
      "term": 0.2700000000000001
    },
    {
      "lag": 2,
      "term": 0.07200000000000005
    },
    {
      "lag": 3,
      "term": 0.018900000000000017
    },
    {
      "lag": 4,
      "term": 0.004860000000000006
    },
    {
      "lag": 5,
      "term": 0.001215000000000002
    },
    {
      "lag": 6,
      "term": 0.0002916000000000006
    },
    {
      "lag": 7,
      "term": 6.561000000000017e-05
    },
    {
      "lag": 8,
      "term": 1.3122000000000033e-05
    },
    {
      "lag": 9,
      "term": 1.9683000000000054e-06
    }
  ],
  "models": {
    "independent_blocks": {
      "model": "independent_blocks",
      "description": "registered composition with n_eff = n",
      "effective_n": 10.0,
      "degrees_of_freedom": 9,
      "variance_inflation_factor": 1.0,
      "se_repeat_j": 0.44271887242357305,
      "repeat_only_interval_j": {
        "lower": 3.998569910577878,
        "upper": 6.001430089422122
      },
      "se_metrology_j": 0.2,
      "se_total_j": 0.48579831205964474,
      "t_critical_95": 2.262,
      "half_width_j": 1.0988757818789163,
      "metrology_aware_interval_j": {
        "lower": 3.9011242181210837,
        "upper": 6.098875781878917
      },
      "deterministic_bound_total_j": 4.0,
      "decision_interval_j": {
        "lower": -0.09887578187891632,
        "upper": 10.098875781878917
      },
      "t_statistic": 10.292337119907728,
      "raw_two_sided_p": 2.8137596845291562e-06,
      "floor_gate": {
        "rule": "abs(mean_j) > registered_floor_j",
        "registered_floor_j": 3.5,
        "passes": true
      },
      "direction_gate": {
        "rule": "both endpoints of both fully composed intervals have the same strict sign",
        "metrology_aware_direction": "positive",
        "decision_direction": null,
        "passes": false
      }
    },
    "ar1_estimated_rho": {
      "model": "ar1_estimated_rho",
      "description": "finite-n AR(1) repeat-variance sensitivity",
      "effective_n": 5.764703479529582,
      "degrees_of_freedom": 4,
      "variance_inflation_factor": 1.7346946006000001,
      "se_repeat_j": 0.5830953110063568,
      "repeat_only_interval_j": {
        "lower": 3.3813274166463536,
        "upper": 6.618672583353646
      },
      "se_metrology_j": 0.2,
      "se_total_j": 0.6164415152450393,
      "t_critical_95": 2.776,
      "half_width_j": 1.7112416463202291,
      "metrology_aware_interval_j": {
        "lower": 3.288758353679771,
        "upper": 6.711241646320229
      },
      "deterministic_bound_total_j": 4.0,
      "decision_interval_j": {
        "lower": -0.7112416463202291,
        "upper": 10.71124164632023
      },
      "t_statistic": 8.111069544062861,
      "raw_two_sided_p": 0.0012562137624456703,
      "floor_gate": {
        "rule": "abs(mean_j) > registered_floor_j",
        "registered_floor_j": 3.5,
        "passes": true
      },
      "direction_gate": {
        "rule": "both endpoints of both fully composed intervals have the same strict sign",
        "metrology_aware_direction": "positive",
        "decision_direction": null,
        "passes": false
      }
    },
    "fixed_effective_n_halving": {
      "model": "fixed_effective_n_halving",
      "description": "fixed effective-n halving (a named pessimistic scenario, not a bound)",
      "effective_n": 5.0,
      "degrees_of_freedom": 4,
      "variance_inflation_factor": 2.0,
      "se_repeat_j": 0.626099033699941,
      "repeat_only_interval_j": {
        "lower": 3.2619490824489636,
        "upper": 6.738050917551036
      },
      "se_metrology_j": 0.2,
      "se_total_j": 0.6572670690061992,
      "t_critical_95": 2.776,
      "half_width_j": 1.824573383561209,
      "metrology_aware_interval_j": {
        "lower": 3.175426616438791,
        "upper": 6.824573383561209
      },
      "deterministic_bound_total_j": 4.0,
      "decision_interval_j": {
        "lower": -0.824573383561209,
        "upper": 10.824573383561209
      },
      "t_statistic": 7.607257743127308,
      "raw_two_sided_p": 0.001602484161944936,
      "floor_gate": {
        "rule": "abs(mean_j) > registered_floor_j",
        "registered_floor_j": 3.5,
        "passes": true
      },
      "direction_gate": {
        "rule": "both endpoints of both fully composed intervals have the same strict sign",
        "metrology_aware_direction": "positive",
        "decision_direction": null,
        "passes": false
      }
    }
  },
  "comparison": {
    "direction_gate_outcomes_agree": true
  }
}
```

## Git diff --stat

```text
 docs/paper/round7/dependence-sensitivity.md |  56 ++--
 scripts/dependence_sensitivity.py           |  45 ++-
 tests/test_dependence_sensitivity.py        | 452 +++++++++++++++++++---------
 3 files changed, 358 insertions(+), 195 deletions(-)
```

## Verification notes

The worktree remains uncommitted and limited to the requested three files. The later duplicate canonical-suite invocation was interrupted after hanging; no measurement or `[QUIET-MAC]` command was run.

