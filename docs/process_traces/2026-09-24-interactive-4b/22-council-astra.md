```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Continuation is useful with narrower claims and preserved attribution safeguards.",
  "workspace":{"base_requested":"main","base_mode":"exact","head_start":"40708669fa203756d510abbe379e90e11c5c5196","head_end":"40708669fa203756d510abbe379e90e11c5c5196","upstream_end":"40708669fa203756d510abbe379e90e11c5c5196","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"should_fix"},{"id":"F3","severity":"should_fix"}]},
  "verification":[{"id":"V1","kind":"inspection","cmd":"git status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},"expected":{"exit_code":0,"tail_regex":"^## HEAD \\(no branch\\)$"}}],
  "flags":[{"id":"F1","kind":"lead_ruling","level":"blocking","text":"Scatter cannot replace attribution uncertainty.","needs":"Adjudicate C3 before continuation."}]
}
```

## Findings

**F1 — Modify C3.** Repeatability does not bound stable, arm-correlated bias. Comparing a worst-case bound with realized scatter does not establish that the bound is wrong. Exact proposed text:

> Report drift ratios and nominal and widened intervals. Nominal equivalence requires both 99.375% paired-log intervals inside [log(0.97), log(1.03)]. Record stability as each arm’s sample SD(E)/mean(E) ≤1% and every cell’s idle-baseline mean ≤1 W; these are descriptive checks, not attribution bounds. EQUIVALENT additionally requires the energy interval widened by anchor, drift and edge bounds without √n shrinkage inside the same margins. Otherwise report nominal agreement, INCONCLUSIVE-by-attribution.

Preserve the original C3 result and disclose that this amendment followed observed data.

**F2 — Scope F-A.** Say: “In session 2, the tested default-launchd configuration failed closed on all three D attempts at the 55-second idle-baseline timeout.” This establishes operational non-viability **under that configuration**, not universal inability to measure under D. Q1’s numerical bias remains unestimated, not scientifically moot. No raised-timeout witness is needed to reject unchanged D operationally; such a run would be a separate diagnostic. Interactive is a supported candidate requiring the gated PR/council, not yet a proven universal cure. September causation remains a hypothesis.

**F3 — Continue with a fresh registration.** Six new pairs, three I→SH and three SH→I in frozen randomized order, one run per cell, are reasonable. Preserve validity/retry rules; exclude stage 0 and stopped-U1 observations. Freeze stopping and any second look. Estimated E power is 0.806 at 1.5× estimated SD but only 0.445 at 2×: accept inconclusiveness.

Keep B×2 as a descriptive throttling control, outside paired inference; missing/failed probes require investigation, not claims of small-effect sensitivity. Include warm-up/control time beyond ≈46 minutes.

Before capture, resolve the existing ≤130 ms cadence requirement: observed I cadence reaches 132 ms. Do not silently drop it. SH validates a contemporary shell comparison, not July equivalence.

## Residual risk

One evening cannot establish cross-night transportability. Before reporting to Ed, archive the council disposition, registration, failed-attempt evidence and restoration records; drain all agents before measurement. No writes, tests or measurements performed.

**PROCEED WITH CHANGES: narrow F-A; amend C3 as above; freeze continuation and resolve cadence criterion.**