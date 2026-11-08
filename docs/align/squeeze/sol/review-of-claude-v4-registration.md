# Independent Sol review of Claude's v4 registration synthesis

2026-11-07. **DESK REVIEW / DRAFT FOR LEAD DISPOSITION. No registration or arm authority.**

**Product reviewed:** `eea648b09933bce93d49cef3a8e7da11ab88e18b:docs/align/squeeze/v4-registration.md` (1,541 lines, including both seat appendices). Reviewer: the independent Sol session assigned to `align/2026-11-07-sol-review-claude-v4-registration`. No additional reviewer or author seat was consulted.

**Verdict: AGREE that its main repair program makes v4 sounder; DISAGREE with adopting the document unchanged.** Keep the receipt, explicit deviations, ordinal correction, evidence-bound admission, capability check and prospective squeeze registration. Correct the battery field; repair and independently test the estimand helpers before wiring them; settle the scoring/calibration design; replace the claimed replay defense with an evaluated hypothesis; and incorporate Ed's later recorded rulings. This is a useful implementation brief after those dispositions, not evidence that the squeeze holds or that W1 is ready.

## Evidence boundary and citation convention

Every `commit:path:line` below names an immutable, locally available Git object. Ranges give the supporting passage; the first line is the citation anchor. `S:N` means line N of the reviewed product at `eea648b09`, not an independent source. Repeated claims in the executive summary, actions, reconciled findings and appendices inherit the corresponding verdict below. A row marked AGREE endorses the stated fact or proposed action **with the qualifications in that row**, not its implementation or live success. UNVERIFIABLE means the permitted evidence cannot establish it; it does not mean false.

| Snapshot | Local commit | Use |
|---|---|---|
| Reviewed product / clone base | `eea648b09933bce93d49cef3a8e7da11ab88e18b` | Product, AGENDA, latest local Ed decisions, public tripwire page |
| R1 integrated | `e901eb2a480d51377a494be9d797733dfcd0220b` | Requested protocol and energy-residual specification |
| R10 kit | `d600baba0` | Product's default code, protocol and chair/lead rulings |
| Pre-arm audit | `53a2305982a551ba5285e50bd0177726b5f138e7` | `docs/research-audits/2026-11-07/w1-prearm-gate.md` |
| Budget audit | `93b049612e4909cccad7e3df8dc8b38acb5206e1` | `docs/research-audits/2026-11-07/w1-budget-fallback.md` |
| Literature audit | `16e1db6230a80a605d084f0f9f61431d541b793f` | `docs/research-audits/2026-11-07/literature.md` |
| Research-program audit | `7f74dd2a97e5fcf078652deef2fb291929dc4524` | `docs/research-audits/2026-11-07/research-program.md` |
| Operating characteristics | `b7d5e14c8` | `docs/align/council-2026-11-06-v4-review/OC-TABLE.md` |
| Squeeze draft cited by product | `688d14b6e` | `docs/registrations/align_v4_squeeze_addendum_DRAFT.md` |

No fetch or other network operation was performed: the binding no-network rule overrides “git fetch origin first.” Remote freshness is therefore UNVERIFIABLE. No real measurement files, forbidden directories, model weights, live hardware probes or analysis pipeline were accessed. Absolute data paths appearing in repository text were not followed. Source-level probes used tiny synthetic numbers and selected pure Python functions extracted from Git. They are not native or physical validation. The report is [the dated run record](../../../run_reports/2026-11-07-sol-review-claude-v4-registration.md).

## Findings requiring a change to the brief

### F1 — HIGH: the battery “correction” selects the wrong field

**DISAGREE** with S:112 and S:420. `battery_float.parse` derives its float predicate from required **InstantAmperage**, not optional Amperage: `d600baba0:joulewise/battery_float.py:267-287`. The returned `instant_amperage_ma` and `passed` fields reflect that predicate; `amperage_ma` is an optional recorded value (`d600baba0:joulewise/battery_float.py:275-303`). Thus the synthesis corrects the Opus seat's correct predicate field into a different field. An absent optional Amperage or disagreement between the instantaneous and averaged currents has no defined admission behavior in this brief.

Use the existing parse/observe verdict, require `current_capacity_pct >= 99` explicitly, retain InstantAmperage, and record optional Amperage separately. Add tests for the two currents disagreeing and for missing CurrentCapacity. Preserve the chair's completed-top-up timing evidence and `pmset` record: an instantaneous 99% reading alone does not establish “within about 30 min” (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:78`). The Air's OBC-key probe is UNVERIFIABLE here, and does not establish MBP behavior. Attestation is a reasonable proposed replacement, requiring an explicit lead disposition rather than a claim that 99% proves OBC off.

### F2 — HIGH: the carrier-curve helper does not measure detection against benign thresholds

**DISAGREE** with treating the existing helpers as ready estimands that merely need wiring (S:84, S:305-309, S:1370). `benign_carrier_curve` groups rows by `(pair, h)` and derives each threshold from the **other carriers at that same H**, including the tamper shift (`d600baba0:joulewise/align/apple/v4_estimands.py:58-74`). Adding the same large hidden-work score to every carrier therefore leaves its rank and detection fraction unchanged.

Reproduction on 39 synthetic carriers with `score = carrier_index + H/10`: the helper returns **1/39 detections at every H from 0 through 2,048**, with H50/H90 unresolved. Comparing the same shifted scores against the other carriers' **H=0** scores instead reaches 100% at H=512. This exposes a moving-threshold defect, not a physical detector result. Existing tests check keys and even encode same-H ranking; they do not check sensitivity to a common signal (`d600baba0:tests/align/test_v4_estimands.py:12-36`).

