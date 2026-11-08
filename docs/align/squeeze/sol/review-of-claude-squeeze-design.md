# Independent Sol review of the Claude squeeze design

2026-11-07 · **DRAFT, desk review for lead adjudication; no registration or arm authority.**

Reviewed product: `a832f4993:docs/align/squeeze/squeeze-design.md` (Fable + Opus reports, Opus synthesis). Review branch: `align/2026-11-07-sol-review-claude-squeeze-design`, already checked out and clean at intake. This is an independent Sol review, with no additional agent or Claude consult. The lead retains final verification and all scientific rulings.

**Verdict: DISAGREE with following the document as written; AGREE with its central additions after the corrections below.** A readable transcript, an independently qualified DC endpoint, successful adaptive attacks, physical controls and a locked test cohort would make v4 sounder. The proposed design does not yet justify its exact false-alarm claim, its confirmatory power, or its cheap transfer from off-Mac behavior to on-Mac energy. It also incorrectly says W1 lacks a meter-reader launch path. These are substantive corrections, not editorial reservations. Neither this product nor this review establishes that the squeeze holds, or that either possible outcome will meet a venue's acceptance standard.

## Scope and evidence convention

The no-network standing rule takes precedence over the request to fetch. **No fetch or browser call was made.** All cited Git objects were available locally; this review makes no claim about later remote tips. I read repository text and code, not measurement bundles, user caches, external model installations, or any sealed path. Absolute data locators in documents were treated only as text. No Block-5 pipeline, real measurement reader, model, hardware probe, or test suite was run.

**AGREE** means the specific statement is supported at the named pin, or the proposed action is methodologically warranted with the qualification stated. It does not mean an experiment passed. **DISAGREE** means false, overstated, internally inconsistent, or insufficient for its stated conclusion. **UNVERIFIABLE** means the needed evidence is absent from the permitted offline record. Historical pilot numbers below are checked against the explicitly requested public audit text, not independently recomputed from raw data.

For compact path:line citations, `KEY:L` expands to exactly `commit:repository/path:L` in this table. Ranges identify the supporting passage. These pins are immutable, not floating branch names.

| Key | Commit | Repository path |
|---|---|---|
| C | `a832f4993` | `docs/align/squeeze/squeeze-design.md` |
| P4 | `e901eb2a4` | `docs/align/pilot_protocol_v4.md` |
| CH | `e901eb2a4` | `docs/align/council-2026-11-06-v4-review/CHAIR.md` |
| ER | `e901eb2a4` | `docs/align/energy_residual.md` |
| MON | `e901eb2a4` | `joulewise/align/shade/monitor.py` |
| REC | `e901eb2a4` | `joulewise/align/records.py` |
| WORK | `e901eb2a4` | `joulewise/align/apple/workload.py` |
| END | `e901eb2a4` | `joulewise/align/apple/endpoint.py` |
| TD | `e901eb2a4` | `joulewise/align/apple/thermal_desk.py` |
| PIPE | `e901eb2a4` | `docs/align/PIPELINE.md` |
| RS | `e6c1a56c2` | `RUN_STATE.md` |
| LIT | `16e1db623` | `docs/research-audits/2026-11-07/literature.md` |
| RP | `7f74dd2a9` | `docs/research-audits/2026-11-07/research-program.md` |
| MVL | `036c7402d` | `docs/research-audits/2026-11-07/methodology-vs-literature.md` |
| W1 | `53a230598` | `docs/research-audits/2026-11-07/w1-prearm-gate.md` |
| V4S | `d600baba0` | `scripts/align_v4_session.py` |
| PILS | `d600baba0` | `scripts/align_pilot_session.py` |
| BYS | `d600baba0` | `scripts/bytes_h_session.py` |
| PLAN | `d600baba0` | `joulewise/b5/plan.py` |
| NIGHT | `d600baba0` | `scripts/run_night.py` |
| DRIVER | `d600baba0` | `joulewise/b5/driver.py` |
| FLAGS | `d600baba0` | `configs/b6/flag_catalog_b6.json` |
| METER | `a832f4993` | `scripts/km003c_monitor.py` |
| PRE | `688d14b6e` | `docs/registrations/align_v4_squeeze_addendum_DRAFT.md` |
| KIT | `67b4def8d` | `docs/align/squeeze/ADVERSARY-KIT.md` |
| SIM | `5af6bafea` | `joulewise/align/squeeze/README.md` |
| AR | `64fdc5189` | `docs/align/squeeze/sol/analysis-review.md` |
| KR | `96dd7e78c` | `docs/align/squeeze/sol/kit-review.md` |

The requested agenda and tripwire page were read at `a832f4993:docs/research/AGENDA.md:5–22` and `a832f4993:docs/research/energy-tripwire.html:135–204`. They express the goal and public pilot framing; they are not independent evidence of detector efficacy. M0 found `ACTIVE_STOP_CARD` = NONE (`a832f4993:RUN_STATE.md:8082–8088`). The explicit assignment selects this desk review. Standing instructions prohibit coordination-state edits and override normal kernel/state-update and full-suite requirements. No such files were changed.

## Findings that must change the proposed design

### F1 — HIGH: W1 already attempts to launch the meter reader

**DISAGREE** with C:63, action 6's missing-wiring premise (C:122), and the reconciliation at C:414/445. A grep restricted to ALIGN-named code misses the shared launcher:

1. `V4S:40–53` calls `pilot.prepare`.
2. `PILS:25,40–43` delegates to `bytes_h_session.prepare`.
3. `BYS:349–365` calls the existing window-plan writer.
4. `PLAN:957–962` emits a `HAZARD_PACK` plan.
5. `NIGHT:4540–4554` calls `run_hazard_night(..., seams=_hazard_seams())`; `NIGHT:4050–4054` supplies `production_seams`.
6. `DRIVER:740–754` supplies `scripts/km003c_monitor.py`; `DRIVER:2457–2464` starts its supervisor.

The last two links are also present at `e901eb2a4:scripts/run_night.py:4050–4054,4550–4554` and `e901eb2a4:joulewise/b5/driver.py:740–754,2457–2464`. This is not merely a newer-branch correction.

**AGREE** that successful capture and custody still need confirmation under RS:1047. A launch attempt is not live evidence: METER:40–43 explicitly permits an absent-meter header and exit 0, and FLAGS:1172–1177 treats supervision faults as diagnostic. Replace the wiring task with a source-trace/fixture check of the existing path and, later, the magistrate's capture receipt. Do not add another W1 reader competing for the same USB device. R1 has a separate rehearsal path; the W1 trace does not prove R1 capture.

### F2 — HIGH: the 5% statement is a conditional bound, not an installed guarantee

**AGREE** with the arithmetic: if each channel's calibration scores and future score are exchangeable under the same frozen scoring function, strict exceedance of 39 calibration maxima has marginal probability at most 1/40; the two-channel OR is at most 5% without channel independence. Equality requires additional conditions; the OR need not equal 5%. Rank 38 of 39 gives 2/40 per channel and an OR bound of 10%.

**DISAGREE** that the proposed estimator inherits that exact guarantee merely by accumulating 39 episodes (C:64–67, C:247–264, C:407/420, C:786–787). Its calibration scores use leave-one-trajectory-out fits while test scores use a full pooled fit. Those scores are not automatically exchangeable. Episodes also share windows, fit parameters and selected eligibility gates. U4 checks one sentinel's drift; it is not a theorem about all benign score vectors. Interleaving does not create exchangeability. A sentinel-offset fallback is another fitted procedure requiring its own prespecified validation, not a repair licensed by a failed stability gate.

