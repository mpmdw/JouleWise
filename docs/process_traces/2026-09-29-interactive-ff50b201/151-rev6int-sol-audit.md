```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"AUDIT: FINDINGS — seven findings; P8 replay and synthetic campaign pass; historical W1/W2 replay refuses.",
  "workspace":{"base_requested":"1b419f0e49534363ebb0aafe3f8931a286d01615","base_mode":"exact","head_start":"1b419f0e49534363ebb0aafe3f8931a286d01615","head_end":"1b419f0e49534363ebb0aafe3f8931a286d01615","upstream_end":"0009b97657d6ef794410a89fbd5a063912a3b957","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[
    {"id":"F1","severity":"blocker","file":"scripts/harvest_window.py","line":116,"title":"Precommit R9 replay reads stored and derived B","verification":"V7"},
    {"id":"F2","severity":"blocker","file":"scripts/issue_calibration_acceptance_generation.py","line":2500,"title":"Historical Revision 5 R7 replay now requires P8","verification":"V4"},
    {"id":"F3","severity":"should_fix","file":"scripts/prewindow_check.sh","line":164,"title":"Driver arguments containing claude or codex trigger check 8","verification":"V6"},
    {"id":"F4","severity":"should_fix","file":"scripts/harvest_window.py","line":132,"title":"Harness dispositions disagree with ledger dispositions","verification":"V8"},
    {"id":"F5","severity":"should_fix","file":"scripts/issue_calibration_acceptance_generation.py","line":1539,"title":"Issuer rejects producer records for slots without recordings","verification":"V9"},
    {"id":"F6","severity":"should_fix","file":"tests/test_powermetrics_fiducial.py","line":622,"title":"Behavioral exact-stop tests survive a cap revert","verification":"V3"},
    {"id":"F7","severity":"nit","file":"joulewise/powermetrics_fiducial.py","line":88,"title":"Pinned-file diff includes two comment additions beyond the cap line","verification":"V12"}
  ]},
  "verification":[
    {"id":"V1","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/p8_probe.py > /tmp/rev6audit/p8.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["20260722T145535-e941c821 EQUAL","20260722T194118-9dc0749d EQUAL","20260722T214220-1acdbbc0 EQUAL","N1_3_MEMBERS=PASS"]},"expected":{"exit_code":0,"tail_regex":"N1_3_MEMBERS=PASS"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_powermetrics_fiducial.DetectorTests.test_detection_cell_budget_is_the_ruled_corpus_calibrated_value tests.test_powermetrics_fiducial.DetectorTests.test_production_default_budget_spends_past_the_retired_ceiling tests.test_powermetrics_fiducial.DetectorTests.test_flat_loss_projection_exhausts_production_cap_before_deadline > /tmp/rev6audit/cap_actual.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/cap_mutation.py > /tmp/rev6audit/cap_mutation.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["MUTANT exact_stop_survived=True"]},"expected":{"exit_code":0,"tail_regex":"MUTANT exact_stop_survived=False"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -B /tmp/rev6audit/rev5-replay-frozen.py --baseline /tmp/rev6audit/issuer-baseline.py --scratch /tmp/rev6audit/rev5-production > /tmp/rev6audit/rev5-production.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["REFUSED: registration Revision 5 requires active predecessor d079_calibration_acceptance_v2_n17_r8","current refused with exit 3"]},"expected":{"exit_code":0,"tail_regex":"WI13_W1W2_REPLAY=PASS byte_identical=true"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/campaign.py > /tmp/rev6audit/campaign2.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MUTATION_r9_capture=REFUSED Revision 6 R9 record refused: R9 capture identity or disposition disagrees with ledger","CAMPAIGN_AND_3_MUTATIONS=PASS"]},"expected":{"exit_code":0,"tail_regex":"CAMPAIGN_AND_3_MUTATIONS=PASS"}},
    {"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/dwell_probe.py","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["claude_argument: exit=1 expected=0","codex_argument: exit=1 expected=0","real_claude: exit=1 expected=1","real_codex: exit=1 expected=1"]},"expected":{"exit_code":0,"tail_regex":"claude_argument: exit=0 expected=0"}},
    {"id":"V7","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/r11_probe.py > /tmp/rev6audit/r11.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PRECOMMIT_R9_B_READ=CONFIRMED stored=true derived=true","R9_SERIALIZED_B_VALUE=false equality_boolean_discarded=true"]},"expected":{"exit_code":0,"tail_regex":"PRECOMMIT_R9_B_READ=CONFIRMED"}},
    {"id":"V8","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/invalid_disposition.py > /tmp/rev6audit/invalid_disposition.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LEDGER_DISPOSITION=ordinary-invalid HARVEST_DISPOSITION=invalid","INVALID_CAPTURE_CONSUMER_REFUSED=Revision 6 R9 record refused: R9 capture identity or disposition disagrees with ledger"]},"expected":{"exit_code":0,"tail_regex":"INVALID_CAPTURE_CONSUMER_REFUSED=.*disagrees with ledger"}},
    {"id":"V9","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/no_recording.py > /tmp/rev6audit/no_recording.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["scripts.issue_calibration_acceptance_generation.PrepareRefusal: Revision 6 R9 record refused: R9 cells malformed"]},"expected":{"exit_code":0,"tail_regex":"CAMPAIGN_AND_3_MUTATIONS=PASS"}},
    {"id":"V10","kind":"suite","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_acc_25g83_rev6 tests.test_harvest_window tests.test_cap_replay_harness tests.test_prewindow_check tests.test_issue_p8_pin_delta > /tmp/rev6audit/focused.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V11","kind":"test","cmd":"TMPDIR=/tmp/rev6audit PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rev6audit/driver_tests.py > /tmp/rev6audit/driver_tests.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK","driver selected=13"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V12","kind":"inspection","cmd":"git diff --numstat origin/main...HEAD -- joulewise/powermetrics_fiducial.py","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["3\t1\tjoulewise/powermetrics_fiducial.py"]},"expected":{"exit_code":0,"tail_regex":"^1\\s+1\\s+joulewise/powermetrics_fiducial.py$"}}
  ],
  "flags":[{"id":"R1","kind":"residual_risk","level":"nonblocking","text":"Synthetic campaign injected detector results and archived disposition placeholders; real driver record writers, harvest producer, committed records and issuer were exercised. Full suite and live hardware validation were not run.","needs":""}]
}
```