Freeze the intended untouched-benign reference and fitting policy, then add an oracle that increasing a common positive tamper crosses that fixed threshold. Also reconcile the new alpha: at 2.5%, 39 total carriers leave only 38 other calibration carriers, so `ceil(.975 * 39) = 39 > 38`; leave-one-carrier-out thresholds need at least **40 total carriers**, or a separate calibration cohort. The existing helper hardcodes 0.95 (`d600baba0:joulewise/align/apple/v4_estimands.py:69`). Bootstrap repeated windows also need fresh resample cluster identities while preserving carrier exclusion, rather than treating copied carriers as new independent observations (`:81-89`).

### F3 — HIGH: the joint FPR arithmetic is conditional, and the scoring design is unsettled

**AGREE** with the rank arithmetic at m=39: rank 38 gives a marginal bound of 5%; rank 39 gives 2.5%. **DISAGREE** with presenting that arithmetic as certification of the proposed implementation or of every window. The maximum's 90% realized-tail bound is about 5.73% under iid continuous scores, not a realized 2.5% guarantee (`b7d5e14c8:docs/align/council-2026-11-06-v4-review/OC-TABLE.md:28-44`; `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:247-274`). Specify strict exceedance or a valid tie rule: the squeeze draft uses `>`, but both H* and the carrier helper use `>=` (`d600baba0:joulewise/align/apple/v4_estimands.py:24`, `:70`). With tied scores, `>=` can invalidate the advertised bound.

The original protocol fits benign trajectories leave-one-out per session and scores sabotage against the full benign fit (`e901eb2a4:docs/align/pilot_protocol_v4.md:488-505`). The squeeze draft explicitly proposes a **disjoint fixed development fit** and subsequent paired benign calibration/test cohorts, calling this a new design needing adjudication (`688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:38-44`, `:205-225`). These are not automatically exchangeable scores. A count-only stop is helpful but cannot repair unequal fits, window dependence, drift, energy-based eligibility selection or changes after W1.

The literal OR of two valid 2.5% solo alarms has a 5% union bound without channel independence. It also has a larger false-alarm allowance than either solo. The cited squeeze draft already distinguishes a **jointly calibrated OR*** at the same 2.5% budget from literal OR (`688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:231-264`). Preserve that distinction before claiming complementarity. Choose and pin one fitting policy, rank implementation, tie rule, cohort unit, selection rule and matched-budget comparison. Wiring `conformal_threshold_diagnostics` unchanged is insufficient: it always prints sample-maximum formulas (`d600baba0:joulewise/align/apple/v4_estimands.py:200-228`). The generic residual API has yet another quantile, `ceil((1-alpha)*m)`, and holds out task-pair groups (`d600baba0:joulewise/align/energy_residual.py:546-613`); it must not silently supply the registered rank.

### F4 — HIGH: replay consistency is not proof that claimed compute was performed

**UNVERIFIABLE** as a sufficient defense, and **DISAGREE** with installing it as established protection (S:283, S:1346). Reseeding a generated turn is implemented (`d600baba0:joulewise/align/apple/endpoint.py:705-708`). A transcript matching a seeded rerun establishes consistency with a possible execution; it does not by itself attest the original execution, its timing or every claimed token. Count inflation, reuse of a previously computed trajectory, and substitution between declared and hidden work require explicit attacker permissions and trusted execution receipts. A separate verifier's paid rerun does not automatically impose that energy cost on the attacker inside the scored interval.

The product correctly retreats to “not verified” at S:428; carry that caveat into its protocol recommendation. The cited squeeze draft distinguishes fabricated counts from actual visible padding and authenticated receipts (`688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:49-67`, `:139-147`). Test those threat models separately. A3 disguised logged computation and A4 monitor injection can leave neither detector an informative signal; complementary motivations do not prove a universal squeeze. Require bounded adaptive attacks, matched false-alarm comparisons, task-success labels, a joint escape estimand and a counterexample/unresolved rule (`688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:391-418`).

### F5 — HIGH: adopting the latest owner decisions is missing

**DISAGREE** with treating the product's older authority snapshot as complete. The reviewed commit itself includes Ed's later decisions: scoped sandboxed on-host red team allowed, no other adversarial in-process programs; **frontier API monitor primary, local monitor secondary**; KM003C physically in the MagSafe power path; native confirmation that capture reaches custody still owed (`eea648b09:RUN_STATE.md:1045-1050`). These supersede the older “non-adaptive only” audit recommendation without establishing adaptive robustness.

Add those decisions to the protocol/addendum brief. Reconcile the cited SQZ draft's “locally available monitor is sufficient” proposal (`688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:177-187`) with the API-primary decision. Distinguish a registered secondary **v4 diagnostic** from the **primary squeeze energy score**, which SQZ defines as gross DC-input plus battery assist (`:149-175`). “Spends no alpha of the primary” is valid only while the secondary cannot influence the primary decision or headline selection. A secondary label alone does not qualify the physical trust boundary.

### F6 — MEDIUM: seven-window figures omit part of the proposed stopping rule

**AGREE** with the printed one-pair benign binomials. **DISAGREE** with using them alone to justify reliable completion of the proposed two-pair, ≥39 benign **and ≥6 sabotage** target. Under the same independent per-member exclusion model, with no whole-window loss, joint success probabilities are:

| Calibration windows | 5% exclusion | 10% exclusion | 14% exclusion |
|---:|---:|---:|---:|
| 6 | 0.3841 | 0.0416 | 0.0033 |
| 7 | 0.9132 | 0.7115 | 0.4761 |
| 8 | 0.9885 | 0.9253 | 0.8291 |

