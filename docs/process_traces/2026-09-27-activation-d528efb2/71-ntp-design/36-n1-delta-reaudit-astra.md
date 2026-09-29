```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1 survives for separately grouped descendants; the fix introduces an OFF-failure recovery wedge; the witness-category bypass also survives.",
  "workspace": {
    "base_requested": "3ad82b43",
    "base_mode": "exact",
    "head_start": "3ad82b436e2a44d6e6178b914c66b8684dc9f6ab",
    "head_end": "3ad82b436e2a44d6e6178b914c66b8684dc9f6ab",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"D1","severity":"blocker","file":"scripts/run_night.py:1006","summary":"Absence of the original process group still authorizes query and ON while a descendant in another group survives.","introduced":false,"same_signature":"Execution F1"},
      {"id":"D2","severity":"should_fix","file":"joulewise/network_time_window.py:354","summary":"After an OFF refusal and failed immediate ON, the driver's empty start claim prevents every subsequent recovery attempt.","introduced":true},
      {"id":"D3","severity":"nit","file":"joulewise/network_time_window.py:40","summary":"The category regex can backtrack into a quoted process/category token in the message payload.","introduced":false,"same_signature":"Contract N1"},
      {"id":"D4","severity":"nit","file":"tests/test_run_night.py:873","summary":"The saved F1 regression errors on the old implementation because its ON mock returns None, rather than reaching its safety assertions.","introduced":true}
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"AUDIT_LABEL=new-selected /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/replay_selected.py new","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK","SAFETY_BLOCKED 0"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"AUDIT_LABEL=old-selected /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/replay_selected.py old","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=19, errors=6)","SAFETY_BLOCKED 0"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V3","kind":"test","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/off_failure_regression.py old","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["RECOVERY_AFTER_OFF_FAILURE restored on_retried True marker_present False"]},"expected":{"exit_code":0,"tail_regex":"restored on_retried True marker_present False"}},
    {"id":"V4","kind":"test","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/off_failure_regression.py new","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["AssertionError: a known never-launched chain must permit the failed ON retry"]},"expected":{"exit_code":0,"tail_regex":"restored on_retried True marker_present False"}},
    {"id":"V5","kind":"other","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/probes_killpg.py new","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PROBES_COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"PROBES_COMPLETE"}},
    {"id":"V6","kind":"other","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/recovery_descendant.py new","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["RECOVERY_DESCENDANT restored descendant_alive True on_called True marker_present False"]},"expected":{"exit_code":0,"tail_regex":"RECOVERY_DESCENDANT"}},
    {"id":"V7","kind":"test","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/mutate_guards.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["off exit 1","route exit 1"]},"expected":{"exit_code":0,"tail_regex":"route exit 1"}},
    {"id":"V8","kind":"inspection","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/doc_bundle_check.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DOC_BUNDLE_COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"DOC_BUNDLE_COMPLETE"}},
    {"id":"V9","kind":"suite","cmd":"AUDIT_LABEL=new-suite /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/run_tests.py new tests.test_network_time_window tests.test_run_night tests.test_night_gate tests.test_arm_retry tests.test_launch_window","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=6, errors=13, skipped=9)","SAFETY_BLOCKED 0"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V10","kind":"test","cmd":"AUDIT_LABEL=repo-recheck-final /opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/recheck.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK","SAFETY_BLOCKED 0"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V11","kind":"test","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/real_replay.py","cwd":"/tmp/ntp-n1delta-d528efb2/new","observed":{"result":"pass","exit_code":0,"tail":["REAL_REPLAY_COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"REAL_REPLAY_COMPLETE"}},
    {"id":"V12","kind":"test","cmd":"/opt/homebrew/bin/python3 -B /tmp/ntp-n1delta-d528efb2/amplify_f1.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["old exit 1","new exit 0"]},"expected":{"exit_code":0,"tail_regex":"new exit 0"}}
  ],
  "flags": [
    {"id":"E1","kind":"environment","level":"nonblocking","text":"The 476-test run had 13 Git-context errors and two CLI subtest failures in the archive checkout; all 14 affected tests passed in the real checkout. Four remaining 8-second bind-supervisor watchdog failures reproduced on e7371399. Native pgrep could not obtain the process list; descendant probes used native killpg(pgid,0) through the injectable absence seam.","needs":"Lead reruns the four watchdog tests in its supported verification environment."},
    {"id":"E2","kind":"residual_risk","level":"nonblocking","text":"Contract N5 remains a future scope dependency: N3 must populate OLD_IDLE_PLANS, but its ruled scope omits network_time_window.py.","needs":"Explicitly include joulewise/network_time_window.py in N3's assignment."}
  ]
}
```

