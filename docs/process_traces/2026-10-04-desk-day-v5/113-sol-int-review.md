```json
{
"schema":"claude-codex-report/v1",
"genre":"review",
"status":"findings",
"completion":"complete",
"summary":"REVIEW: FAIL; one blocker and four major defects reproduced; requested suite also fails.",
"workspace":{"base_requested":"898c49a7","base_mode":"exact","head_start":"898c49a786a3696ca1a4493d544a50714056f875","head_end":"898c49a786a3696ca1a4493d544a50714056f875","upstream_end":"0477ceb49b92421f0ba9c2b9b7eb54760f3d7ec2","branch":null},
"pathspec":[],
"unowned_dirty":[],
"verdict":{"result":"REVIEW: FAIL","findings":[{"id":"F1","severity":"blocker","file":"joulewise/t0_rehearsal.py","line":1292,"title":"G9 rejects successful native two-root desk closeout","evidence":"V3"},{"id":"F2","severity":"should_fix","file":"scripts/capture_t0_step.py","line":817,"title":"R0 trusts a stream maximum not bound to authenticated sizing","evidence":"V4"},{"id":"F3","severity":"should_fix","file":"scripts/write_v5_qualification_plan.py","line":381,"title":"Missing stage list refuses only after consuming launch","evidence":"V5"},{"id":"F4","severity":"should_fix","file":"joulewise/v5_qualification.py","line":381,"title":"Battery boundary replay does not authenticate occurrence timing","evidence":"V6"},{"id":"F5","severity":"should_fix","file":"scripts/harvest_v5_g2b_window.py","line":697,"title":"First guard-attested admission abort has no ruled fresh-s1 exception","evidence":"V7"}]},
"verification":[
{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/run_suite.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED tests/test_v5_pack_rehearsal.py::ObservedDeskMappingTests::test_desk_observation_backup_assembly_and_real_evaluators"]},"expected":{"exit_code":0,"tail_regex":"(?m)^[0-9]+ passed.*$"}},
{"id":"V2","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/prior_controls.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".......                                                                  [100%]"]},"expected":{"exit_code":0,"tail_regex":"7 passed"}},
{"id":"V3","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/desk_repro_full.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REAL_DESK_CLOSEOUT=COMPLETE","G9_NATIVE_DESK_STAGE=desk backup roots differ from the s1 ARM/plan","G9_AFTER_SINGLE_ROOT_GUARD_CURE=backup does not cover both s1 runs roots and custody","G9_AFTER_TWO_ROOT_AND_FOUR_COPY_CURES=ALL_FOUR_DESK_STAGES_PASS"]},"expected":{"exit_code":0,"tail_regex":"ALL_FOUR_DESK_STAGES_PASS"}},
{"id":"V4","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/frequency_repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["TRUE_320_SECOND_12_PPM_GATE=False","R0_WITH_ALTERED_ONE_SECOND_GATE=PASS","AUTHOR_WITH_CAPTURED_ONE_SECOND_MAX=PASS","ARM_WITH_CAPTURED_ONE_SECOND_MAX=True"]},"expected":{"exit_code":0,"tail_regex":"ARM_WITH_CAPTURED_ONE_SECOND_MAX=True"}},
{"id":"V5","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/stage_repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MISSING_STAGE_LIST_AUTHOR=PASS","AUTHORED_ROW_COUNT=15","STAGE_LIST_ATTESTED=False","CHAIN_STAGE_GUARD_EXIT=1"]},"expected":{"exit_code":0,"tail_regex":"CHAIN_STAGE_GUARD_EXIT=1"}},
{"id":"V6","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/battery_repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REVERSED_BOUNDARY_MONOTONIC_STAMPS=300,200,100","ASSEMBLER_AND_BOTH_HARVEST_SHARED_REPLAY=True"]},"expected":{"exit_code":0,"tail_regex":"ASSEMBLER_AND_BOTH_HARVEST_SHARED_REPLAY=True"}},
{"id":"V7","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/admission_repro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["ALL_S1_INSTRUMENT_RECOVER_END_STATE=True","ONLY_REARM_OVERRIDE_IS_RECOVER_NO_SCIENCE=True"]},"expected":{"exit_code":0,"tail_regex":"True"}},
{"id":"V8","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/mutate.py all","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"stop_census"}},
{"id":"V9","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/g4_controls.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["G4_6ms=FAIL: RAW anchor residual exceeds 5000000 ns or differs from arithmetic","G4_slew=FAIL: R0-to-author kernel frequency word changed","G4_12ppm=FAIL: R0 kernel frequency exceeds the stream clock budget"]},"expected":{"exit_code":0,"tail_regex":"G4_12ppm=FAIL:\\ R0\\ kernel\\ frequency\\ exceeds\\ the\\ stream\\ clock\\ budget"}},
{"id":"V10","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/g4_mutations.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["residual=KILLED","frequency=KILLED","gate=KILLED","G4_MUTANTS=3 KILLED=3"]},"expected":{"exit_code":0,"tail_regex":"G4_MUTANTS=3\\ KILLED=3"}},
{"id":"V11","kind":"test","cmd":"TMPDIR=/tmp/dd5-intrev PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-intrev/run_replay_safe.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["SCRATCH_REDIRECT_CONFIRMED=/tmp/dd5-intrev/replay"]},"expected":{"exit_code":0,"tail_regex":"SCRATCH_REDIRECT_CONFIRMED=/tmp/dd5-intrev/replay"}}
],
"flags":[
{"id":"C1","kind":"verification_gap","level":"nonblocking","text":"9 skips: 4 require GAMMA freeze authority, 5 concern OS/sandbox availability. Metal emitted an ignored exit diagnostic. Component controls are not live validation.","needs":"After fixes and freeze authority, execute the complete joined occurrence replay."},
{"id":"C2","kind":"verification_gap","level":"nonblocking","text":"Suite: 5 failed, 378 passed, 9 skipped, 255 subtests passed. Three writer subcases omit kernel_frequency; ARM expects freeze refusal but gets registry mismatch; desk fixture lacks already-OFF setter witness.","needs":"Resolve the baseline test expectations/fixtures and rerun the requested suite."},
{"id":"C3","kind":"scope_deviation","level":"nonblocking","text":"Pytest bypassed the memory scratch redirect: replay fixtures used /tmp/dd5-replay. Temporary children were cleaned. Corrected replay confirms /tmp/dd5-intrev/replay. No repository files changed.","needs":""},
{"id":"C4","kind":"residual_risk","level":"nonblocking","text":"38/39 guard mutants were killed; deletion of the duplicate desk overlap guard survived its positive-case test. Three additional G4 mutants were killed.","needs":""},
{"id":"C5","kind":"baseline_drift","level":"nonblocking","text":"origin/main advanced 0a3b8806 to 0477ceb4 (records only); target/merge base unchanged. Design 786e4604 to bf92e7d4 added ruling 76 C during testing. This is the requested A/B review.","needs":"Assess addendum C separately before seal."}
]
}
```