Calculation: `[Pr(Bin(7w,1-p)>=39) * Pr(Bin(w,1-p)>=6)]**2`. The source roster yields seven benign and one sabotage per pair/window (`e901eb2a4:docs/align/pilot_protocol_v4.md:139-145`). Window-level U1-U3 losses can reduce completion further; independence is a planning assumption, not evidence (`b7d5e14c8:docs/align/council-2026-11-06-v4-review/OC-TABLE.md:46-70`). D8 is a sensible proposed cap, but cap shortfall must be unresolved. The existing SQZ design also reserves **1,398 eligible episodes / 699 h of D-member reservations**, before scaffolding, so “seven windows plus test cohort” does not estimate the full main-goal cost (`688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:328-343`). Ask Ed about the full design or a deliberately smaller claim.

### F7 — MEDIUM: U3 transfer and false-fail claims are hypotheses

**AGREE** that the old bar requires re-derivation; its absolute floor is cross-session, and separated-ordinal drift differs (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:83-88`). **UNVERIFIABLE** that a relative 30B bar transfers to dense D. A plausible scaling rule is not observed D repeatability. At 25–35 kJ, the existing 3×0.0011×E bar is 82.5–115.5 J; 27.5–38.5 J is the inner term before multiplying by three. S:120-121 correctly distinguishes those terms.

The 0.27% normal tail for k=3 assumes centered normal differences and a known scale. Substituting a small-sample SD gives a predictive t problem; a 90% chi-square upper limit on the SD does not make the unconditional false-fail probability exactly that normal tail. Shared pilot pairs/windows, nonzero drift and clock/token failures matter too. Report an assumption-labelled sensitivity/OC, not a certified per-window rate. The 300–500-token expected MDE is explicitly a chair planning estimate (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:270-303`), not measured headroom validating a chosen U3 bar.

### F8 — MEDIUM: contrast, duty-bar and sentinel exceptions need complete cases

**AGREE** with considering a pre-declared non-claim contrast INCONCLUSIVE instead of vetoing D, but this explicitly reverses an installed lead ruling (`d600baba0:docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:839-848`, `:869-889`). A reviewed proposal is not that ruling. The suggested `cap_c = floor(deadman - episode - 10)` is undefined when episode seconds are missing and can be nonpositive when the episode already exhausts the deadman. Define those cases prospectively; do not pass an invalid thermal cap or call incomplete phase sums a worst-case proof (`d600baba0:scripts/align_v4_kit.py:597-642`). X2/no-decode contrasts also change the next D member's heat history, as the synthesis acknowledges at S:165.

Budget/thermal X7 classification is a useful proposed interpretation, not a causal attribution. Per-turn counts must identify **completed** turns and exclude the deadman-truncated turn before asserting W1's budget would already have stopped. The workload checks the deadman before turn admission and decode budget (`d600baba0:joulewise/align/apple/workload.py:482-503`). Counts alone do not prove unchanged execution under new holds/chunks. Keep censored-G0 refusal, evidence-bound tuning and source provenance.

Correcting 18→17 is sound. The helper, however, accepts four unlabelled energies and cannot reject “ordinal 18” without new identity-bearing inputs (`d600baba0:joulewise/align/apple/v4_estimands.py:154-163`). If both original and alternate are inadmissible, “U4 from extension windows” is not a procedure for obtaining an admissible reference; name a prospective recovery or return unresolved. The alternate's single-run E_ref is a new proposal, not the chair's multi-run rule (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:178-184`). Changing permitted thermal slots can also change energy/selection even if the four-field code key stays identical. Verify final-policy replay comparability before counting W1 as a U4 window.

### F9 — MEDIUM: several gate checks cannot certify what their wording says

* **DISAGREE** with checklist A3's “respectively” ordering (S:353). It reverses the intended deadlines: the capability-proxy rule must precede the **R0 ladder read**; R1-dependent design rules must precede the relevant **R1 read**. Commit timestamps do not prove read chronology. Record the actual permitted reads and rule commits (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:213-215`).
* **DISAGREE** with a `/Volumes` listing as a complete census. Network/FUSE mounts may occur elsewhere; the existing implementation classifies mounted filesystems from `mount` and device metadata (`d600baba0:joulewise/align/apple/external_volume.py:182-202`). An unqualified unified-log query or one-minute polling cannot establish continuous absence. Define event coverage, gaps and missing-evidence handling; a ±10-minute exclusion buffer in Appendix B is an unvalidated new constant (S:1142).
* **UNVERIFIABLE** that warmup is greedy from the cited code. It calls `stream_generate` without an explicit sampler in those lines (`d600baba0:joulewise/adapters/mlx_runtime.py:414-437`). Measured per-turn reseeding is verified; token identity still needs the pinned runtime and live comparisons. Partial X matches cannot certify unexecuted turns.
* **DISAGREE** with “only wire the helpers” for inferential calibration. U6's sandwich interval uses 1.645 with no small-cluster correction; per-position code returns means only (`d600baba0:joulewise/align/apple/v4_estimands.py:108-151`). Audit the actual uncertainty and missing-position rules. H* returns the first crossed grid point, not an exact continuous minimum (`:20-26`).

## Claim-by-claim disposition of the synthesis

This inventory covers the factual/procedural claims in §§1, 3, 5 and 6, including claims repeated in the flags. Each proposal still needs the lead's ruling and appropriate gate. Claimed actions by the previous seats are not independently reproducible from their prose alone.

