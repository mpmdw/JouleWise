# Counter-review: "Calibrating the Calibrator: External Validation of `powermetrics`"

**Reviewer:** Opus 5 counter-reviewer (adversarial charge: kill it)
**Target:** `scratchpad/portfolio/prop-wall-meter-validation.md`
**Ground truth checked against:** desk checkout at main — `docs/paper/draft-v1.md`,
`docs/decision_log.md` (D-092 §5676, D-117 tail), `docs/strategy/2026-08-06-impressiveness-roadmap.md`,
`docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md`, `TASK_QUEUE.md` A26/P2-048,
`docs/paper/related_work_draft.md`, `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`.

## Verdict: **WEAK**

Scores (1–10):

| axis | score |
|---|---|
| novelty | 4 |
| feasibility | 4 |
| mvp_leverage | 5 |
| venue_fit | 5 |
| original_goals | 3 |

The *work item* survives — C8 is ratified (D-092), the Q6/D-018 bridge design exists,
and the bibliography gap is real. The *paper proposal* does not. It is not a paper; it
is a revision to §6 of the paper Ed is already writing, wrapped in a title that promises
a result the apparatus cannot produce.

---

## Fatal flaws

### F1. The headline claim is not identifiable on this apparatus. (fatal to the framing)

The thesis says the study can "determine whether `powermetrics` preserves the absolute
gain … of whole-request LLM energy." It cannot. Paired idle/active differencing removes
the constant terms, leaving

    ΔE_wall ≈ [ ΔE_SoC·(1+ε_pm) + ΔE_DRAM + ΔE_fan + ΔE_other ] / η(P) ± ΔE_battery

where ε_pm is the counter bias the paper claims to measure. A single wall meter yields
one number, β, that is a *product* of counter bias, the non-SoC incremental power tree,
and the charger efficiency curve. β = 1.3 is equally consistent with "`powermetrics` is
perfect and the rest of the laptop costs 30%" and with "`powermetrics` under-reports by
25%." Nothing in the design separates them — a sealed MacBook offers no SoC-rail DC tap,
which is precisely the affordance Desrochers-class RAPL validations had and this one does
not. The proposal is admirably explicit that wall agreement cannot validate the *phase
split*; it is silent on the fact that it cannot validate the *total gain* either. That
silence is the flaw, because the title, the thesis sentence, and Contribution 1 all rest
on it.

Corollary, and this one Rivoire will circle in red: Contribution 1's acceptance gate —
held-out residual ≤ max(floor, 5% of ΔE_wall) — tests **linearity and stability of a
fitted mapping, never accuracy**, because α and β are fit from the data. A clean 5%
held-out pass is fully compatible with `powermetrics` being 30% wrong. Calling that
"whole-request gain validation" is a category error printed in the contributions list.

### F2. Two of four contributions are already in `draft-v1.md`, unmeasured.

