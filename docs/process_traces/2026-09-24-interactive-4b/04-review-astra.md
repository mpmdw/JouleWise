```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REDESIGN the decision experiment: retain the launch-context comparison, but replace its equivalence rule, confounded states, and incomplete measurement specification.",
  "workspace": {
    "base_requested": "7dd24d7b",
    "base_mode": "exact",
    "head_start": "7dd24d7bc374779674003580ea15d0287af1c12d",
    "head_end": "7dd24d7bc374779674003580ea15d0287af1c12d",
    "upstream_end": "7081ca06a3301eddbaf0bf5cbc4daafa738be75b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REDESIGN",
    "findings": [
      {"id":"F1","severity":"blocker","title":"Decision rule cannot establish equivalence"},
      {"id":"F2","severity":"blocker","title":"States cannot identify the proposed causes"},
      {"id":"F3","severity":"blocker","title":"Production integration requires production clock evidence"},
      {"id":"F4","severity":"should_fix","title":"OS mechanism telemetry is insufficient"},
      {"id":"F5","severity":"should_fix","title":"Sampler and workload effects are confounded"},
      {"id":"F6","severity":"should_fix","title":"Workloads and positive control need tighter definitions"},
      {"id":"F7","severity":"should_fix","title":"Stage the experiment and narrow its authority"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch; git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","7dd24d7bc374779674003580ea15d0287af1c12d"]},
      "expected":{"exit_code":0,"tail_regex":"7dd24d7bc374779674003580ea15d0287af1c12d"}
    }
  ],
  "flags": [
    {
      "id":"R1",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"Read-only design review; no launch, power capture, or quiet-machine validation performed.",
      "needs":"Lead-controlled execution after design revision."
    }
  ]
}
```

## Findings

1. **F1 — BLOCKER: replace the materiality and equivalence rules.** Three cells/context are insufficient to justify “not compromised.” Recomputed pilot cell medians span **4.90%** for default-context CPU time and **3.31%** for Interactive LM time. There are only two launchd cells/context, no energy observations, and a different LM from the proposed experiment.

   Three independent, symmetric null differences have matching signs **25%** of the time; that is the sign condition’s probability, not the complete rule’s false-positive rate. Multiple endpoints and drift further undermine it. Conversely, a real **5 J / 200 J = 2.5%** bias passes the 3% rule.

   **Change:** preregister paired contrasts, primary endpoints, multiplicity handling, and confidence intervals. Distinguish *material difference*, *equivalence demonstrated*, and *inconclusive*. Set separate latency and absolute-joule margins; translate joules/token using the actual fixed token count. Use a small energy-variance pilot to size an independent fixed confirmation sample. Within-cell repeats are not independent cells. Preserve production attribution uncertainty alongside sampling uncertainty.

2. **F2 — BLOCKER: Q2–Q4 are not identifiable as written.** Q2 promises an attended **shell** comparison, but no shell arm exists; its decision row substitutes attended I. A also permits agent load, while U removes it and changes brightness. “175 ms daytime versus 248 ms archived nighttime” does not prove idle causes additional throttling.

   **Change:** define A as quiet, human-attended, with the same display settings/content and power policy as U; prohibit agents in both. Add a matched shell reference or explicitly narrow Q2 to I(A) versus I(U). Verify HID idle, display state, and assertions throughout cells—not only at entry. Ten minutes since input does not establish settled maintenance activity.

   A process census establishes association, not whether idle itself or maintenance caused the difference. Narrow Q3 accordingly; reserve causal attribution for a follow-up intervention. Defer Q4, then use repeated **U–S–U** comparisons with verified display transitions and settling. A single A→U→S sequence confounds state with time.

3. **F3 — BLOCKER: §4 matches production’s integral only after its timeline is established.** The adapter converts rail milliwatts to watts, assigns each record support ending at its anchored timestamp, and the reducer integrates power × clipped support duration. Thus the proposed rectangular integration is correct; trapezoidal integration would be wrong here.

   **Change:** reuse the [adapter’s clock-evidence path](/Users/edr/code/wt-4b-osctx-astra/joulewise/adapters/powermetrics.py:502), including the current anchor method, first-record semantics, complete-frame handling, and stop-bracketing sample. Reuse [interval integration](/Users/edr/code/wt-4b-osctx-astra/joulewise/reduce.py:167). Recording wall and monotonic boundaries alone does not align plist intervals. Require complete segment coverage and propagate anchor/boundary uncertainty.

   Define LM windows to exclude loading/warm-up and measure each repeat separately. Report **gross CPU+GPU+ANE rail energy**; the idle segment is diagnostic, not an automatic baseline subtraction or whole-machine measurement.