## Findings

- **F1 — blocker**, `scripts/harvest_window.py:116`: REPORT mode decodes stored B and compares derived B before R9 is written or committed. Discarding the equality boolean afterward does not satisfy Revision 6 §4/R11. Command: V7.
- **F2 — blocker**, `scripts/issue_calibration_acceptance_generation.py:2500`: the historical R7 W1/W2 preparation refuses after the active default moves to P8. The baseline produces n=12; shipping code exits 3. Tests mask this through an `ACTIVE_ACCEPTANCE_ID` patch. Command: V4.
- **F3 — should-fix**, `scripts/prewindow_check.sh:164`: whole-command matching blocks driver arguments `/tmp/claude/window.json` and `/tmp/codex/window.json`. Real agent names correctly block. Command: V6.
- **F4 — should-fix**, `scripts/harvest_window.py:132`: harvest copies detector disposition `invalid`, while the ledger records `ordinary-invalid`; the issuer requires equality and refuses. Command: V8.
- **F5 — should-fix**, `scripts/issue_calibration_acceptance_generation.py:1539`: harvest emits null cells/ratio for no-recording slots, but the consumer unconditionally requires numeric fields. The three-window campaign otherwise reaches sufficient counts. Command: V9.
- **F6 — should-fix**, `tests/test_powermetrics_fiducial.py:622`: at a scratch-mutated cap of 165,000, both behavioral exact-stop tests pass because they compare against the mutated constant. The separate literal-value test fails. Command: V3.
- **F7 — nit**, `joulewise/powermetrics_fiducial.py:88`: the diff changes the cap line and adds two comments; the requested exactly-one-line condition is unmet. Command: V12.

P8 loads, validates and is the default; R7 still loads. Its recursive diff is pins, notes, identity and digest only. Three raw member replays were EQUAL. The real producer-record campaign accepted n=35, and all three digest/field mutations refused. Focused checks passed **73 + 13 + 3 tests**. No repository files changed; HEAD remained fixed.

## Residual risk

The synthetic campaign’s injection boundaries and omitted full-suite/live checks are recorded in R1. The lead’s next step is to resolve the findings before sealing; any estimator-byte correction requires updating P8’s pins and reissue evidence.