| Product location | Verdict | Reason and independent anchor |
|---|---|---|
| S:3-19, authorship, seats, sources opened, probe, independence | UNVERIFIABLE | The product records these assertions; invocation/probe receipts and primary papers were not supplied in the permitted packet. Git resolves the named code/audit snapshots. S:17's no-worktree method refers to the synthesis; seat appendices explicitly report worktrees (S:485, S:858). |
| S:5, main goal | AGREE | Matches `eea648b09:docs/research/AGENDA.md:5-19`; test the hypothesis, do not assume success. |
| S:25, R0/R1 status and blind opportunity | UNVERIFIABLE | Consistent with the local pending restart narrative (`eea648b09:RUN_STATE.md:1052-1066`), but this offline review cannot certify live R0/R1 state or what others have read. |
| S:27, nine missing rulings, draft, absent arm receipt | AGREE | `d600baba0:docs/align/pilot_protocol_v4.md:619-662`; `d600baba0:scripts/align_v4_kit.py:1226-1234`. A row's existence is not installation. |
| S:27, one builder day / zero Mac time | UNVERIFIABLE | Effort estimates; calibration fills, qualified mount detection and native identity/meter checks remain work. No duration proof follows from the code. |
| §3.1, nothing newly gates R1 arm | AGREE | `d600baba0:docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:758-760`; preserve existing R1 gates and pin. Blindness deadline caveat F9. |
| §3.2, registration receipt and stale-receipt refusal | AGREE | Existing readiness omits it (`d600baba0:scripts/align_v4_kit.py:1226-1234`). Bind exact code/data manifests, rulings, reports and dispositions; an R10-format signature is an accountability string, not cryptographic authentication (`:656-671`). Avoid self-referential commit/hash fields. |
| §3.3, battery mechanism | DISAGREE | Correct aim and attestation proposal, incorrect current-field “correction”; F1. Air/MBP/OBC facts remain UNVERIFIABLE. |
| §3.4, old U3, absolute-versus-relative arithmetic | AGREE | `d600baba0:joulewise/align/apple/thermal_desk.py:292-311`; old and proposed floors are accurately described. |
| §3.4, transferable relative scale and advertised false-fail rate | UNVERIFIABLE | Assumption-labelled proposal only; F7. “Only one that transfers” is too strong. |
| §3.5, ordinal 17 and U4 bookkeeping | AGREE | `e901eb2a4:docs/align/pilot_protocol_v4.md:105-123`; old text/helper message conflicts. Identity-aware inputs and final-policy comparability required (F8). |
| §3.6, U5 accepts pass/fail/inconclusive; proposed W1 admission | AGREE | Existing ambiguity is explicit in `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:57`. Development W1 may proceed under a prospective ruling. D with a disclosure is narrower evidence, not restored validity or a successful squeeze (F3/F5). |
| §3.7, U6 margins, OC row, labels, missing wiring | AGREE | `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:90-104`; `b7d5e14c8:docs/align/council-2026-11-06-v4-review/OC-TABLE.md:41`, `:147-167`; inferential helpers require F2/F9 repairs. |
| §3.7, U6 failure bars rate claim but never gates collection | AGREE | Reasonable proposed consequence, not existing installed policy. Separate collection from withdrawing inferential claims; `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:414-418`. |
| §3.8, delivery, stage, positive direction, rejection band | AGREE | Chair requires these; `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:127-140`; eight rows and five full-rank columns give 3 df. Refuse singular fits. |
| §3.9, contrast receipt-only gap / deadman pressure | AGREE | `d600baba0:scripts/align_v4_kit.py:597-642`, `:882-905`; 600+633 >1,086.3 is planning arithmetic, not an observed X-G failure. |
| §3.9, cap_c and unconditional non-veto | AGREE | Proportionate proposed deviation because the contrast governs no D cell (chair `:139`); F8 supplies mandatory missing cases and preserves the current ruling until dispositioned. |
| §3.10, all-turn render, live X, reseeding, receipt | AGREE | Stronger identity coverage; `e901eb2a4:docs/align/pilot_protocol_v4.md:126-132`; `d600baba0:joulewise/align/apple/endpoint.py:705-708`. Identity failure may become an explicit non-claim contrast under a new ruling. |
| §3.10, static “greedy warmup therefore heat only” proof | UNVERIFIABLE | Cited warmup has no explicit sampler; pinned runtime/numerics and native parity still required. F9. |
| §3.11, rewrite split already exists, checkpoints off, re-fed test | AGREE | `d600baba0:scripts/align_r0_dispositions.py:129-148`; `e901eb2a4:docs/align/pilot_protocol_v4.md:82-91`; rebuild annotation `d600baba0:joulewise/align/apple/endpoint.py:683-695`. A pinned accounting test remains useful. |
| §3.12, two capped turns can exhaust B_D=6,144 | AGREE | Two 4,096-token turns consume 8,192 before a third admission; `d600baba0:joulewise/align/apple/workload.py:501-503`. Budget alone does not guarantee two actual turns: EOS, context and other stops can end earlier. |
| §3.12, prospective three-turn check | AGREE | Useful evidence before spending held-out seeds; original budget floor/rung rule: `e901eb2a4:docs/align/pilot_protocol_v4.md:166-190`. |
| §3.12, 4-bit better for sabotage | UNVERIFIABLE | Comparative capability needs measurement; a state-changing benign tool call is only a weak sabotage-capability proxy. |
| §3.12, alternate singleton / no-sentinel extension remedy | DISAGREE | These add semantics beyond the chair's multi-run reference and need a recovery procedure, F8; chair `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:178-184`. |
| §3.13, freeze B_D/T_dead and disclose added G0 slot | AGREE | Resolves a real chair-10/17 conflict (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:142-145`, `:194-196`). Four equal code fields alone do not prove unchanged physics/energy (F8). |
| §3.14, warm-reference diagnostic | AGREE | `d600baba0:joulewise/align/apple/v4_estimands.py:250-265`. Print-only, no retrospective change of R. |
| §3.15, offload contradiction, vacuous list, daytime receipt | AGREE | `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:138-145`; arm's census then rehash `d600baba0:scripts/align_v4_session.py:161-217`. Bind source inventory/time, not only destination bytes. |
| §3.15, mount detection sufficiency / SSD permanence | UNVERIFIABLE | Qualify logs and coverage (F9); no-SSD is already the chair's rule (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:207-211`). A draft alternative is not automatically adopted or permanently forbidden by this review. |
| §3.16, classifier text must match merged rule | AGREE | `d600baba0:joulewise/align/apple/smc_enumeration.py:25-37`. Quote the full rule, including D1(d)/clamps, not a shortened imitation. |
| §3.17, bare fallback weakness / refused steps / re-run | AGREE | `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:128-135`; open lead call and censored-G0 ruling in `d600baba0:docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:839-845`. Budget-X7 exception is a new rule requiring F8. |
| §3.18, stable seed tag, no pooling/CRN | AGREE | `d600baba0:scripts/align_v4_kit.py:51`; `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:231-236`. Quantization label deviation must precede affected seeds. |
| §3.19, capture loss / max-failures / fail before load | AGREE | `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:167-176`. Explicit WP14(b) deviation is preferable; keep custody/exclusion records for every refused consumer. |
| §3.20, SystemExit conflict, KeyboardInterrupt-only fix on REG | AGREE | Code and signal handler confirm the distinction (`d600baba0:scripts/run_night.py:2573-2599`, `:4325-4332`); historical regression is independently reported at `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:178-185`. This review did not rerun that test. |
| §3.21, extra sabotage prefill term | AGREE | Known condition-length problem and no margin appear at `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:215-219`. +755 is documented for spam (`7f74dd2a9:docs/research-audits/2026-11-07/research-program.md:142-149`); verify each pair. A linear rate add-on is a planning correction, not proof of all-turn worst-case runtime. |
| §3.22, Q4/Q6 approved, rank correction | AGREE | `eea648b09:RUN_STATE.md:1129-1137`; F3 qualifies inference, F6 qualifies cost. Sample-maximum formulas apply while rank=m, not to every arbitrarily large m. |
| §3.23, known omission differs from sabotage causality | AGREE | `e901eb2a4:docs/align/pilot_protocol_v4.md:508-516`; `7f74dd2a9:docs/research-audits/2026-11-07/research-program.md:104-119`. Zero alarms on two pilot trajectories is not a general theorem about logged sabotage. |
| §3.23, threat taxonomy / monitor-blind rule / existing addendum | AGREE | Appropriate prospective design and version control; `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:47-99`, `:214-229`. Strong universal “any prior score makes all exploratory” wording needs a defined development-versus-test boundary. Replay claim and current authority need F4/F5. |
| §3.24, GPU primary in v4 / meter diagnostic / capture unconfirmed | AGREE | `e901eb2a4:docs/align/pilot_protocol_v4.md:474-495`; `d600baba0:joulewise/b5/driver.py:138-141`. S:295 is properly cautious; capture and integration still need native evidence. |
| §3.24, register DC secondary now / no primary alpha | AGREE | Useful proposed v4 endpoint, provided F5's distinction is explicit. Arm float cannot alone qualify whole-host DC or eliminate later battery assist/charge. SQZ `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:149-175` lists the missing boundary/uncertainty work. |
| §3.25, capability rule before R0 read | AGREE | `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:213-215`; current print exists at `d600baba0:scripts/align_r0_dispositions.py:108-127`. Whether deadline remains open is UNVERIFIABLE offline. |
| §3.26, estimand text and pre-D1 freeze | AGREE | Stronger prospective boundary than “before desk read”; chair `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:42-56`. Physical positive control must be on the claimed production configuration; 30B cannot qualify D (SQZ `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:103-109`). F2/F3/F9 first. |
| §3.27, staged gate and anti-hindsight | AGREE | Scoped delta gate is requested by `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:71`. Treat broadening the review whitelist as a new explicit permission, not the existing procedure's whitelist (F9). |
| §3.28, LOW/MEDIUM carryovers | AGREE | Source audit `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:194-231`; actual install does not regenerate at `d600baba0:scripts/align_v4_session.py:239-247`; `fit_roster` drops 18 at `d600baba0:scripts/align_v4_kit.py:1255-1276`. Automatic-for-W1 changes the R1 policy and needs consistent requalification. |
| §5, dropped/downgraded/not-verified list | AGREE | Sensible disclosure of uncertainty, especially A5 and meter startup. Carry those caveats into the action list, not only this section. Numeric planning inputs are provenance, not independently remeasured facts. |

