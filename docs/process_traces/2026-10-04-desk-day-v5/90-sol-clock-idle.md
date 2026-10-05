```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend idle 75 s, zero retry backoff, a measured-rate stream budget, and narrowly limited admission recovery; drift-aware T-0 admission detects large resyncs but weakens small-step detection.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "599bc4ae09a8b287807df3f75e840031c2958a22",
    "head_end": "599bc4ae09a8b287807df3f75e840031c2958a22",
    "upstream_end": "599bc4ae09a8b287807df3f75e840031c2958a22",
    "branch": "design/2026-10-04-v5-qualification-block"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Register combined clock and admission remedy", "action": "needs_ruling"},
      {"row": "Qualification capture", "action": "wait_for"},
      {"row": "Blanket whole-pack recovery after science", "action": "do_not_start"}
    ]
  },
  "verification": [{
    "id": "V1",
    "kind": "inspection",
    "cmd": "git status --short --branch",
    "cwd": ".",
    "observed": {
      "result": "pass",
      "exit_code": 0,
      "tail": ["## design/2026-10-04-v5-qualification-block...origin/design/2026-10-04-v5-qualification-block"]
    },
    "expected": {"exit_code": 0, "tail_regex": "^## design/2026-10-04-v5-qualification-block"}
  }],
  "flags": [{
    "id": "F1",
    "kind": "lead_ruling",
    "level": "blocking",
    "text": "Recommendations require prospective registration changes before qualification.",
    "needs": "Adjudicate values and recovery eligibility, then implement and verify at the measurement head."
  }, {
    "id": "F2",
    "kind": "verification_gap",
    "level": "nonblocking",
    "text": "Read-only source inspection and arithmetic only; the named G10 helper is absent from this checkout.",
    "needs": "Verify G10 implementation at the final measurement head."
  }]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Idle **75 s**, retry backoff **0 s** | needs_ruling | Regeneration and re-pinning | All science, bound and reference configs |
| T-0 **5 ms + 12.5 ppm × actual RAW span** | needs_ruling | Consistent author, ARM, G4 and G10 changes | Clock-attestation semantics |
| Post-G10/R0 frequency gate and per-stream sizing | needs_ruling | Length-matched replay and duration bounds | Member and bracket clock budgets |
| One admission-only fresh `s1`, before any science energy window starts | needs_ruling | Explicit prospective recovery clause | Existing no-rerun doctrine |
| Qualification capture | wait_for | Above changes, final verification, agent stand-down | Dedicated measurement Mac |

## Critical path

**1. My recommendation is (a)+(b), idle 75 s, and a restricted (e), for this qualification night.** Keep the pinned estimator unchanged.

Use these **proposed design thresholds**: after G10’s OFF and at every R0, require **|f| ≤ 3.50 ppm**; size with **ρ = |f| + 0.25 ppm**. Require, for each continuous stream,

`H_length + stamp_resolution + numeric_padding + ρ·T_stream ≤ 4.90 ms`.

With **H ≤ 3.60 ms**, **0.10 ms reserved for resolution, padding and design slack**, and **T_stream ≤ 320 s**, this gives exactly **4.90 ms** at the frequency gate. The 320 s envelope is a proposal grounded in record 44’s largest 619 s member envelope minus its separate 300 s cooldown; it must be verified after regeneration, including retry and guards. Longer streams require a tighter frequency gate. ([Record 44:40–47](/Users/edr/code/JouleWise-wt-dd5-block4/docs/process_traces/2026-10-04-desk-day-v5/44-block4-sizing.md:40))

This protects two different errors: **H** bounds initial trace placement, while **ρT** bounds accumulated displacement between elapsed sample support and wall-clock measurement boundaries. Both belong in the energy uncertainty; neither replaces the other. ([uncertainty_evidence.py:911–924](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/uncertainty_evidence.py:911))

Choose **75 s** because it has whole-stream precedent; 55 s rests on a tighter, less reliable compromise. Preserve the hard **60 s native baseline** requirement and actual **5 ms effective-bound** admission. Neither 75 s nor a frequency reading guarantees bounded placement. The prefix replay’s occasional failures around 90 s reinforce that limitation. ([registration:143–149](/Users/edr/code/JouleWise-wt-dd5-block4/configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:143), [estimator:1065–1075](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/uncertainty_evidence.py:1065), [MEMO:364](/Users/edr/night-archive/ia-0a40/MEMO.md:364))

Keep admission thresholds unchanged: they exclude unrelated CPU/GPU activity that contaminates the idle baseline and can accompany inference. Backoff improves recovery opportunity; it does not establish quietness. ([controller.py:1210–1243](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/controller.py:1210))

**2. A drift-aware T-0 bound is sound as a coarse resync detector, with an explicit loss of sensitivity.** Register **12.5 ppm**, rather than approximately 12: the memo reports a **12.29 ppm** draw. At 3600 s, the raw-delta ceiling becomes **50 ms**. With drift of either sign bounded by that cap, only a single step **greater than 95 ms** is guaranteed to trigger despite cancellation. Thus it catches the reported >0.5 s resync, but cannot retain the claim “every >5 ms step is detected.” Endpoint checks also cannot exclude cancelling steps. ([MEMO:81–95](/Users/edr/night-archive/ia-0a40/MEMO.md:81))

G10 must demonstrate violation of the **new span-dependent author ceiling** and the exact author refusal. Merely observing >5 ms movement no longer suffices. ARM and G4 replay must change alongside the author and helper: both independently enforce the current 5 ms ceiling. ([arm_readiness.py:6852–6857](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/arm_readiness.py:6852), [t0_rehearsal.py:640–648](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/t0_rehearsal.py:640))

**3. Prefer restricted (e) now; implement new-stream retry for the claim campaign.** Allow one fresh whole-roster `s1` only for authenticated idle-admission failure **before any science energy window starts**, with fresh authorization/T-0 and preserved failed evidence. An abort after earlier science cannot receive that blanket allowance under the current no-rerun rule. ([registration:257–275](/Users/edr/code/JouleWise-wt-dd5-block4/configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:257))

New-stream retry is worthwhile if recovery must cover **every member**. It touches sampler lifecycle, custody and retry-artifact promotion, beyond adding a sleep. Then **300 s outside both streams** is reasonable, while admission still decides whether the burst ended. ([powermetrics.py:188–200](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/adapters/powermetrics.py:188), [452–458](/Users/edr/code/JouleWise-wt-dd5-block4/joulewise/adapters/powermetrics.py:452))

**4. The pre-mortem overstates precision.** Its **0.46** is a sparse-data model result, not a calibrated night-failure probability; correlated daemon bursts undermine independent-member reasoning. It correctly acknowledges that 300 s backoff never fired live. Likewise, all replay prefixes bounded at ≥130 s establishes a useful design observation, not a universal minimum. ([MEMO:289–292](/Users/edr/night-archive/ia-0a40/MEMO.md:289), [364](/Users/edr/night-archive/ia-0a40/MEMO.md:364))