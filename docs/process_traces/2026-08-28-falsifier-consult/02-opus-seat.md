# Opus 5 seat — falsifier consult (2026-08-28)

Model: claude-opus-5[1m]. Read-only. No other seat file read.

## 1

**The director's algebra is correct. I re-derived it independently and
corrected two of the brief's own citations (§Arithmetic).**

`detection_floor.py:806-843` evaluates `TERM B > point_gate`, with
`point_gate = g(n)·max(max|r_i|, P)` (:788-803) and `P = prediction_extra +
t_{0.95,n−1}·s_r·√(1+1/n)` (:689-702). `g(10) = 1.0` (:664-673, :108),
`t(9) = 2.262`, so `P = 2.3724 s_r` absolute. Absolute TERM B (:821-831) is
`max_i(|r_i| + w_i(n−1)/n + (Σw − w_i)/n)`; with equal widths `h` the added
term is `2h(n−1)/n = 1.8h`, identical for every `i`, so TERM B =
`max|r| + 1.8h`.

- **Regime 1 (`max|r| ≥ 2.3724 s_r`):** reduces to `max|r| + 1.8h >
  max|r|` — true for any `h > 0`, **unconditionally**. Widths are never
  zero: the allowance is `max(observed_drift_s, 0.009724)`, bound at
  `calibration_bracketing.py:1971` (the constant is at :211; the brief's
  ":199-214" points at the n=19 sibling, not the binding).
- **Regime 2:** true iff `h > (2.3724 s_r − max|r|)/1.8`. Since deviations
  sum to zero, `max|r| ∈ [0.9487 s_r, 2.8460 s_r]`, so in regime 2 the
  threshold ranges over **(0, 0.7909 s_r]**. "h ≳ 0.26 s_r" is the single
  point `max|r| = 1.9044 s_r`.

Comparative is weaker still: `max_i(|d_i| + w_i)` (:735-746) against
`max(max|d|, |mean Δ| + 2.3724 s_Δ)`; regime 1 again gives any `w > 0`.
**Empirical margin:** in the diagnostic cells widths moved the floor
0.2888 → 3.153 J (≈2.86 J) against a regime-2 width threshold of ≈0.096 J.
Cleared by ≈30×.

**CAN falsify:** all-zero widths — but :816-817 returns `False` at
`not any(widths)` *by construction*, so that branch tests nothing physical
and is unreachable in production; the regime where scatter grows until
`2.3724 s_r > max|r| + 1.8h`, i.e. scatter exceeds the whole joule-valued
timing envelope; exact equality (`results-fill-registry.md:222`), measure
zero. **CANNOT falsify:** anything in regime 1, ever; whether the widening
is *large*, only that it is nonzero; whether it survives a common-mode
treatment (§2); the headline verb — "dominates" in English means "much
larger than," the code means "larger by any margin."

**Recommendation:** Confirm C2. The predicate is near-vacuous —
unconditionally true in regime 1, cleared by ≈30× in the only cells
observed — and the §3 zero-width sentence (`draft-v1.md:103`) is vacuous
for a predicate monotone in `h` that returns `False` at `not any(widths)`
by construction. Delete that sentence regardless of the ruling on 2–4.

**Strongest counter:** Near-vacuity is a property of *this instrument*, not
of the criterion — the same predicate would be routinely false on a
hardware-counter platform. Pre-registration demands decidability before the
data and falsifiability in principle, not a coin flip; both hold.

## 2

*Which ratio.* `R = TERM B / TERM A_guarded`, per component, per cell — the
same two quantities the coded predicate compares and the same sixteen rows
frozen at `results-fill-registry.md:246-261`. The coded boolean is exactly
`R > 1`, so a threshold on `R` strengthens an existing registration: no new
emitted field, no new estimator id, one extra division at the desk fence.
Do **not** use `corner_widened_guarded / point-only`; that numerator is
`_corner_maximized_unguarded_floor` (:856ff), a strictly larger and
different quantity, and it is what produced 10.92/5.92/7.02 — using it
invites the "you picked the number that passed" reading.

