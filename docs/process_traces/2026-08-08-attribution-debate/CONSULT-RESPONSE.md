# Attribution debate — consult response of record (2026-08-08, Ed-ordered)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge. Ordered by
Ed in-thread (D-123 item 3): "are you and Sol sure you can't measure
the phases better? debate with Sol about how to attribute better."

**MAGISTRATE ADOPTION (Fable, 2026-08-08):** the memo's verdicts are
adopted. (1) For marginal phase-energy MEANS: signal sizing is the only
in-scope lever — boundary assignment is already fractional-overlap,
cadence is an instrument-identity change, the 10.818 ms screen is
estimator repeatability dominated by GPU DVFM physics (not clocks), and
event-clock sharpening is worth <0.0004 J. The question CLOSES for
means. (2) For ABBA CONTRASTS: real, repo-demonstrated headroom exists —
the common-mode estimator (FLOOR-COMMONMODE-01) historically cut the a5
decode comparative floor 6.46 J -> 2.13 J. ORDERED: the bounded
current-D-102-semantics replay runs BEFORE pack freeze; promote to a
named, prospectively registered claim estimator only if the gain holds
at >=~2x or >=2 J; otherwise close without delaying collection. The
promotion, if it happens, must not reopen the issued acceptance
artifact or void calibration corpora, and rides the full D-118/D-121
gate.

---

## Positions

**Bottom line:** for the D-123 **marginal prefill/decode energy means**, signal sizing is the only material in-scope lever. However, there is one demonstrated analysis-side improvement for **ABBA phase contrasts**, so the broader attribution question does not close completely.

| Question | Verdict | Evidence and likely gain |
|---|---|---|
| 1. Boundary assignment | **NO** | Current reduction already fractionally clips interval-average samples by exact time overlap. Proposed fractional attribution gains **0 J** over current behavior. |
| 2. Sampler cadence | **NO in ruled scope** | 50 ms is uncharacterized and changes the governed instrument identity, invalidating the issued calibration basis. |
| 3. Clock alignment / drift | **NO** | The 10.818 ms term is estimator-repeatability variation, not clock-read resolution. Passed windows already lie below it, so tighter brackets save **0 ms** under the current `max()` rule. |
| 4. Boundary definition | **NO** | Existing alternative events are only microseconds sharper, worth less than **0.0004 J** at the observed 33 W transition. A genuinely sharper semantic event requires runtime instrumentation. |
| 5. Repetition / ABBA | **REAL HEADROOM for contrasts only** | A repo-recorded common-mode replay reduced the historical a5 decode comparative floor from **6.46 J to 2.13 J**—a **4.33 J / 67% / 3×** improvement. It does not improve individual phase-energy means. |

### 1. Boundary-assignment estimator — NO

The current path is neither nearest-edge nor containment assignment:

- Powermetrics records become interval supports `[timestamp-elapsed, timestamp]` (`joulewise/adapters/powermetrics.py:1996-2010`).
- Integration computes `power_w × exact temporal overlap` for every support crossing the requested phase (`joulewise/reduce.py:167-180`).
- The fiducial estimator likewise fits the interval-average overlap model rather than thresholding sample endpoints (`joulewise/powermetrics_fiducial.py:479-506`; `docs/contracts/powermetrics_fiducial.md:38-56`).

Therefore fractional allocation is already implemented. Interpolating power *within* an averaging interval would add an unobserved waveform assumption; it could move the point estimate but cannot provably narrow the bound. The calibration corpus’s 22.741–33.559 ms fiducial range would remain unless a new estimator were validated, which is an estimator-identity/instrument program.

### 2. Sampler cadence — NO within scope

Production requests 100 ms, while retained traces show median intervals of approximately 119–128 ms, or 7.8–8.4 effective samples/s (`docs/reviews/2026-07-11-p2044-design-consult.md:20-38`). The repository contains no physical 50 ms characterization, so it cannot establish sample quality, overhead, or a joule improvement from halving the request interval.

In an ideal sampler, halving cadence would halve support width. That does **not** imply halving the measured ~1 J term here: the calibrated edge residual contains DVFM-ramp aliasing and anchor uncertainty, not merely half a sample period. D-078 also found that even a perfect fiducial leaves the 3.3–6.1 ms bundle-local term above the 0.99–2.9 ms bound required by the old repeatability-only gate (`docs/decision_log.md:4664-4671`).

Although changing `power_hz` is mechanically a config edit, scientifically it is an instrument change: `sampling_interval_ms` is an exact D-102 identity-epoch field, and changing it forces acceptance-bound re-derivation and new calibration evidence (`docs/decision_log.md:6369-6379`). It is therefore outside this consult’s ruled scope.

### 3. Clock alignment and the 10.818 ms screen — NO

The 10.818 ms value is the range of nineteen session-level **fiducial-bound estimates**, not clock API resolution or direct clock drift:

- Corpus mean: 26.950 ms.
- Sample SD: 2.971 ms.
- Range: 10.817749 ms.
- Fit-region coverage resolution: 0.1 ms.

Window B’s decomposition is decisive: **93.28%** of its excursion came from pulse-onset residuals caused by a GPU DVFM ramp, while wall-minus-monotonic movement was −0.201 ms, opposite the failure direction (`docs/decision_log.md:4823-4838`). Thus the screen mostly covers variation in the physical pulse/estimator result, including its extreme-value statistic—not coarse clock reads.

Cheap protocol changes do not help:

- Protocol v3 already uses 59 pulses for the 95/95 maximum. Since `B_fiducial` is the maximum across pulse edges, adding pulses cannot systematically lower it.
- Passed windows have observed bracket drift around 0.484–1.281 ms, already far below 10.818 ms. Making those brackets tighter leaves `max(observed, 0.010818)` unchanged.
- Lowering the screen itself requires replacing the issued D-102 artifact and revalidating its identity epoch—the explicitly excluded instrument program.

### 4. Boundary definition — NO

MLX defines prefill end/decode start at the first yielded token (`joulewise/adapters/mlx_runtime.py:554-634`). The first token event is already available, but it is stamped immediately afterward.

A read-only check over 178 retained bundles found:

- prefill-end → decode-start: median **5.0 μs**, maximum **11.9 μs**;
- decode-start → first-token event: median **1.19 μs**, maximum **2.86 μs**.

Even the maximum 11.9 μs difference at the observed ~33 W transition is under **0.0004 J**, four orders below the attribution issue. The event clock is not the weak link. The semantic limitation is that MLX exposes the first yielded token rather than an internal GPU “prefill finished” fence; obtaining the latter requires touching runtime instrumentation and redefining the phase contract.

### 5. Repetition structure — REAL HEADROOM, but only for contrasts

ABBA cancels order trends and steady point bias, but the uncertainty implementation deliberately does not average deterministic attribution bounds toward zero:

- Each ABBA block currently receives `(w_A1+w_B1+w_B2+w_A2)/2` from four independently adversarial member sets (`joulewise/floor_extraction.py:1501-1513`).
- Across repeated blocks, deterministic bounds are averaged as bounds, not divided by `sqrt(n)` (`joulewise/analysis_engine/estimators.py:422-447`). That is correct unless covariance/common mode is explicitly governed.

The unresolved over-conservatism is that the dominant fiducial component is shared across all four members governed by the same bracket. The repository already measured the consequence: a common-mode proxy changed the a5 decode comparative floor from 6.46 J to 2.13 J. This is genuine, material headroom recorded under `FLOOR-COMMONMODE-01` (`docs/process/state_kernel.json:1118-1147`).

It does **not** narrow any individual member’s ~1 J marginal phase attribution. It helps only a contrast whose shared shift can cancel after re-integrating all four measured curves jointly.

A related `PHASE-SHARE-ESTIMAND-01` candidate correctly observes that prefill and decode share one anti-correlated interior boundary. Its impact has not been quantified, so I classify it **MARGINAL/UNPROVEN**, not a second REAL item. It is relevant only to a joint phase-share/asymmetry estimand, not separately reported phase means.

## Disagreements

I disagree with the strongest version of “signal sizing is the only real lever.” It is true for **marginal phase-energy means**, cadence, clocks, and boundary assignment. It is not true for **ABBA phase contrasts**, where the repository has already demonstrated a 3× common-mode improvement.

I also disagree with describing 10.818 ms primarily as clock drift. It is a repeatability allowance for the complete fiducial-bound estimator, whose observed failure mode is dominated by GPU transition physics and estimator aliasing.

## Open questions

The only consequential choice is whether to promote the common-mode ABBA estimator before the prospective packs freeze. Its historical 6.46→2.13 J result predates the issued D-102 semantics and therefore needs one current-semantics replay before being treated as the expected prospective gain.

No open question remains for boundary clipping, cadence, additional fiducials, or alternate existing runtime events.

## Recommendation

1. **Common-mode ABBA estimator — rank 1.**  
   - **Impact:** demonstrated historical reduction of 4.33 J, 67%, or 3× on a comparative floor.  
   - **Cost:** approximately 0.5–1 desk-day for a current-D-102 replay; 3–5 desk-days to productionize and pass the full review gate.  
   - **Revalidation:** new named floor/claim estimator, prospective registration, identical covariance treatment in calibration floor and consuming claim, re-extraction/mint, D-118/D-121 review. It should **not** reopen the issued calibration-acceptance artifact or void raw calibration corpora.  
   - **Decision:** run only the bounded current-semantics replay before pack freeze. Promote if the gain remains at least roughly 2× or 2 J; otherwise close it without delaying collection.

2. **Joint phase-share envelope — rank 2, MARGINAL pending arithmetic.**  
   Pursue only if phase share/asymmetry becomes a paper estimand. Do not complicate the marginal phase-energy cells for it.

3. **Do not spend on cadence, clock-screen reduction, more fiducials, edge interpolation, or marker replacement.** Each is either already implemented, negligible, unproven, or an excluded instrument-identity change.

Thus: **signal sizing is the only real lever for the reported marginal prefill/decode energies; common-mode covariance is one additional real lever for ABBA contrasts.**

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Marginal phase energies have no material in-scope attribution improvement beyond signal sizing, but a common-mode ABBA estimator has demonstrated 3x comparative-floor headroom and merits one bounded current-semantics replay.","pathspec":[],"verification":["Read repository at df20d5c34215ad4fbf5882bdcb0537e1e53374fe","Inspected powermetrics adapter, reducer integration/envelopes, fiducial estimator, calibration acceptance/bracketing, MLX phase events, floor extraction, analysis deterministic-bound propagation, D-078/D-079/D-102/D-122/D-123, and detection-floor contract","Read-only arithmetic checked phase-event spacing across 178 retained bundles","git status --short --branch: clean main tracking origin/main"],"flags":["no_edits","no_quiet_mac","base_head_inferred_df20d5c"]}
