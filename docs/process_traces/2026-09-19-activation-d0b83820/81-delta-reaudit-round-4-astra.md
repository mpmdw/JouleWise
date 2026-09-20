```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"The accepted first-launch boundary holds, but two publication paths silently lose diagnostics; required suites have baseline/environment failures.",
  "workspace":{"base_requested":"df5c483e","base_mode":"exact","head_start":"9f4dda28c70efe2851115627ced90ee8ef2fb9f7","head_end":"9f4dda28c70efe2851115627ced90ee8ef2fb9f7","upstream_end":"6032b9e93220f9c9b9a04ca6d1dc75aa4aa92942","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "counts":{"blocker":0,"should_fix":2,"nit":0},
    "findings":[
      {"id":"R1","severity":"should_fix","title":"Publication silently discards newly discovered artifact errors","call_site":"scripts/run_night.py:1064-1066,1095-1101; _courier_prelaunch:1366","counterfactual":"Real run_night/result/inventory/publisher/courier, fake git/email transport: chmod chain.stdout.log to 000 after result creation. Both publisher calls return None, the destination omits the file, the immutable result retains its non-null hash, reporting_errors is empty, and publication success is logged. attempted=1, sent=true, launches=1.","recommendation":"Return and carry newly discovered inventory omissions into the prompt and surviving publication records."},
      {"id":"R2","severity":"should_fix","title":"Post-delivery publication errors survive only in a discarded in-memory report","call_site":"scripts/run_night.py:1803-1807,1096-1100","counterfactual":"The real publisher succeeds before delivery, then its second push raises OSError. run_night returns GO with attempted=1/sent=true/launches=1. The error is appended to report.diagnostics but appears in neither the already-issued prompt nor night.log, result.json, courier.json or the attempt journal.","recommendation":"Persist or emit post-delivery diagnostics while preserving successful delivery and the original measurement verdict."}
    ]
  },
  "verification":[
    {"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-reaudit4/custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night > /tmp/stagea-reaudit4/run-night.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 224 tests in 157.236s","FAILED (failures=1, errors=1, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-reaudit4/related-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_night_gate tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_sample_quiet_predicate_evidence tests.test_night_agent_install tests.test_gen_state > /tmp/stagea-reaudit4/related.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 264 tests in 1113.256s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4 > /tmp/stagea-reaudit4/quick.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=193.313 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-reaudit4/audit-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-reaudit4/audit.py cases","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["BOUNDARY CASES PASS: 8 attempted=1/sent=true/launches=1; safety attempted=0/sent=false/launches=0"]},"expected":{"exit_code":0,"tail_regex":"BOUNDARY CASES PASS"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-reaudit4/identity-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-reaudit4/audit.py identity","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 14 tests in 4.801s","OK","PROTECTED REGRESSIONS + SAFETY + RECIPIENT PASS: 14 tests"]},"expected":{"exit_code":0,"tail_regex":"PROTECTED REGRESSIONS.*PASS"}},
    {"id":"V6","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-reaudit4/audit.py concurrent","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["CONCURRENCY PASS"]},"expected":{"exit_code":0,"tail_regex":"CONCURRENCY PASS"}},
    {"id":"V7","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-reaudit4/diagnostics.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIAGNOSTIC LOSS COUNTERFACTUALS CONFIRMED"]},"expected":{"exit_code":0,"tail_regex":"COUNTERFACTUALS CONFIRMED"}},
    {"id":"V8","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-reaudit4/consult79-head.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LOCK RACE (explicitly deferred): final HEAD still launches twice on empty-lock interleave","CONSULT79 HEAD REPLAY PASS; eleven existing outcome regressions unchanged"]},"expected":{"exit_code":0,"tail_regex":"CONSULT79 HEAD REPLAY PASS"}},
    {"id":"V9","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-reaudit4/replay-old.py barrier","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OLD DEFECT ASSERTION REJECTED: barrier"]},"expected":{"exit_code":0,"tail_regex":"OLD DEFECT ASSERTION REJECTED: barrier"}}
  ],
  "flags":[
    {"id":"F1","kind":"environment","level":"nonblocking","text":"/bin/ps is denied; pgrep cannot obtain the process list. The related-suite cleanup test and quick-tier AXI identity tests require host census. Exact names appear below.","needs":"Lead reruns the host-dependent checks outside this sandbox."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"The blocked-journal test hits its 8-second watchdog. A scratch replay with the df5c483e driver reproduces the same failure.","needs":"Lead adjudicates or resolves this baseline failure before accepting the suite gate."},
    {"id":"F3","kind":"verification_gap","level":"nonblocking","text":"One run_night fixture randomly received /tmp/qpe-fixture-reft3nq6; generator refused its t3 substring. The isolated test replay passed.","needs":""}
  ]
}
```

## Findings

