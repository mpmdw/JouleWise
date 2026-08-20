```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "L10 is STILL-OPEN: no valid current-family sacrificial lifecycle exists, and its required stable ED replay remains open.",
  "workspace": {
    "base_requested": "5bd7acf",
    "base_mode": "exact",
    "head_start": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "head_end": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "upstream_end": "b9e197a61e884ee1040bcbc6f9f1092a7c027282",
    "branch": "detached HEAD; main is a later descendant"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "seat": "L10-SACRIFICIAL-FULL-LIFECYCLE",
    "result": "STILL-OPEN",
    "charter_component_disposition": "NOT-READY",
    "coverage": "17/18 independently enumerated evidence classes directly examined; the retained a9/a10 corpus is off-repo and unreadable here. Coverage is independently UNVERIFIED for READY purposes.",
    "ed_row": {
      "id": "ED-L10-1",
      "status": "OPEN"
    },
    "strongest_reason": "The required same-head production-pack L10 lifecycle has no receipt, while the only frozen family examined (_v3) is ruled to lapse and require a _v4 re-freeze; it therefore cannot establish present armability."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git log --oneline -3 && git merge-base --is-ancestor bfc3236 HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5bd7acf Merge pull request #160 from mpmdw/integration/phase2-transaction",
          "bfc3236 Merge impl/r2-s0-mint-resolver: the executed D-146/D-147 transaction (S0-S5), gate-authorized"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5bd7acf.*phase2-transaction"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest discover -s tests -p 'test_analysis_finalizer.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 10 tests in 12.137s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest discover -s tests -p 'test_analysis_manifest_v3.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 12 tests in 0.437s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/extract_detection_floors.py --runs-root /nonexistent/l10-runs --spec /nonexistent/l10-spec.json --out \"$TMPDIR/l10-review/detection-floor-extraction.json\" --evaluation-basis-sha256 0000000000000000000000000000000000000000000000000000000000000000 --hash-bundles",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "error: --evaluation-basis-sha256 and --consumption-semantics-id are required together"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "required together"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 scripts/record_window_duration_margins.py --repository-root . --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v3 --runs-root \"$TMPDIR/l10-review/runs\" --receipt-root \"$TMPDIR/l10-review/custody\" --pack-identity plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "{\"detail\": \"operator pack identity is not pack-derived\", \"reason\": \"pack_identity_invalid\", \"status\": \"REFUSE\"}"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "pack_identity_invalid"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "canonical unittest discovery completed successfully"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The a9/a10 corpus is Ed-held off-repo, so its existence and any unrecorded transcript could not be inspected. Repository records nevertheless continue to list the replay as owed.",
      "needs": "Provide a custodied transcript with all commands and exit codes, or formally replace the row if the D-146 barrier makes its specified positive proof impossible."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "This review is pinned exactly to requested head 5bd7acf, but main has advanced to b9e197a. This NOT-READY verdict is conservative and does not certify the later head.",
      "needs": "Any later READY attempt must use its final named head."
    }
  ]
}
```

## Findings

Verdict: **STILL-OPEN**. In charter vocabulary, L10 is **NOT-READY**, with an independent **UNVERIFIED** coverage condition. ED-L10-1 is **OPEN**.

Evidence universe: 18 independently enumerated classes—target-head topology; D-148.5 lifecycle ruling; F1 code, frozen-pack compatibility, operator wiring, C-028 delta, and replay; F2; F3; F4; F5; four CLI obligations; ED-L10-1; retained-corpus admissibility; and baseline/coverage. I directly examined 17; the off-repo a9/a10 corpus was unavailable. Positive probes passed for the new finalizer/manifests suites and the valid `_v3` identity advanced beyond the identity gate. Negative probes reproduced F2 and stale-F3 refusals.

- **L10-1 — blocker — F1 remains open.** The code repair exists: the U7-named functions are present at [analysis_manifest_v3.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/joulewise/analysis_manifest_v3.py:2777) and the consumer accepts only finalized-v3 at [inputs.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/joulewise/analysis_engine/inputs.py:592). But direct validation of the frozen contrast `_v3` prospective manifest produced four refusals; no current pack lifecycle transcript exists; and the queue still says the L10 replay is required at [state_kernel.json](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process/state_kernel.json:3234). The `_v3` fuse is ruled to lapse and `_v4` re-freeze is compelled ([MAGISTRATE-RULING.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:23), [r2](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r2.md:74)). Required work: make the `_v4` prospective bytes valid for the delivered contract, wire the operator procedure, then capture the complete `_v4` lifecycle at one final head.

- **L10-ED — blocker — ED-L10-1 remains open.** It is a stable, pre-sitting qualification, not T0. The ED ledger marks it OPEN and still owed at [30-ED-QUALIFICATION-rows.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:609) and [summary row 15](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:977). Current Ed-facing documents still say “a9/a10 desk replay” is owed ([ed-evening-checklist.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process/ed-evening-checklist.md:24)). Failure scenario: no CLI-level PASSED-basis proof before a claim-bearing close-out.

- **L10-COV — blocker — coverage is unverified.** The baseline manifest still pins `ac3fe1d` and `_v1` packs; its only commit is `694442c`. The current L10 surface includes the new finalizer, 3 `_v3` packs, and 447 changed files / 68,247 insertions in the examined scope. No independent re-enumeration or adversarial coverage attack was located. This independently bars READY.

- **L10-2 — should_fix — F2 remains open.** The literal extraction command at [window_runbook.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/phase_2/window_runbook.md:1766) omits the co-required semantics id; execution exits 2 exactly as enforced at [extract_detection_floors.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/scripts/extract_detection_floors.py:101).

- **L10-3 — should_fix — F3 remains open.** The copied `WINDOW_ID` is `_v2` at [window_runbook.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/phase_2/window_runbook.md:190); the `_v3` plan carries the `_v3` identity at [plan_tree.json](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json:3717). The stale literal reproduces `pack_identity_invalid`; the true `_v3` identity progresses to the next `member_missing` gate.

- **L10-4 — should_fix — F4 and the four CLI gaps remain open.** `FLOOR-BIND-01` is still queued with its same-custody fence live ([state_kernel.json](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/docs/process/state_kernel.json:1268)); no prospective cross-session licence was found. There is also no current CLI transcript for the salvage, supersession, v2 aggregate-mint, or waiver obligation.

- **L10-5 — nit — F5 remains open.** The executable backup probe recorded `bundle_count=5` for three bundle directories plus `campaign_manifests` and `instrument_validation`, matching the flawed counter at [backup_runs.sh](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC10/scripts/backup_runs.sh:31).

Sibling-assembly adjudication: `19-ROW-L10-sacrificial-lifecycle.md` wins the material divergence. Its claim that the U7-named functions exist is confirmed; `ROW-L10.md`’s zero-grep claim is false at the merged head. Its stronger conclusion is also confirmed: the frozen `_v3` manifests do not satisfy that validator. Both assemblies remain correct that no same-head lifecycle, ED replay, F2 repair, F3 current-family repair, or FLOOR-BIND-01 closure exists. Their branch-only statements are superseded by the verified merge: S0–S5 is now on `main`.

The single strongest reason is the missing current-family lifecycle: L10’s own closure criterion requires it, and the `_v3` family it would have exercised is now ruled expired rather than armable.

## Residual risk

The retained a9/a10 corpus could contain an unrecorded replay, but it was not available to inspect; the repository’s current evidence still records the work as owed. No quiet-Mac or live-hardware action was attempted.