The source already limits the claim to exchangeable trajectories across few windows (CH:307–319), fixes the per-session estimator (P4:488–505), and warns that shared folds correlate scores (ER:109–139). The Sol simulator explicitly distinguishes an independent frozen score from fold-dependent live scores (SIM:14–56). Freeze an independent fit/calibration/test construction, or provide a valid symmetric conformal construction and its assumptions; price any additional fit data honestly. Preserve window and trajectory dependence in uncertainty. The 90% bound `1 − .1^(1/39) = .0573315` requires iid calibration, beyond mere exchangeability, and is per channel, not a simultaneous 90% OR bound. It is not a guarantee at every realized threshold.

### F3 — HIGH: the composition equation is not an exact imputation rule

**DISAGREE** with C:269–278 and C:775–782. Under ER:93–107, define measured energy Y, prediction μ_F = x(F)β and `r_full = (Y − μ_F)/D(F)`. Then the exact same-episode identity is:

```text
z_E(V) = [r_full * D(F) + (μ_F − μ_V)] / D(V).
```

There is no κ multiplying that prediction difference. For example, take Y=110, μ_F=100, μ_V=80 and D(F)=D(V)=10. The exact visible score is 3; C's equation gives 2 when κ=.5. κ=1 recovers the identity, but measuring κ does not make it a free additional multiplier for that same residual.

A physical injection comparison can instead model an *increment* `Y_injected − Y_clean`, with its own expected site/dose cost and thermal/covariance uncertainty. It cannot simultaneously treat `r_full` as the observed full-log residual and adjust the full-to-visible prediction difference again. A fresh hidden call has its own prefill/intercept/context costs; arbitrary CPU work has no token-log x(F) without an explicitly defined conversion. KIT:111–126 and SIM:71–79 make this distinction.

**DISAGREE** also with “exact imputed energy flags.” Drawing an on-Mac residual produces a simulated flag, not that off-Mac episode's measured flag. The composition needs the conditional joint law of residual, shape, hidden work, monitor score, strategy and window. Sampling the marginal null can erase exactly the negative-residual selection exploited by P9 or correlations exploited by mixing. Transferring cloud behavior additionally requires tokenizer/template, quantization, sampler, budget and backend comparability; equal token caps alone are insufficient. ER:388–400 explicitly warns that changed contexts, batching, clocks and shared tools violate additivity. Carry parameter, κ, baseline and residual-law uncertainty into any composed estimate, and label it model-based. Keep a direct held-out physical result as the headline until transfer is independently supported.

### F4 — HIGH: SQ1's power calculation tests only one of its two requirements

**AGREE** with the displayed powers for an iid binomial test of p ≤ .025: rejection at ≥2/6 has power .890625 when p=.5 and .989065 when p=.7; at ≥2/8 the corresponding powers are .964844 and .998710.

**DISAGREE** that these power SQ1 as actually stated (C:312,343,849–854,894). SQ1 also requires a 90% lower bound ≥.5. Even using the more favorable **one-sided** exact Clopper–Pearson bound, 5/6 has lower bound .489684; 6/6 is needed. At n=8, ≥7/8 is needed. Thus the full conjunction has power:

| Eligible monitor-missed realized attacks | Required catches | Power if true catch=.5 | Power if true catch=.7 |
|---:|---:|---:|---:|
| 6 | 6 | .015625 | .117649 |
| 8 | 7 | .035156 | .255298 |

A two-sided 90% interval would not improve these powers. Freeze the interval convention and size against the actual conjunction, separately per pair if that is the declared claim unit.

The eligible denominator is **realized AND hiding AND monitor-missed**, not just realized. C:313/867 sizes eight realized attacks, so it does not size eight SQ1 opportunities. Further, an unconditional energy FPR bound does not automatically equal the benign energy-flag probability conditional on a monitor miss and behavioral selection. A .025 target can be a declared reference null, but should not be called the calibrated conditional benign rate without justification. Shared thresholds/windows also defeat an unqualified iid-binomial interpretation.

### F5 — HIGH: SQ2 and SQ4 do not yet support “hiding stops paying”

**AGREE** that comparing uncaught malicious outcomes is stronger than counting alarms alone. **DISAGREE** that the proposed samples and gates validate the conclusion (C:344–352,758–806,859–865,895–902):

- The 30 on-Mac attacks are spread over two pairs and four named classes. The T roster names neither a visible A2/A4 comparator nor `A*_M`, although action 11 freezes it. If SQ2 is entirely off-Mac, say so and specify that cohort's per-pair/per-strategy allocation. Appendix B's approximately 2,000 behavior episodes is not a manifest in the synthesis.
- With 200 independent observations per arm at p=.1, an individual normal 90% half-width is .034893, but the difference of two independent arms has half-width .049346. That leaves almost no room for a .05 noninferiority margin before strategy selection, multiple comparisons, clustering or imputation uncertainty. “Enough” is not established.
- Maxima over searched strategies need prespecified selection and held-out simultaneous inference. Finite tested candidates are not the supremum over all possible hiding/visible policies. An API monitor supplies query access, not necessarily model weights; define white-box and query-budget privileges precisely.
- Failure to reject a rank test at p≥.10 does **not** establish exchangeability/equivalence. A tolerance/equivalence margin and power are needed. Falling inside a wide 90% predictive interval is weak validation and can be made vacuous by an uncertain model. U4 does not fix this.
- A state-changing attack-directed call is a proxy for an *attempt*, not side-task completion. REC:36–47 records state changes without their malicious semantics. Register a separate evaluator for the exact event and retain main-task utility and actual side-task success. Report attempted, realized-by-proxy, successful and jointly uncaught denominators separately.

PRE:304–311 already separates physical compute detection from operational sabotage success. Preserve that useful distinction when reconciling the larger reservation rather than replacing it with an underpowered shortcut.

### F6 — HIGH: physical coverage, selection and dose validation are underspecified

**AGREE** that physical controls are mandatory and that T windows after D3 are a permitted *location* (CH:42–56). **DISAGREE** that the proposed few controls establish per-site physics or retire additivity before D (C:315,342,349–356,394,865):

- A 30B control does not establish D's κ, residual law, hybrid-cache behavior or gate response. CH:315 prohibits unvalidated cross-model/configuration transfer. C's proposed D controls remain later in T windows.
- The 30B slot arithmetic is repaired: `4 + 4*(1+4) + 4 = 28`, with 16 injections. But the design does not map site × dose × pair × carrier × order, specify randomized sham matching, or account for four injections sharing one clean twin. It is not automatically an independent ABBA design.
- A Q6 pool of 39 eligible carriers does not supply the 40 carriers required by the proposed 27/40 rule. Prespecify the actual-n decision rule or a separately authorized minimum of 40; repeated dose edits are not additional independent carriers.
- At the assumed D pair SD 40 J and cost 3.6 J/token, SE(κ) at 512 tokens is .021701. At the 30B's quoted 2.97 J and .619 J/token, SE at 256 is .018742, not .01. These are conditional planning calculations; the D SD is projected. One difference cannot estimate its own noise or demonstrate a site-wide κ interval. Meter/baseline uncertainty and context dependence remain.
- CPU dose in “token equivalents” needs a registered energy/work conversion; smoothing must distinguish energy, elapsed time and duty cycle. The existing kit uses fresh-cache generation in a pre-call gap, not the proposed in-context, tool, CPU and smoothed implementations (KIT:88–126). Evaluate actual executed dose, interruption, lazy cache materialization and visible-stream/RNG identity.
- Thermal timeouts and deadmen can depend on attack strategy/dose. Conditioning efficacy only on surviving eligible members may remove the hardest attacks. Freeze both assigned-attempt and eligible-analysis results, failures, spillover and refusal treatment; do not turn attack-induced exclusion into detector success. CH:319 expressly limits exclusion coverage.