DELTA: FINDINGS

## Findings

**D1 — BLOCKER: execution F1 survives for descendants in separate process groups.**

The new check at [run_night.py:1006](/Users/edr/code/JouleWise-wt-ntp-n1delta-d528efb2/scripts/run_night.py:1006) proves only the original group absent. Production quiet-evidence code creates recorder and collector children with `start_new_session=True`; its repair/cleanup runs later, after the driver’s query/ON path.

Executed a harmless native sleeper in a separate group. With the original group proved absent using `killpg(pgid, 0)`, the driver returned GO, performed **OFF → query → ON**, wrote `chain.exited`, and removed the marker while the descendant remained alive. Recovery independently returned `restored` under the same condition. Both revisions exhibit this signature. Settings and log commands were injected; sleepers were terminated afterward.

The same-group control correctly withheld query/ON on the candidate. The remaining requirement is proof covering every capturing descendant group before either driver or recovery proceeds. [Reproduction output](/tmp/ntp-n1delta-d528efb2/probes-killpg-new.log).

**D2 — SHOULD-FIX: the fix introduces a recovery dead end after an OFF refusal.**

Both OFF-failure branches close the empty start claim and write `chain.exited` with `launch_failed=true`, but never complete `chain.started`. If immediate ON fails, the marker remains. New recovery then attempts to decode the empty start file at [network_time_window.py:354](/Users/edr/code/JouleWise-wt-ntp-n1delta-d528efb2/joulewise/network_time_window.py:354), returns `marker_invalid`, and never retries ON.

Executed through the real driver with injected command results and a prohibition on spawning the chain:

| Revision | Subsequent recovery, with ON now available |
|---|---|
| `e7371399` | `restored`; ON retried; marker removed |
| `3ad82b43` | `marker_invalid`; no ON retry; marker retained |

The assertion passes on the old revision and fails on the candidate. Give these branches an explicit, durable “Popen never ran” state that recovery understands, while preserving the immediate ON attempt and F2’s refusal of genuinely unknown identities. [Regression](/tmp/ntp-n1delta-d528efb2/off_failure_regression.py), [candidate failure](/tmp/ntp-n1delta-d528efb2/off-regression-new.log).

**D3 — NIT: contract N1 survives through regex backtracking.**

The new category regex can match a second `timed[...]` token inside the message. A timestamped text-category line whose payload is:

`quoted timed[11]: [com.apple.timed:data]`

still supplies the witness and yields `clean` on both revisions. Parse the actual process/category fields without permitting the match to restart inside the payload.

**D4 — NIT: F1’s saved regression has an incidental old-revision error.**

At [test_run_night.py:873](/Users/edr/code/JouleWise-wt-ntp-n1delta-d528efb2/tests/test_run_night.py:873), the ON mock returns `None`. On the old implementation, this raises `TypeError` before the safety assertions. Changing only that scratch mock to return `{"exit_code": 0}` produces the intended **assertion failure on old / pass on new**. That corrected counterfactual was executed.

**Disposition of every original finding**

`F→P` means assertion failure on `e7371399`, pass on `3ad82b43`; `E→P` means an uncaught error on old, pass on new. The [full test-name manifest](/tmp/ntp-n1delta-d528efb2/selected.json) and [old replay](/tmp/ntp-n1delta-d528efb2/old-selected.log) preserve exact cases.

