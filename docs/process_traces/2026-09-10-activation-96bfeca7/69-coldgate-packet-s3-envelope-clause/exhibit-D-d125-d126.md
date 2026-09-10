# Exhibit D — D-125 / D-126 texts
## D-125: Ed's morning ratification batch — D-124 signed off, lineage envelopes ratified, D-117 cl.1 amended for successors, the 40-hour window

**Date:** 2026-08-08 morning. **Status:** RATIFIED (Ed, in-thread).

1. **D-124 signed off.** Ed's condition ("if instrument gets better")
   is exactly the property: the two-shared-edge common-mode estimator
   tightens comparative floors 4-5x on repo-demonstrated evidence, under
   the full registration conditions of D-124. FLOOR-COMMONMODE-01's
   implementation must land through the full gate BEFORE pack freeze so
   the estimator identity pre-registers in pack bytes.
2. **Q1+Q13 envelope adoption ratified on trust.** Magistrate
   clarification recorded: this governs SUCCESSOR calibration-acceptance
   arithmetic (drift screen + budget ceiling derivation), not workload
   profiles; screens/ceilings become lineage-monotone t-family envelopes
   inheriting the genesis screen 0.010818 as a lower bound — the
   allowance can only strengthen. With Ed's ratification the consult's
   transcription condition is met: **D-117 clause 1 is AMENDED for
   successor artifacts** from "every mint uses max(drift, 0.010818)" to
   "genesis lower bound + lineage-envelope rule"; the genesis literal
   remains binding as the floor and for every mint under the issued
   artifact. Freeze-until-ruled ends.
3. **The 40-hour window.** Ed grants ~40 continuous hours including
   quiet-window nights (Ed available for §5A arm/disarm taps). The plan
   of record is `docs/strategy/2026-08-08-40h-plan.md`; RUN_STATE points
   to it as the resume script across /clear.

## D-126: U2 second convening — synthesis of record; COLD-GATE-U2-PENDING resolves to this entry

**Date:** 2026-08-08. **Status:** ADOPTED (magistrate transcription of
the sealed second convening; both judges' rulings custodied at
`docs/process_traces/2026-08-07-u2-coldgate/`).

1. **Outcome.** Partial ratification + one joint remand, per
   SYNTHESIS-V2.md: six first-round objections verified moot in the
   exhibit's bytes by both sealed judges (Q2 observed-max screen, Q4
   one-way door, Q6 abandoned-brick, Q7 bare-None loader, Q9
   unbarriered publication, Q11 fabricated successor_probe).
2. **Ratified with binding amendments:** Q2; Q4 (plus the two-site
   freeze test obligation on `_SUPPORTED_COUNT_BOUNDARY_RULES` and its
   recompute branch); Q5 (the cold judge's closure definition is
   BINDING — an observation ceases to be "new" only via an explicit
   decision-log disposition by content_id plus the next successor's
   prior_observation_set recording the disposing decision ID; consuming
   code lands with the first disposing ruling, not before); Q6; Q7; Q8
   (registry authority ratified; the migration shim DELETED by
   convergent ruling — `_load_registry_for_current_active_selection`
   collapses to the plain committed load); Q9 (strict with the shim
   gone); Q11; the Q13 n>=19 licensing floor.
3. **Q1+Q13 joint remand: RESOLVED** by the lineage-monotone envelope
   design (Q1Q13-REMAND-CONSULT.md), ratified by Ed as D-125. The
   silent clamp is removed; issuance refuses
   `successor_screen_exceeds_budget_ceiling` when screen >= ceiling;
   cap = ceiling − screen with no max(0,·); runtime classification and
   record fields per consult §6.
4. **Q12 OPEN** pending re-presentation on the FULL register text.
   Packet rule hardened (second occurrence of the truncation class):
   register/finding quotes run to END OF DOCUMENT SECTION, never to an
   assembler-chosen paragraph boundary.
5. **Q10 DEFERRED** to the recovery gate; the exception may not be
   exercised on a live night before the predicate re-verifies on the
   ledger-resident substrate.