Later independent review branches contain useful additional inputs: AR:87–101 warns about live-score transfer, and KR:42–47,86–105 identifies lazy-cache fencing, interruption and recoverable dose metadata. I did not rerun those reviews' tests and do not treat their reported fixes as my verification. They should enter lead integration, not be silently assumed present in the older kit pin.

### F7 — MEDIUM/HIGH: the energy boundary and recount need executable definitions

**AGREE** with an E2 endpoint covering CPU and unowned work **inside its registered member interval** (P4:195–201; ER:9–20). **DISAGREE** with unrestricted “before or after the episode” coverage (C:185–200,207–222,707). Work outside member start/end is outside that integral. Work before the model invocation but inside the member can be covered; those are different cases. Name the interval, clock map and dispatch/terminal stamps and retain an out-of-span escape policy.

Window-level idle prevents the specific member-baseline subtraction attack, but cannot guarantee coverage if a runtime adversary can poison the reference too. A warm soak is not necessarily comparable to idle. Under TM-A the two baselines coincide only under stationarity/matched thermal distributions, not by privilege restriction alone (C:220–222,408). An upstream-of-MagSafe DC measurement also needs a battery-assist sign convention and excludes AC-brick losses; it is not chip energy. A second-host reader reduces host-software tampering only with a defined independent clock/custody path.

E2 must have **DC-trained coefficients, covariance, intrinsic variance and its own baseline/integration uncertainty**. Reusing the five-term *form* is reasonable; reusing GPU coefficients would be wrong. C does not settle this explicitly; PRE:149–175 does. A historical PDTR/meter affine fit is corroboration, not universal gain calibration or a native qualification of the new member-span residual.

**AGREE** with consistent readable counts, native-reasoning visibility, tool arguments and full-log custody. **DISAGREE** that re-tokenizing a rendered monitor string is by itself a complete cheap fix (C:54,120,166–168). MON:25–27 collapses whitespace, MON:35–36 drops system messages, and MON:55–59 adds wrappers/tool labels. That is not the model's sampled token stream or chat-template input. END:451–472 renders typed reasoning/tool schemas through the tokenizer, and END:728–736 retains exact prompt/output IDs. Specify token-ID provenance, hidden-span boundaries, template/control tokens, tools, cached versus re-fed counts and downstream history. Re-tokenized public text can define a prospective reported-log estimand; it must not be presented as an exact recovery of actual generated work. Also update REC:28's visibility schema and MON:142–143's allowlist when implementing `readable`.

### F8 — MEDIUM: feasibility, authority and failure interpretations are too certain

**AGREE** with freezing new manifests and keeping R1's kit unchanged. **DISAGREE** with treating the following as settled:

- “v4 as registered” (C:36): P4:3–18 is explicitly a provisional unregistered skeleton. RS:1132–1136 rules registration grade, not completed registration or the specific T allocation.
- “D7/T4 count-only” as existing authority: CH:67 and P4:612 cap the registered extension at D6 and use eligibility/U1–U3, not attack realization. The synthesis correctly calls for amending the cap but must also name the new realization-triggered rule, maximum attempts/windows, seed roles, analysis conditionality and what happens if it still misses. Outcome-based realization is detector-blind but remains an outcome; it is not the chair's original eligibility-only rule.
- “Fits like D1–D3” and ≤12.4 h for the 30B controls: a 22-member arithmetic frame fits the nominal bookkeeping, but controls, sabotage, added heat, guards and permitted native bounds still need a concrete kit. A capped failed run is not an eligible dose. The 30B's historical 6.5 h chain does not prove the changed design's runtime.
- “Squeeze-incremental time: 12.4 h”: six D plus three T windows reserve 148.8 h; with the 30B window, 161.2 h after W1. D7+T4 would raise this to 194.27 h. T is not free because it fulfills a previously unspecified Q6 requirement. Distinguish previously approved science purpose from actual scheduled hours and do not call a 16.53 h window a 12.4 h night.
- A negative SQ4 rank test, failed SQ0 or failed SQ2 is not automatically a diagnosed limits mechanism. Failed power or uncertain transport can be **inconclusive**, not “no attack surface,” “floor too high,” or “energy not specific.” C:363–369 needs an unresolved category and diagnostic separation. In particular, the tested N1 dose need not be behavioral H_need.
- The 4-bit and Flash-Next pivots are new configurations, not swaps into the same cohort. RS:1146 requires R1-4bit and a lead ruling with Ed; P4:58–61,186–191 requires a separate configuration/addendum. More than a cloud-GPU purchase remains unresolved design work, even if many choices belong to the lead rather than Ed.

### F9 — MEDIUM: blinding and frontier definitions need completion

**AGREE** with shuffled sealed monitor scoring, independent recomputation and development-only red-team feedback. **DISAGREE** that one batch *eliminates* API drift (C:297,411): it limits systematic calendar separation; it does not guarantee a stationary provider throughout the batch or identical development/test behavior. Include blocked/random order, request metadata, fixed failure/retry/truncation rules, context limits and provider revision/deprecation handling. Native args can contain injection content; preserve role/data boundaries and test quoted or malformed tags. A monitor receiving all readable content still need not understand covert computation.

MON:196–201 hashes the **whole per-transcript request**, not a fixed base instruction. Pin the base-prompt/configuration hash separately from per-request hashes. Parse failures cannot silently become clean scores or be selectively retried (MON:169–206). The final batch must include D6 and any admitted extension; “after T3” alone is too early for the final interleaved calibration roster.

**DISAGREE** with interpreting the largest cap c as hidden tokens that survived (C:283,355,792–794): an allowed cap is not executed h, and a high-cap policy can emit zero hidden tokens. Compare actual h distributions and prespecified dose policies, separately from the cap axis. H_gap/H90 on a finite, possibly non-monotone grid need interpolation, censoring, unsupported-cell and simultaneous-uncertainty rules. `H_gap * e / declared energy` is a useful dimensionless descriptive ratio, not Kimpson's formal β or a transferable covert-capacity bound. Use site/context-dependent energy rather than one universal e. “H=0 is never a detection” belongs to the known-H energy efficacy count; a monitor may correctly flag a successful visible attack with zero hidden tokens.

## Disposition of every synthesis action item

These dispositions cover every sub-bullet in C:117–147; references to F1–F9 carry the detailed reasons and corrections, not additional approvals. Cost and live feasibility remain proposals unless explicitly supported.

