```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: callee keyword conflict, missing replay plan locator, and missing delegated baseline anchor; no files changed.",
  "workspace": {
    "base_requested": "main + seat-1 contract",
    "base_mode": "descendant",
    "head_start": "7b9d4a7b2ecc39c60c6e61b583c8e0ab434a7bd5",
    "head_end": "7b9d4a7b2ecc39c60c6e61b583c8e0ab434a7bd5",
    "upstream_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "branch": "feat/2026-09-08-d176-seat3-consumer"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor main HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The brief names night_plan, go_receipt and the confirmation pair as FOUR required callee keywords. Contract section 3 instead names night_plan, go_receipt, authenticated_go_receipt and go_receipt_sha256.",
      "needs": "Rule whether all six keywords must use the missing sentinel; recommended to preserve both the contract's CLI-to-callee authentication and mandatory confirmation transport."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Replay must re-read the pinned night plan and persisted attempt, but neither the exact 26-key GO nor the exact 22-key consumption schema retains its path. verify_consumed_launch has no night_plan argument.",
      "needs": "Specify the durable authenticated plan locator for replay and child execution, and authorize any necessary wire amendment."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Bridge protocol sections 1 and 7 require prompt-supplied BASE_HEAD, BASELINE_MANIFEST and BASELINE_DIGEST before delegated writes; these anchors were not supplied.",
      "needs": "Supply the runner-owned baseline anchors or explicitly rule that this runner replaces that baseline procedure."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Acceptance suites were not run because this is a pre-write NEEDS_RULING return.",
      "needs": "Run the requested rc-gated acceptance after implementation."
    }
  ]
}
```

## Change

No writes or commits. Read the full contract and inspected the consumer, replay, child, and installer routes.

Three rulings are needed:

1. **Keyword interface:** Recommend six sentinel-required inputs: the contract’s four GO/plan keywords plus the existing confirmation pair.
2. **Replay plan locator:** Options are a persisted locator, a ruled custody-relative location, or an explicit replay argument propagated through every caller. Recommend a persisted locator so child and historical replay remain self-contained; the lead must select its wire location.
3. **Baseline authority:** Supply the baseline anchors or expressly supersede that procedure for this runner. This blocks even independent registration edits under [bridge protocol §7](/Users/edr/code/JouleWise-wt-d176-seat3/docs/contracts/bridge_protocol.md).

## Verification notes

All seat-3 §9 production/test pins remain **NOT PINNED**: B1–B5, S1, S3–S6, N1/N2, and the applicable §10.1 clauses. No refusal regression or implementation acceptance is claimed.

Resume with the three rulings; then registration, implementation, clause-map pins, and logged acceptance can proceed.