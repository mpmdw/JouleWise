```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented scoped X1 chain/ARM fixes; consumer wiring, shared fixtures, live census, and a watchdog timing gap remain.",
  "workspace": {"base_requested":"e1a6d8b0","base_mode":"exact","head_start":"e1a6d8b0be13b9d89bea38789bb81608e9cf18f4","head_end":"e1a6d8b0be13b9d89bea38789bb81608e9cf18f4","upstream_end":null,"branch":"feat/2026-10-05-v5-qual-x1"},
  "pathspec": [
    "joulewise/arm_readiness_evidence_t0.py",
    "joulewise/night_gate.py",
    "scripts/capture_t0_step.py",
    "scripts/check_v5_arm_abort.py",
    "scripts/ed_session/capture_t0_anchor_positive_control.py",
    "scripts/prewindow_check.sh",
    "scripts/run_night.py",
    "scripts/write_v5_qualification_plan.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_capture_t0_step.py",
    "tests/test_prewindow_check.py",
    "tests/test_run_night.py",
    "tests/test_t0_anchor_positive_control.py",
    "tests/test_v5_arm_abort.py",
    "tests/test_v5_qualification_plan.py",
    "joulewise/dwell.py",
    "joulewise/prewindow.py",
    "tests/fixtures/v5_qualification/dwell/0526Z.txt",
    "tests/fixtures/v5_qualification/dwell/0820Z.txt",
    "tests/fixtures/v5_qualification/dwell/1305Z.txt",
    "tests/fixtures/v5_qualification/dwell/1748Z.txt",
    "tests/fixtures/v5_qualification/dwell/c1.txt",
    "tests/fixtures/v5_qualification/dwell/c2.txt",
    "tests/test_v5_block4_x1.py"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation":"partial","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V1","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-x1/replay_baseline.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["3.M network before active-plan guard True"]},"expected":{"exit_code":0,"tail_regex":"3\\.M network before active-plan guard True"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x1 tests.test_v5_qualification_plan tests.test_v5_arm_abort tests.test_capture_t0_step tests.test_t0_anchor_positive_control tests.test_prewindow_check","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (errors=2)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"test","cmd":"TMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x1 tests.test_v5_qualification_plan.PlanWriterTests.test_backup_destination_cannot_nest_in_separate_plan_custody tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=5, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.PackNightProducerTests tests.test_run_night.Ruling76DriverTests tests.test_run_night.WindowDeadlineTests","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK (skipped=6)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"test","cmd":"cd /tmp/dd5-x1/origin-main\nTMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.PackNightProducerTests tests.test_run_night.WindowDeadlineTests","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK (skipped=6)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V7","kind":"test","cmd":"TMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=5)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V8","kind":"test","cmd":"cd /tmp/dd5-x1/origin-main\nTMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=4)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V9","kind":"test","cmd":"cd /tmp/dd5-x1/base\nTMPDIR=/tmp/dd5-x1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests.test_signalled_child_cannot_hold_cleanup_past_budget","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V10","kind":"lint","cmd":"git diff --check\nbash -n scripts/prewindow_check.sh","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"scope_deviation","level":"blocking","text":"Unmodified consumers block terminal-path binding, two-root backups, campaign ledger selection, and G10 custody replay at harvest.","needs":"Expand scope below; integrate and verify at the final reviewed H."},
    {"id":"F2","kind":"verification_gap","level":"blocking","text":"The G10 evaluator integration test still errors: its shared mocked G2 fixture has no native context or two-root layout. V2's separate missing re import was fixed; its serial replay passed.","needs":"Migrate the requested shared fixture factories, then rerun PositiveControlTests.test_real_author_refusal_and_record_validate_under_evaluate_g10."},
    {"id":"F3","kind":"environment","level":"blocking","text":"Live Mac resident replay unavailable: pgrep rc 3 Cannot get process list; /bin/ps EPERM. Synthetic CPU tests do not close this gate.","needs":"Lead/Ed retain pgrep plus two ps samples about 1 s apart outside this sandbox; record the supplied WO-CENSUS-SEMANTICS cure."},
    {"id":"F4","kind":"lead_ruling","level":"blocking","text":"The unattended executor exists, but registration lead time remains unbound and pack_t0 remains 360 s, below the 600 s minimum dwell.","needs":"Bind FILL[T0-CAPTURE-CLI], pre-T0 X, allowance and trigger against the 2700 s dwell cap and 3600 s author span before seal."},
    {"id":"F5","kind":"verification_gap","level":"blocking","text":"Four isolated 8 s watchdog failures match origin/main. Signal cleanup additionally times out here; the individual case passes at base (7.737 s) and origin/main (7.892 s). Full test_run_night is not green.","needs":"Lead investigate the narrow startup/cleanup timing difference and rerun supervision plus test_run_night under controlled load."},
    {"id":"F6","kind":"residual_risk","level":"nonblocking","text":"3.M is in unlisted scripts/magistrate_watchdog.py: git_probe precedes the active-plan guard; unchanged.","needs":"Assign the network guard to its owning lane."},
    {"id":"F7","kind":"environment","level":"nonblocking","text":"Early py_compile emitted bytecode to runtime-managed PYTHONPYCACHEPREFIX outside task scratch. Later checks used in-memory compilation and suppressed bytecode; no unlisted repository paths changed.","needs":""}
  ],
  "scope_expansion": {"requested_paths":["scripts/run_campaign.py","scripts/harvest_v5_g2b_window.py","scripts/v5_s1_desk_closeout.py","scripts/produce_t0_rehearsal_bundle.py","joulewise/t0_rehearsal.py","tests/test_arm_readiness.py","tests/test_t0_rehearsal.py"],"reason":"Close unlisted consumers and migrate shared G2 fixture factories.","blocked_work":"End-to-end closure of 1.3, 1.17, 1.18, 1.20 and the G10 integration check.","minimal_change":"Thread selected ledger paths; enforce STOP path; back up both roots; preserve/replay the G10 custody tree; stage pinned disjoint contexts in fixtures."}
}
```

## Change

Implemented chain environment and stage authentication, pinned two-root contexts, unattended capture/staging, shared dwell and CPU predicates, readiness-anchored OFF settle, ledger-input propagation, and G10 custody, signal, span and EOF guards.

Checkout substitution was already fixed at base. Changes remain uncommitted; all four pinned estimators are unchanged.

## Verification notes

Earlier fixture and probe-accounting failures were corrected and replayed. The shared G10 fixture error and watchdog timing gap remain as flagged. Four watchdog failures also reproduce on `origin/main`; the additional signal-cleanup timeout remains unresolved.

The canonical suite was not started.

## Residual risk

Scope expansion, T-0 scheduling rulings and controlled-load verification are required before acceptance. Live gates remain PROVISIONAL.