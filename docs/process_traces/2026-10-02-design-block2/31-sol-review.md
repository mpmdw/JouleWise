```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"MERGE: safety checks pass; stale runbook span; base-matched environment failures.","workspace":{"base_requested":"b317866d0","base_mode":"exact","head_start":"8a8635a7ba40b41574fc4e7af898b5ad74cb73dd","head_end":"8a8635a7ba40b41574fc4e7af898b5ad74cb73dd","upstream_end":"b317866d04b4b2af1eaf4522df6563d87e8bafe3","branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"decision":"MERGE","findings":[{"id":"G2A-01","severity":"should_fix","file:line":"docs/phase_2/window_runbook.md:2317","claim":"Minor: runbook still states span 33556/window 34456; emitted span is 17248. Refresh the recipe.","evidence_executed":"checks.py recomputed 7947.40625 fixed + 9300 allowance -> 17248; author_command.py authored a 19980 s window."}]},"verification":[{"id":"V1","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"fail","exit_code":1,"tail":["Ran 257 tests in 143.729s","FAILED (failures=9, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_agent_install","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 82 tests in 689.619s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 104 tests in 0.971s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V4","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_g2_phase_d","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 15.483s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V5","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_generate_g2a_probe_inputs","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 28 tests in 1.320s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V6","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_summarize_g2a_prefill_probe","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 14 tests in 0.562s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_select_g2a_prefill_length","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 8 tests in 0.078s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V8","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_window","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 11.008s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V9","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_derivation_night","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 50 tests in 27.157s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V10","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_check_window_provenance","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 36 tests in 37.473s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V11","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_g2a_window","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 5.212s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V12","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_g2a_window","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 21 tests in 10.914s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V13","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night","cwd":"/tmp/g2a-lane-review/base","observed":{"result":"fail","exit_code":1,"tail":["Ran 255 tests in 121.778s","FAILED (failures=8, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V14","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_campaign.G2aLowCountCampaignTests","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 11.719s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V15","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go","cwd":"/tmp/g2a-lane-review/head","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 4.920s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V16","kind":"test","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-lane-review/revision6_tests.py /tmp/g2a-lane-review/head","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 1.643s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V17","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-lane-review/checks.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["screen_matches_live_acceptance True","check_fences True"]},"expected":{"exit_code":0,"tail_regex":"True|SELECT|PASS"}},{"id":"V18","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-lane-review/screen.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["check_exit 0","PASS generated Phase D matches pinned runbook bytes"]},"expected":{"exit_code":0,"tail_regex":"True|SELECT|PASS"}},{"id":"V19","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-lane-review/harvest_cases.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["{\"case\": \"low-count\", \"verdict\": \"SELECT\", \"exit\": 0, \"stdout_custody_only\": true, \"causes\": [], \"archive_created\": true, \"low_count_valid\": true, \"count_under_three_recorded\": true, \"selector_tokens\": 1024}"]},"expected":{"exit_code":0,"tail_regex":"True|SELECT|PASS"}},{"id":"V20","kind":"test","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-lane-review/mutants.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["{\"mutant\": \"d-generator-span-removed\", \"exit\": 1, \"failures\": [\"ERROR: test_typed_calibration_refusal_path_is_night_custody (tests.test_gen_g2a_window.G2aInspectionTests.test_typed_calibration_refusal_path_is_night_custody)\", \"ValueError: NIGHT_PROGRAMMED_SPAN_S must be one literal export in the pinned chain\", \"Ran 1 test in 0.792s\", \"FAILED (errors=1)\"]}"]},"expected":{"exit_code":0,"tail_regex":"FAILED"}}],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"The same eight driver failures at head/base occur because the venv disables the battery fixture in child Pythons.","needs":""},{"id":"F2","kind":"residual_risk","level":"nonblocking","text":"One additional head driver test hit its 8 s watchdog; focused replay passed. Revision 6 focused replay: 16/16 pass at both heads.","needs":""},{"id":"F3","kind":"residual_risk","level":"nonblocking","text":"Harvest fixtures mock ledger/bracket/raw seams; actual mock capture, reduction and strict validation proved low-count behavior.","needs":""},{"id":"F4","kind":"environment","level":"nonblocking","text":"Optional full campaign: base interrupted; head PID 76991 remains active after sandbox denied SIGINT. Required checks complete.","needs":"Lead: stop PID 76991 and its scratch descendants."}]}
```

## Findings