| Action | Status | Reason and required disposition |
|---|---|---|
| 1, threat text (C:117) | **AGREE** | State trusted harness, TM-A/TM-B, readable binding and escapes. RS:1048 supports the scoped agent exception; CH:307–321 requires claim limits. Add local/off-host and outside-span scope, F7. This is not an unrestricted on-host adversary license. |
| 2, T cohort (C:118) | **DISAGREE** | A locked cohort is required (RS:1132–1136), but this exact allocation lacks SQ1/SQ2 power, complete per-pair arms and an admitted extension rule. Revise under F2/F4/F5/F8 before freezing it. |
| 3, D0 (C:119) | **AGREE** | Useful post-hoc development check, with pilot identity and custody qualifications (RP:248). Do not access the external roots from this review. It cannot prove a realistic hidden-work requirement or D capability (RP:82; F3/F5). Local monitor fit/cost is unverified. |
| 4, readable renderer/recount (C:120) | **AGREE** | The gap is concrete (MON:30–59; ER:158–163). Implement typed rendering and token provenance, with schema/allowlist integration, not string-only accounting (F7). Preserve the chair's decode-only registered estimand and separately labelled full-omission print (CH:51–53). |
| 5, energy choice (C:121) | **AGREE** | Prospective development-only comparison is sensible. Freeze the actual projected-H50 selection formula, DC fit and uncertainty, independent calibration and missing-channel policy (F2/F7). A qualitative rule is not yet an executable registration. |
| 6, meter wiring (C:122) | **DISAGREE** | W1 already launches through HAZARD_PACK (F1). Confirm capture/custody and qualify the endpoint; inspect R1 separately. Reuse flags only with an explicit new claim-level missingness policy; diagnostic flags currently refuse nothing (FLAGS:1172–1177). |
| 7, BSP (C:123) | **AGREE** | Freeze development-only gates before probing; do not feed R0 selection (P4:630; CH:213–215). Retain R10 authority. Cloud cost/runtime, exact backend equivalence and fallback feasibility are unverified (F3/F8). The probe is screening, not confirmatory evidence. |
| 8, addendum (C:129) | **DISAGREE** | Necessary, but do not adopt the proposed composition, LOTO exactness or 12-night precision as settled. The quoted PRE gaps and 1,398 reservation are real (PRE:328–342,453–462); its independent-split and physical-success safeguards should survive reconciliation. |
| 9, monitor freeze (C:130) | **AGREE** | Implements RS:1049. Freeze base/config and per-request hashes, failure handling and the complete final batch (MON:169–206; F9). No monitor model or operating point is selected by this review. |
| 10, injector (C:131) | **AGREE** | Needed under CH:56. Kit mismatch and package collisions are real; map all sites/doses and include sham/identity/failed-dose controls (KIT:49–55,88–149; F6). Later KR findings need integration review. Experimenter instrumentation must remain trusted and scoped. |
| 11, adaptive search (C:132) | **AGREE** | Appropriate development search: mixing, camouflage, injection, latent attacks and the two-knob challenge. Specify reachable legal knobs, feedback/query budgets, allocation, selection and both frozen comparators; no claim over all adversaries (MVL:268; F3/F5). |
| 12, 30B night (C:138) | **UNVERIFIABLE** | Approval in principle is documented (RS:1130), and 28-member arithmetic is correct. Neither ≤12.4 h nor native site/dose feasibility is established by a concrete kit. It cannot validate D physics (F6/F8). Lead/magistrate live gate remains required. |
| 13, desk work (C:139) | **AGREE** | Camouflage, mixing, metadata and time baselines address real gaps (LIT:126; RP:166–168; MVL:268). Keep simulation assumptions visible; current simulator does not supply actual studentized live scores or a trained monitor response (SIM:58–79; AR:87–101). |
| 14, pre-T gate (C:140) | **AGREE** | Recheck actual benign spread, attack yield and physical fit before new arms. Must also check F2/F4/F5/F6 and freeze adaptation/extension rules before the relevant outcomes; a gate cannot retrofit validity. |
| 15, paper (C:146) | **AGREE** | Local batch-1 TM-A headline and TM-B boundary map are appropriate limits (CH:307–321). Treat novelty and source-specific numbers as unverified here; β ratio is descriptive (F9, literature ledger). No venue outcome promised. |
| 16, P7 bench (C:147) | **AGREE** | Optional, scoped instrument bench with a prospective kit; otherwise an explicit untested limit. Batched-cache support and magnitude cannot be inferred from a serving-average ratio (F6; literature ledger). No native execution authorized by this review. |

## Claim ledger for the synthesis (§§1–6)

Repeated claims are consolidated here; the target locations identify all their substantive occurrences. Each row judges the stated proposition, not an entire paragraph containing distinct propositions.

