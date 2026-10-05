```json
{
"schema":"claude-codex-report/v1",
"genre":"implementation",
"status":"findings",
"completion":"complete",
"summary":"Closed the approved X2 STOP-harness gap; all 22 scratch-safe X2/X4 tests pass.",
"workspace":{"base_requested":"d60bf6cd","base_mode":"exact","head_start":"d60bf6cdd8d76f27778c4cba66e807c31834bb72","head_end":"d60bf6cdd8d76f27778c4cba66e807c31834bb72","upstream_end":"0a3b8806b0c0b1451f50fec4fe6843da72d4889e","branch":"feat/2026-10-05-v5-qualification-code"},
"pathspec":[
 "joulewise/evidence_night.py",
 "joulewise/night_agent_install.py",
 "joulewise/t0_rehearsal.py",
 "joulewise/v5_qualification.py",
 "scripts/check_v5_arm_abort.py",
 "scripts/harvest_v5_g2b_window.py",
 "scripts/harvest_v5_qualification.py",
 "scripts/produce_t0_rehearsal_bundle.py",
 "scripts/run_campaign.py",
 "scripts/run_night.py",
 "scripts/v5_s1_desk_closeout.py",
 "tests/test_arm_readiness.py",
 "tests/test_evidence_night.py",
 "tests/test_harvest_v5_g2b_window.py",
 "tests/test_install_night_agent.py",
 "tests/test_t0_rehearsal.py",
 "tests/test_v5_arm_abort.py",
 "tests/test_v5_s1_desk_closeout.py",
 "scripts/assemble_v5_battery_boundaries.py",
 "tests/fixtures/v5_qualification_harvest/block3_battery/SOURCE.json",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/g2a-small-p0512-r01/events.jsonl",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/g2a-small-p0512-r01/instrument_calibration/instrument_evidence.json",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/g2a-small-p0512-r01/metadata.json",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-post/instrument_evidence.json",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-post/raw/battery_float.post.ioreg",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-post/raw/battery_float.pre.ioreg",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-pre/instrument_evidence.json",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-pre/raw/battery_float.post.ioreg",
 "tests/fixtures/v5_qualification_harvest/block3_battery/capture-tree/instrument_validation/d117-g2a-prefill-probe-20261004T1305Z-cal-pre/raw/battery_float.pre.ioreg",
 "tests/fixtures/v5_qualification_harvest/block3_battery/t0-receipt.json",
 "tests/test_v5_block4_x4.py",
 "tests/test_v5_block4_x2.py"
],
"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"pending_verification"},
"verification":[
 {"id":"V1","kind":"test","cmd":"TMPDIR=/tmp/dd5-x4 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x2 tests.test_v5_block4_x4","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 22 tests in 84.154s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
 {"id":"V2","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-x4 PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/dd5-x4/resume-inspect.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["resume delta confined to X2 fixture; Python compilation passed; four pinned estimators unchanged; diff check passed"]},"expected":{"exit_code":0,"tail_regex":"diff check passed"}}
],
"flags":[
 {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"The prior broad requested run was non-green and canonical/evidence-install batches were interrupted. This approved resume reran X2/X4 only; original registry/G9 and journal-timeout findings remain.","needs":"Lead rerun the broader suites with scratch-safe fixtures at the integrated head."},
 {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"ARM-only a1/a2 battery assembly still depends on X3 native T-0 capture records retaining plan identity, phase=t0 and exact raw stdout. Those files remain untouched.","needs":"Integrate X3 capture payload and replay the assembler per occurrence."},
 {"id":"F3","kind":"baseline_drift","level":"nonblocking","text":"Earlier baseline comparisons used frozen b2ff2f36. origin/main is now 0a3b8806, including unrelated MLX changes; this resume has no failed X2/X4 methods to compare.","needs":"Use current upstream for final integration verification."}
]
}
```

## Change

Registered and retained STOP at the chain’s transcript path and updated the harvest locator. Only the X2 harness changed in this resume; earlier X4 work is preserved.

Changes remain uncommitted. X3-owned parts and pinned estimators are unchanged.

## Verification notes

The X2 harness isolates unrelated G10 source collection. X4 retains native G10 replay and real archived-byte authentication coverage.

## Residual risk

Broader suite verification and X3’s ARM-only T-0 capture payload remain open.