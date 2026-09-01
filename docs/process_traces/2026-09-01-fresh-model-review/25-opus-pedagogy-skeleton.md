# 25 — Opus 5 pedagogy audit of the _v5 skeleton (read-only, first-use test as its own dimension)

Both files read in full. Report follows.

---

# Pedagogy audit — `draft-v2-skeleton.md` (987 ll.) + `round7/survival-map.md`

**Scope note first, because it changes the brief.** The Abstract (skeleton:23–45), Introduction (47–70) and Conclusion (641–649) carry **no KEEP text** — the survival map classifies all three REWRITE (`survival-map.md:32, :44, :357`), and the skeleton holds only build notes there. The KEEP-inherited reader prose is §2 (74–119), §5 (462–487), §8 (604–628) and Appendix A (656–938). The order-defect risk therefore lands on §2 and §5, not the abstract/intro/conclusion. Factual accuracy untouched, per brief.

## First-use failures

All lines `draft-v2-skeleton.md`.

| Term | First use | Built at | Verdict | One-line fix |
|---|---|---|---|---|
| *powermetrics* | :74 | :687 (A.3.1) | **FAIL** | At :74 gloss "macOS's built-in power sampler, `powermetrics`". |
| the 9.724-ms **screen** (and the 10.164835 ms limit) | :90 | nowhere | **FAIL** | Replace "screen" with "minimum allowance", and state where both constants come from. |
| **whole-window allowance** | :94 (Fig. 2 caption) | :380–383 | **FAIL** | At :94: "a separately measured joule allowance for slow non-linear drift across the whole window (Section 4)". |
| **admitted** (energy / member / block value) | :189 | :466, §5 | **FAIL** | Gloss at :189: "admitted = passed the Section 5 entry checks, so may bear a claim". |
| **independent unit** (the *n* in every formula) | :201 | nowhere | **FAIL** | At :201: "one independent unit is one repeated run for the absolute component and one A/B/B/A block for the comparative component". |
| guarded published **floor** | :255 | :369 (`cell floor`) | **FAIL** | Move the floor/`guarded` definition (:366–378) before :255, or name it "the published bound built below". |
| **dominance / dominates** | :256 (`dominance_ratio_zero_denominator`), :360 | nowhere | **FAIL** | Gloss once: "dominates, in this paper's fixed sense: allowed boundary movement at least doubles the point-only bound". |
| **registered** (rounding, multiplier, refusal rule) | :268 | nowhere | **FAIL** | "registered = fixed in the pre-collection plan whose fingerprint is retained". |
| **member** (of a block) | :274 | :466, §5, in a different sense | **FAIL** | At :274: "member — one of the four runs in the block". Reconcile with §5's stage-member sense. |
| **the producer** | :275 | nowhere | **FAIL** | Delete the internal role name: "before these two movements are combined into one width". |
| \(b\), the **authenticated shared edge bound** | :278 | never linked to :90 "operative bound" or :908 `B_fiducial` | **FAIL** | "\(b\) is the window's operative bound from Section 2". |
| **MLX** | :360 | nowhere | **FAIL** | "MLX, Apple's on-device inference framework". |
| post-campaign **inserted-gap check** | :360 | build note :598 only | **FAIL** | One clause at :360, or an explicit forward pointer to §7 Future work. |
| **resolution bound** | :368 | Intro build note :60 only | **FAIL** (conditional on the Intro being written to spec) | Gloss at :368 regardless: "the largest false difference the cell admits". |
| measured **reference-trajectory excursion** / issued **repeatability bound** / same **family** | :381–382 | nowhere | **FAIL** | Build all three from physical inputs; as written \(A_k\) is uncomputable. |
| **raw probabilities** \(p_{(1)},p_{(2)}\) | :409 | nowhere | **FAIL** | Name the test that produces them (statistic, distribution, tails) before Holm is applied. |
| **not resolvable** | :416 | ledger claims §6 (:974); §6 is later and unwritten | **FAIL** | Gloss at :416: "the estimate does not clear the cell floor". |
| both **complete uncertainty intervals** | :416 | :419–421, *after* use | **FAIL** | Name the two at :416 before requiring them. |
| **deterministic allowance** (0.25 J) | :421 | nowhere | **FAIL** | State its physical source and how it is computed, or drop it from the example. |
| **planning-only amount** / **planning sum** | :424–425 | nowhere | **FAIL** | Delete both sentences, or build the retired quantity they warn against. |
| **stage** | :98, :466 | nowhere (:466 defines *admit*, not *stage*) | **FAIL** | "a stage is one declared group of runs measured back-to-back inside a window". |
| **freeze receipt** | :487, :674 | nowhere | **FAIL** | "a record fixing the plan bytes and the time they were frozen". |
| **reducer** | :568 | nowhere | **FAIL** | "the program that turns a run bundle into phase energies". |
| **pre-registered** vs "fixed before collection" | :567 vs :259, :476 | — | PASS, note | Pick one phrase and use it everywhere. |

**PASS, worth recording** (these are done well and should be the model for the fixes): `science window` (:84), `plateau` (:86), `monotonic clock` (:88), `cell` (:172), `point only` / `unguarded` (:189–190), Student-\(t\) prediction amount (:199–207), `corner` (:238–245), the twofold threshold's *forcing problem* (:166–170), `not_applicable` absolute \(R_{cm}\) (:333–335), `signed clearance or shortfall` (:428), `fail-closed` (:462), nearest-rank p95 (:469), `binary64` (:301), and the whole of A.3.2–A.3.7, which meets the replication bar cleanly.

