```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"V2 improves the experiment but leaves invalid decision rules, overstated historical comparability, and incomplete uncertainty propagation.",
  "workspace":{
    "base_requested":"eec7acaa",
    "base_mode":"exact",
    "head_start":"eec7acaa4ee3018bd5f7118aa03ba7868e8c779b",
    "head_end":"eec7acaa4ee3018bd5f7118aa03ba7868e8c779b",
    "upstream_end":"eec7acaa4ee3018bd5f7118aa03ba7868e8c779b",
    "branch":null
  },
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "decision":"RUN AFTER LISTED FIXES",
    "findings":[
      {"id":"N1","severity":"blocker","title":"Decision procedure lacks valid sequential error control"},
      {"id":"N2","severity":"blocker","title":"Margin definition and energy uncertainty remain incomplete"},
      {"id":"N3","severity":"should_fix","title":"SH cannot establish historical equivalence"},
      {"id":"N4","severity":"should_fix","title":"Execution and mechanism controls need explicit completion"}
    ]
  },
  "verification":[{
    "id":"V1",
    "kind":"inspection",
    "cmd":"git status --short --branch; git rev-parse HEAD; git rev-parse origin/main",
    "cwd":".",
    "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","eec7acaa4ee3018bd5f7118aa03ba7868e8c779b","eec7acaa4ee3018bd5f7118aa03ba7868e8c779b"]},
    "expected":{"exit_code":0,"tail_regex":"eec7acaa4ee3018bd5f7118aa03ba7868e8c779b"}
  }],
  "flags":[]
}
```

## Findings

**Original findings:**

- **F1 — PARTIAL:** paired contrasts improve matters; sequential testing, margins, and power remain unresolved.
- **F2 — PARTIAL:** causal daemon claims removed; SH provenance and continuous state verification remain inadequate.
- **F3 — PARTIAL:** production anchoring is correct; uncertainty must enter decisions.
- **F4 — PARTIAL:** better telemetry; `%cpu` is a decaying average, not interval CPU consumption; mechanism claims remain overstated.
- **F5 — PARTIAL:** sampler CPU recorded; production launch-chain fidelity and attribution controls remain incomplete.
- **F6 — PARTIAL:** longer probes and bounded B are good; runtime, cache reset, synchronization, and token-failure rules remain unspecified.
- **F7 — PARTIAL:** staging and installation authority corrected; offline validation and sizing remain outstanding.

**N1 — Sequential statistics.** Paired log-ratios are reasonable for positive endpoints and independent blocks. Six-order balance is feasible at both looks. However, 0.0294 is a calibrated nominal boundary, not an additive α split; ordinary 95% Holm intervals and 90% TOST intervals do not implement it. Small-sample studentization and multiplicity require explicit calibration. [Sequential-design documentation](https://www.rpact.org/vignettes/planning/rpact_boundary_examples/).

A conservative, exact replacement:

> “Use all six D/I/SH permutations once per six-block stage, in seeded randomized order. At both looks use 99.375% paired-t intervals, Bonferroni-adjusted over four contrasts and two looks. DIFFERENT requires the entire interval beyond a materiality boundary; EQUIVALENT requires it entirely inside both boundaries; otherwise INCONCLUSIVE.”

The pilot’s 2–5% **ranges are not paired SDs**. If paired SD were 2–5%, even unadjusted 90% half-widths at n=6 would be 1.65–4.11%; adjusted widths above are 3.70–9.24%. Six can establish equivalence only with sufficiently smaller paired variability. At n=12, adjusted widths remain 1.95–4.86%.

Add:

> “Before capture, report power and 80%-power MDE for the actual stopping/materiality rules across plausible paired SDs; include equivalence power. Outcome-derived MDE is descriptive, not evidence that the design was adequately powered.”

**N2 — Margins and energy.** `min()` tightens conservatively, but does not resolve an outcome-dependent denominator, gross/net mismatch, energy-dependent rate margin, or percent/log conversion.

Replace with:

> “Freeze an independent positive net-decode reference E₀ before confirmation: δE=min(0.03,5 J/E₀), δR=0.03; log bounds are log(1−δ), log(1+δ). Nonpositive net energy invalidates log analysis. Preserve production eligibility gates and propagate anchor, phase-boundary, idle-baseline and drift uncertainty into decision intervals. Validate reduction offline before capture.”

Counter/integral agreement checks arithmetic; shared anchoring can make both agree while both misattribute boundary energy. Guard bands do not isolate the prefill/decode boundary.

**N3 — SH reference.** Scout 03 establishes only inferred non-launchd provenance, with unknown parent mode/QoS and a different OS build.

Replace historical reproduction claims with:

> “SH is a contemporary shell reference, not a validated July/August reconstruction. Record ancestry, environment, assertions and effective policy; equivalence supports this tested configuration only.”

**N4 — Remaining controls.** Add:

> “Preserve the production driver→zsh→Python chain. Verify display/HID state throughout cells; preregister interruption handling and settling. Record cumulative CPU deltas; label unmeasured mechanisms unknown. Pin runtime/tokenization/cache reset, synchronize completion, and reject token/output mismatches. Timer coalescing and E/P placement remain hypotheses.”

**§7 calls:** secondary display testing and conditional sampler-off follow-up are reasonable for an end-to-end effect. A single sandwich remains exploratory. The variance-pilot ruling is wrong: α control does not provide power. “Both blocker sets adopted” overstates completion.

**Verdict: RUN AFTER LISTED FIXES.**

## Residual risk

Read-only review; no hardware validation. Fable’s tracked review contains only a verdict, limiting independent assessment of its full reasoning.