4. **F4 — SHOULD_FIX: measure mechanisms without claiming more than telemetry supports.**

   | Mechanism | Could matter; minimum detection change |
   |---|---|
   | App Nap | Possible for eligible application/responsibility contexts; utility QoS does not prove App Nap. Record actual nap status where available, ancestry and assertions; otherwise label unknown. Apple documents separate priority, timer and I/O effects. [App Nap](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/power_efficiency_guidelines_osx/AppNap.html) |
   | Task role, QoS, timer coalescing, E/P placement | Record task policy and requested/effective QoS for workload workers and sampler, not just Python’s main thread before MLX import. Add bounded wake-delay observations and segment cadence distributions. Utility does **not** establish E-core confinement; aggregate cluster residency cannot identify which process ran there. [Apple scheduling guidance](https://developer.apple.com/videos/play/tech-talks/110147/) |
   | Metal scheduling | Host submission priority and GPU contention could affect latency. The pilot does not establish a QoS→Metal queue-priority mapping. Compare synchronized GPU timings and GPU residency/frequency; investigate command-buffer timing only if differences appear. |
   | Brightness zero, ProMotion, WindowServer | Brightness zero must remain a distinct display-on condition. Record brightness, display power state, configured refresh mode, visible content and WindowServer activity. Do not infer actual refresh rate from brightness or advertised mode. Keep dynamic refresh behavior explicitly unknown unless measured. |
   | Thermal/fan history | Record available thermal pressure, frequencies and fan/temperature telemetry across cells; standardize warm-up and bounded settling. Here `pmset -g therm` returned errors, so it cannot certify thermal health. |
   | DAS/duetactivityscheduler, Spotlight, Photos, backupd, fseventsd, XProtect | Replace the entry-only top-15 snapshot with low-rate, timestamped process CPU deltas and available I/O/memory-pressure observations across the whole cell. Retain OS activity in analysis. A non-OS-only 20% threshold misses cumulative small loads, I/O contention and short bursts. |

5. **F5 — SHOULD_FIX: separate instrument behavior from workload behavior.** Launching both under D or I estimates the combined production-context effect, but cannot distinguish workload scheduling from sampler perturbation or timing error. Powermetrics’ own CPU work contributes to measured rail power; different sampling rates may change that contribution.

   **Change:** retain the joint-context comparison as primary, record sampler CPU time and cadence, and add limited sampler-off timing controls. If the joint comparison differs, cross sampler context with workload context. Verify actual post-`sudo` sampler policy where observable; root privilege alone proves neither preservation nor removal of inherited restrictions. Preserve the production driver→zsh→Python launch/environment structure in the diagnostic entry path.

6. **F6 — SHOULD_FIX: strengthen workloads and use B only for what it validates.** The pilot’s ≈0.4-second CPU/GPU repetitions cover very few power intervals. Its `lm200_s` records a maximum token request, not observed tokens, prefill/decode phases, or output identity.

   **Change:** lengthen microbenchmark timing windows to cover many actual samples; explicitly synchronize GPU completion. Pin model revision, runtime, prompt, tokenization, decoding and output count/hash; exclude compilation/loading and reset per-request cache state consistently.

   B demonstrates gross CPU scheduling sensitivity. It does not validate 3% sensitivity, energy alignment, or GPU sensitivity—the pilot GPU times scarcely change. Use one bounded B check/state outside primary D/I blocks. B failing the arbitrary 1.5 ratio should trigger control investigation, not automatically invalidate every measurement.

7. **F7 — SHOULD_FIX: overall verdict — REDESIGN the experiment, retain its useful components.** First validate timeline reduction offline. Then establish energy variance and quiet A/U references; run powered, balanced randomized D/I blocks, with explicit pair identities and bounded settling. The written “D,I,B then I,D,B, repeated” does not uniquely specify three cells/context. Defer display sleep and detailed causal profiling until primary results warrant them.

   Remove the automatic “all three templates” installation decision: the third template is the magistrate, and the night template also renders the dead-man job. Neither is validated by an inference-cell comparison.

   Use an exclusive, lead-controlled agent-free window, unique temporary labels/paths, deadlines and cleanup restricted to owned processes. This review’s authority cannot execute that experiment. A detected effect flags relevant historical data for validation; a null result cannot certify all historical workloads or nights.

## Residual risk

Exact macOS 26.6.2 scheduling, sudo transitions, and brightness-zero refresh behavior remain unverified. The historical cadence record lacks tracked raw plists, limiting independent re-analysis.