**G2A-01 — minor, nonblocking:** [window_runbook.md:2317](/Users/edr/code/JouleWise-g2a-review/docs/phase_2/window_runbook.md:2317) retains the superseded span and window example. The generator emits **17248 s**. No blocking production defect was observed.

All requested modules existed and ran, including both new modules. No tracked file changed. The diff touched none of the fenced production paths.

The Revision 6 audit covered every changed driver region:

| `run_night.py` lines | Effect on Revision 6 |
|---|---|
| 3078–3084 | Adds exact registration-byte SHA discrimination. |
| 3087–3097 | Retains 7680 s and the original deadline calculation; chain-span parsing applies to other registrations. |
| 3111–3123 | Adds classification/error handling; a valid Revision 6 registration uses the existing budget. |
| 3137–3159 | Retains both manifest evidence fields, manifest authentication and prior-session checks when the discriminant is true. |
| 3164–3165 | Retains literal `SESSION_ID` parsing. |
| 3209–3210 | Retains the Revision 6 start-record schema. |
| 3398–3399 | Retains manifest admission before the unchanged OFF/settle/dwell path. |

The 16 focused admission/start-record tests passed at both revisions: head `Ran 16 tests in 1.643s / OK`; base `Ran 16 tests in 1.554s / OK`. Existing Revision 6 assertions were preserved after the ruled registration-fixture correction.

All four scratch mutants were caught:

| Mutant | Test that went red |
|---|---|
| G2-a span absent | `NightDriverTests.test_generic_calibration_uses_literal_budget_without_manifest` |
| Revision 6 fixture registration replaced with D-166 | `NightDriverTests.test_start_manifest_first_window_records_null_prior_and_all_conditions` |
| Discriminant inverted | Generic admission test above and `test_standard_plan_budget_preserves_programmed_span_and_gate_cost` |
| Generator span export removed | `G2aInspectionTests.test_typed_calibration_refusal_path_is_night_custody` |

The missing-span negative test stayed green. Additional traces confirmed that both missing-span and D-166 registration cases refused before OFF, without reading the Revision 6 manifest or claiming the chain.

Span recomputation was:

- Fixed work: `5400 + 160 + 1944 + 393.40625 + 50 = 7947.40625 s`.
- Stated allowances: `20×240 + 4×300 + 8×180 + 1440 + 420 = 9300 s`.
- Integer span: `ceil(17247.40625) = 17248 s`.
- Rounded window: `ceil((17248 + 2700)/60)×60 = 19980 s`.

At t0 + 10 s, the admission runway was 2722 s, preserving the full 2700 s dwell cap.

Screen comparison against the live acceptance returned **True**, using exact decimal comparison. A stale source literal made `--check` exit 1; regeneration followed by `--check` exited 0. The comparator value was not printed.

Argv-only and combined argv-only/verify-only runs preserved identical 34-entry before/after listings and produced the reservation arguments consumed by the installer parser. Verify-only alone invoked a reservation stub without creating capture directories. G2-a render-only passed; the full installer suite passed at head and base. Base tail: `Ran 82 tests in 701.431s / OK`.

The authoring command produced a v2 plan, chain, sidecar and schedule in scratch. Shell syntax and driver preflight passed. Producer tests exercised the stale 76-row ledger and arbitrary snapshot refusals; the typed refusal export was checked.

Harvest fixture results were:

| Fixture | Verdict |
|---|---|
| Complete sweep | SELECT |
| Invalid small member | RECOVER |
| Pre-screen stop | RECOVER |
| Archive copy mismatch | REFUSED |
| Before completion boundary | REFUSED |

Their stdout contained custody information only. A valid low-count member remained valid, recorded its count, and caused the selector to choose 1024 under D-166. The separate actual mock campaign/reducer/strict-validator test completed both members with `max_failures=1`.

## Residual risk

Complete-harvest fixtures mock ledger authentication, bracket assessment and raw-validator results. This is fixture orchestration evidence; no live capture or model loading was performed.

The broad driver failures comprise eight base-matched battery fixture failures and one head-only watchdog timeout that passed focused replay.

**Cleanup remains:** the optional whole-campaign base run was interrupted. Head scratch worker **PID 76991** remained active after a separate cleanup command received `Operation not permitted`. The lead should verify its identity under `/private/tmp/g2a-lane-review/head` and stop it and its descendants before quiet-machine work. The optional whole-campaign comparison is incomplete; all requested review checks finished.