6. **Cross-cutting:** CH-1 (writer copied-scalar unit) deadline is
   before the first successor issuance or any live night relying on
   writer dispositions, whichever comes first. The U2 landing gauntlet
   REQUIRES a writer≠reviewer lens over the 965-line successor test
   surface (torn-publication, rollback, durability-uncertain,
   receipt-authentication paths). No successor can issue until rework
   round 2 + the remand resolution + the landing gauntlet + CH-1 have
   all landed.
7. **Tuple rule:** this decision ID replaces `COLD-GATE-U2-PENDING`;
   an issued artifact may never embed a tuple member with no
   decision-log entry.

## D-127: Autonomous window loop chartered — scoped time-toggle + verified relaunch harness (partial D-114 reversal)

**Date:** 2026-08-08 (Ed, in-thread during the 40h window). **Status:**
RATIFIED by D-128 (build authorized; install gated; initially CHARTERED).

1. **What Ed authorized.** Claude Code drives the full experiment loop
   across multi-day unattended stretches: harvest → mint → judge →
   build/freeze next pack → toggle network time off → launch the
   supervisor → EXIT for the capture; the window's final step relaunches
   a fresh headless session. Ed's involvement reduces to optionally
   remote, or zero once the toggle lands.
2. **Zero-agent during capture is UNCHANGED.** The agent fully exits for
   the ~3h capture; this charter removes the human toggle and the
   relaunch gap, not the contamination fence. (The dormant-app
   characterization number becomes moot for this design — full exit,
   not residency.)
3. **Scoped toggle.** Sudoers rule for exactly the two fixed
   systemsetup network-time commands (exact path, exact argv, no
   wildcards). Honest risk register: worst-case abuse is TIME
   MANIPULATION, which for this project is a measurement-integrity
   vector (clock anchors, drift screens) — detectable by the existing
   custody/drift chain; not a general-privilege surface. D-115's
   install conditions bind (sudo -k fresh auth; authenticated staged
   content; interpreter isolation); Ed personally runs the single sudo

## Q1Q13 remand consult (envelope rule)

Reconstructing all 30 D-116-valid observations gives:

- the same extrema and range
- sample SD: `0.002947531588352414`
- 95% prediction: `0.008525415306447831`
- 99% ceiling: `0.011489826907224958`
- range-screen cap: `0.000671826907224958`

Thus the actual 30-member draw remains coherent, but only narrowly; it does not invalidate the approximately 67% repeated-sampling failure probability.

### 2. Binding arithmetic design: choose (b), with lineage envelopes

Choose the existing 95% and 99% two-draw prediction family, but make both operatives lineage-monotone:

\[
Q_{95,g}=t_{0.975,n_g-1}s_g\sqrt2,\qquad
Q_{99,g}=t_{0.995,n_g-1}s_g\sqrt2
\]

\[
S_g=\max(S_{g-1},Q_{95,g}),\qquad
C_g=\max(C_{g-1},Q_{99,g})
\]

\[
\text{cap}_g=C_g-S_g,\qquad
A_g=\max(\text{observed drift},S_g)
\]

Genesis remains:

- `S₀ = 0.010818`
- `C₀ = 0.012093166090593858`

The 95% and 99% candidates should use the same `1e-18`, `ROUND_HALF_EVEN` comparator quantum; presentation rounding remains separate.

This is not raw option (b): the D-117 literal remains the genesis lower bound, and neither screen nor ceiling may fall as more observations arrive. It is also not option (e): sufficiently increased drift dispersion automatically raises both quantities.

The ordering is algebraic. For every nondegenerate corpus, `Q95 < Q99`; by induction, if `S(g−1) < C(g−1)`, then:

\[
\max(S_{g-1},Q_{95,g}) < \max(C_{g-1},Q_{99,g})
\]

A zero-SD corpus is still safe because the strictly ordered inherited pair dominates. Consequently, `P(screen >= ceiling)=0` for valid derivations, apart from implementation defects caught by the issuance backstop.

Using the same 99% statistic for both screen and ceiling is rejected: once that candidate dominates, screen equals ceiling, cap becomes zero, the budgeted-drift lane disappears, and issuance must refuse. The never-zero allowance would cease to be a floor and become the maximum admissible drift itself.