| Original finding | Disposition and executed regression |
|---|---|
| Execution F1 | **Partial.** Same-group case fixed; separate-group signature survives as D1. Saved driver test E→P; corrected scratch test F→P. Recovery’s `test_exited_child_record_does_not_override_live_group`: F→P. |
| Execution F2 | **Fixed for unknown identity.** Empty-start and unknown-identity dead-man tests, plus `test_unknown_pgid_with_exited_record_is_not_proof`: F→P. |
| Execution F3 / Contract B1 | **Fixed.** Preserved-real-log parsing and unindented continuation-marker precedence tests: F→P. Both supplied real logs now parse completely. |
| Execution F4 | **Fixed.** `test_orphaned_raw_query_file_does_not_block_retry`: F→P; orphan bytes remain unchanged and the next numbered query attests successfully. |
| Execution F5 | **Fixed.** `test_non_object_off_receipt_is_unattested`: F→P. |
| Contract B2 | **Fixed fixture integration.** Original baseline pack test fails by assertion; revised test passes on both revisions. Existing assertions remain. New empty-enforced-set pack test also passes on both. |
| Contract S1 | **Fixed.** Exact cold-registry equality: F→P. Both document policy blocks equal `render_policy()`. |
| Contract S2 | **Coverage added.** Interval comparison, clock pair, registered builds, boot mismatch, wall-short lead, nonzero exit, census/deadline abort, exception after OFF, OFF exception, recovery refusal, and rehearsal paths execute. Coverage-only cases generally P→P because their behavior was already correct. Both OFF-guard and route-guard deletion runs fail **by assertion**; intact tests pass. |
| Contract S3 | **Fixed.** `test_pending_restore_states_write_registered_refusals_before_off`: E→P; old errors are missing refusal files. Candidate records both registered reasons. |
| Contract S4 | **Fixed.** Five-reading H7 span/rate comparison against the estimator: F→P. Real W1-d04 span also matches its recorded estimator value. |
| Contract N1 | **Partial.** Original category-in-payload test F→P; expanded payload still bypasses it—D3. |
| Contract N2 | **Fixed.** Invalid-OFF-JSON authenticated-marker test: F→P. |
| Contract N3 | **Fixed at driver cleanup.** Query `TypeError` restoration test: E→P; candidate attempts ON. |
| Contract N4 | **Fixed.** Both OFF-failure ordering tests: F→P; ON precedes close/exit recording. D2 is a separate subsequent-recovery regression. |
| Contract N5 | **Reported; future scope action remains.** No runtime regression applies. |
| Contract N6 | **Confirmed independently.** Read real W1-d04 evidence, SHA-256 `668a17130cdad9bbc8d0e8f3de882a469eaf414c1ed51ce2f8a65971b314b002`; `clock_anchor.clock_stamps` contains all five readings. Computed span equals stored `0.00148773193359375` s. |
| Contract N7 | **Unchanged style nit.** The test class remains between module-level constants. The fix brief requested N1–N4, plus reporting/confirmation for N5–N6. |

All **42 added or changed tests pass** on the candidate. The old implementation produced **19 assertion failures and 6 errors**, including subtest results.

The three lead-owned edits check out: both policy blocks are byte-exact, and the GO paragraph accurately describes the additional launch refusals and unopened pack route. Preserved-log replay still finds all 42 corrections in the two window ranges and reproduces the four excluded members plus eight clean members, using hypothetical OFF receipts solely to isolate H6.

**Same-signature statement:** execution **F1** and contract **N1** survive in the forms above; N7 remains unchanged. D2 is a newly introduced functional regression.

Next: repair D1 and D2, retain the unknown-identity refusal, and rerun the supplied counterexamples before accepting N1.

## Residual risk

The full scoped run exercised **476 tests**, with nine skips. After successful rechecks of the archive-checkout failures, four unchanged bind-supervisor watchdog failures remain; each reproduced on the old implementation. This is **not a fully green suite**.

Live bench checks remain lead-owned. No real settings commands, system-log queries, captures, or laptop-battery reads were performed. Repository files and HEAD remained unchanged.