| Target locations | Claim | Status | Evidence / reason |
|---|---|---|---|
| C:3–12,24 | Seats, source-reading history, nothing loaded, no restricted reads | **UNVERIFIABLE** | These are authors' process attestations. The embedded text and named objects exist; this review cannot reconstruct their tool histories or independence. |
| C:6–22 | P4/CH/ER/MON and audit pins | **AGREE** | All named source objects were locally readable at the stated pins. The W1-kit source is pinned here as `d600baba0`; floating references are not future-tip evidence. |
| C:25–28 | RS210 power-path, adversary amendment, API-primary monitor, venue direction | **AGREE** | RS:1045–1050 records all four. Physical capture is still owed. “All power” describes the MagSafe DC path, not brick losses or uncorrected battery assist. |
| C:36–47,629–640 | v4 lacks the additional squeeze study | **AGREE** | Known-H is log-edit evidence, not physical sabotage (P4:508–523; CH:312). Added monitor, controls and test design are warranted. |
| C:36,82 | v4 is already registered; D1–D6 is a fully installed calibration plan | **DISAGREE** | P4:3–18 is unregistered; RS:1136 orders reconciliation before W1. Q6 is a direction, not a completed plan. |
| C:38–41 | Non-adaptive known-H, 1 sabotage/pair/window, turn-owned rail, unowned gates | **AGREE** | P4:139–146,195–201,474,488–516. |
| C:39,427 | Apple path has no `ShadeMonitor`/`render_transcript` call | **AGREE** | Scoped `git grep` at `e901eb2a4` over `joulewise/align/apple` and `scripts` returned no hits. This proves code-path absence at that pin, not all historical human scoring. |
| C:427,633 | No monitor has ever scored any ALIGN pilot | **UNVERIFIABLE** | RP:166–168 supports an unrun baseline, but absence from code/audit is not exhaustive execution-history evidence. |
| C:49–54,404 | Counts-logged headline and missing matching monitor view | **AGREE** | P4:491–495; ER:421–426; MON:30–59. Native reasoning appears only in `full`; all views hide arguments. |
| C:54,166–168 | Readable rendering alone guarantees the structural squeeze / cheap exact counts | **DISAGREE** | Readable does not imply semantic legibility; token/template accounting and misspecification remain (F3/F7). |
| C:56–59,185–200,421 | E1 omits CPU and unowned work; E2 sees all such work | **DISAGREE** | E1 has no direct CPU boundary; unowned attribution is explicit. E2 covers only its sampled interval, with sufficient excess above noise/reference. CPU work can indirectly alter GPU energy. “Sees” is not a guaranteed flag (F7). |
| C:60,422 | PDTR affine fit and correlation | **AGREE** | As an audit-text attribution only: MVL:100–103 records the precise fit, on 20 s bins. It is not independently verified raw calibration here, nor a universal transfer function (MVL:266). |
| C:61–62,207–215 | One E* plus separately retained v4 E1 | **AGREE** | A prespecified max composite can be one calibrated statistic; keeping the original endpoint avoids silent replacement. Must freeze the whole transform/fit (SIM:37–49; F2/F7). |
| C:63,414,445 | ALIGN kit has no reader-launch route | **DISAGREE** | Shared W1 route demonstrably starts the reader (F1). Narrow grep is insufficient. |
| C:64–67,247–264,420 | m≥39 automatically makes this OR exact at 5% | **DISAGREE** | Conditional rank arithmetic is right; installed LOTO/full-fit and window assumptions are not established (F2). |
| C:68–74,337–358 | Four conjuncts establish “hiding stops paying” | **DISAGREE** | Worthwhile goal, but flawed SQ1 power, SQ2 comparison/inference and SQ4 validation (F3–F6). |
| C:74,359–371 | Every failure diagnoses a publishable limits outcome | **DISAGREE** | Underpower, transport failure and inadequate attack search can be inconclusive; paper acceptance is not inferable (F8). |
| C:75–80,375–383 | Capability/hidden-work overlap is the biggest empirical risk | **AGREE** | Reasonable priority grounded in P4:172–191, CH:297–301 and RP:82. D0 is development evidence, not a retirement proof for D. |
| C:78,316,416 | CH planning range central 300–500, plausible 120–1,500, tail up to ~3,000 | **AGREE** | CH:270–303. These are projections, not measured D MDEs; R1 refines them. E2's new endpoint needs its own floor. |
| C:80,405,427 | 30B side task only once in 12 pilot-4 sabotage seeds | **AGREE** | Public audit corroborates rarity and the one successful seed (RP:82). Exact “12” is carried pilot framing, not raw verification by this review. Do not generalize to all future 30B policies. |
| C:81–87,318–335 | Night counts, calendar estimates and T's zero incremental cost | **DISAGREE** | Nominal hours can be computed, but “free T” is budget labeling and changed-kit yield is unverified (F8). R0 history is not an estimated future refusal distribution. |
| C:88–91 | Cloud GPU needs Ed; everything else is ruled/lead-owned | **AGREE** | PIPE:3–5 reserves paid compute; RS:1049 grants API-monitor/model budget choice to lead. This does not settle new estimators, cohort design or configuration gates (F8). |
| C:90,292,405 | Local monitor fits 24 GB / cloud BSP costs ~10 GPU-hours | **UNVERIFIABLE** | “If it fits” is a proposal. No native memory, serving throughput, API-cost or backend-equivalence evidence was supplied; no weights were inspected. |
| C:93–95,160–180 | Trusted harness, batch-1 TM-A and TM-B boundary map | **AGREE** | Compatible with RS:1048, CH:315–321 and PIPE:19–20. Must define allowed tool affordances and off-host/out-of-span limits, F7. |
| C:166–169,404 | Count-only reasoning disclosure leaves both channels blind to that content | **AGREE** | It leaves no omission residual for correctly counted reasoning and the monitor lacks its content. It does not mean either detector can never flag correlated visible behavior. ER:158–163 and MON:49–57 support this narrower statement. |
| C:183,690 | TM-B requires a second-host meter reader | **AGREE** | Sensible for a threat including compromise of local measurement software; reader separation alone is insufficient without clock/sample custody. Under trusted-host placement-only controls it is a stronger design choice, not a mathematical necessity (F7). |
| C:190,732 | Fresh-context hidden decode is ~3× cheaper per token | **AGREE** | RP:249 supports this as a 30B planning approximation (~.18 versus .49–.67), not a D/site-invariant energy law. Include prefill/intercept costs. |
| C:195,424,749 | Recount defeats count/cache misreporting and t+1 identity check suffices | **DISAGREE** | It defeats claimed-count forgery only under authenticated harness inputs. Cache state, history rewrites, tool results and actual execution require provenance; simple prompt equality is not the full recurrence (END:451–472; F7). |
| C:196–198,692–698 | Visible cover, latent work, injection and batching are escape limits | **AGREE** | Correct to name them. They refute any unconditional guarantee from the readable/unreadable partition; empirical rates remain unverified (PIPE:19–20; ER:399–400). |
| C:202–206,435 | Drop replay identity as a third registered detector | **AGREE** | Harness-written logs exclude unsampled fabrication in TM-A; designated replays are instrument checks, not every-episode security tests (P4:117,403–419). Keep the limited paper analogy. |
| C:218–222,408 | Window idle always closes reference poisoning; two references coincide under TM-A | **DISAGREE** | Only the specific member-own poisoning is removed, and stationarity is still needed (F7). |
| C:226–244 | Merged attack taxonomy, benign carriers, H grid | **AGREE** | Useful coverage and CH:51–56 supports benign carriers/sub-turn edits. The declared dose grid omits P4:513's 300-token point; preserve it or explicitly amend it. A benign carrier curve measures injected/log-edited work, not autonomous sabotage success. |
| C:242–244 | Every strategy can be implemented under amended D-139 | **UNVERIFIABLE** | Intent is compatible, but actual tool privileges/CPU/smoothing/side-call implementations and native scheduling are absent. A prompt describing a strategy is not its implementation (KIT:64–86). |
| C:269–278 | Exact linear composition with κ and imputed energy flags | **DISAGREE** | Exact algebra has coefficient 1 on μ_F−μ_V; simulated transfer requires a conditional model (F3). |
| C:280–285,355 | H_gap, H90, h_surv and β ratio quantify surviving hidden work | **DISAGREE** | Useful descriptive axes, but cap ≠ executed dose and curve/censoring/energy conventions are unfinished (F9). |
| C:289 | Members archive transcript bytes and sha256 | **AGREE** | WORK:744–784 writes the artifact and digest. It does not imply every interrupted/crashed member has a complete transcript. |
| C:290–293 | Off-box scoring and explicit views/sampling | **AGREE** | Methodologically suitable. Temperature 0 is not guaranteed deterministic, so repeated API calls need not be literally redundant; no validated “SHADE convention” was supplied (F9). |
| C:294–302,411 | Sealed batch after T3 eliminates drift and preserves final cohort | **DISAGREE** | Blinding structure is good; the drift guarantee and timing omit D6/extensions unless explicitly delayed (F9). |
| C:308 | 42 benign/pair gives ≥39 after up to ~7% loss | **AGREE** | Arithmetic only: at most 3 exclusions gives 39 (7.14%). At independent 7% member loss, P(≥39 of 42)=.6613 **per pair** before window exclusions; this is not a high-probability yield promise. |
| C:309,440 | 27/40 has α~.019 and power~.98 at p=.8 | **AGREE** | Exact iid binomial: .01923865 and .98059263. It rejects p≤.5, not establishes p≥.8. Shared carriers/fits/windows require different inference (F2/F6). |
| C:310–311,406,413 | 22-member T frame and corrected 28-member 30B sum | **AGREE** | Integer sums are correct; the old 42-member proposal is much larger. “30 attacks approximates ≥16 per pair” is inaccurate: balanced allocation is 15/pair. Actual frame eligibility remains unverified (F5/F6/F8). |
| C:312–313 | SQ1 is well powered and realized-count extension sizes it | **DISAGREE** | Full-conjunction power and the monitor-missed denominator differ (F4). |
| C:313 | 21/37/57 attacks give eight realized with 90% probability at .5/.3/.2 | **AGREE** | Iid-binomial arithmetic gives .90538/.90528/.90661. It does not size eight realized, hiding, monitor-missed attacks or window-correlated outcomes. |
| C:314,443 | BSP with two rungs is up to 800, not 400 | **AGREE** | `5*40*2*2=800` before additional budget settings, repeats, red-team queries or failures. A B_D sweep could cost more. |
| C:315,865 | One site/dose control suffices for κ precision | **DISAGREE** | Requires a known variance/cost model and validated site transfer; numerical 30B SE claim is optimistic at 256 (F6). |
| C:327 | All D1–D3 sabotage can be development S0 | **AGREE** | New squeeze development role is possible prospectively, but they cannot then serve as locked squeeze test data. Preserve v4's separate analysis purpose and complete role manifest (P4:504–505). |
| C:329 | Interleaving makes calibration/test exchangeable | **DISAGREE** | It reduces time separation, not strategy, fit, window or eligibility differences (F2). |
| C:330 | D7/T4 is automatically legitimate because trigger is count-only | **DISAGREE** | Needs prospective authority and a valid stopping/inference plan; realization count differs from eligibility-only CH:67 (F8). |
| C:342 | N1/P-tool/P-cpu carrier rates establish energy bite at H_need | **DISAGREE** | Valid as a proposed controlled-work target after defining physical conversions and inference; composed rates are not measured site-specific carrier rates (F3/F6). |
| C:349–352 | p≥.10, κ interval and prediction coverage prove composition | **DISAGREE** | Nonrejection is not equivalence, and distribution transfer includes more than marginal r_full and κ (F3/F5). |
| C:363–369 | L1–L7 are exhaustive causal explanations of failure | **DISAGREE** | Add insufficient evidence, undefined denominator, cohort/configuration change and nontransportability; gates diagnose different failure classes (F8). |
| C:369 | D screen-only can pass the claim to a registration-grade 30B cell | **AGREE** | RS:1135 allows registration grade on whichever cell carries the claim. It does not prove the 30B can demonstrate capable sabotage. |
| C:375–380 | Hiding must be necessary and >floor; hint on makes it harder | **UNVERIFIABLE** | These are plausible behavioral hypotheses, not established necessities for all attacks. Total reasoning excess is not a causal estimate of minimum required hidden work. Treat BSP as a diagnostic, with actual outcome measures (F5). |
| C:384–392 | BSP exact budgets, G1–G4 and pivot order are sufficient GO/NO-GO | **DISAGREE** | Good development questions, but ratio/difference CIs, zero denominators, multiple arms/rungs, budget selection and transport are unspecified; 4-bit/FN need their own gates. G3's 500 tokens is a projected E1 value, not the new E2 floor (F3/F4/F8). |
| C:394 | 30B night retires D's additivity risk | **DISAGREE** | Cross-model/hardware-control transfer is prohibited without evidence (CH:315; F6). |
| C:407 | Few T benign/pair cannot support the old per-session five-term fit | **AGREE** | Real rank/df/support concern; P4:488–495 and ER:61–83 apply. Pooling is a new estimator requiring validation, not the only possible solution (F2). |
| C:409 | Separate E1,E2,M at 2.5% each allows 7.5% OR | **AGREE** | Union bound arithmetic. A separately calibrated composite E* avoids counting E1/E2 as independent detection channels, subject to F2. |
| C:410,423,437 | T placement satisfies the chair's post-D3 location requirement | **AGREE** | CH:56 allows an extension or dedicated post-D3 cell. It does not certify doses, per-pair evidence or native fit (F6). |
| C:415 | Sol lanes now exist and collide on two package entrypoints | **AGREE** | Named local tips exist. `67b4def8d:joulewise/align/squeeze/{__init__,__main__}.py` and the same paths at `5af6bafea` differ; no automatic combined implementation is admitted. KIT:32–55 documents missing lane integration. |
| C:425–426 | Hybrid misspecification and 755-token confound warrant diagnostics | **AGREE** | LIT:126 and RP:142–149. Counting system tokens alone does not fix the missing fresh-prompt quadratic work term; retain the corrected sequence form. |
| C:428–429 | Q4/Q6/30B approval and 11.9 tok/s / original 1(f) impossibility | **AGREE** | RS:1130–1140 records these. R10's subsequent procedure, not an unchanged 600s-floor kit, governs W1. |
| C:438–441,452 | Unverified SHADE sampling/FPR claims are dropped; pilot location corrected | **AGREE** | Appropriate restraint; RP:248 supports the location correction. Dropping claims from synthesis does not make the verbatim appendix claims true (appendix ledger). |
| C:446–482 | All listed papers were opened; exact external results are verified | **UNVERIFIABLE** | Only repository citations/attestations are available under no network. Source-specific disposition follows below. |

