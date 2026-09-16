```json
{
"schema":"claude-codex-report/v1",
"genre":"review",
"status":"findings",
"completion":"complete",
"summary":"FINDINGS: outer signal catch overwrites completed terminal exit codes; runbook omits the new teardown-exception outcome.",
"workspace":{"base_requested":"efdaed879e1d13d06de719f10a4b7b504601cdb4","base_mode":"exact","head_start":"efdaed879e1d13d06de719f10a4b7b504601cdb4","head_end":"efdaed879e1d13d06de719f10a4b7b504601cdb4","upstream_end":null,"branch":null},
"pathspec":[],
"unowned_dirty":[],
"verdict":{
"findings":[
{"id":"F1","severity":"should_fix","location":"joulewise/night_agent_install.py:515-517","title":"Outer catch overwrites the outcome already completed by teardown","detail":"SIGTERM at exception-warning entry leaves resolved=false. Inner finally completes teardown; outer catch then assigns 143 before terminal no-op teardown. Reproduced on Python 3.14.7 and 3.9.6: retained 4 -> 143 (night loaded), restore failure 1 -> 143, teardown failure 1 -> 143, committed SUCCESS 0 -> 143 after stdout OSError (both loaded). Violates runbook §1.3. The code follows the dictation; lead adjudication is required."},
{"id":"F2","severity":"nit","location":"docs/phase_2/derivation_night_runbook.md:1434-1441","title":"Four-outcome table omits round 6c teardown failures","detail":"Engine :427-430 now returns RETAINED/1 with \"teardown failed; retained: ...\" before absence is established. The table only describes retention as exit 4 and exit 1 after proven absence. Add the new outcome and diagnostic."}
],
"class_1":"NO",
"class_2":"NO",
"predicate_cases":"957 fixture invocations: 477 foreground, 480 inherited SIGINT=SIG_IGN; zero hits. Cases include lying bootouts, UNKNOWN, failed bootstrap, commit refusal and uninstall. Direct ENGINE clock reads on both interpreters: selected/cutoff/read 60/120/59 -> rc0, both loaded; 60/120/60, 60/120/61, 120/60/60, 120/60/61 -> rc2, neither loaded. Applied the ruled run-mutated-file and attempted-bootout predicates.",
"SIGNAL_CLASS":"NO",
"signal_cases":"12 seam checks passed on each interpreter: except-warning, unwind frame/block entry, refusal/commit, two pending signals and simultaneous unblock, restore order, changed mask, teardown exception, uninstall entry. F1 cases completed teardown, restored masks/dispositions and returned without handler escape.",
"double_unwind":"COMMITTED -> SUCCESS/0; ROLLED_BACK/3; RETAINED/4. Second unwind: empty filesystem/fake-log diffs on both interpreters. F1 overwrites result outside teardown.",
"reversions":["shell: FAILED (failures=2) -> OK; 2 tests","module empty value: FAILED (failures=2) -> OK; 1 test","raised_once: FAILED (errors=1) -> OK; 1 test","outer catch: FAILED (errors=3) -> OK; 3 tests","restore order: FAILED (failures=2) -> OK; 1 test","teardown catch: FAILED (errors=1) -> OK; 1 test","run entry_mask: FAILED (failures=1) -> OK; 1 test"],
"shell":"Current ordered args[] implementation preserves order, duplicates and caller-relative absolutisation. Old-shell reversion: empty render-only caused rc0 and two fake bootstraps; uninstall caused rc0 and two fake bootouts. All restored regressions GREEN.",
"custody":"Source clean at requested HEAD; baseline digest matched; engine/shell restored byte-for-byte. All mutations in authorized delta6-copy; logs in delta6_audit. No real launchctl. Evidence: *.log, reversions.json, cases-*.jsonl, seams-full.json."
},
"verification":[
{"id":"V1","kind":"test","cmd":"python3 -B delta6_audit/run_module.py foreground tests.test_night_agent_install","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"fail","exit_code":1,"tail":["Ran 48 tests in 880.757s","FAILED (failures=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V2","kind":"test","cmd":"python3 -B delta6_audit/run_module.py foreground tests.test_install_night_agent","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 51 tests in 64.599s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V3","kind":"test","cmd":"python3 -B delta6_audit/run_night_mirror.py foreground","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 101 tests in 19.477s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V4","kind":"test","cmd":"python3 -B delta6_audit/run_module.py ign tests.test_night_agent_install","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 48 tests in 637.825s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V5","kind":"test","cmd":"python3 -B delta6_audit/run_module.py ign tests.test_install_night_agent","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 51 tests in 51.738s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V6","kind":"test","cmd":"python3 -B delta6_audit/run_module.py ign tests.test_run_night","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 101 tests in 19.546s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V7","kind":"test","cmd":"python3 -B delta6_audit/reversions.py","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.169s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V8","kind":"test","cmd":"python3 -B delta6_audit/extra_probe.py Extra && /usr/bin/python3 -B delta6_audit/extra_probe.py Extra","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 6.813s","OK","Ran 3 tests in 8.402s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V9","kind":"test","cmd":"python3 -B delta6_audit/real_seams.py && /usr/bin/python3 -B delta6_audit/real_seams.py","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta6-copy","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 5.456s","OK","Ran 12 tests in 5.386s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}
],
"flags":[
{"id":"G1","kind":"environment","level":"nonblocking","text":"Foreground engine: 9 failures involving 0.75s fake-print timeouts/early refusal or missed publication; not chased. Absent-unknown retention cells: bootstrap_failure/uninstall=True/deadman/rc9/priors=False; commit_refusal/uninstall=False/both labels/{113-with-wrong-label,hang}/priors={False,True}; all marker_loaded=False, clock=1789498800.0. Other failures: cross_two, closed_stdout(priors=True), stdout_failure, cleanup_clock. Full tracebacks retained. Named test_retention_product passed both modes.","needs":"Lead owns clean final-head replay and the separate timeout diagnosis."},
{"id":"G2","kind":"environment","level":"nonblocking","text":"Initial foreground run_night: one scratch-layout disjointness error. Replayed with sibling checkout/fixture directories inside delta6-copy: all 101 passed; inherited-ignore also passed.","needs":""}
]
}
```

## Findings

- **F1 — should fix:** The outer catch replaces completed outcomes `0`, `1`, and `4` with `143`. Reproduced on both interpreters; lead adjudication is required.
- **F2 — nit:** Runbook §1.3 omits the new teardown-failure outcome and warning.

## Residual risk

No full-suite or live-launchctl verification was performed, as instructed. Final replay and merge authority remain with the lead.