The allowance’s new meaning is precise: it is the larger of the observed drift and a nondecreasing, genesis-anchored 95% two-draw prediction floor. It never authorizes a drift above the independently maintained 99% ceiling.

### 3. Corpus universe: parent basis plus post-cutoff additions

Use two explicitly different universes:

- **R2.8 trigger universe:** every authenticated, content-distinct, valid same-epoch observation. It currently counts 30, including the two valid Window-B fiducials.
- **Derivation basis:** the parent derivation corpus plus valid same-epoch content first appearing after the parent cutoff and judged under the parent artifact before absorption.

Therefore the eleven valid observations already known at the D-116 cutoff but absent from the n=19 basis remain bound-inert, including both Window-B fiducials. They remain in `prior_observation_set` and trigger counting.

This separation is directly supported by D-109:

- R2.2 says the derivation corpus remains the exact n=19 threshold-producing set.
- R2.8 calls its full-valid universe the “Counting rule for the … trigger,” not the derivation basis.
- R2.5/R2.6 and the ratified Q11 disposition permit genuinely new, parent-judged observations to be absorbed prospectively.
- D-116 demonstrates the separation in practice: 30 observations count, while the bound remains n=19 and Window-B is explicitly bound-inert.

At the 38-count trigger, if eight post-cutoff valid observations were added, the trigger count would be 38 while the derivation basis would be 27. The next trigger boundary would be 76, derived from the trigger count—not 54 from the derivation basis.

Window-A-lineage-only is rejected because a historical directory/window label is not a durable metrology rule. The full-valid basis is rejected because it contradicts D-116’s explicit bound-inertness statement.

### 4. Option ranking

1. **(b), lineage-monotone 95%/99% envelope — selected.** Stable as n grows, structurally ordered, never-zero, and responsive to increased dispersion. D-102 already authenticates both statistics. This remand must explicitly amend D-117 clause 1 from permanent equality to a genesis lower bound.
2. **(e), freeze until ruled.** Strongest pre-remand authority reading and the mandatory fallback if the amendment is not transcribed. It is safe but turns degradation-triggered issuance into a desk ruling and supplies no automatic growth.
3. **(d), capped range.** Coherence would require `k < 2.575829…√2 ≈ 3.642773`; `k=3.5` would work algebraically but is unratified and suppresses isolated degradation as approximately `kD/√n`. Choosing `k≈3.641406` merely reverse-engineers the favorable genesis draw and leaves negligible margin.
4. **(c), rolling fixed-size subset.** “Most recent 19” has no authoritative selector and merely freezes the failure probability near 20% per issuance. The exact original 19 is option (e), not a rolling-subset design.
5. **(a), full-corpus range.** Its crossing probability tends to one. It is licensed only as the ratified genesis derivation, not as an unbounded successor rule.

A pure level shift need not enlarge the drift-dispersion statistic; Q2’s preflight observed-maximum comparator handles that failure class. A mixed old/new degraded regime or increased variability raises the two-draw predictions. A systematic-invalid observation remains a persistent refusal rather than being fitted away.

### 5. Issuance-time refusal

Retain the ordered backstop permanently:

- Compare the stored, post-quantization Decimal operatives.
- Refuse exactly when `screen >= ceiling`.
- Margin: zero; strict positive headroom is required, but no invented epsilon is added.
- Refusal: `successor_screen_exceeds_budget_ceiling`.
- Compute cap as `ceiling - screen`; never use `max(0, …)`.

The validator must also require `cap == ceiling - screen` and `cap > 0`. The selected design makes the refusal unreachable for correctly derived artifacts, but it remains necessary against rule drift, malformed artifacts, and numerical/rounding defects.

### 6. Runtime ordering and record

After validating `screen < ceiling`, classify in this order:

1. `drift > ceiling` → `budget_exceeded`, refuse `instrument_calibration_mismatch`.
2. Else `drift > screen` → `passed_budgeted`.
3. Else → `passed_screen`.
4. Mint allowance only after a passing classification.