*Which threshold.* **R ≥ 2**, defended semantically, not empirically: 2 is
the smallest value at which the timing term is at least as large as
everything else combined — the minimum content of "dominates" and of the
paper's gloss "edge placement contributed more than scatter"
(`draft-v1.md:298`). ≥3 has no semantic anchor; the only reason to reach
for it is that it clears the diagnostic minimum 5.92 with margin, which
*is* peeking. Say so in the paper. `R ≥ 2` is genuinely failable: it
requires `1.8h ≥ max|r|`, and `s_r` scales with per-block energy while `h`
is set by a fixed ~30 ms envelope, so a larger `_v5` pair can fail it.

*Common-mode — the highest-value item here.* For the **absolute**
component a shift δ common to every member cancels **exactly** in
`r_i = x_i − x̄`, so a shared fiducial term `s` should contribute **zero**
to TERM B. The code charges `1.8s`, because `_common_mode_block_half_width`
(`floor_extraction.py:447-478`, called :620) composes shared+local *within*
a block and then hands `comparative_false_effect_floor` ten independent
scalars (:630-633). If the shared term dominates the local ones — C4's
claim that ~30 ms is mostly repeatable bias — the absolute finding may be
substantially an artefact of re-independising a common term. Comparative
`max_i(|d_i| + w_i)` selects one `i`, so a shared term enters once either
way; small inflation there.

So **`R_independent` gates** (the built, registered, replayable estimator)
and `R_common_mode` is a pre-registered *mandatory disclosure* with a
registered consequence: if `R_cm ≤ 1` for the absolute component, the
null-outcome framing is used and the headline may not say "dominates." Do
not gate on `R_cm` — a cross-block shared-fiducial estimator is not built,
needs its own D-124-style registration, and building it before
2026-09-01/02 is where this blows the window.

*Where it lives.* The pack's prospective manifest is validated by
`analysis_manifest_v3.py`, **not** `analysis_manifest.py`: schema
`joulewise.analysis_manifest.v3.prospective` (:26; emitted at
`generate_configs.py:1663`), key set `_PROSPECTIVE_TOP_KEYS` at
**:997-1012**, exact-set enforced at :1756 and :1896-1900. The brief cites
the **v1** schema and mis-numbers it besides; its conclusion survives — a
new top-level key *is* an exact-set contract change — but is avoidable.
Each contrast already carries
`floor_estimator_registration` (`:1049`; generator :944, :968, :1501) whose
*interior* no `_exact_keys` call validates, and which is hashed into the
frozen semantics by `_prospective_semantics` (:1531-1542, `contrasts`
included), asserted equal to `frozen_semantics_sha256` at :2704 and
re-asserted at finalization (:4051). A `dominance_criterion` sub-object
added to the dict returned by `two_shared_edge_common_mode_registration()`
(`detection_floor.py:483-520`) is therefore **minted into the pack,
byte-bound into the semantics digest and plan tree, D-157/D-140 compliant,
with zero validator amendments.** Do not touch `_COMMON_MODE_PARAMETERS`
(:132-177) — that moves `COMMON_MODE_PARAMETER_SHA256` (:178) and every
fixture pinned to it.

Pre-registration force, ranked: (1) the `floor_estimator_registration`
sub-object — *minted*, cheap; (2) a new `_PROSPECTIVE_TOP_KEYS` key —
minted, but an exact-set contract change across three validators plus the
finalized projection, i.e. a mint-path change, i.e. **a further estate**
under D-157 R-3; (3) the `design` block — same cost, wrong home; (4)
registry + RQ row only — *declared*, not minted; necessary, insufficient
alone. Adopt (1) **and** (4).

*Cost.* ≈1 Sol-day: registration dict, regenerated goldens pinning
generator bytes, `[R_*]`/`[R_CM_*]` registry rows, the RQ-row edit,
deletion of `draft-v1.md:103`'s last sentence. Fits inside the ≈2 Sol-days
D-164 (`decision_log.md:191`) already bought for the `_v5` re-pin
**provided it lands before the generation** — before estate 12 and the
~2026-09-01/02 night. A slip past the re-pin converts it into option (2)'s
cost.