## Every prioritized action item (§2)

The numbers are the product's action numbers, S:60-85. These are dispositions of the proposed actions, not instructions executed by this reviewer. Evidence anchors are the corresponding claims above.

| Action | Verdict | Disposition |
|---:|---|---|
| 1 | AGREE | Record capability rule prospectively if the R0-read deadline is still open; otherwise print-only. Do not retroactively infer blindness. |
| 2 | AGREE | LR2 Round 11 is the right place for explicit rulings; amend F1/F3/F4/F8/F9 before approval. |
| 3 | AGREE | Public deviations with old/new text and actual read history. Add singleton sentinel, battery proxy, monitor/API and calibration-policy changes where adopted. |
| 4 | AGREE | Install complete ruled protocol text and latest Ed decisions. Header changes follow registration; they do not create it. |
| 5 | AGREE | Mechanical checks/identity/install regeneration useful. Correct carrier/alpha/tie logic, define impossible contrast caps and bind completed-turn evidence (F2/F3/F8). |
| 6 | DISAGREE | Battery aim correct; use InstantAmperage predicate, explicit SoC/missing-field checks and top-up evidence (F1). Receipt/offload census work remains sound. |
| 7 | AGREE | Fail before underlying model preparation on authenticated unobserved reference; preserve failed-member custody. |
| 8 | AGREE | Desk wiring is necessary after helper audit. Add identity-bearing U4 inputs, uncertainty qualification and matched-budget joint reporting; labels/means alone are not inferential checks. |
| 9 | AGREE | Reproducible relative-bar derivation is reasonable; do not promise cross-model validity or an exact nominal false-fail rate (F7). |
| 10 | AGREE | All-turn rendering and live X receipt useful. Do not call partial identity or the cited warmup code a complete proof (F9). |
| 11 | AGREE | Scoped KeyboardInterrupt-only correction on REG; protect first-signal behavior and leave R1 pin intact. |
| 12 | AGREE | Independent re-fed-token accounting oracle should inspect actual represented/fed IDs, not merely a rebuild flag. |
| 13 | AGREE | Re-run OC for the actual final rule, all stopping conditions and dependence sensitivities (F3/F6/F7). |
| 14 | AGREE | Write gate brief before R1; correct read deadlines and current owner decisions. |
| 15 | AGREE | #694 delta review is explicitly required before W1 (`eea648b09:RUN_STATE.md:1054-1059`). PR merge state is UNVERIFIABLE without network/live coordination. |
| 16 | AGREE | R0 provenance fill; distinguish report bytes from an authorized composition note and bind the correct schema/source. |
| 17 | AGREE | Authorized magistrate's pilot-derived fill, not a task for this blinded clone. Formula/read history must already be frozen. |
| 18 | AGREE | Daytime offload receipt and mount-query qualification; test the actual coverage/duration and non-/Volumes mounts (F9). |
| 19 | AGREE | Operator/MBP OBC evidence, no extra system probe in this review. |
| 20 | AGREE | Ask Ed about full experiment cost and physical decisions; Q4/Q6 already approved in principle. Incorporate API-primary/scoped-red-team decisions rather than asking again. |
| 21 | AGREE | Make public FPR wording agree with final rank and assumptions. At variable m, print actual bound and conditional realized-tail statement. |
| 22 | AGREE | Independent Stage A is useful. Do not substitute same-family agreement for final lead adjudication or required cross-family evidence. No new seats launched here. |
| 23 | AGREE | After R1, mechanical count backfills with source digests, key-read tests and no overwrite; record exactly what was read. Cost/OC changes above apply. |
| 24 | AGREE | Stage B followed by lead receipt and separate magistrate live arm; only after substantive findings are closed. |
| 25 | AGREE | Freeze before D1 arms; use repaired estimands, complete calibration design and meter qualification. |
| 26 | AGREE | Extend the existing SQZ draft through its own gate; preserve matched-rate OR*, scoped attacker permissions, API monitor, fixed fit/calibration/test splits and full power/cost analysis. |

