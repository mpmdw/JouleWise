```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Four prospective calibration-night draft files are written; two ruled-text ambiguities need a ruling before the registration can be sealed.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "e77b56500b9825c58092cbddf04e457ebe0d1ee7",
    "head_end": "e77b56500b9825c58092cbddf04e457ebe0d1ee7",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-calnight"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/01-registration-draft.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/02-km003c-logger-design.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/03-desk-smoke-plan.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/04-open-questions.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import ast,re; d=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft\"); f=sorted(d.glob(\"*.md\")); assert len(f)==4; s=(d/\"03-desk-smoke-plan.md\").read_text(); ast.parse(re.search(\"python3 - <<.PY. >> .*?\\\\n(.*?)\\\\nPY\",s,re.S).group(1)); print(\"PASS four files; smoke Python parses\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS four files; smoke Python parses"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS four files; smoke Python parses"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; d=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft\"); pat=re.compile(r\"((?:/Users/edr/[^\\s`(),;]+|(?:configs|joulewise|scripts|docs)/[^\\s`(),;]+?)):(\\d+)(?:-(\\d+))?\"); refs=[(p,int(b or a)) for f in d.glob(\"*.md\") for p,a,b in pat.findall(f.read_text())]; assert len(refs)>=10; assert all(Path(p).is_file() and len(Path(p).read_text(errors=\"replace\").splitlines())>=n for p,n in refs); print(\"PASS\",len(refs),\"file:line citations\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS 20 file:line citations"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS 20 file:line citations"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## docs/2026-09-24-278ebc9e-calnight",
          "?? docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\?\\? docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: R-Q2's adjacent idle brackets cannot literally surround prefill and decode separately while preserving their continuous KV state.",
      "needs": "Rule whether both phases share the rung's idle bookends."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the ruled bytes-law equation is inconsistent at its 512-token baseline for nonzero κ.",
      "needs": "Rule whether to omit L=512 from the fit or amend the normalization."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The model-loading desk smoke and census dry-check were specified but not run in this drafting seat.",
      "needs": "Run them before sealing, under their stated gates."
    }
  ]
}
```

## Change

Files drafted:

- [01-registration-draft.md](/Users/edr/code/wt-278ebc9e-calnight/docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/01-registration-draft.md)
- [02-km003c-logger-design.md](/Users/edr/code/wt-278ebc9e-calnight/docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/02-km003c-logger-design.md)
- [03-desk-smoke-plan.md](/Users/edr/code/wt-278ebc9e-calnight/docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/03-desk-smoke-plan.md)
- [04-open-questions.md](/Users/edr/code/wt-278ebc9e-calnight/docs/process_traces/2026-09-24-activation-278ebc9e/50-calnight-registration-draft/04-open-questions.md)

Ten-line summary:

1. The draft places calibration night after issued 25G83/v4 acceptance and G2-a.
2. It registers twelve alternating 600 s envelopes with six replicates per model.
3. It specifies seeded rung order, pinned prompts, forced decode and idle brackets.
4. Its timing table reserves 300 s for rung computation, subject to desk measurements.
5. It follows the ruled rung-drop order if that budget fails.
6. It defines rail and KM003C segment measurements, alignment and boundary labels.
7. It proposes a ±0.10 W stopwatch-equivalence band and ±100 mA battery screen.
8. It specifies segment-level claims, the shared-κ diagnostic and held-out prediction.
9. The logger design preserves a whole-window, SHA-256-pinned passive log.
10. The smoke and census checks are specified for later execution; nothing was armed or committed.

## Verification notes

All 20 detected file:line references resolve. Git status shows only the authorized directory. The smoke was not run, as instructed. The cold gate needs to resolve the two **NEEDS_RULING** items before this can become a sealed registration.

## Open questions — verbatim from the draft

1. **Registration seed and repeated-night parity.** Options: (a) fixed `27840700`, SHA-256 sort per envelope, parity flips on future night ordinal; (b) a different committed seed/PRNG. **Recommend (a)** and publish all twelve orders in the seal. The council fixes seeded order and cross-night counterbalancing, not the seed or generator.
2. **Prompt content and exact token IDs.** Options: (a) one deterministic pinned token-ID prefix sliced at each L, with an 8192-token copy for sustained prefill; (b) separately rendered, pinned prompts at each L. **Recommend (a)** for controlled position and byte-identical prefixes, with thinking-off template identity checked before seal.
3. **What counts as a 600 s envelope and outer window.** Options: (a) 600 s including load, idle and compute, with reader overhead calibration in a separate setup allowance; (b) put overhead inside each 600 s. **Recommend (a)**, freeze pitch/settle/closing allowance and demonstrate the chain fits before arm.
4. **Feasibility and rung dropping.** Options: (a) three-repetition worst observed per-model desk upper times and a ≥30 s margin, then drop 16384 before 32768 if necessary; (b) a different prospective upper-time statistic/margin. **Recommend (a)**. Freeze one common rung set for all twelve envelopes after smoke.
5. **Idle brackets for prefill versus decode — NEEDS_RULING.** Options: (a) share the ≥30 s rung bookends as the adjacent idle baseline for both phases, keeping continuous prefill→decode and marking the shared baseline; (b) add an idle between phases, which may invalidate KV continuity; (c) define B1 only for the composite rung and leave phase contrast unavailable. **Recommend (a)**, provided the gate accepts “adjacent” to mean the rung's adjacent idles. R-Q2's required `ρ(decode)−ρ(prefill)` rules out (c) without a new ruling. This is the one semantic gap the drafting seat cannot close by assertion.
6. **Rail/meter integration and missing frames.** Options: (a) common host marker windows, native-frame overlap integration, time-weighted meter receipts and fixed 2 s end trim, refusing missing support; (b) resample both series to fixed bins. **Recommend (a)** and pin exact gap/clock-jump cutoffs before seal. Never optimize lag against the observed workload.
7. **Battery flow.** Options: (a) exclude if any 2 s `ioreg` `InstantAmperage` sample is outside ±100 mA across segment plus adjacent idles; (b) a wider threshold or model-based correction. **Recommend (a), PROPOSED**, subject to a desk confirmation that the field exists and sign/units are as assumed. No sudo or post-hoc correction.
8. **Thermal pressure.** Options: (a) log raw `pmset -g therm` every 5 s and rely on existing night refusals, reporting pressure by segment; (b) add a new pressure exclusion threshold. **Recommend (a)** unless the cold gate identifies a physical threshold prospectively; no filtering after looking at energy.
9. **Reader-overhead segments.** Options: (a) OFF–ON–ON–OFF, four 30 s idle segments before the calibration envelopes, reader then ON throughout; (b) different balanced order/duration. **Recommend (a)** for the calibration night, with setup allowance; for the G2-a rider R-ORDER explicitly permits passive whole-window logging only, so no on/off segments there.
10. **KM003C transport and log failure.** Options: (a) archived bulk `GetData(ADC)` at target 0.5 s, host receipt stamps, immutable import; reader errors are diagnostic for G2-a and render B1/calibration claim unavailable without changing driver refusals; (b) HID reader or a stricter night-level refusal. **Recommend (a)** after dry-check. Do not change G2-a registered refusal semantics.
11. **Vendor accuracy and boundary disclosure.** Options: (a) pin the official [POWER-Z support page](https://www.power-z.com/blogs/technical-support/power-z-km003c-km002c-technical-support) and its linked user manual, resolve which of the manual's gain-error columns applies to this hardware revision, and cite it beside the exact DC-after-charger boundary label; (b) report no numeric calibration claim if that mapping cannot be resolved. **Recommend (a)**; the archived protocol probe itself supplies no accuracy specification.
12. **Bytes-law κ fit — NEEDS_RULING.** The ruled `J/token(L)/J/token(512)=1+κ·KV(L)/W` is inconsistent at L=512 for any nonzero κ. Options: (a) fit the ruled form only for L>512 and retain L=512 as normalization; (b) amend RHS to `1+κ·[KV(L)−KV(512)]/W`. **Recommend (a)** as the narrowest clarification, then use unweighted envelope-level least squares with one shared κ across models and report per-model/rung residuals; lock byte convention and exact weight byte counts before seal. The drafting seat does not adopt this recommendation without the ruling.
13. **“Stopwatch-equivalent” test.** Options: (a) **PROPOSED ±0.10 W** on paired rung-minus-512 decode mean-power differences, with 95% t intervals wholly inside the band separately for both instruments and models; (b) a different numeric band justified by measured ≤5 J/512 segment scale. **Recommend (a)** only if desk smoke proves every decode ≤50 s; otherwise return to cold gate before registration.
14. **Held-out predictor and missing replicates.** Options: (a) six folds each holding out one envelope of each model, training only on the other ten and reporting MAE/bias per model, with missing cells reported but never imputed; (b) separate night-level holdout, which this one night cannot supply. **Recommend (a)** and state that it estimates within-night prediction error only.
15. **Exact battery and meter coverage refusal.** Options: (a) any unavailable current field, raw meter digest mismatch, unsupported ADC, clock discontinuity or no clipped-frame support invalidates the affected B1 segment; (b) allow bounded gaps and imputation at pre-registered cutoffs. **Recommend (a)** until a desk log quantifies normal gaps; preserve the driver's original night result and disclose analysis-level invalidity.
16. **The final seal and ordering evidence.** Options: (a) freeze acceptance ID/digest, 25G83/v4 vector, HEAD, model/prompt/reader/chain hashes, seed, orders, smoke rows, rung set and vendor spec in one registration manifest after cold gate; (b) dispersed pins. **Recommend (a)**. R-ACC-6 places the issued acceptance before G2-a and this night; R-ORDER requires G2-a first and its rider's four conditions independently.