**R1 — should_fix: newly discovered inventory failures disappear.** At [the publisher’s error-entry skip](/Users/edr/code/JouleWise-wt-sareaudit4-d0b83820/scripts/run_night.py:1064), errors discovered after the immutable result was written are discarded. The reproduction preserved a successful result inventory, made `chain.stdout.log` unreadable, and observed an omitted published file, empty prompt diagnostics, and a success log. [Reproduction results](/tmp/stagea-reaudit4/diagnostics.log).

**R2 — should_fix: post-delivery failures have no surviving diagnostic.** [Final reporting](/Users/edr/code/JouleWise-wt-sareaudit4-d0b83820/scripts/run_night.py:1803) collects errors into a report that `run_night` then discards. A failed second publication returned GO without recording the failure anywhere persistent. Successful delivery and the measurement verdict should remain intact; the publication failure still needs an observable record. [Reproduction script](/tmp/stagea-reaudit4/diagnostics.py).

**E1 — ruling coverage**

| 79a item | Assessment |
|---|---|
| 1 | **IMPLEMENTED AS RULED.** Post-chain preparation stays in `run_night`, crosses the shared guard, and passes facts/diagnostics onward. Minimal REFUSED fallback uses exclusive creation and preserves existing objects. |
| 2 | **IMPLEMENTED AS RULED.** Repair follows successful acquisition; the loser returns immediately. Refresh, heartbeat reset, argv construction and diagnostic logging are guarded. Fallback recipient is a tested constant. |
| 3 | **DEVIATES in diagnostic preservation.** Null-hash entries, absence handling, explicit evidence-discovery failures and safe publisher diagnostics exist. However, newly discovered error entries are silently discarded by publication: R1. |
| 4 | **DEVIATES in diagnostic preservation.** Bookkeeping guards prevent failures from hiding successful delivery, but post-delivery diagnostics can disappear: R2. `allow_courier=False` remains separate. |
| 5 | **IMPLEMENTED AS RULED.** All 16 boundary regressions pass; required fixture shapes and event-controlled concurrency are present. The eleven protected regressions remain unchanged. These tests do not detect R1/R2. |

The entire delta changes only `scripts/run_night.py` and `tests/test_run_night.py`; no unrelated edits were found. All three ownership helpers and the entire `dead_man` function are **byte-identical** to `df5c483e`. No flock implementation was introduced. Existing release calls were wrapped by the ruled bookkeeping guard. `git diff --check` passed.

**E2 — consult 79 Q1, row by row**

Here, `optional(...)` means `_courier_optional(report, label, operation)`.

| Q1 site | HEAD containment |
|---|---|
| `_calibration_refusal`: existence, read, decode, validation, formatting | `optional("post-chain result", prepare_result)` encloses the call. |
| Post-chain refusal creation | Same `"post-chain result"` guard. |
| `_write_driver_refusal`: receipt processing, validation, serialization | Same guard encloses these transitive operations. |
| Refusal persistence: exclusive open/write/fsync/close | Same guard; failure proceeds to independently guarded minimal persistence. |
| Post-chain interpretation: indexing, string conversion, verdict selection | Same `"post-chain result"` guard. |
| `_write_result`: refusal paths, inventory, mapping, exclusive write | Same guard; failure sets result unavailable and REFUSED fallback status. |
| Artifact discovery: refusal/rerun globs and evidence traversal | Raised errors cross `"post-chain result"` or guarded `"durable record"`; evidence traversal also records an explicit incomplete-inventory entry. R1 concerns discarded returned errors. |
| Artifact inspection and hashing | `_artifact_entry` catches stat/read failures; enclosing result/publication operations also cross the shared guard. Fixed directories produce null-hash error entries. |
| Result logging | Inside `"post-chain result"`; failure after successful result creation preserves its verdict. |
| `_finish_reporting` pre-courier publication | Moved into prelaunch: `optional("durable record", ...)`. |
| `_durable_record`: subprocesses, copies, directories, Git operations, logging | Internal `except Exception` returns a diagnostic; prelaunch also uses `"durable record"`. R1/R2 concern diagnostic retention. |
| `run_courier` entry | `mkdir` and lock acquisition remain prerequisites and can escape before successful ownership. Repair/logging moved into guarded prelaunch. |
| `_evidence_cleanup_error` | `optional("evidence repair", ...)`, plus its existing internal exception conversion. |
| Transitive evidence imports, cleanup, journal and refusal operations | Contained by `_evidence_cleanup_error`, itself under `"evidence repair"`. |
| Lock acquisition and initial metadata publication | Unchanged; failures can still prevent obtaining ownership. Explicitly deferred by 79a. |
| Lock-refused return | Immediate return with `heartbeat_seen=False`; no heartbeat inspection or repair. |
| Per-attempt refresh and heartbeat reset | `optional("lock metadata", ...)` and `optional("heartbeat reset", ...)`. |
| `_courier_argv`: template, watchdog and cleanup-path access | `optional("courier prompt", ...)`; failure selects filesystem-independent fallback argv. |
| `Popen` | Reached after guarded preparation. Existing `OSError` retry handling remains; process-creation failures are outside the guarantee. |