**Recommendation:** Before `_v5` generation, register a
`dominance_criterion` sub-object inside each contrast's
`floor_estimator_registration`: `R = TERM_B / TERM_A_guarded` per
component; gate `R ≥ 2` on the independent-corner treatment; mandatory
reporting of `R_common_mode` with a registered null-outcome consequence at
`R_cm ≤ 1`; a provenance clause stating the threshold was fixed from the
claim's semantics and from no collected generation. Mirror in the registry
and RQ row; keep the coded boolean, renamed the **label** predicate.
≈1 Sol-day, rides `_v5`, no new estate.

**Strongest counter:** `R ≥ 2` is still a number chosen by authors who have
seen 10.92/5.92/7.02, and framing does not erase that. The common-mode rule
also commits the paper to a desk derivation whose inputs (separated
shared/local terms) are required by the RQ row (`draft-v1.md:96`) but not
proven to be emitted in the form the derivation needs.

## 3

The steelman is stronger than the panel allows. *Provenance:* the coded
predicate predates the corpus, was written for the D-078 terminal gate, and
has been replayed byte-for-value by two custody seats
(`results-fill-registry.md:255-259`); a threshold invented by authors
holding 10.92/5.92/7.02 adds exactly one researcher degree of freedom — the
thing pre-registration exists to remove. *The paper does not rest on this
boolean:* the RQ table (`draft-v1.md:95-97`) carries bidirectional criteria
— containment (`I_δi ∋ 0`, `M ≤ m`), closure `max D_i ≤ 1e-6 J`, invariance
inside both `L_H` and `L_F`, `D_hold ≤ A_drift`, `max t_j ≤ 180 s` — and
already scopes dominance as a *label* predicate (:96). *Risk:* D-140
forbids post-mint repair, D-153 makes a non-config cure a new family
generation, D-157 R-3 makes a mint-path change a new estate; a
mis-specified criterion cannot be repaired after the mint.

**Recommendation:** Reject the steelman, adopt its two true parts — report
`R` per cell as a column in Tables 2 and 3 regardless of the ruling, and
keep the coded boolean, renamed the *label* predicate, so nothing already
replayed is discarded. What defeats it: the authors themselves reached for
a falsification demonstration at `draft-v1.md:103` and produced a vacuous
one. A JouleSort co-author will notice that the sentence proves the
predicate is monotone in `h`, not that the finding is real.

**Strongest counter:** If the threshold cannot be defended without
reference to the retired-era ratios, status quo plus an honest descriptive
column is more defensible than a threshold a reviewer can call
reverse-engineered.

## 4

D10 has the optics right and the mechanism wrong. Two titles frozen before
collection under a published selection rule is a registered branch,
structurally identical to the null row's `F_train` fallback
(`draft-v1.md:95`) — the outcome→framing mapping is fixed in advance, the
opposite of steering. The real defect is that the rule is §1's near-certain
boolean: a branch whose PRIMARY arm is taken with probability ≈1 is not a
contingency, it is a title with a disclaimer. Two facts settle it. Item 28
(`03-MAGISTRATE-RULING.md:231-234`) and the registry's held-title section
(`results-fill-registry.md:263-274`) both condition on `_v4`, which D-164
(`decision_log.md:191`) makes never collected — the trigger no longer
exists and the text is stale today. And the protocol-first framing is true
under *both* branches; a framing that survives both needs no branch.

**Recommendation:** **Replace.** Fix one protocol-first title now, before
collection; put the outcome in the abstract's first two sentences. Retain
the attribution-limited phrasing as a candidate *subtitle*, added only if
the registered `R ≥ 2` gate passes — a subtitle is a result statement, a
title is a framing commitment, and only the latter is what "fixed before
collection" protects. In the same edit strike `_v4` from item 28 and the
registry section and substitute `_v5`; a ruling conditioned on a generation
that will never exist is the ruled-not-installed shape this project has
already been bitten by.

