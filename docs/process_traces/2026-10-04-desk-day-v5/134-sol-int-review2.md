```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"REVIEW: FAIL; five major defects reproduced; requested venv suite: 76 failed, 462 passed, 9 skipped, 335 subtests passed.",
  "workspace":{"base_requested":"6796b8e033b8515e12b8c1e6a8da3b94014f7266","base_mode":"exact","head_start":"6796b8e033b8515e12b8c1e6a8da3b94014f7266","head_end":"6796b8e033b8515e12b8c1e6a8da3b94014f7266","upstream_end":"e7d13a1706d6352e0b3d9624dcf4c897671393da","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"result":"REVIEW: FAIL","delta_from":"898c49a7","findings":[
    {"id":"D1","severity":"should_fix","file":"joulewise/prewindow.py","line":57,"title":"T-0 dwell ignores busy processes outside the named-daemon list","evidence":"V2"},
    {"id":"D2","severity":"should_fix","file":"joulewise/v5_qualification.py","line":170,"title":"Admission abort masks an earlier unbounded successful member","evidence":"V2"},
    {"id":"D3","severity":"should_fix","file":"joulewise/v5_qualification.py","line":435,"title":"R3-corrected NULL cannot authorize fresh s1","evidence":"V3"},
    {"id":"D4","severity":"should_fix","file":"scripts/harvest_v5_g2b_window.py","line":506,"title":"Observation-producer fault converts re-armable abort to END STATE","evidence":"V2"},
    {"id":"D5","severity":"should_fix","file":"joulewise/v5_qualification.py","line":308,"title":"Two identical NULL outcomes still permit third s1 authorization","evidence":"V4"}
  ]},
  "verification":[
    {"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_v5_*.py tests/test_harvest_v5_*.py tests/test_t0_rehearsal.py tests/test_t0_anchor_positive_control.py tests/test_capture_t0_anchor_positive_control*.py tests/test_kernel_clock.py tests/test_arm_readiness_evidence_t0.py tests/test_capture_t0_step.py tests/test_prewindow_check.py tests/test_revision6_seal.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED tests/test_arm_readiness_evidence_t0.py::ArmReadinessEvidenceT0Tests::test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent"]},"expected":{"exit_code":0,"tail_regex":"(?m)^\\d+ passed.*$"}},
    {"id":"V2","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev2/repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["UNLISTED_99_PERCENT_PROCESS_T0_READY=True","T0_DWELL_WITH_BUSY_UNLISTED_PROCESS_EXIT=0","EARLIER_SUCCESSFUL_MEMBER_CLOCK=unbounded","ADMISSION_SCAN_OTHER_CAUSES=[]","HARVEST_WITH_PRODUCER_FAULT={'verdict': 'RECOVER', 'cause_codes': ['guard_attested_idle_admission_abort', 'qualification_observation_producer_fault'], 'end_state': True, 'next_step': 'design_consult_cold_gate'}"]},"expected":{"exit_code":0,"tail_regex":"HARVEST_WITH_PRODUCER_FAULT=.*"}},
    {"id":"V3","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev2/replay_native.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REAL_STRUCTURAL_HARVEST_INITIAL=REFUSED","REAL_IDENTICAL_BYTE_REHARVEST=NULL","FRESH_S1_USING_CANONICAL=REFUSED:fresh_s1_predecessor_not_rearmable","FRESH_S1_USING_CORRECTED-REHARVEST=REFUSED:previous_attempt_outside_block_archive","NEW_AUTHORIZATION_PUBLISHED=False"]},"expected":{"exit_code":0,"tail_regex":"NEW_AUTHORIZATION_PUBLISHED=False"}},
    {"id":"V4","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev2/repeated_null.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["TWO_CONSECUTIVE_NULL_CODES=[['chain_never_started'], ['chain_never_started']]","THIRD_S1_WRITER=STAGED","THIRD_CREATE_ONCE_AUTHORIZATION=True"]},"expected":{"exit_code":0,"tail_regex":"THIRD_CREATE_ONCE_AUTHORIZATION=True"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev2/mutations.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["dispatch-list-digest=SURVIVED","MUTANTS=14 KILLED=13 SURVIVED=1"]},"expected":{"exit_code":0,"tail_regex":"MUTANTS=14 KILLED=14 SURVIVED=0"}},
    {"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev2/stage_digest_probe.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["CHANGED_SINGLE_STAGE_BASELINE=REFUSED","ADDITIONAL_DISPATCH_DIGEST_MUTANT=KILLED"]},"expected":{"exit_code":0,"tail_regex":"ADDITIONAL_DISPATCH_DIGEST_MUTANT=KILLED"}},
    {"id":"V7","kind":"suite","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_controller_g2b_attachment tests.test_controller_battery_float tests.test_battery_float_consumers","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^OK$"}},
    {"id":"V8","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev2/fixture_cap_probe.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK","SCRATCH_T0_STAGE_CAP_FIXTURE_ADAPTER_PASS=True"]},"expected":{"exit_code":0,"tail_regex":"SCRATCH_T0_STAGE_CAP_FIXTURE_ADAPTER_PASS=True"}},
    {"id":"V9","kind":"suite","cmd":"TMPDIR=/tmp/dd5-intrev2 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_v5_*.py tests/test_harvest_v5_*.py tests/test_t0_rehearsal.py tests/test_t0_anchor_positive_control.py tests/test_capture_t0_anchor_positive_control*.py tests/test_kernel_clock.py tests/test_arm_readiness_evidence_t0.py tests/test_capture_t0_step.py tests/test_prewindow_check.py tests/test_revision6_seal.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=48, errors=28, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"(?m)^OK.*$"}}
  ],
  "flags":[
    {"id":"C1","kind":"verification_gap","level":"blocking","text":"Required suite is red, independently of watchdog timing: shared T-0 sizing fixture lacks t0_stage_cap (fixed.keys), and two G4 positive controls lack the sizing binding. An in-memory cap correction made two sampled tests pass; no repository fixture was edited.","needs":"Repair the fixtures, disposition D1-D5, add discriminating regressions, and rerun V1 before seal."},
    {"id":"C2","kind":"verification_gap","level":"nonblocking","text":"Existing stage-list test does not kill digest-guard deletion because its changed file duplicates a row. A scratch single-row substitution test kills that mutation.","needs":"Add the single-row substitution regression."},
    {"id":"C3","kind":"residual_risk","level":"nonblocking","text":"Fixture evidence only; admission probes substitute plan-load, launch and battery seams while running real classification, archive and history code. Four joined occurrence cases remain skipped for missing D-134 freeze authority; no live qualification was performed.","needs":"Lead owns the joined/live verification after fixes and freeze authority."}
  ]
}
```

