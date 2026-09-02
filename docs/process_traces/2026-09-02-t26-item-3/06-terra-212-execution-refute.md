```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Review complete: M2 and added M9 survived; the requested T-0 reason-code census does not detect M8; tree is clean.",
  "workspace": {
    "base_requested": "6075389a",
    "base_mode": "descendant",
    "head_start": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "head_end": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "joulewise/arm_readiness_evidence_t0.py"
  ],
  "unowned_dirty": [],
  "mutations": [
    {"id":"M1","mutation":"600_000_000_000 -> 600_000_000_001","outcome":"KILLED","killed_by":["test_t0_liveness_bound_refuses_at_600s_plus_1ns","test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns","test_rehearsal_t0_liveness_bound_refuses_at_600s_plus_1ns"]},
    {"id":"M2","mutation":"600_000_000_000 -> 599_999_999_999","outcome":"SURVIVED","killed_by":[]},
    {"id":"M3","mutation":"remove lower 0 <= liveness half","outcome":"KILLED","killed_by":["test_t0_liveness_bound_refuses_negative","test_clock_probe_r1_duration_quorum_and_horizon_boundaries_gate","test_clock_probe_rejects_every_non_integer_and_ordered_endpoint_reversal"]},
    {"id":"M4","mutation":"remove upper liveness half, retaining pre-ruling lower bound","outcome":"KILLED","killed_by":["test_t0_liveness_bound_refuses_at_600s_plus_1ns","test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns","test_rehearsal_t0_liveness_bound_refuses_at_600s_plus_1ns"]},
    {"id":"M5","mutation":"use r1_batch_finished_monotonic_raw_ns in conjunct","outcome":"KILLED","killed_by":["test_t0_liveness_bound_refuses_at_600s_plus_1ns","47 failures total, including rehearsal and schema positive controls"]},
    {"id":"M6","mutation":"issuance valid_until = validity_origin + horizon + 1 s","outcome":"KILLED","killed_by":["test_issuance_passes_t0_when_r1_batch_is_600s_minus_1ns_old","test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent"]},
    {"id":"M7","mutation":"stamp validity_origin before the fifteen-row loop","outcome":"KILLED","killed_by":["test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns"]},
    {"id":"M8","mutation":"change predicate refusal to evidence_author_t0_predicate_refused_mutant","outcome":"KILLED","killed_by":["test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns"]},
    {"id":"M9","mutation":"added: change upper comparator <= to <","outcome":"SURVIVED","killed_by":[]}
  ],
  "verdict": {
    "findings": [
      {
        "id":"F1",
        "severity":"should_fix",
        "file:line":"joulewise/arm_readiness.py:6349",
        "counterfactual_input":"M2 cap = 599_999_999_999 ns",
        "observed_outcome":"All 166 mandated tests passed. The claimed −1 ns pass test does not bind the exact 600 s inclusive boundary."
      },
      {
        "id":"F2",
        "severity":"should_fix",
        "file:line":"joulewise/arm_readiness.py:6485",
        "counterfactual_input":"M9 replace <= _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS with <",
        "observed_outcome":"All 166 mandated tests passed. Exact 600 s is not tested at either arm or issuance site."
      },
      {
        "id":"F3",
        "severity":"should_fix",
        "file:line":"joulewise/arm_readiness_evidence.py:2337",
        "counterfactual_input":"M8 new T-0 author reason code string",
        "observed_outcome":"The direct issuance test killed M8, but tests.test_arm_readiness_integration passed 9/9 while mutated: its reason-code census scans readiness_* literals in arm_readiness.py and does not reject the changed T-0 author reason."
      }
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 224.694s","FAILED (failures=3, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=3, skipped=7\\)"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 166 tests in 217.607s","OK (skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 194.129s","FAILED (failures=3, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V4","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 196.724s","FAILED (failures=3, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V5","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 208.292s","FAILED (failures=47, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V6","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 207.620s","FAILED (failures=1, errors=1, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V7","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 208.612s","FAILED (failures=1, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V8","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 166 tests in 202.892s","FAILED (failures=1, skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V9","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 166 tests in 209.718s","OK (skipped=7)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V10","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_integration","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 9 tests in 2.783s","OK (skipped=5)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V11","kind":"test","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_passes_t0_when_r1_batch_is_600s_minus_1ns_old","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 5.022s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V12","kind":"suite","cmd":"python3 -m unittest tests.test_arm_readiness_evidence_author tests.test_capture_t0_step tests.test_arm_readiness_integration","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 64 tests in 128.262s","OK (skipped=5)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=5\\)"}},
    {"id":"V13","kind":"suite","cmd":"python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 166 tests in 210.574s","OK (skipped=7)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=7\\)"}},
    {"id":"V14","kind":"inspection","cmd":"git status --short --branch && git diff --exit-code -- joulewise/arm_readiness.py joulewise/arm_readiness_evidence_t0.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","no dirty paths"]},"expected":{"exit_code":0,"tail_regex":"HEAD \\(no branch\\)"}}
  ],
  "flags": [
    {"id":"F4","kind":"environment","level":"nonblocking","text":"The ordinary checkout attempted to create the common-worktree index.lock outside the sandbox. Each mutation was restored with git checkout -- <allowed path> using a disposable GIT_INDEX_FILE under the pre-set TMPDIR; final tracked-file diffs and hashes are clean.","needs":""},
    {"id":"F5","kind":"residual_risk","level":"nonblocking","text":"Same-signature statement: none applicable (first round).","needs":""}
  ]
}
```

## Findings

- F1–F2: the exact inclusive 600 s upper boundary is not covered. Both a reduced constant and an exclusive comparator survive.
- F3: the generic reason-code census does not cover T‑0 author refusal literals; M8 is caught only by its dedicated behavioral assertion.

## Residual risk

The normal author-entry fake-clock tests exercise the real public authoring function and pass at +1 ns refusal / −1 ns acceptance. `_MIN_IDLE_NS` is 600e9 and value-equal to the liveness constant, but no test binds that equality.