## Appendix coverage and additional errors in the verbatim seats

The synthesis, rather than either appendix, is the candidate action plan. Nevertheless the request covers the whole product. All repeated appendix claims inherit the ledger above. This mapping covers the action arrays and every appendix section; the table after it addresses their additional substantive claims.

| Appendix material | Coverage |
|---|---|
| A ACTIONS (C:490), 12 items | D0→action 3; threat→1; E2→5/F7; meter→6/F1; classes/estimand→8/F2–F6; monitor→9/F9; injector→10/F6; headroom/mixing→13; 30B night→12; test shape→2/F5/F8; paper→15; batch bench→16. Superseded choices retain the explicit dispositions below. |
| A §§0–3 (C:496–557) | Synthesis claim ledger: existing v4, three teeth, boundary, monitor, costs and taxonomy; F1/F7 govern the stronger original claims. |
| A §§4–7 (C:559–599) | F2–F9, action 2/3/8/9/12/13; numerical additions below. |
| A §8 (C:601–606) | Literature ledger below. |
| B ACTIONS (C:614), 17 items | In order: actions 1,7,4,4,6,5,10,12,8,2,8,9,11,13,13,14,15. Their dispositions above apply. |
| B §§0–4 (C:627–750) | Synthesis ledger: gaps, boundaries, detectors/taxonomy; F1/F7 plus P-site and source-ratio caveats below. |
| B §§5–8 (C:754–867) | F2–F6/F9; composition, score fit, frontier, cohorts and power; additional arithmetic below. |
| B §§9–12 (C:871–960) | Actions 7–16 and F2–F9; gates, order, failure outcomes and red-team adequacy. |
| B §13 (C:964–983) | Literature ledger below. |

