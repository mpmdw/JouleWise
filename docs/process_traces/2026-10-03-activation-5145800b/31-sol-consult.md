```json
{
  "schema": "claude-codex-report/v1",
  "genre": "triage",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a newly sealed block after maintenance clears, with a delayed existing admission retry; block 2 is closed.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "28b785803c857ffb6ca894f41c4df2ac8f2b5c8f",
    "head_end": "28b785803c857ffb6ca894f41c4df2ac8f2b5c8f",
    "upstream_end": "28b785803c857ffb6ca894f41c4df2ac8f2b5c8f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "regions": [
      {"region": "block-2 evidence", "disposition": "preserve"},
      {"region": "next registration", "disposition": "ruling"},
      {"region": "admission retry", "disposition": "compose"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "This completed consult recommends prospective changes; it authorizes no measurement window.",
      "needs": "Orchestrator ruling, then cold registration seal."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Maintenance attribution is probable; a bounded delay cannot guarantee maintenance has finished.",
      "needs": "Retain unchanged admission thresholds and terminal abort."
    }
  ]
}
```

## Decision matrix

**Recommend option (a): a newly sealed block 3, retaining the complete sweep and adding a delay to the existing admission retry.** This answers the prefill-length question without interpreting partial results. Block 2 remains closed: registration §7 explicitly sends the second RECOVER to consultation and ruling, rather than another arm (`configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md:203`).

| Region | disposition | evidence | exact action |
|---|---|---|---|
| New block 3 | ruling | Registration §§7, 11–12 | Authorize prospectively after cause treatment. Cold-seal operating state, retry timing, window budget, unchanged validity/selection, fresh identities, no pooling, and an explicit cumulative stop/escalation rule. One window ≈5.5 h; allowing one recovery reserves ≈11 h. |
| Immediate `_v5` at 4096 | ruling | D-166 ratification A2/A4 (`docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md:29`, `:53`) | **Not automatically permitted.** “No rung clears” follows an evaluable sweep; incomplete evidence does not establish that condition. A cold amendment must authorize bypassing selection, fix 4096 prospectively, replace the selection-hash contract, and specify honest reporting. Saves 1–2 diagnostic windows; claim-bearing collection retains its separate gates. |
| Select/top up from w2 | preserve | Registration §§7–8 | Reject: no SELECT window, no pooling or in-window recollection. Zero extra windows buys no authorized answer. |

**Cause ruling: both transient machine state and a retry-design limitation.** The recorded maintenance launch immediately before r03 supports a removable disturbance, with probable rather than proven process attribution (`docs/process_traces/2026-10-03-activation-5bffbeaf/00-session-record.md:45`). Re-arming after it finishes removes the present disturbance; re-arming alone does not prevent recurrence.

The controller proceeds from a rejected first admission attempt through an environment observation directly into attempt 2, with no explicit waiting interval (`joulewise/controller.py:1107`, `:1123`). That is inadequate temporal separation for a multi-minute disturbance, though the rejection itself correctly protects quietness.

## Composition recipe

1. **Apply Ed’s setting-first rule before coding.** Establish whether one reversible setting/command demonstrably suppresses **both** named activities throughout the window. These records establish none; do not assume stopping Photos alone handles duet maintenance. A pre-window “not due” check is insufficient protection against later scheduling: the existing check observes current daemon CPU and load (`scripts/prewindow_check.sh:85`, `:96`).

2. **Absent a demonstrated suppression, delay the existing retry.** Propose one fixed **300 s** pause after CPU-busy-only rejection, before the fresh environment guard and second full admission attempt (`joulewise/controller.py:1110`). Preserve both attempts and abort on the second rejection (`joulewise/controller.py:1142`). Add a validated, default-zero delay field at `joulewise/schemas.py:468`, enabled only by block 3’s pinned diagnostic policy. Preserve the existing CPU threshold, sample minimum and abort action (`configs/campaign_policies/quiet_mac_p2_production.json:24`, `:34`). The 300 s value is prospective judgment, not an inferred maintenance duration.

3. **Seal timing explicitly.** Keep the ≈5.5 h ceiling and let waiting consume existing allowance, with expiry still RECOVER; disclose that repeated waits may exhaust it. Review the sizing allowances at `scripts/gen_g2_phase_d.py:28`. If the gate instead enlarges the ceiling, report that additional cost before arming.

4. Verify delayed retry, unchanged rejection, retained evidence and deadline behavior with focused tests; then the canonical suite. This consult ran inspections only.

**Keep `--max-failures 1`.** Once a small member finally fails, the exact-five roster cannot satisfy SELECT. Continuing cannot repair that window. The runner breaks at its failure limit and returns nonzero for failures (`scripts/run_campaign.py:8886`, `:8949`).

Distinguish **admission retry within one member** from restarting a failed member. The former already exists and policy requires exactly one fully evidenced retry (`joulewise/schemas.py:483`). A truly pre-capture wait does not re-collect anything. But r03 was **before prefill, not before all capture**: idle admission persists raw telemetry (`joulewise/adapters/powermetrics.py:273`, `:297`). Relaunching that failed member under block 2 would conflict with §7; delaying its existing internal attempt prospectively should be explicitly sealed.

## Rulings

**F1:** Orchestrator must choose the prospective route; no existing seal authorizes it.

**F2:** No demonstrated systematic, non-removable cause. The matching re-harvest reports 12 valid/bounded members and 12 not recorded. Missing anchors are not defective anchors. w1 was a corrected attachment defect, not clock evidence (`docs/process_traces/2026-10-03-activation-adaebcc6/00-session-record.md:63`). Maintenance may outlast 300 s; the retained abort handles that uncertainty.