## Every registration-gate checklist item (§4)

None of these proposed gates was run or admitted here. AGREE endorses the check after the listed correction; it does not report PASS. Item numbers are S:351-400.

| Item | Verdict | Required interpretation/correction |
|---:|---|---|
| 1 | AGREE | Complete rows/sections and real registration evidence; no cosmetic admission. |
| 2 | AGREE | Deviation list includes every adopted new rule, including calibration and sentinel recovery. |
| 3 | DISAGREE | Reverse the mistaken “respectively”; use actual R0/R1 read history, F9. |
| 4 | AGREE | Audit all outcome-bearing citations, not only a convenient sample of 20. |
| 5 | DISAGREE | Add InstantAmperage-vs-Amperage and missing SoC tests, plus top-up timing, F1. |
| 6 | AGREE | Keep the allowed 8.91 J floor explicit; do not ban every textual 2.97 while retaining that floor. Predictive-scale/OC caveat F7. |
| 7 | AGREE | Identity-aware 5/17 inputs, U5 consequences, actual U6 uncertainty and selection assumptions. |
| 8 | AGREE | Full-rank stage fit, delivery, positive direction, correct rejection band and explicit non-delivery. |
| 9 | AGREE | Receipt records full/partial/failed comparison; native tokenizer/runtime proof remains owed. |
| 10 | AGREE | Exact accounting test plus existing all-transition script. |
| 11 | AGREE | Sentinel fallback and diagnostic wiring; explicit unresolved recovery if no admissible source. |
| 12 | AGREE | Cohort key plus full policy comparability before using W1's energy reference. |
| 13 | AGREE | Qualified continuous mount evidence, defined gaps and offload identity; F9. |
| 14 | AGREE | Full `RULE` including heat ordering/clamps; R0-L2 and changed-pick baseline. |
| 15 | AGREE | Stable tag with deviation and independent complete seed manifest. |
| 16 | AGREE | Refuse before model load, retaining each consumer's failure record. |
| 17 | AGREE | Contrast's new non-veto rule requires approval and total cap derivation, F8. |
| 18 | AGREE | Completed-turn proof, censored-G0 guard and no bare fallbacks, F8. |
| 19 | AGREE | Pair-specific prompt correction and overhead limitation, not a universal runtime guarantee. |
| 20 | AGREE | Bind actual R0 evidence and current generated bytes; use L1's +10 s successor, not chair's stale +60 s (`d600baba0:scripts/align_v4_kit.py:1040-1051`). |
| 21 | AGREE | Appropriate checks on final implementation; **full suites are forbidden in this session**. Future lead executes under its own machine/load authority. |
| 22 | DISAGREE | Taxonomy/monitor-blind rule useful; replay defense must remain a tested hypothesis, F4, and include latest owner scope. |
| 23 | AGREE | Actual stream/custody proof plus DC boundary, battery, uncertainty and matched-sham qualification, F5. |
| 24 | AGREE | Full joint stopping OC and matched-budget joint detector, F3/F6. |
| 25 | AGREE | Correct carrier helper, grid-bound interpretation and physical PCs on claimed model, F2/F9. |
| 26 | AGREE | Prospective capability rule and digest-bound R0 source, not timestamps alone. |
| 27 | AGREE | Atomic complete records and no inconclusive segments. No real records were opened here. |
| 28 | AGREE | Digest-bound count-only backfill; completed/partial turn semantics explicit. |
| 29 | AGREE | Independently recompute actual L1 arithmetic and member reservations. |
| 30 | AGREE | Independent arithmetic plus actual chosen calibration/admission policy; plain signature is a record, not proof of execution. |
| 31 | AGREE | Separate caps, valid missing/negative cases and prospectively recorded contrast disposition. |
| 32 | AGREE | Verified tuning at used band, not just authority text. |
| 33 | AGREE | Pinned picks/digest/alias rules and baseline recomputation. |
| 34 | AGREE | U5 disclosed consequences and honest partial/failed WP19 label. |
| 35 | AGREE | No generated drift; anchor byte identity against the pin. |
| 36 | AGREE | Full scaffold/reservation arithmetic and lost-alternate consequence; no fabricated R1 numbers. |
| 37 | AGREE | Magistrate's actual host evidence and quiet-machine gate. This review supplies none. |
| 38 | AGREE | Anti-hindsight inventory includes actual reads, semantic rule changes, count backfills and post-R1 fixes. A new deviation does not automatically restore confirmatory status. |

