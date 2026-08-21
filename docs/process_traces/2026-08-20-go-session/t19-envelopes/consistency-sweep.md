```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Four load-bearing documentation drifts found; gate states, errata handling, PR/hash claims, and Codex usage snapshots otherwise reconcile.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "b01d9a2d64e2",
    "head_end": "b01d9a2d64e2",
    "upstream_end": "b01d9a2d64e2",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [".decisive-replay/"],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","title":"Kernel V4 transaction still instructs the superseded 111-path allowlist"},
      {"id":"F2","severity":"should_fix","title":"Generated restart projection points to T12/T13 instead of the committed T18/T19 report"},
      {"id":"F3","severity":"should_fix","title":"T19 Codex-run count has three incompatible documented values"},
      {"id":"F4","severity":"should_fix","title":"Histsem contract authority link and pinset-absence vocabulary contradict the adopted consult"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"python3 scripts/gen_state.py --check",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"git diff --check",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags":[
    {
      "id":"F1",
      "kind":"baseline_drift",
      "level":"nonblocking",
      "text":"No files were modified; the pre-existing untracked .decisive-replay/ directory was preserved.",
      "needs":""
    }
  ]
}
```

## Findings

| ID | Doc:line | Conflicting statements | Current primary evidence | Minimal fix |
|---|---|---|---|---|
| F1 | [state_kernel.json:3587](/Users/edr/code/JouleWise/docs/process/state_kernel.json:3587), generated [TASK_QUEUE.md:623](/Users/edr/code/JouleWise/TASK_QUEUE.md:623) | V4 says “111-path allowlist”; RUN_STATE, the T18/T19 report, and contract say 111 → **112**. | [rh-ruling.md:70](/Users/edr/code/JouleWise/docs/process_traces/2026-08-20-go-session/rh-ruling.md:70) records the binding cold-pass amendment; [contract:115](/Users/edr/code/JouleWise/docs/contracts/receipt_histsem_verifier.md:115) agrees. | Change the kernel V4 goal to “112-path allowlist” and regenerate TASK_QUEUE/RUN_STATE projections. |
| F2 | [state_kernel.json:22](/Users/edr/code/JouleWise/docs/process/state_kernel.json:22), generated [RUN_STATE.md:4323](/Users/edr/code/JouleWise/RUN_STATE.md:4323), [RUN_STATE.md:27](/Users/edr/code/JouleWise/RUN_STATE.md:27) | Generated intake calls T12/T13 the latest report; T19.2 says its report note is “owed.” | The T19.2 addendum is committed in [2026-08-20-t18-t19-session.md:603](/Users/edr/code/JouleWise/docs/run_reports/2026-08-20-t18-t19-session.md:603). | Repoint `latest_report` to T18/T19 in the kernel, regenerate, and replace “owed” with “landed.” |
| F3 | [RUN_STATE.md:27](/Users/edr/code/JouleWise/RUN_STATE.md:27), [T18/T19 report:643](/Users/edr/code/JouleWise/docs/run_reports/2026-08-20-t18-t19-session.md:643) | RUN_STATE says runs 51–62; report says 51–64; supplied current ledger truth is 51–65. The committed continuation itself currently stops at run 58. | Current custody count supplied for this sweep: **51–65**. | Reconcile the canonical T19 ledger through run 65, then update both summaries to that exact range. |
| F4 | [receipt_histsem_verifier.md:4](/Users/edr/code/JouleWise/docs/contracts/receipt_histsem_verifier.md:4), [contract:31](/Users/edr/code/JouleWise/docs/contracts/receipt_histsem_verifier.md:31), [contract:90](/Users/edr/code/JouleWise/docs/contracts/receipt_histsem_verifier.md:90) | Contract cites `rh-ruling` as authority, but that ruling says absent HEAD pinset returns `histsem_pinset_absent`; contract body says ordinary readiness. The refusal table also ambiguously says an absent pinset always refuses. | The adopted consult says an unambiguous absent-at-HEAD path returns ordinarily: [rh-consult.md:13](/Users/edr/code/JouleWise/docs/process_traces/2026-08-20-go-session/t19-envelopes/rh-consult.md:13), [rh-consult.md:42](/Users/edr/code/JouleWise/docs/process_traces/2026-08-20-go-session/t19-envelopes/rh-consult.md:42). | Add the consult as the superseding authority and narrow `histsem_pinset_absent` to a present-but-invalid/missing governed row or worktree-read case. Preserve the original ruling as custody. |

- Gate state / row count: NONE. The historical 83-row checkpoint predates the closure transaction; kernel now has 86 active rows after retiring one and registering four. `_v4` remains blocked on `ED-MINT-LICENSE-01`; `WINDOW-COUNCIL-GATE` is a separate quiet-Mac gate.

- PRs, hashes, verdicts: NONE apart from F3’s run-count provenance. #166 `0c3c1a6`, #167 `cd50dc7`, closure `1bc918a`, and `aedf530` reconcile.

- ERRATA/deviation propagation: NONE. E-1–E-4 correctly retain immutable original records and provide the correction channel; no current summary repeats a retracted claim as current fact.

- Codex usage: NONE. 16.0%, ~20%, and ~13–15% are timestamped snapshots; the historical ~15% figures are explicitly corrected, while T19.2 and its addendum agree on ~20%.

## Residual risk

No source-code or external CI re-review was performed. The reported 51–65 ledger truth is not yet fully represented in the committed ledger files.