## Findings

REVIEW: FAIL

1. **F1 — BLOCKER:** [t0_rehearsal.py:1292](/Users/edr/code/JouleWise-wt-dd5-intrev/joulewise/t0_rehearsal.py:1292) requires ARM custody to equal plan custody, while the native desk producer requires them to be separate. Its next check at line 1300 also rejects the producer’s fourth `night_custody` copy. **V3:** native close-out returned COMPLETE, then G9 rejected both mismatches in sequence. Correcting those checks in memory let all four desk stages pass. Derive and verify the actual four-root source set.

2. **F2 — MAJOR:** [capture_t0_step.py:817](/Users/edr/code/JouleWise-wt-dd5-intrev/scripts/capture_t0_step.py:817) trusts `t_stream_max_s` from an internally valid, unbound gate file. **V4:** with the sizing record still at 320 seconds, replacing the gate maximum with one second admitted a 12 ppm draw through R0, author derivation and the ARM predicate; the 320-second budget failed. Bind the maximum to authenticated sizing and verify that binding downstream.

3. **F3 — MAJOR:** [write_v5_qualification_plan.py:381](/Users/edr/code/JouleWise-wt-dd5-intrev/scripts/write_v5_qualification_plan.py:381) checks the stage-list file only inside the launched chain. **V5:** a missing list still produced all 15 authored PASS rows; the list was absent from launch attestation, and the shell guard exited 1. `launch_window.py:329–359` consumes the capability before executing that guard. Authenticate and preflight the list before consumption.

4. **F4 — MAJOR:** [v5_qualification.py:381](/Users/edr/code/JouleWise-wt-dd5-intrev/joulewise/v5_qualification.py:381) replays battery age against each record’s stored wall time without binding its timing to the required occurrence boundary. **V6:** archived raw readings with reversed arm/publication/T-0 monotonic stamps `300/200/100` assembled successfully and returned True through the shared harvest replay. Bind observations to the original lifecycle artifacts and enforce boundary timing/order.

5. **F5 — MAJOR:** [harvest_v5_g2b_window.py:697](/Users/edr/code/JouleWise-wt-dd5-intrev/scripts/harvest_v5_g2b_window.py:697) lacks ruling 76 B.4’s first admission-abort exception. **V7:** the shared disposition returned END STATE for `s1` instrument RECOVER; the harvester’s sole override is `recover_no_science`. Implement the authenticated, first-abort-only fresh-`s1` disposition, including exclusion of other RECOVER causes.

## Residual risk

The requested suite finished with **5 failed, 378 passed, 9 skipped, 255 subtests passed**. Fixture/schema failures are detailed in C2. Seven courier, observer and non-claim controls passed.

Mutations killed **38/39 guards**, plus **3/3 additional G4 guards**. The surviving mutation exercised only a positive desk case.

Joined production replay remains unverified without freeze authority. This report uses the requested A/B specification snapshot; concurrently added addendum C needs separate assessment.