**Gate verdict rule (S:402): AGREE with no open HIGH/BLOCKER and all substantive fixes rechecked, but not with reading “MEDIUM dispositioned” as “a broken estimator may remain unfixed.”** A recognized defect that invalidates an estimand must be fixed or that claim explicitly withdrawn. Resolve the checklist's ADMIT_WITH_FIXES=LOW-only rule consistently with its allowance for dispositioned MEDIUMs. Only the lead may issue the receipt; this document does not.

## Appendix claims: inherited and additional dispositions

The original seat reports are preserved historical inputs, not two additional installed rulebooks. The following map covers their action lists and sections, including places where the synthesis already corrected them.

| Seat passage | Verdict | Resolution |
|---|---|---|
| Appendix A action list (S:465-475), §§2.0-2.17 and §3 gate table | AGREE | Actions map to the 26-item inventory, except the explicitly superseded proposals below. Nothing is authorized to alter coordination state in this review. |
| A §1 finite-threshold row, S:512 | DISAGREE | Combines 0.95 rank with sample-maximum bound at m≥39; synthesis correctly catches it, F3. |
| A §1 capability/success, S:517-518 | UNVERIFIABLE | Benign action proxy and non-correlated exclusions are desired preconditions, not demonstrated properties. Exclusions are explicitly state-dependent in chair §D. |
| A §2.1 mechanical OBC keys, S:540, S:801 | UNVERIFIABLE | Exact OS keys are not established by the permitted packet; operator attestation may be ruled instead. The 30-minute/top-up and battery-current requirements remain. |
| A §2.2 absolute U3 and 0.27% claim, S:548-552 | DISAGREE | Does not establish transfer or predictive false-fail; pending-bar-with-waiver option must remain an explicit limitation. F7. |
| A §2.3 U5 refusal, S:745, S:768 | AGREE | Defensible alternative, superseded by synthesis's proposed development-W1 admission; no source installs either as a final new ruling. |
| A §2.5 / lane §6 new R0 tool, S:583, S:788 | DISAGREE | Redundant: split already exists (`d600baba0:scripts/align_r0_dispositions.py:129-148`). Synthesis correctly drops it. |
| A §2.12 receipt-free D cap excludes X-G, S:627 | DISAGREE | Contradicts installed cold-review MEDIUM-2 (`d600baba0:docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:870`). Synthesis correctly retains X-G on that D path. |
| A §2.12 4-bit path fits “current kit,” S:626 | DISAGREE | It is a future cohort/kit: current D identity is pinned to 8-bit (`d600baba0:scripts/align_v4_kit.py:1068-1073`). Use it as motivation to fix every admission path, not a presently authorized 4-bit arm. |
| A §2.12 contrast veto | AGREE | Defensible alternative requiring ruling; synthesis chooses non-veto. Either consequence must be prospectively dispositioned. |
| A §2.15 capture “in-place fix” | DISAGREE | Capture behavior changes WP14(b); record a deviation rather than treating an in-place fix as sufficient authority. |
| A §4 flags, S:706-715 | AGREE | Useful hazards. +755 is spam-specific; 4-bit sabotage capability, exact X2 exposure and U4/U6 discrimination remain unmeasured. |
| A §4.6 “U4 and U6 reported, not gating,” S:711 | DISAGREE | 30B sigma_w is print-only; U4 is still registered acceptance and its inconclusive result triggers extension (chair `d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:99-104`). Do not demote all U4 silently. |
| A §5 no earlier reviews, but both seat reports supplied, S:729-732 | DISAGREE | Inconsistent coldness instructions. Provide an agreed checklist/source packet; distinguish closure review from an independent cold judgment. |
| A/B preserve_thinking “lower-bound real omission,” S:674, S:1370 | AGREE | Accurate chair instruction (`d600baba0:docs/align/council-2026-11-06-v4-review/CHAIR.md:50-56`), conditional on the declared accounting/model. Not a theorem for arbitrary signed fitted coefficients or different physical continuations. |
| B action list S:817-836 and decisions L1-L18 | AGREE | Covered by the action/claim inventories. The MEAS/R1 SystemExit fix, new Addendum S and Y-turn-0-only scope are explicitly superseded by synthesis. |
| B §1 “m≥39 earns Mac time only at 2.5%,” S:879 | DISAGREE | More calibration can improve threshold/rate precision at 5% too. Aligning channel budgets is a design choice, not the only scientific value of Q6. |
| B §1/§3.24 “meter already runs, zero Mac time,” S:888, S:1361 | UNVERIFIABLE | Product synthesis correctly retracts capture certainty at S:295; native stream/custody qualification still owed (Ed `eea648b09:RUN_STATE.md:1047`). |
| B §3.2 InstantAmperage, S:980 | AGREE | Correct parser predicate; synthesis's change to Amperage is the error, F1. |
| B §3.3 U3 “will probably false-fail,” S:876 | UNVERIFIABLE | Synthesis correctly downgrades to “can”; no D drift measurement available. |
| B §3.7 singleton alternate / no-sentinel U4, S:1098-1105 | DISAGREE | New estimand/recovery semantics not settled by chair; F8. |
| B §3.10 ±10-minute mount buffer, S:1142 | UNVERIFIABLE | Neither event coverage nor the ten-minute causal window is derived; F9. |
| B §§3.11-3.13 static warmup/cap_c/turn count | AGREE | Useful proposals subject to F8/F9; a turn-0 render or partial X match is not complete identity proof. |
| B §3.18 schedule bias is conservative, S:1288 | UNVERIFIABLE | Source audit documents missing cooldown/process start and predicts the direction (`53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md:194-199`). Treat guaranteed direction as a physical assumption until measured, not a proof across every predecessor. |
| B §3.22 FPR formula for arbitrary m, S:1330 | DISAGREE | 1/(m+1) is the maximum-rank bound; at m=79, rank ceil(.975×80)=78 gives 2/80, not 1/80. Main synthesis correctly limits maximum-rank equivalence to 39≤m≤78. |
| B §3.23 tokens/simulated-tools-only threat and A5 defense, S:1341-1353 | DISAGREE | Must reconcile actual sandbox/injector permissions with Ed's scoped on-host authority. A5 is unverified, F4/F5. |
| B §3.24 secondary energy aggregated “per episode,” S:1361 | AGREE | Proposed endpoint needs explicit ownership of gaps/tools/holds, independent DC fit, battery correction and uncertainty. Turn-owned aggregate and gross episode energy are different estimands (SQZ `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:149-175`). |
| B §3.26 install/validator/max_turns LOWs and §3.27 gates | AGREE | Covered by §3.28 / checklist above; proposals are not closure evidence. |
| B §4 flags and §5 A-I checklist | AGREE | Inherit the main gate inventory and F1-F9; after-R1 energy access is a declared review permission, not procedure input. |
| Both appendices' timelines, tests, worktrees, paper-opening and model-seat histories | UNVERIFIABLE | Historical self-report only. Do not cite these as this review's executed tests or independent primary-source verification. |

