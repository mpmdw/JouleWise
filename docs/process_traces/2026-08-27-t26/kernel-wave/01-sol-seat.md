```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Six content findings, including four blockers; ledger cardinality, pointer validation, generated state, and count arithmetic are otherwise correct.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "e4eadeb73c35c9aa712a71812ac928cdb65f5e8c",
    "head_end": "e4eadeb73c35c9aa712a71812ac928cdb65f5e8c",
    "upstream_end": "7945da1102979fb27590e1dfed98c7977bf55def",
    "branch": "kernel/t26-wave"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "refuse_pending_fixes",
    "clean_checks": [
      "Exactly 18 task IDs were added; none removed or invented.",
      "gen_state --check validates schema, files, anchors, dependencies, and generated projections.",
      "Kernel and EXPECTED_IDS both contain 108 tasks.",
      "quiet_mac count is 13 and both new quiet_mac rows carry lead_only."
    ],
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "row_id": "CALEXITS-EVIDENCE-BYTES-01",
        "field": "goal; acceptance.evidence[1]",
        "title": "The row retains the temp-path hypothesis that the registered reproduction disproved."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "row_id": "BRACKET-BINDING-CLI-01",
        "field": "fences[1].rule; acceptance lifecycle",
        "title": "The row encodes the impossible post-verdict producer shape superseded by current R-3 prime."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "row_id": "L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01",
        "field": "acceptance.evidence[2]",
        "title": "Acceptance invents a magistrate-waiver path not present in the ruling."
      },
      {
        "id": "B4",
        "severity": "blocker",
        "row_id": "T0-ENV-PARSER-UNIFY-01",
        "field": "acceptance.evidence[1]",
        "title": "Acceptance incorrectly requires both parser boundaries to emit the capture wrapper's reason code."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "row_id": "D-078",
        "field": "registry amendment scope",
        "title": "The amendment broadens the unreadable condition beyond residual R-4's selected-marker branch."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "row_id": "RQ-ATTRIBUTION-DOMINANCE",
        "field": "one-line note",
        "title": "The registry cell is not Variant A column-for-column."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q tests/test_gen_state.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-wave']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "[0-9]+ passed"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "HEAD forked from 8ac78312 while origin/main advanced twice during review to 7945da11; the final two-dot diff includes upstream-only R-3-prime and DIRECTOR-BRIEF changes as deletions.",
      "needs": "Rebase the kernel commit onto current origin/main, apply the findings, and review the resulting diff."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The required pytest command failed before collection because the read-only seat has no writable temporary directory; the named tests themselves use tempfile.",
      "needs": "Rerun the exact pytest command in a writable verification environment."
    },
    {
      "id": "FL3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Live GitHub metadata for PR #217 was not queried because the command allowlist excluded gh; origin/feat/bracket-binding-cli at 94947441 and current upstream ruling bytes were inspected.",
      "needs": "Confirm PR #217 state and head after rebasing."
    }
  ]
}
```

## Findings

**B1 — blocker — `CALEXITS-EVIDENCE-BYTES-01`, `goal` and `acceptance.evidence[1]`.**

- Row: “temp-path bytes leak into the two evidence artifacts” and “The root cause of temp-path bytes reaching evidence is identified and cured.”
- Source: [WAVE-ROWS.md](/Users/edr/code/JouleWise-wt-wave/docs/process_traces/2026-08-27-t26/WAVE-ROWS.md:21) says “root cause is case-selection/ordering nondeterminism, both subtests one defect.” The row’s own [status note](/Users/edr/code/JouleWise-wt-wave/docs/process/state_kernel.json:794) says the temp-path hypothesis is contradicted and “not a temp-path leak.”
- One-line cure: rewrite the goal and second evidence item to require deterministic same-case selection/ordering, treating the `instrument_evidence.json` difference as downstream of `events.jsonl`.

**B2 — blocker — `BRACKET-BINDING-CLI-01`, `fences[1].rule` and lifecycle acceptance.**

- Row: “the CLI re-derives window identity from the whole-window verdict’s `evaluation_basis`.”
- Current source (`origin/main` commit `c8b1b8fe`, R-3′): the evaluator requires the binding as an input; the builder takes “NOTHING from a verdict,” and the order is frozen plan + finalized ledger → build binding → whole-window verdict → finalize.
- One-line cure: rebase and replace the post-verdict rule with R-3′’s exact producer-before-verdict lifecycle and its producer→evaluator→finalizer byte-identity regression.

**B3 — blocker — `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01`, `acceptance.evidence[2]`.**

- Row: “The executed rehearsal record exists before the first spent window, **or the magistrate’s explicit waiver is recorded in its place**.”
- Source: [D-078’s adopted item 4](/Users/edr/code/JouleWise-wt-wave/docs/decision_log.md:9139) says the rehearsal “re-runs the full edge at the same head before any window is spent”; it provides no waiver alternative.
- One-line cure: delete “or the magistrate’s explicit waiver is recorded in its place.”

**B4 — blocker — `T0-ENV-PARSER-UNIFY-01`, `acceptance.evidence[1]`.**

- Row: both boundaries must refuse under `evidence_author_t0_capture_environment_invalid`.
- Source: [S9-08b](/Users/edr/code/JouleWise-wt-wave/docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/SHORTLIST.md:379) requires a shared exact parser plus unknown/missing-key regressions at both boundaries, but does not unify their reason vocabularies. At HEAD, the evidence-author boundary maps parser failures through `_underivable(kind)` to `evidence_author_t0_<kind>_underivable`; only the capture wrapper owns `evidence_author_t0_capture_environment_invalid`.
- One-line cure: say each boundary must preserve and assert its existing registered boundary-specific refusal mapping.

**S1 — should-fix — `D-078`, registry-amendment scope.**

- Row: “the selected prospective manifest **(or its marker)** exists but cannot be read.”
- Source: [residuals.md R-4](/Users/edr/code/JouleWise-wt-wave/docs/process_traces/2026-08-27-t26/s11-collector-manifest-id/residuals.md:80) supports only “An `OSError` reading a selected marker.”
- One-line cure: replace “selected prospective manifest (or its marker)” with “selected marker.”

**S2 — should-fix — `RQ-ATTRIBUTION-DOMINANCE`, `one-line note`.**

- Row: inserts a registration-date/promotion-rule parenthetical and a draft link.
- Source: [Variant A](/Users/edr/code/JouleWise-wt-wave/docs/paper/RQ-ATTRIBUTION-DOMINANCE-registry-row-draft.md:47) contains neither addition; all other columns match.
- One-line cure: replace the note cell with Variant A’s exact note text.

## Residual risk

The required pytest suite remains unexecuted because collection needs writable temporary storage. Also, the branch must be rebased before another final-head review: current `origin/main` contains the authoritative R-3′ correction absent from this head.