**Strongest counter:** A protocol-first title undersells a genuine finding.
If `_v5` reproduces dominance at `R ≈ 7`, the attribution-limited title is
the one that gets the capstone read, and the device — rebuilt on §2's gate
rather than on the vacuous boolean — is a legitimate pre-registered way to
earn it. Dropping it for optics trades a real benefit for an appearance.

## Arithmetic

All recomputed by me; constants executed against the repo's own functions.
`DF` = `joulewise/detection_floor.py`.

- TERM B abs `0.9h + 0.9h = 1.8h` ⇒ `max|r| + 1.8h` (DF:821-831); cmp
  `max_i(|d_i|+w_i)` DF:735-746 (:836); gate `g(n)·max(max|r|,P)`
  DF:788-803 (:838-841); zero-width `False` DF:816-817.
- Executed: `small_sample_guard_factor(10)=1.0`, `(5)=1.5` (DF:664-673;
  :108, :109); `student_t_critical_95(9)=2.262`; `P/s_r = 2.262·√1.1 =
  2.372405614560883` (DF:689-702).
- Σr=0, `s²=Σr²/(n−1)` ⇒ `max|r| ∈ [s√0.9, 9s/√10] =
  [0.9486832980505138 s, 2.846049894151541 s]`. Regime-2 ceiling
  `(2.372405614560883 − 0.9486832980505138)/1.8 = 0.7909568425057607 s_r`;
  `h=0.26 s_r` ⟺ `max|r| = 2.372405614560883 − 0.468 = 1.9044056145608832
  s_r`.
- Never-zero width: `"0.009724"` `calibration_bracketing.py:211`; binding
  `allowance = max(drift, screen)` :1971; rule string :1980; projection
  :794.
- Ratios recomputed `3.153/0.2888 = 10.9176`, `2.922/0.4934 = 5.9222`,
  `2.184/0.3113 = 7.0157` (`draft-v1.md:103`, :298). Margin: widening
  `3.153 − 0.2888 = 2.8642 J` vs `0.7909 × 0.2888/2.3724 = 0.0963 J`
  ⇒ ≈30×.
- Common-mode (my derivation): a common δ leaves `r_i` unchanged ⇒ shared
  term costs 0 in absolute TERM B; code charges `2s(n−1)/n = 1.8s`. Sites
  `floor_extraction.py:447-478`, :620, :630-633.
- Manifest **(brief correction)**: pack schema
  `joulewise.analysis_manifest.v3.prospective` (`analysis_manifest_v3.py`
  :26; emitted `generate_configs.py:1663`); `_PROSPECTIVE_TOP_KEYS` 14 keys
  :997-1012, exact-set enforced :1756, :1896-1900. The brief's
  `analysis_manifest.py` `TOP_KEYS` is **:36-46** (not 37-47),
  `DESIGN_KEYS` **:47-54** (not 48-55), schema v1 :21 — wrong schema here.
- `floor_estimator_registration`: contrast key `analysis_manifest_v3.py`
  :1049; opaque passthrough :1605-1607; `_prospective_semantics` :1531-1542;
  digest equality :2704; finalization :4051. Producer DF:483-520;
  `COMMON_MODE_PARAMETER_SHA256` over `_COMMON_MODE_PARAMETERS` :132-186.
- D-164 `decision_log.md:191`; D-157 R-3 :184; D-153 :180; D-140 :173.
- Item 28 `paper-goal-consult/03-MAGISTRATE-RULING.md:231-234`; item 34
  :265-272; sixteen TERM rows `results-fill-registry.md:246-261`, method
  block :197-245, title pair :263-274.
- Panel `04-SYNTHESIS.md`: C2 :27-40, C3 :42-48, D10 :163-165, §3 items 1–2
  :195-199, item 17 :244.

## Confidence

High on §1 (re-derived and executed against the repo's own functions) and
§2's *mechanism* (verified at five call sites); medium on §2's threshold
*value* and on the size of the common-mode inflation — the within-block
composition is an outward excursion enclosure, not a plain sum, so "1.8s
charged for a term that should cost 0" is an upper bound; medium-high on
§3–§4, which are judgment, not arithmetic.