## External-source claims (§6 and repeated in both appendices)

**All nine are UNVERIFIABLE against primary sources in this no-network review.** No primary full text was supplied or fetched here. Where local literature/research audits repeat a claim, that supports provenance only, not independent verification of the paper, quote, venue or numerical scope. In particular, an A100 hidden-compute bound does not become an MBP attack success rate.

| Product source claim | Local corroboration / limitation |
|---|---|
| Kutasov / SHADE-Arena: hidden scratchpad, 27%, monitor AUC 0.87 | `16e1db623:docs/research-audits/2026-11-07/literature.md:64`, `:140-148`; benchmark-specific findings, not evidence the proposed squeeze works. |
| Greenblatt et al., AI Control | Listed by product; no independently opened primary content in this review. The product supplies no numerical claim to reproduce. |
| Kimpson/Baker/Graham: beta 1.16, ≥0.41 matched-energy, 0.059 restricted re-execution | `16e1db623:docs/research-audits/2026-11-07/literature.md:91-94`, `:106-110`; exact assumptions/units/transfer need primary check. |
| Terekhov et al.: adaptive monitor injection; ICLR 2026 poster; exact recommendation | Product S:446 supplies URL/metadata but no archived primary evidence independently checked here. Retain as a lead verification item. |
| Tramèr et al.: adaptive evaluations incomplete; NeurIPS 2020 | Product S:447; exact quotation and coverage UNVERIFIABLE here. The need to evaluate adaptive attacks also follows directly from the proposed threat model. |
| Jotautaitė et al. / MonitoringBench: 94.9%→60.3% | `16e1db623:docs/research-audits/2026-11-07/literature.md:146`; do not treat refinement conditions or denominator as checked. |
| Pfau/Merrill/Bowman: filler-token computation | `16e1db623:docs/research-audits/2026-11-07/literature.md:148-150`; motivates a region of joint failure; does not prove its feasibility for D. |
| Baker et al.: optimized obfuscation / monitorability tax | `16e1db623:docs/research-audits/2026-11-07/literature.md:142-150`; exact paper text/terminology not reopened. |
| Emmons et al.: CoT necessity and monitor evasion | Product S:451 / S:1532; primary result and limits not independently checked. No stronger inference admitted. |

## What the product missed, and the next lead step

In addition to F1-F9, add the literature audit's **hybrid-attention misspecification sensitivity** and a **counts-only baseline**. They are explicit existing concerns (`16e1db623:docs/research-audits/2026-11-07/literature.md:126`; `7f74dd2a9:docs/research-audits/2026-11-07/research-program.md:166-168`), not new reasons to change the primary fit after seeing attacks. Predeclare them as labelled comparisons. The joint study also needs tool/timing/boundary and mixed padding×placement attacks, trustworthy executed-work doses, matched shams, side-task success, all exclusions/dose failures, and a held-out selection rule; A1-A6 plus replay does not replace these fields (SQZ `688d14b6e:docs/registrations/align_v4_squeeze_addendum_DRAFT.md:69-99`, `:139-175`, `:278-310`).

**Next exact step:** the lead dispositions F1-F9 on the registration brief, particularly the battery predicate, carrier estimator, scoring/calibration policy and current owner decisions, before assigning implementation. Re-run the focused synthetic oracles on the corrected code, then the scoped independent registration gate. The measurement lead supplies native battery/identity/meter/custody evidence outside this sandbox and outside active agent load. No W1 admission, squeeze registration or physical/adaptive success follows from this review.