- Contribution 4 ("matching totals is compatible with energy redistributed between
  phases") is **already written**, verbatim in substance, at `draft-v1.md:180` and
  `related_work_draft.md:15`, sourced to [JayOstapenco]. It requires zero measurement,
  zero meter, and zero nights. It is not a contribution; it is a paragraph that exists.
- Contribution 2 (load-dependent rather than constant gap) is the **published headline
  finding of Jay/Ostapenco**, already cited in the draft as such. Replicating it on Apple
  silicon is a platform note, not a finding.

That leaves Contribution 1 (not identifiable, F1) and Contribution 3 (the boundary
conclusion-flip test on the 1.5B-vs-7B contrast). Contribution 3 is the one genuinely
new, genuinely MVP-relevant item in the proposal — and it is already predeclared in
`docs/campaign_packs/q6_c5_2_10_rail_vs_wall.md` as the frozen conclusion-flip test. So
the proposal's four contributions reduce to one, and that one was designed a month ago.

### F3. Fan hysteresis will manufacture Contribution 2 as an artifact.

The design is four output-length levels (128/512/1024/2048 tokens) and reads
slope/residual structure across them as evidence of load-dependent counter gain. On an
M3 Max MacBook Pro, longer sustained decode means higher sustained die temperature means
higher fan RPM — a non-SoC load of order several watts (uncertain; must be measured),
**thermally lagged by tens of seconds to minutes and therefore hysteretic in run order,
not a function of instantaneous load**. That term rises monotonically with output length.
It will appear as ΔE_wall superlinear in ΔE_SoC, i.e. exactly the signature the paper is
built to report as "load-dependent `powermetrics` gain." The proposal has no fan-RPM
covariate, no display-state control, no thermal-state admission term, and no cooldown
accounting in the described blocks. Counterbalancing level order does not fix a
hysteretic term; it smears it into residual structure, which then trips the 5% gate for
the wrong reason. The same confound contaminates Contribution 3: 7B runs longer and
hotter than 1.5B, so a boundary "flip" is the *expected* result from fans alone and
would say nothing about the counter.

### F4. The battery term is unbounded and is 5–10× the signal.

The proposal's own planning value is ~51 J for a 1.5B decode. A residual battery
charge/discharge flux of ±5 W over a 60 s block is ±300 J. "Charge-neutral, recorded
battery observations" is the right instinct, but no mechanism is proposed that resolves
the battery term to the ~1 J scale this instrument works at. macOS optimized charging,
periodic top-off cycles, and Apple-silicon burst draw supplemented from the cell are all
live. This is checkable at a bench in an afternoon **with no meter**, and it is not in
the plan — it sits downstream of "borrow the WT310E."

### F5. Venue/location conflict with the quiet-window protocol — unaddressed.

A borrowed, in-calibration WT310E plus a mains-voltage inline fixture from a university
lab will plausibly have to be operated *in that lab*, or under supervision. The JouleWise
claim window requires a controlled quiet environment, zero background activity, 2–4 hours,
operator bookends, and thermal/environmental admission gates — and environmental
contamination is this project's single most expensive historical failure mode (the
Ventura screensaver episode; "another environmental refusal" is the named risk in the
roadmap's rank-1 row). The proposal never states where the confirmatory window happens.
If the meter cannot come to the instrumented unit under the standard gates, the
wall-validation window is not admissible under the same regime as the D-117 windows and
the comparison loses its warrant. This is a scheduling/logistics question with a binary
answer that has not been asked.

### F6. Cost is understated ~2× on nights and omits calendar entirely.

The proposal's headline cost is "one non-claim pilot plus one new 2–4 h quiet window."
The repo's own strategy doc rates this expansion at **4–8 weeks, 1 pilot plus 1
confirmatory session**, and the desk list the proposal itself enumerates — importer, raw
schema, meter-metadata/calibration binding, sync residual, fixed-range uncertainty,
paired reducer, held-out regression, refusal reasons, corrupt-trace tests, hash-bound
custody — is *a second instrument's entire calibration-acceptance regime*. Note that
P2-048 is **SHELVED** in `TASK_QUEUE.md` and the Q6 pack is an explicit "pre-hardware
DRAFT … not frozen until the boundary-pair hardware and calibration manifest are known."
"Already-designed" is honest about the design contract but understates the build. Given
this repo's delivery record on comparable machinery (D-079 issuance: multiple PRs, two
cold gates, a full C-028 gauntlet), realistic cost is 5–9 weeks wall-clock, 2–3 nights
including one contingency, contending directly with P1.

### F7. It is not a paper.

The proposal's own venue section says: reuse MVP §§1–5 almost intact, reuse the D-117
result structure, reuse related work, "add … a paired wall/SoC figure," "do not rewrite
the paper as a generic power-meter benchmark." That is a description of a section edit.
In a 20-direction portfolio it duplicates `prop-mvp-icpe-upgrade` rather than competing
with it.

## Does it answer a question the MVP needs answered? No.