**The skeleton's own First-use audit ledger (:940–987) is not a defence.** It omits every term above except `not resolvable`, and two of its rows are false: `support` (:951) is claimed for Section 2 but appears only in an unwritten build note (:523); `resolvability` (:974) is claimed for §6 but first fires at :416. A ledger that passes a text failing 23 terms should itself be treated as a defect.

## Replication gaps

1. **:90 — the window bracket.** `10.164835 ms` and `9.724 ms` arrive with no derivation, no units story, and no worked example. A reader cannot rebuild the operative bound. *Fix: one sentence of provenance per constant, plus a two-line worked bracket (pre-bound, post-bound, difference, resulting operative bound).*
2. **:275–302 — shared/local split.** "the producer", and "pads the extrema outward by 64 half-units of binary64 … rounding at the largest input magnitude" — the padding rule cannot be reimplemented from the text (half-unit of what magnitude, applied where, why 64). *Fix: state it as `pad = 64 × ulp(max|input|) / 2` or the true rule, with the forcing problem (printed enclosure must not round inward).*
3. **:278 — provenance of \(b\).** Three names exist for one quantity across the paper: "accepted capture bound" (:86), "operative bound" (:90), \(B_{\mathrm{fiducial}}\) (:908), plus "authenticated shared edge bound" (:278). No sentence maps them. *Fix: one naming bridge in §2 and reuse a single name.*
4. **:370–378 — \(g(n)=\max(1,\sqrt{9/(n-1)})\).** No forcing problem, no derivation, no citation; and "Fewer than five units remain diagnostic because the registered multiplier does not authorize a published component there" is circular. *Fix: give the origin of the 9 and the \(n\ge5\) cut in physical/statistical terms.*
5. **:380–385 — \(A_k\).** Composed from two undefined artifacts (gap-table row above). Uncomputable as written.
6. **:406–419 — the direction gate.** Holm's *mechanics* are worked well, but the tests being corrected are never specified, so the gate cannot be replicated. Add: statistic, null, one- or two-sided, and how \(p\) is obtained from the ten block differences.
7. **§4 has no diagram.** It is the paper's most algorithmic section (corner enumeration, the \(2\times2^n\) sign sweep, two gates) and Figure 3 exists only inside a build note (:456). *Fix: mark "Figure 3 required here" in the reader-facing text and specify it — three paths: evidence exclusion, magnitude against \(F_{\mathrm{cell}}\), direction from both intervals.*
8. **:520–535, the 37-of-50 negative,** is entirely a build note, which is legitimate — but the note omits a diagram requirement. Record supports clipped to a prefill interval is exactly the spatial thing a reader will otherwise picture wrong. *Fix: add "diagram required: record supports vs the prefill interval, overlap count marked" to the build note.*
9. **:548–569, G2-a.** No diagram, and the Qwen3-8B probes are "recorded but did not select it" with no reason given — an unexplained arm invites the reader to ask why it exists. *Fix: one clause on why the large model was probed at all.*

## Order defects

- **:94 → :380.** \(A_k\) used in the Figure 2 caption, defined ~290 lines later. §2 is KEEP text inheriting `_v4` phrasing; §4 was rewritten around it.
- **:189 / :274 → :466.** `admitted` and `member` are §5 vocabulary used throughout §4. §5 follows §4 in both orders, so this is inherited, not introduced — but it still fails, and the fix is a gloss in §4, not a section move.
- **:255 → :369.** "guarded published floor" precedes the `cell floor` build by 114 lines *inside one section*. This one is purely a `_v5` internal ordering artefact and is the cheapest to fix: move the safeguard passage (:366–404) ahead of the closing paragraphs of the ratio passage, or forward-name it.
- **:353–364 before :366–432.** The Outcome sentence forms now sit *before* the safeguards and gates. Branch A leans on "dominates" and "inserted-gap check", neither built at that point. In the frozen draft the gates were their own section (`survival-map.md:191`); the merge into §4 put the conclusions ahead of two of their inputs.
- **:416 → :974.** The ledger assigns `resolvability` to §6; §4 uses it first.
- **:550–560.** Inside the G2-a passage, "the three-record minimum" (:551) precedes the overlap rule that defines it (:558–560).

## Verdict

**FAIL — 23 FAIL rows** (22 terms plus the false ledger rows), 9 replication gaps, 6 order defects.

Three fixes with the largest reader payoff:

1. **Build the four uncomputable quantities in §4** — \(A_k\)'s two source artifacts (:381), \(g(n)\)'s origin (:370), the 0.25 J deterministic allowance (:421), and the test behind the raw \(p\) values (:409). Everything downstream of the ratio — floor, both gates, every results-table column — is currently unreplicable, and this is the section the advisor will read hardest.
2. **One naming bridge for the timing bound** (:86 / :90 / :278 / :908), plus deleting "screen", "the producer", "registered", and "reducer" as unglossed internal vocabulary. Cheap, and it removes the exact class of defect that cost five round-trips on "converge".
3. **Reorder §4: safeguards and gates before the Outcome sentence forms**, and gloss "dominates" and "inserted-gap check" at :360. The two branch sentences are the paper's headline; today both depend on terms the reader has not been given.
