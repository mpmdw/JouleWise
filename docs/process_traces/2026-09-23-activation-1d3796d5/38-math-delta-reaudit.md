```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 1 leaves a percent-reference scoring blocker and a reference-validation coupling; two of five mutants survive.",
  "workspace": {
    "base_requested": "47ea644d",
    "base_mode": "exact",
    "head_start": "ed1c820567a773a81ab84dbe2256a317b3013741",
    "head_end": "ed1c820567a773a81ab84dbe2256a317b3013741",
    "upstream_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 1, "should_fix": 2, "nit": 0},
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Eligible percent references score incorrect against their own text", "path": "joulewise/benchmark_import_math.py", "line": 306},
      {"id": "F2", "severity": "should_fix", "title": "Annotation validation still depends on the mutable response parser", "path": "joulewise/benchmark_import_math.py", "line": 550},
      {"id": "F3", "severity": "should_fix", "title": "Named tests miss a dangerous scorer denial regression", "path": "tests/test_benchmark_import_math.py", "line": 182}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 62 tests in 1.239s", "OK (skipped=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 62 tests.*OK \\(skipped=2\\)"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONPATH=. python3 -B /tmp/jw_math_delta_audit.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["parser_agreement 4040 / 4040", "self_score_against_production_expected 4025 / 4040", "matches_fixture True matches_production True"]},
      "expected": {"exit_code": 0, "tail_regex": "matches_fixture True matches_production True"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONPATH=. python3 -B /tmp/jw_math_annotation_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["baseline_annotation_count 320", "population_under_scorer_only_percent_change 4040", "annotation_validation ValueError MATH annotation 14 answer mismatch"]},
      "expected": {"exit_code": 0, "tail_regex": "annotation_validation ValueError MATH annotation 14 answer mismatch"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "python3 -B /tmp/jw_math_delta_mutants.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["M2_rejoin_eligibility_to_scorer exit 0", "M4_remove_case_insensitive_magnitude_denial exit 0", "M5_restore_unbalanced_pilot exit 1"]},
      "expected": {"exit_code": 0, "tail_regex": "M4_remove_case_insensitive_magnitude_denial exit 0"}
    }
  ],
  "flags": [
    {"id": "R1", "kind": "verification_gap", "level": "nonblocking", "text": "Real tokenizer rendering and the MLX decode path were outside this read-only, no-model seat.", "needs": "Separate model-runtime lane"}
  ]
}
```

## Findings

**F1 — blocker.** The response denial compares percent marks against the normalized `expected_answer`, which has already lost the reference’s `\%` ([scorer](/Users/edr/code/wt-1d3796d5-ref-math/joulewise/benchmark_import_math.py:303)). Across all **4,040** eligible rows, boxing each row’s own source answer and scoring it against its production expected answer yielded **15 incorrect** outcomes. Three of those rows occur in both n=64 and n=128. For example, `test/prealgebra/768.json` has source answer `20\%` and expected answer `20`; `\boxed{20\%}` scores incorrect. The same response scores correct when the scorer receives the original reference text. Synthetic references `5\text{ million}` and `5\mathrm{i}` also pass the frozen reference parser but fail this self-score. The denial needs the reference-side notation, or eligibility must exclude forms it cannot score consistently.

**F2 — should_fix.** Eligibility uses the frozen parser, but [annotation validation](/Users/edr/code/wt-1d3796d5-ref-math/joulewise/benchmark_import_math.py:550) reparses `source_answer` with the mutable response parser. I built and validated a 320-item n=64 manifest and sidecar, then made a scorer-only change interpreting `20\%` as `1/5`. Eligibility stayed **4,040**, while validation refused the unchanged sidecar with `MATH annotation 14 answer mismatch`. A mutant reconnecting both eligibility checks to the response parser survived all 62 named tests. With a scorer-only change on a selected answer, that mutant changed the population from 4,040 to 4,030 and changed the pilot and n=128 hashes. Validate source answers with `canonical_reference_v1` and test the separation using a reference present in the fixture.

**F3 — should_fix.** Removing case insensitive matching from the new magnitude-word denial survived all 62 named tests. Executed counterexample: the candidate scores `\boxed{5\text{Million}}` against `5` incorrect; the mutant scores it correct. The golden pairs cover lowercase words only ([tests](/Users/edr/code/wt-1d3796d5-ref-math/tests/test_benchmark_import_math.py:182)).

### Contract answers

| Clause | Result at production call site |
|---|---|
| Y1 | **Closed.** License and both pointer paths are required; receipt values come from read bytes. Missing and corrupted-file tests refuse with receipt names. The constant-license mutant was killed. |
| Y2 | **Partial; F2.** Eligibility itself is frozen. My mixed-number scorer-only change left **4,040** rows, population statistics, and all three hashes unchanged. Reference and response parsers agree on **4,040/4,040** eligible source answers. Annotation validation remains coupled. |
| Y3 | **Closed.** Builder and validator require the complete arm-specific prompt; the appended-turn test and my relaxed-builder mutant fail. |
| Y4 | **Closed for the specified cases.** Named tests exercise exact large integers, `\fbox{7}` as a box, fraction reduction, answer/last-box mismatch, and the listed normalization and box-order pairs. |
| Y5 | **Open; F1 and F3.** The denial introduces 15 real reference self-score failures; the uppercase-word mutant survives. The documented `5,120` grouping case remains correct. |
| Y6 | **Closed.** Quarantine text assigns malformed to D-047.6 and capped to M2/AP-5M PENDING. |
| Y7 | **Closed.** The real pilot is subject interleaved, has 80 items, is disjoint from both test sets, and n=64 is a per-level prefix of n=128. The old pilot ordering mutant was killed. |
| Y8 | **Closed for `\boxed 5`.** The last brace-less box wins in the named test. |
| Y9 | **Closed.** Omitted `lfs_pointer_blob_sha1` refuses; the present field round-trips. The named suite’s GSM8K serialization checks pass. |
| Y10 | **Closed.** The eligibility note gives 2 duplicate rows, 954 non-rational references, 5 plain-comma references, and retention for all five levels. |

My raw-row recomputation found **5,001 rows**, **4,040 eligible**, and independently reproduced the fixture’s canonical ID-list SHA-256 hashes:

| Set | SHA-256 |
|---|---|
| Pilot | `04c04ffec881aed3d970da059945587f1d2abecaf05b7361e05c1babf1b12d53` |
| n=64 | `bf94123715a95328fc89bdf6fdbe5388ea803214283d764fd8113aede618b0d2` |
| n=128 | `7ebb2d9defaf4d973bd975e7d7e0dcd6862c0fcdf47fec5bb3ac42127ccede92` |

**Same-signature statement:** unauthenticated receipt **no**; scorer/eligibility coupling **yes** (F2); prompt-shape laxity **no**; surviving scorer mutant **yes** (F3). Of five temporary mutants, receipt authentication, prompt shape, and pilot ordering were killed; parser recoupling and case-sensitive magnitude detection survived. The repository stayed clean at `ed1c8205`.

## Residual risk

The excluded model-runtime lane remains unverified: this seat did not test real tokenizer rendering or whether MLX decoding preserves `</think>`.