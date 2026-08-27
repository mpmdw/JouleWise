# D-156 residual queue-row drafts

These objects are **DRAFTS awaiting magistrate registration**. They are not
live queue rows, do not amend `docs/process/state_kernel.json`, and confer no
implementation authority. The proposed ranks, priorities, and wording remain
subject to the magistrate's registration pass.

## Q1-B — predecessor-bound chained recovery

Proposed priority and lane: `p2_next_slice`, `agent` — the ruled fresh-root or
non-claim disposition is safe now, while a same-root recovery schema is a
bounded code-and-contract design rather than a live-hardware task.

```json
{
  "acceptance": {
    "evidence": [
      "A ruling defines a predecessor-bound successor record that hash-binds the exact prior supersession row and gives both consumers one deterministic chain truth table",
      "Real-recorder regressions cover an already-selected occurrence failing again in one window, a valid successor chain, a fork, a missing predecessor, and a corrupted predecessor",
      "Both whole-window membership and the cooldown join select or refuse identically for every ruled chain shape",
      "The design records strict-subset latest-wins as rejected because whole_window_verdict_conflict forbids choosing a later disposition over a preserved conflict"
    ],
    "pointer": {
      "json_pointer": "/tasks/SUPERSESSION-CHAINED-RECOVERY-01/acceptance",
      "label": "SUPERSESSION-CHAINED-RECOVERY-01 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "A separately ruled predecessor-bound successor record permits sound same-root recovery after an already-selected occurrence later fails."
  },
  "authority": {
    "label": "D-156 Q1-B chained-supersession residual",
    "path": "docs/decision_log.md"
  },
  "dependencies": [],
  "fallback": null,
  "fences": [
    {
      "authority": {
        "label": "whole_window_verdict_conflict operator rule",
        "path": "docs/phase_2/window_runbook.md"
      },
      "rule": "Do not widen the cooldown join to ignore strict-subset rows because that is rejected latest-wins conflict laundering"
    },
    {
      "authority": {
        "label": "D-156 current disposition",
        "path": "docs/decision_log.md"
      },
      "rule": "Until a successor schema is separately ruled and landed, use a fresh runs root or retain the member as non-claim evidence"
    }
  ],
  "flags": [],
  "goal": "Rule and implement a predecessor-bound chained-supersession schema for the operational forcing case where an already-selected occurrence later fails: the runbook prescribes rerun-and-record-supersession for anchor_fallback_member_unusable and incomplete_existing, so a member failing twice in one window is not exotic; preserve the rejected cheap alternative on record because widening the cooldown join to ignore strict-subset rows is latest-wins, forbidden by whole_window_verdict_conflict.",
  "id": "SUPERSESSION-CHAINED-RECOVERY-01",
  "lane": "agent",
  "priority": "p2_next_slice",
  "rank": 20,
  "status": "queued",
  "status_note": "Drafted from D-156 Q1-B; ruling-first because the record schema and two-consumer chain semantics are not yet owned by a contract.",
  "stop_card": null
}
```

## Q4-B — cross-consumer divergence cure

Proposed priority and lane: `p1_phase_gate`, `agent` — identical legacy bytes
producing selection in one consumer and refusal in another is a soundness
boundary that should precede future claim consumption, but needs no hardware.

```json
{
  "acceptance": {
    "evidence": [
      "Before any cure, a regression constructs a legacy or hand-edited log with an older still-valid supersession and a later third-occurrence supersession and exhibits whole-window selection versus cooldown refusal on identical bytes",
      "That pre-cure regression also proves the D-093 totals audit reports clean for two valid same-bundle rows, preserving the per-bundle blindness as an explicit should-fix",
      "A ruling chooses the shared fail-closed disposition and defines how both consumers handle every multiple-row same-bundle shape",
      "After the cure, all three consumer call sites — whole-window membership, the cooldown join, and the membership-binding path at joulewise/whole_window.py:4700-4714 — return the same ruled disposition on the unchanged divergence fixture"
    ],
    "pointer": {
      "json_pointer": "/tasks/SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01/acceptance",
      "label": "SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "Legacy or hand-edited supersession logs cannot make whole-window membership select while the cooldown join refuses on the same bytes."
  },
  "authority": {
    "label": "D-156 Q4-B cross-consumer divergence residual",
    "path": "docs/decision_log.md"
  },
  "dependencies": [],
  "fallback": null,
  "fences": [
    {
      "authority": {
        "label": "D-156 no-consumer-change ruling for the write-time guard",
        "path": "docs/decision_log.md"
      },
      "rule": "Do not fold this consumer-contract cure into the supersession write-time-refusal change"
    },
    {
      "authority": {
        "label": "D-156 historical-byte disposition",
        "path": "docs/decision_log.md"
      },
      "rule": "Preserve legacy and hand-edited log bytes; the cure may not rewrite or delete historical supersession rows"
    }
  ],
  "flags": [],
  "goal": "Rule and cure the legacy cross-consumer divergence: for a log not written by the guarded recorder, a later third occurrence leaves the older supersession valid, so the cooldown join at joulewise/analysis_engine/inputs.py:2337-2368 refuses while whole-window membership through scripts/run_campaign.py:4766-4782 selects on identical bytes; a THIRD consumer on the membership-binding path, joulewise/whole_window.py:4609 (_supersession_is_logged) and :4700-4714, carries the same exactly-one-match shape and must be included in the ruled truth table.",
  "id": "SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01",
  "lane": "agent",
  "priority": "p1_phase_gate",
  "rank": 17,
  "status": "queued",
  "status_note": "Drafted from D-156 Q4-B; acceptance requires the divergence to be exhibited before any cure so agreement cannot be asserted tautologically.",
  "stop_card": null
}
```
