```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Seat-81 reproductions close, but three related diagnostic-loss paths remain; launch-boundary and protected regressions pass.",
  "workspace":{"base_requested":"87c380781d7025cde9954a28309bc45ede3a38db","base_mode":"exact","head_start":"87c380781d7025cde9954a28309bc45ede3a38db","head_end":"87c380781d7025cde9954a28309bc45ede3a38db","upstream_end":"6032b9e93220f9c9b9a04ca6d1dc75aa4aa92942","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "counts":{"blocker":0,"should_fix":3,"nit":0},
    "findings":[
      {"id":"R1","severity":"should_fix","title":"Post-launch courier diagnostics are excluded from persistence","call_site":"scripts/run_night.py:1812; producers at 1243,1512,1538-1539","counterfactual":"Real run_night/result/inventory/publisher/courier with fake Git/email: inject sent-marker fsync or attempt-journal PermissionError after launch. Each returns GO, attempted=1, sent=true, Popen=1, and two successful fake pushes. The specific diagnostic exists only in report.diagnostics; prompt and all four durable reporting surfaces lack it.","recommendation":"Track the cutoff at actual prompt issuance and persist subsequent run_courier diagnostics too."},
      {"id":"R2","severity":"should_fix","title":"Publisher error return still drops omission names after a successful push","call_site":"scripts/run_night.py:1102-1109","counterfactual":"After result creation, chmod chain.stdout.log to 000 and replace night.log with a directory. Both fake Git pushes succeed, but both publisher returns say durable record failed: IsADirectoryError and omit the unreadable chain artifact name. Its immutable result hash remains non-null and the published artifact is absent; GO and delivery remain intact.","recommendation":"Retain omissions on exception returns and distinguish completed push from failed local logging."},
      {"id":"R3","severity":"should_fix","title":"Failure of the late-log sink discards the original and secondary diagnostics","call_site":"scripts/run_night.py:1817-1819","counterfactual":"During the second fake push, chmod only night.log to 0400 and raise OSError POST_SEND_FAILURE. The guard records that error and the late-log PermissionError only in memory. Neither reaches the prompt, night.log, result.json, courier.json or attempt journal; other custody files remain writable and delivery still returns GO.","recommendation":"Use another surviving durable surface when the late-log append fails, without changing delivery or measurement status."}
    ]
  },
  "verification":[
    {"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-fresh87/custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night > /tmp/stagea-fresh87/run-night.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 226 tests in 148.500s","FAILED (failures=1, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"^OK"}},
    {"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-fresh87/related-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_night_gate tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_sample_quiet_predicate_evidence tests.test_night_agent_install tests.test_gen_state > /tmp/stagea-fresh87/related.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 264 tests in 1007.836s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"^OK"}},
    {"id":"V3","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4 > /tmp/stagea-fresh87/quick.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=185.411 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-fresh87/closure-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-fresh87/closure.py > /tmp/stagea-fresh87/closure-rerun.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REMAINING DIAGNOSTIC LOSS COUNTERFACTUALS CONFIRMED"]},"expected":{"exit_code":0,"tail_regex":"COUNTERFACTUALS CONFIRMED"}}
  ],
  "flags":[
    {"id":"E1","kind":"environment","level":"nonblocking","text":"The sandbox denies /bin/ps and pgrep process census. Nine process-census tests were skipped; host-dependent failures are named in the report.","needs":"Lead owns unsandboxed verification."},
    {"id":"E2","kind":"environment","level":"nonblocking","text":"The blocked-journal test hits its 8-second watchdog in this sandbox; the supplied lead record says its unsandboxed runs pass.","needs":""},
    {"id":"E3","kind":"residual_risk","level":"nonblocking","text":"The first drop-omitted mutant run also hit a random fixture basename containing t3. Its replay killed the mutant with one expected assertion failure and zero errors.","needs":""}
  ]
}
```

## Findings

**R1 — should_fix:** The [diagnostic cutoff](/Users/edr/code/JouleWise-wt-safresh2-d0b83820/scripts/run_night.py:1812) is taken after `run_courier` returns. Its comment is false: sent-marker persistence, attempt bookkeeping, and lock-release diagnostics can arise after the prompt was issued. Reproduced independently with fsync and attempt-journal failures; both diagnostics disappear despite writable reporting surfaces.

**R2 — should_fix:** The [publisher exception return](/Users/edr/code/JouleWise-wt-safresh2-d0b83820/scripts/run_night.py:1102) bypasses the new omission return. Two successful simulated pushes followed by actual log-directory errors yielded generic publication-failure messages and lost the unreadable artifact’s omission diagnostic.

**R3 — should_fix:** The [late logging guard](/Users/edr/code/JouleWise-wt-safresh2-d0b83820/scripts/run_night.py:1819) prevents an exception from changing delivery status, but provides no surviving record when that log write fails. Making only `night.log` read-only loses both the second-push failure and the logging failure.

All four counterfactuals returned **GO, attempted=1, sent=true, Popen=1**. [Reproduction script](/tmp/stagea-fresh87/closure.py) · [Observed output](/tmp/stagea-fresh87/closure-rerun.log).

**F1 — bench scope, callers, and seat-81 replay**

The diff contains only the two intended fixes and associated tests: two files, 44 insertions, two deletions. No unrelated changes; `git diff --check` passes. Closure remains incomplete for the reasons above.

All eight production callers were checked:

- `_courier_prelaunch:1375` and `_finish_reporting:1814` append the returned diagnostic literally.
- `_finish_reporting:1802,1810` and `dead_man:3339,3374,3392,3409` ignore it in the deferred paths.

No caller interprets non-`None` as a failed publication or changes the verdict because of it. The omission wording in the prompt is honest; `result_unavailable` remains false. R2 concerns the publisher’s own exception wording and discarded omissions.

The new guarded log call does **not** suppress delivery or change the exit code when it raises; R3 demonstrates that while exposing diagnostic loss.

Seat 81’s two original counterfactuals now observe:

```text
late_inventory_denial: rc=0 attempted=1 sent=true Popen=1
publisher_returns (both): durable record omitted unreadable artefacts: night/chain.stdout.log (PermissionError)
prompt_reporting_errors: durable record omitted unreadable artefacts: night/chain.stdout.log (PermissionError)
published_file_exists=false; result retains sha256=42c6377c2ded7c55568ea5e91ce08d85214e73929d3fe536704f36fefea2cd7e; push_success_logged=true
post_delivery_publication_failure: rc=0 attempted=1 sent=true Popen=1
diagnostic: durable record failed: OSError: POST_SEND_FAILURE
persisted_diagnostic=true; prompt_diagnostic=false
```

[Adapted reproduction](/tmp/stagea-fresh87/diagnostics.py) · [Raw output](/tmp/stagea-fresh87/diagnostics.log).

**F2 — mutation checks**

Both requested mutants are killed:

```text
MUTANT drop_omitted KILLED failures=1 errors=0
MUTANT no_late_log KILLED failures=1 errors=0
```

The updated real-publisher test kills `drop_omitted`; the new post-delivery log test kills `no_late_log`. The new omission-prompt test mocks publication, so **that test alone would let `drop_omitted` survive**. The combined three-test set detects both requested mutants, but misses R1–R3.

[Mutation harness](/tmp/stagea-fresh87/mutants.py) · [Omission result](/tmp/stagea-fresh87/drop-omitted-rerun.log) · [Logging result](/tmp/stagea-fresh87/no-late-log.log).

**F3 — real driver cases and concurrency**

| Counterfactual | Attempted | Sent | Popen | Exit |
|---|---:|---|---:|---:|
| Outcome chmod `000` | 1 | true | 1 | 0 |
| `_write_result` raises | 1 | true | 1 | 3 |
| Existing `result.json` directory | 1 | true | 1 | 3 |
| Fixed artifact becomes directory | 1 | true | 1 | 0 |
| Heartbeat is directory | 1 | true | 1 | 0 |
| Unusable `night.log` after chain | 1 | true | 1 | 0 |
| `_courier_argv` raises `UnicodeError` | 1 | true | 1 | 0 |
| Durable publication raises | 1 | true | 1 | 0 |

All ran through real `run_night`. The additional unproven-termination case remained **0 / false / 0**, exit 6. [Case output](/tmp/stagea-fresh87/cases.log).

The event-controlled courier callers produced **winner: 1 / true / 1; loser: 0 / false / 0**. Exactly one repair, one refusal document, and one launch; no loser result work or heartbeat inspection/mutation. [Concurrency output](/tmp/stagea-fresh87/concurrent.log).

The eleven outcome regressions are byte-identical to `df5c483e` and all pass. Their helpers, the three ownership helpers, and `dead_man` are also unchanged. The identity/safety/recipient replay passed all 14 tests. [Identity output](/tmp/stagea-fresh87/identity.log).

**F4 — same-signature closure**

(a) No remaining optional-operation exception site was found that prevents first `Popen` within 79a’s accepted boundary and current producer contracts.

(b) Diagnostic preservation remains open at **R1–R3**, with executable counterfactuals above.

**F5 — record-82 nits**

Both remain queue data:

- Retry logging duplicates existing diagnostics within the bounded retry loop; it does not change delivery or verdict.
- Packet serialization is unguarded, but current fact producers supply JSON-compatible values; no production counterfactual was found. An earlier failed result serialization would leave those facts unchanged, so the earlier guard alone is not proof of safety. `default=str` also would not make serialization universally total.

**F6 — requested suites**

All three commands completed in order. Exact tails:

```text
Ran 226 tests in 148.500s
FAILED (failures=1, skipped=9)

Ran 264 tests in 1007.836s
FAILED (failures=1)

QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=185.411 result=FAIL
```

Failures:

- `BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`: the known sandbox-only eight-second watchdog failure; supplied lead evidence reports unsandboxed passes.
- `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted`: unavailable process census.
- `AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row`: unavailable process identity.
- `AxiControllerEventTests.test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`: unavailable process identity.

`/bin/ps` was directly denied; `pgrep` reported it could not obtain the process list. These census failures are environmental.

[Driver log](/tmp/stagea-fresh87/run-night.log) · [Related-suite log](/tmp/stagea-fresh87/related.log) · [Quick-tier log](/tmp/stagea-fresh87/quick.log).

No repository files changed; HEAD remains pinned and clean. Next: lead closes R1–R3, then verifies and reviews the new final head.

## Residual risk

Git and email transport were simulated; `sent=true` is fixture evidence. Exception containment does not bound blocking operations. The deferred ownership interleave, dead-man reporting paths, pre-boundary chain-exit persistence, and `Popen` failures remain outside this closure claim.