The MVP's claims are *same-boundary* contrasts under a declared floor. A multiplicative
gain error cancels in a ratio and merely scales a difference; `draft-v1.md:11` already
fences this explicitly and honestly ("absolute values remain internal to the named
`powermetrics` SoC boundary; same-boundary contrasts can still be scientifically useful").
`draft-v1.md:36` goes further and makes the *absence* of the wall meter part of the stated
gap. C8 is a reviewer-comfort item, not a soundness item. The one exception is
Contribution 3 — but see F3.

## On the bibliography finding (no published `powermetrics` validation)

It opens less than it looks. Consider *why* the gap exists: the standard RAPL-validation
recipe (Khan/Desrochers/Jay/Ostapenco) works on machines where you can meter the wall
**and** tap the rails, so ε_pm is identifiable. On a sealed, battery-buffered, actively
cooled laptop it is not (F1). A paper that runs the recipe anyway does not fill the gap;
it publishes a transfer function for one MacBook's power tree and labels it validation.
The empty shelf is partly evidence that the well-posed version of this experiment needs
apparatus Ed does not have. Novelty = platform only, and the platform is the reason the
result is weaker than its lineage.

## Original goals: 3/10

The proposal concedes it studies no mechanism axis — no spec decode, MTP, MoE, KDA, KV.
Its claimed service to the "energy-honest reporting / leaderboard-critique" axis is real
but indirect, and its claimed foundation for split inference is thin: split work needs
*two* meters (RUN_STATE is explicit) and a cross-device clock bound, neither delivered here.

## Credit where due

The single best judgment in the proposal is refusing to attach an uncharacterized meter
path to the frozen D-117 windows, and sequencing C8 strictly after they close. That
protects P1 and should be preserved in any surviving version. The kill-criteria section
is also genuinely well-formed — it is simply pointed at the wrong risks (calibration
certificate, fixture) rather than the ones that will actually end it (F1, F3, F4, F5).

---

## Three strengthening moves, if kept

1. **Re-scope to what is identifiable, and re-title.** Kill "validation of `powermetrics`"
   from the title, thesis, and Contribution 1. The honest, defensible object is *the
   AC-to-SoC boundary transfer function for one named stack* — how much energy the machine
   draws that the SoC counter never sees, and whether that fraction is stable across load.
   Then actually attempt the decomposition instead of black-boxing β: log fan RPM (SMC
   sampler) as a modelled covariate, fix display state, and report an explicit
   identifiability limitation stating that one wall meter plus one SoC counter cannot
   separate counter bias from the power tree. This converts a claim reviewers will reject
   into one they will accept — and it is the version that honestly fills the empty shelf.

2. **Move the two owner-controlled kill gates in front of the borrow.** Both need zero
   meter and zero advisor coordination: (a) **battery-flux bound** — log SMC battery
   current/voltage at maximum cadence through a representative quiet decode block and
   demonstrate the net battery term over a block is bounded well below the smallest cell's
   signal; kill on failure. (b) **fan/thermal confound** — log fan RPM across the four
   length levels and show fan power does not correlate with level, or bound it with a
   forced-fan control arm; kill or redesign on failure. One afternoon at the bench can end
   this direction before a single lab-coordination email, and F4/F3 are more likely to kill
   it than the calibration certificate is.

3. **Redesign the cells for the AC side's time constants, and settle the venue up front.**
   Drop the 128-token cell — at ~1–2 s it is below the charger input capacitance, battery
   buffering, and the meter's 100 ms update interval, and cannot be integrated cleanly.
   Promote the sustained repeated-request 60–120 s blocks from fallback to *primary*
   design (they raise the signal without touching the frozen single-request boundary).
   Make "the meter physically comes to the instrumented unit, under the standard admission
   gates" a **precondition negotiated before the borrow**, not a discovery afterward; if
   the fixture cannot leave the lab, that is a pre-borrow kill. Keep the boundary
   conclusion-flip test on the 1.5B-vs-7B contrast as the single headline result — with
   fans modelled — because it is the only contribution the MVP actually consumes.