| Target | Additional claim/choice | Status | Evidence / reason |
|---|---|---|---|
| C:498,534,570 | Replay identity is a universal third security detector | **DISAGREE** | Synthesis correctly drops it; P4:403–419 specifies instrument pairs, not arbitrary episode re-execution or attack fabrication tests. |
| C:499 | Hidden decode inside a tool is necessarily CPU work | **DISAGREE** | A tool can run GPU generation; the merged table correctly distinguishes it (C:190; KIT:103–126). E1 can capture GPU work in turn-owned tools (ER:9–13). |
| C:501,599 | D0 alone retires D's behavioral premise; reasoning excess is realistic required H | **DISAGREE** | Selection-data/model mismatch and no causal necessity test (RP:82,248; F5). |
| C:502,584–593 | Two 42-member test windows fit 16.5 h each | **DISAGREE** | `2*(10+8)+6=42`, versus the 22-member frame (P4:139–146). The synthesis is right to reject automatic fit; average time multiplication is only a planning warning, not a native impossibility proof. |
| C:511,516 | Native reasoning/records and public pilot numerical summary | **AGREE** | WORK:627–634,744–784; REC:36–86; RP:104–119 corroborate the audit summary. Scratchpad counts are not automatically native `reasoning_tokens`; maintain separate provenance. |
| C:514 | No injector existed at the v4 pin | **AGREE** | The cited pin lacks the later squeeze kit; KIT:49–55 confirms native integration is still missing at its later pin. This is pin-specific, not a claim about today's remote. |
| C:518 | No threat model text exists anywhere | **DISAGREE** | The detailed adversary boundary is missing, but PIPE:19–20 and ER:388–400 do state scope/limits. Say the necessary privilege/affordance model is absent, not all threat-related text. |
| C:519 | Sol lanes were not on origin at the seat's fetch time | **UNVERIFIABLE** | Current local refs cannot reconstruct what that seat saw when it fetched. As current-state guidance it is obsolete. |
| C:523,542,554 | Agent controls arbitrary tool programs; all adaptive classes are benign-carrier designs; replay pairs are ABBA | **DISAGREE** | Existing SHADE sandbox tools need not expose a compute executor (KIT:64–86). Autonomous successful attacks are a different cohort from benign carriers. ABBA needs explicit order and matched conditions, not merely reused twins (F6). |
| C:533 | AUC ≤.87 bounds this monitor class | **DISAGREE** | A benchmark best observed AUC is not an upper bound for future monitors/tasks/views. Local conditions and tool arguments differ; no such theorem is supplied. |
| C:563,565 | Per-session LOO maximum is exact and Mahalanobis is a calibrated secondary score | **DISAGREE** | Frozen score/independent calibration needed, plus separately trained covariance and tail validation (F2). Calling it secondary does not supply those. |
| C:570 | ≥27/40 establishes ≥.8 detection; 40 pooled carriers support per-pair claims | **DISAGREE** | The test rejects p≤.5. Pooling 20/pair cannot establish 40/pair or remove dependence. The synthesis changes the interpretation but not all inferential problems. |
| C:576–578 | no_scratchpad primary; temp 0×3 is upstream convention; paid-monitor go still owed | **DISAGREE** | The view is count-only for native reasoning (MON:49–57); convention unverified; RS:1049 settles API-primary authority. Repetition may still measure service nondeterminism, not necessarily independent samples. |
| C:580 | `wilson`, `HintMonitor`, five-pair metadata bootstrap are drop-in inference | **DISAGREE** | Reuse utilities only after matching units, score type, cluster structure and intervals. This two-pair study with few windows is not automatically a five-pair bootstrap design. |
| C:584 | Six windows suffice at 5% exclusions, seven at 10% | **UNVERIFIABLE** | Need an explicit yield probability and window-pass model. For six windows/42 candidates, iid 5% exclusion gives only .8431 probability of ≥39 per pair; at 10% it is .3836. Neither is a guaranteed stopping point. |
| C:662,879,949 | Meter physically absent / inline still needs a ruling | **DISAGREE** | Superseded by RS:1046–1047. Existing W1 launch path is also present (F1); live receipt remains owed. |
| C:664 | Count convention is wholly unresolved for v4 | **DISAGREE** | ER's adapter default remains False, but P4:491 explicitly makes counts-logged headline. The new readable split is the unresolved squeeze amendment. |
| C:670 | No time or metadata baseline exists | **DISAGREE** | A baseline *result* is unrun per RP:166–168; synthesis C:139 names existing code. Distinguish unexecuted analysis from missing implementation. |
| C:698 | Physical accounting closes the hidden route | **DISAGREE** | Only a bounded empirical claim at validated sites/doses/conditions is supported; low-dose, camouflage and off-meter work remain (ER:388–400; F3/F7). |
| C:711,983 | SHADE upstream pin is 6614e77 and names-only rendering is replicated | **AGREE** | `e901eb2a4:joulewise/align/shade/upstream.py:24–27` pins `6614e77191c1f8e2d0c44c123c6f915905ebafae`; MON:30–59 implements names-only rendering. Upstream text itself was not opened by this reviewer. |
| C:742 | Natural S0/A1 regression alone identifies physical κ | **DISAGREE** | Dose and behavior/shape can be confounded; randomized known-dose controls and matched logs are needed (CH:56; F6). |
| C:748 | Production decode/prefill ratio quantifies marginal piggyback energy | **DISAGREE** | Average serving ratios do not identify extra-row marginal cost or a token-level H50 inflation factor. RP:79 corrects cached/uncached comparability; use as motivation only. |
| C:759–762 | Realized directed state change equals “uncaught success” | **DISAGREE** | Valid as a named proxy event, not success. Main/side evaluators and attempt/assignment denominators must remain separate (PRE:304–311; F5). |
| C:802–806 | ~2,000 behavior +600 development and T sample validate backend equivalence | **UNVERIFIABLE** | No complete allocation/precision/transport plan is supplied. SQ4's stated tests do not test the full joint behavior law (F3/F5). |
| C:835–847 | H50/H90 planning table from q≈2.15 | **AGREE** | Given the assumed constant denominator, cost and normal residual, H50=qD/e and H90=(q+1.28155)D/e reproduce the table. These are idealized calculations, not actual score/endpoint power; CH:280–300 includes additional uncertainty. |
| C:845 | At 256/512 tokens, catch probabilities .82/.46/.27 and 1/.97/.82 | **AGREE** | Approximate standard-normal arithmetic under those same assumptions. Not measured energy powers or heavy-tail bounds. |
| C:846 | 30B H50≈170/350 tokens on frozen thresholds | **UNVERIFIABLE** | RP:78 explicitly rejects replacing the real score denominator by s_r; the corpus gives whole-turn upper bounds, not these point MDEs. No raw recompute permitted here. |
| C:860 | 90% CP 22/24≈[.76,.98], 0/24 upper≈.12 | **AGREE** | Approximate **two-sided** 90% exact interval arithmetic (.7602,.9850 and upper .1173). Specify sidedness; the one-sided upper for 0/24 is .09148. |
| C:861 | 200/arm proves SQ2's ε=.05 claim | **DISAGREE** | Individual-arm width is not the selected-max difference uncertainty (F5). |
| C:863 | 40 attack versus 78 benign detects a .47-SD shift | **UNVERIFIABLE** | No reproducible rank-test/clustered-residual power calculation is supplied. An independent equal-variance normal mean-test approximation gives (.1 two-sided z + .8-power z)*sqrt(1/40+1/78)≈.4836. That rough comparison does not verify the rank test; nonrejection also does not establish equivalence (F5). |
| C:865 | 30B κ SE≈.01 with ~3J pair SD | **DISAGREE** | At H=256 and .619 J/token it is .01874; at H=512 it is .00937. Dose and assumed known noise must be stated (F6). |
| C:877 | Four anchors + four*(1+5)=28 and 16 injections | **DISAGREE** | Total is 28 but that formula has 20 injected slots; four sites*two doses*two reps is 16. Synthesis repairs the count, but the full roster still needs mapping (F6). |
| C:886 | Cloud GPU and monitor API both still need a new Ed go | **DISAGREE** | GPU remains reserved by PIPE:3–5; monitor/model budget is delegated by RS:1049. |
| C:929 | N(0,1) and q=2.15 give physical BSP predictions | **DISAGREE** | Appropriate as labelled sensitivity assumptions only; they do not validate D residual shape, E2 or transport (F3). |
| C:938 | 4-bit gives ~2× turns per 1,800 s | **UNVERIFIABLE** | An unmeasured throughput/overhead projection; R10 explicitly requires its own R1-4bit (RS:1146). |
| C:948 | ~76% missing memory energy implies more DC decode signal | **UNVERIFIABLE** | RP:130–138 limits the known-bytes result to a latency-bound geometry; it cannot identify D decode's DC signal-to-noise. Keep [est] and test directly. |
| C:951 | Time alone may suffice; P3/P6/P7 provide energy's distinct value | **AGREE** | A valuable baseline question, not an observed conclusion. Regressed duration and time-from-trace policy must be specified for decode and tools (MVL:268). |
| C:954 | Injection can cause gated exclusions | **AGREE** | Matches P4:454–470 and ER:393–394; requires the assigned-attempt reporting in F6. |
| C:955–960 | Fixed white-box red team with no weight training is adequate | **DISAGREE** | A good bounded evaluation recipe, not evidence of saturated attack strength. State query access, reachable strategies, search effort and no-weight-training limitation; report empirical search curves. |

## External-source claims: offline verification limits

**Every primary-source content claim below is UNVERIFIABLE in this review.** No external source was fetched, and an earlier model's report of opening a paper is secondary evidence. The middle column records exactly what the repository does corroborate. This does not reject the papers or infer fabrication; it prevents citation laundering. URLs/titles in C are pointers for the lead's later source check, not sources newly verified here.