Executed through real `run_night`, with fixture transport:

| Counterfactual | Attempted | Sent | Popen calls | Observed |
|---|---:|---:|---:|---|
| Outcome chmod `000` | 1 | true | 1 | Null hash/`PermissionError`; limitation inline. |
| `_write_result` raises | 1 | true | 1 | Minimal REFUSED result; known chain facts retained; exit 3. |
| Existing `result.json` directory | 1 | true | 1 | Foreign contents intact; primary and fallback failures inline; exit 3. |
| Fixed artifact becomes directory | 1 | true | 1 | Null hash/`IsADirectoryError`; repair limitation inline. |
| Heartbeat is directory | 1 | true | 1 | Reset failure inline. |
| Unusable `night.log` after chain completion | 1 | true | 1 | Inventory and logging failures inline. |
| `_courier_argv` raises `UnicodeError` | 1 | true | 1 | Usable fallback argv and recipient. |
| Durable publication raises after good result | 1 | true | 1 | Original GO verdict/exit preserved; failure inline. |

[Full case records](/tmp/stagea-reaudit4/cases.log). The old seat-78 inventory reproduction also now launches once for both readable and unreadable controls; its old defect assertion fails as expected. Only its publisher mock return was adapted to the new `None` contract. [Replay](/tmp/stagea-reaudit4/old-inventory.log).

**E3 — ownership ordering**

The event-controlled production callers produced:

| Caller | Attempted | Sent | Launches |
|---|---:|---:|---:|
| Winner | 1 | true | 1 |
| Loser | 0 | false | 0 |

Exactly **one repair, one refusal document and one launch**. The loser performed zero result/publication work, zero heartbeat inspections and zero heartbeat mutations. [Evidence](/tmp/stagea-reaudit4/concurrent.log).

The **old barrier reproduction was rerun unchanged inside an observation wrapper**. Its second caller cannot reach `write_refusal`, so the barrier times out after five seconds. The winner catches `BrokenBarrierError` and launches; the old two-document assertion fails with zero documents. **This expected barrier timeout is not a defect.** [Output](/tmp/stagea-reaudit4/old-barrier.log).

Consult 79’s reproductions were also adapted to HEAD’s expected outcomes and rerun. The explicitly deferred empty-metadata lock interleave still permits two launches. [Replay](/tmp/stagea-reaudit4/consult79-head.log).

**E4 — protected regressions and recipient**

All eleven outcome tests are byte-identical to `df5c483e`, with no diff hunks inside them. Their delivery/repair helpers are unchanged too. All eleven pass.

The recipient test exists and passes. Direct template inspection confirms:

`COURIER_RECIPIENT == claude.ai.copper531@passmail.net`

**E5 — safety suppression**

`NightDriverTests.test_unproven_chain_termination_records_unkilled_and_spawns_no_courier` passes. The reporting-failure regression also passes. Independently obstructing result publication with unproven termination produced **attempted=0, sent=false, launches=0**.

**E6 — same-signature closure**

No surviving optional-operation exception site was found that prevents the first `Popen` **after chain-completion facts and successful courier-lock acquisition**, within 79a’s accepted boundary.

There are new ways to hide reporting failures: **R1 and R2**. Primary result-publication failures tested here correctly produce REFUSED handling; they did not report ordinary GO.

**E7 — required suites**

All three requested commands completed in order. Exact tails are recorded in V1–V3.

The failures were:

- `BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`: eight-second watchdog timeout, independently reproduced using the `df5c483e` driver. [Baseline replay](/tmp/stagea-reaudit4/baseline-watchdog.log).
- `EvidenceProbeTests.test_rehearsal_and_wrapper_missing_calibration_always_deliver`: random fixture pathname contained `t3`; isolated replay passed. [Replay](/tmp/stagea-reaudit4/fixture-rerun.log).
- `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted`: sandbox process census unavailable.
- `AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row`: process identity unavailable.
- `AxiControllerEventTests.test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`: process identity unavailable.

The latter three are environmental: `/bin/ps` was directly confirmed denied, and `pgrep` reported it could not obtain the process list.

Next: lead addresses R1/R2 and completes the baseline/host-dependent verification gates. No repository files were changed.

## Residual risk

Delivery and Git transport were mocked; `sent=true` does not establish live email acceptance. Exception containment does not bound blocking operations.

The deferred lock interleave, unchanged dead-man reporting block, pre-boundary chain-exit persistence and `Popen` failures remain outside this closure claim.