## Findings

REVIEW: FAIL

1. **D1 — MAJOR:** [prewindow.py:57](/Users/edr/code/JouleWise-wt-dd5-intrev/joulewise/prewindow.py:57) reuses the named-daemon filter instead of checking every process as addendum E requires. **V2:** an unrelated Python process at 99% CPU passed `t0_check` and the complete ten-minute dwell.

2. **D2 — MAJOR:** [v5_qualification.py:170](/Users/edr/code/JouleWise-wt-dd5-intrev/joulewise/v5_qualification.py:170) skips successful members without checking their clock status. The admission-abort branch also bypasses normal physics assessment. **V2:** successful B1 had an unbounded clock; B2 then aborted admission. Harvest reported only the admission cause, `end_state=false`, and permission for fresh `s1`, contrary to the “no other RECOVER cause” condition.

3. **D3 — MAJOR:** [v5_qualification.py:435](/Users/edr/code/JouleWise-wt-dd5-intrev/joulewise/v5_qualification.py:435) always uses the original verdict for history decisions. **V3:** a harvest-tool fault produced REFUSED; identical-byte re-harvest correctly produced NULL. The original pointer then refused as not re-armable, while the corrected pointer refused as outside the census. R3 cannot discharge this recoverable attempt.

4. **D4 — MAJOR:** [harvest_v5_g2b_window.py:506](/Users/edr/code/JouleWise-wt-dd5-intrev/scripts/harvest_v5_g2b_window.py:506) adds observation-producer faults to structural recovery causes. **V2:** adding only an observer write fault changed an otherwise re-armable admission abort to `end_state=true`, classified as instrument physics. This violates ruling 76’s separation of the two verdicts.

5. **D5 — MAJOR:** [v5_qualification.py:308](/Users/edr/code/JouleWise-wt-dd5-intrev/joulewise/v5_qualification.py:308) admits NULL predecessors without enforcing the general same-refusal-twice consult. **V4:** two authenticated, linked NULL records with identical cause codes still allowed the writer to publish a third fresh-`s1` plan and authorization.

## Residual risk

The requested venv suite finished **76 failed, 462 passed, 9 skipped, 335 subtests passed**. Fixture failures prevent several intended guards from being exercised; they are separate from the known watchdog artefact. Two sampled tests passed after the missing stage-cap allowance was supplied in memory.

Additional controller/battery checks passed **54/54**. Existing tests killed **13/14** guard mutations; a scratch single-stage substitution test killed the remaining digest mutation. Joined live qualification remains unverified. The worktree is clean and all test processes finished.