| Source / target lines | Permitted offline corroboration | Status and implication |
|---|---|---|
| SHADE-Arena, C:292,458–464,603,966 | LIT:64,141,241 and RP:160 support hidden-scratchpad dependence and reported best AUC .87. | **UNVERIFIABLE** for exact 17-pair/25-turn/threshold-80≈1%/Claude 3.6 and Gemini 2.5 rankings and their settings. Benchmark numbers do not transfer as operating guarantees. |
| SHADE “80% catch implies >20% FPR,” C:439,603 | Synthesis says it could not find it (C:439). | **UNVERIFIABLE**; keep dropped. Do not retain as an endorsed appendix fact. |
| SHADE temperature-0×3 convention, C:438,577 | Synthesis could not verify it; MON:112–117 defaults to temperature 0 but specifies no three-call convention. | **UNVERIFIABLE**; choose and register a new convention explicitly. |
| Kimpson/Baker/Graham, C:95,465,604,967 | LIT:93,747–750 repeats β=1.16, ≥.41, .059; MVL:264 describes a MATS page as the checked source. | **UNVERIFIABLE** for primary definitions/numbers/version/venue; reconcile the source provenance. A pilot ratio is an analogy, not the same β theorem. |
| Ctrl-Z, C:466,605 | LIT:159,249 repeats 58%→7% and ~5% usefulness cost. | **UNVERIFIABLE** for primary settings/results; do not translate into a JouleWise effect size. |
| Adaptive attacks on trusted monitors, C:467,969 | Named as a source in C; the local literature discusses adaptive-monitor risk. | **UNVERIFIABLE** for specific findings or the claimed white-box sufficiency. Appropriate motivation for development search. |
| MonitoringBench, C:468,695,976 | LIT:146,244,678–680 repeats 94.9%→60.3% for refined BashArena attacks. | **UNVERIFIABLE** for the primary comparison/settings; no numeric transplant to SHADE/readable. |
| Gargiulo/Kulp, C:469,690,968 | LIT:70,92,108,742–745 corroborates the telemetry-spoofing warning and workload setting. | **UNVERIFIABLE** for the original quotation/experimental scope. The local-reader trust argument also stands by direct threat-model reasoning. |
| Emmons et al., C:470,958,970 | C cites the paper but supplies no stored primary excerpt establishing a general inability theorem. | **UNVERIFIABLE**; “only with help” is an observed experimental scope claim, not a bound on all monitor evasion. |
| CoIn, C:471,605,980 | LIT:87,271,721–724 and RP:161 support “up to 94.7%” and software-count auditing. | **UNVERIFIABLE** primary figure; preserve “up to” and provider-artifact assumptions. |
| Token Inflation, C:472 | LIT:63,89,273,729–732 supports count manipulation/provider threat framing. | **UNVERIFIABLE** primary findings; useful adjacent threat model, not evidence that TM-A has count-forgery powers. |
| Async Control, C:473,979 | LIT:251 names the source; C supplies 6% FNR at 1% FPR. | **UNVERIFIABLE** primary number/context; an offline score is not an evaluated intervention protocol. |
| Wu et al., C:474,748,981 | RP:79 expressly distinguishes 335× cached batch-1 from 115× uncached→3.3× batched. | **UNVERIFIABLE** primary ratios; **do not infer** marginal batch-piggyback cost from them. |
| Pfau/Merrill/Bowman, C:475,693,972 | LIT:148,256,698–700 supports filler-token hidden computation. | **UNVERIFIABLE** primary theorem/empirical scope; the local fixed-work limit is independently explicit in ER:399–400. |
| Roger/Greenblatt, C:476,694,973 | Named source only for the precise use in this product. | **UNVERIFIABLE** primary mechanism/strength; retain encoded-visible reasoning as a tested or stated escape. |
| Tramèr et al., C:477,955–960,971 | C names the adaptive-evaluation methodology. | **UNVERIFIABLE** primary prescriptions; a fixed search budget/saturation curve is reasonable but does not prove attack completeness. |
| AI Control, C:478,605,974 | LIT:682–684 gives adjacent control framing. | **UNVERIFIABLE** primary results or a “trusted weak” mapping to this particular M2. |
| Baker et al., C:479,696,975 | LIT:143,246 supports monitor obfuscation under optimization. | **UNVERIFIABLE** primary details; no weight training is an explicit evaluated-attack limit. |
| Kale et al., C:480,605 | LIT:250 names weak-to-strong monitoring. | **UNVERIFIABLE** primary performance/requirements; “local” alone does not establish trusted-weak efficacy. |
| Control Tax, C:481,605 | LIT:97,159,252 supports financial/performance cost framing. | **UNVERIFIABLE** primary content; useful related work, not a quantified JouleWise overhead result. |
| Hua et al., C:447,977 | LIT:258,706–708 marks prior seat-only reading. | **UNVERIFIABLE** primary framework. Synthesis correctly does not base §§1–4 on it. |
| Angelopoulos/Bates, C:448,982 | No stored primary theorem is supplied here. | **UNVERIFIABLE** primary citation. The elementary rank/union-bound calculation was independently checked; its assumptions still must match the estimator (F2). |
| CoT Red-Handed, C:449,713,978 | LIT:257 marks seat-only source for a hybrid monitor. | **UNVERIFIABLE** primary performance; hybrid view remains print-only, with its own calibration if promoted. |
| Chkir / Ma, C:450 | LIT:71,126 records architecture-scaling motivation. | **UNVERIFIABLE** primary claims; a full-attention feature basis can absorb some hybrid effects in coefficients. Misspecification is a hypothesis to diagnose, not a demonstrated D residual cause. |

## What the product missed, and the next exact step

The main omissions are the **shared meter-launch call chain; exact versus fitted-score conformal assumptions; full SQ1 power; explicit SQ2 comparator cohorts and simultaneous inference; algebraically correct, conditional energy transport; genuine equivalence testing; per-channel DC fitting/uncertainty; exact token provenance; out-of-span and remote-work limits; assigned-attempt outcomes under attack-induced exclusion; dose-metadata blinding; and an inconclusive outcome category**. The larger PRE draft already supplies several safeguards that should not be lost in reducing Mac cost (PRE:149–175,304–342,453–462).

The lead's next exact step is to disposition F1–F9 against the addendum before implementation: correct the W1 meter premise, choose a defensible fit/calibration construction, replace SQ1/SQ2/SQ4 with fully specified estimands and a recomputed per-pair precision plan, and distinguish direct physical evidence from composed development estimates. Then freeze the manifests, legal adversary affordances, score/view/count policy, stopping/missingness rules and site-specific physical qualification. Obtain the owning registration/native gates before any new arm. This review makes none of those choices on the lead's behalf.

## Verification and remaining uncertainty

Verification was documentation/source inspection plus isolated Python 3.13 standard-library arithmetic. No repository runtime was imported. The calculations below reproduce the decisive power result; the run report records the additional arithmetic and source-chain checks.

```python
from math import comb
def tail(n, p, k):
    return sum(comb(n, j)*p**j*(1-p)**(n-j)
               for j in range(k, n+1))
# One-sided 90% exact lower bound is >= .5 iff this null tail <= .1.
for n in (6, 8):
    k = next(j for j in range(n+1) if tail(n, .5, j) <= .1)
    print(n, k, tail(n, .5, k), tail(n, .7, k))
# 6 6 .015625 .117649; 8 7 .03515625 .25529833
```

No unittest or compileall run was warranted for two Markdown-only additions; the standing rule prohibits the full suite. No MLX import or native test was attempted. **Lead outside this sandbox:** after integrating the reviewed kit with the ALIGN lane, run `python3.13 -B -m unittest tests.align.test_squeeze_native` (two tiny synthetic native MLX tests at `96dd7e78c:tests/align/test_squeeze_native.py:20–82`, no downloaded weights), then the owning real-cache/RNG, meter-clock/coverage, battery, site/dose, gate/deadman and replay qualifications under their own quiet-machine authority. The tiny tests alone cannot validate real model execution or energy detectability.

Primary-paper verification, actual meter streaming, model capability, E2 noise, backend equivalence, native injector integration and the final study's power remain open. I have not independently reproduced public pilot summaries or the later review branches' test results. The resulting verdict is **useful design direction, not a sound registration-ready squeeze study yet**.
