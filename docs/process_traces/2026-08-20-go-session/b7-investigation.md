# B7 claim-integrity investigation — 8.611855 J / 1.869502 J in `docs/paper/draft-v1.md`

Read-only, `/Users/edr/code/JouleWise` @ `efc597d`. Nothing modified.

---

## 0. Two corrections to the finding as stated

**(a) The cited line list is wrong about where the live prose is.**
`docs/paper/draft-v1.md:357` opens `<!-- CONDITIONAL-INSERT-TIGHTER-FLOOR` and
`:409` closes it (`END … -->`). **Lines 357–409 are inside an HTML comment** — a
byte-fenced `REPLACE EXACT` / `WITH` swap script, not published prose. Of the
lines the packet names, **364, 367, 372, 375, 388** are all inside that comment.
Only `:124` is live.

Actual live-prose census (lines < 357):

| Line | `8.611855` | `1.869502` |
|---|---|---|
| 124 | 1 | 0 |
| 157 | 1 | 0 |
| 226 | 1 | 0 |
| 258 | 1 | 0 |
| 272 | 2 | 2 |
| **live total** | **6** | **2** |
| file total (incl. comment) | 13 | 8 |

**(b) "relationship unstated" is not the live defect.** `draft-v1.md:272`
states it explicitly and correctly: 1.869502 J is "about 4.6 times tighter than
the 8.611855 J worst-case default"; the tighter *estimator*
(`d124_two_shared_edge_common_mode.v1`) is pre-registered in the frozen packs;
the paper-regime swap "executes at the first post-freeze mint tracked in
`TASK_QUEUE.md` and has not been applied here." That wording landed in `36c9d78`
("B7: … draft-v1.md:250 stale-blocker contradiction corrected") and was
sharpened in `c0ee784` ("estimator-not-number preregistration wording"). **The
B7 finding as written is already cured.**

The real defect is one the sweep did not name and `OPEN-ITEMS.md:829-833` did:
**provenance and era.**

---

## 1. Per-occurrence provenance table

Both numbers have **one** primary source. There is no second lineage.

**Primary source:** `docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md`
- `:78` consumed root `runs_window_a5_20260723`; population = decode ABBA prefix
  `p2015-df-cmp-abba-ph-decode-`, blocks `b01`–`b10`, positions A1/B1/B2/A2.
- `:80` ordered-corpus digest `708fced0…3607`; per-bundle `complete_bundle_sha256` table.
- `:95` acceptance artifact sha256 `316113960c596a6f…` → **`configs/calibration/calibration_acceptance_d079_v2.json`** (verified by `shasum`), i.e. the **original n=19 generation**, first of six.
- `:70` cites max budgetable drift `0.012093166090593858 s` = the `_D102_N19_DERIVATION` constant → confirms n=19 basis independently.
- `:62` "observed drift is below the screen by 8.930913×, so **the screen selects the allowance for both estimators**" → both floors are *screen-dominated*, and that screen is n=19's 10.818 ms.
- **Every numeric mention in that file is prefixed `NON-CLAIM`**, including `:23` "default NON-CLAIM 8.611855 J" and `:103` "a NON-CLAIM two-shared-edge sensitivity … produced a NON-CLAIM **1.869502 J** floor".

Ratifying decision: `docs/decision_log.md:149` (D-124 index row) and `:7956-7959`
— "**Evidence (NON-CLAIM …)**: on the exact a5 decode ABBA corpus under CURRENT
issued semantics, the worst-case-sum default composes an 8.611855 J comparative
floor; … the two-shared-edge variant 1.869502 J." D-124 amendment
(`decision_log.md:8002`): "the reportable floor value is unchanged at 1.869502 J
while its trailing ulps move upward." Full-precision form
`1.8695016260131627 J` at `docs/phase_2/alpha_arm_readiness.md:65`; pinned in
`tests/test_floor_extraction.py:4438` and `tests/test_detection_floor.py:841`
against committed replay fixtures.

| # | file:line | Live? | What it claims to be | Quantity | Corpus | Era / generation |
|---|---|---|---|---|---|---|
| 1 | `draft-v1.md:124` | **live** | "All comparative results **issued in this cycle**… that conservative comparative false-effect floor is 8.611855 J" | comparative false-effect floor, worst-case composition | a5 decode ABBA | anchor-v2; acceptance n=19 |
| 2 | `draft-v1.md:157` | **live** | "the conservative floor alone is 8.611855 J" — input to the practical joint-clearance sizing disclosure | same | a5 | anchor-v2; n=19 |
| 3 | `draft-v1.md:226` | **live** | "the retained token-generation cell's 8.611855 J conservative floor **only as a prospective scale**" → the ~3 J thin-margin warning on the 11.6 J p256 projection | same, used as scale | a5 | anchor-v2; n=19 |
| 4 | `draft-v1.md:258` | **live** | "the retained token-generation contrast cell **has** an 8.611855 J floor" (limitations, §7) | same | a5 | anchor-v2; n=19 |
| 5 | `draft-v1.md:272` ×2 (8.611855) | **live** | "4.6 times tighter than the 8.611855 J worst-case default"; "Results in this cycle's retained corpus **were issued under** the conservative 8.611855 J composition" | same | a5 | anchor-v2; n=19 |
| 6 | `draft-v1.md:272` ×2 (1.869502) | **live** | "On the retained token-generation contrast cell it gives 1.869502 J"; "it yields the 1.869502 J floor" | two-shared-edge comparative floor | a5 | anchor-v2; n=19 |
| 7 | `draft-v1.md:364, 372, 388, 396` | comment | `REPLACE EXACT` targets of the queued swap (mirror sites 1,2,3,4) | — | — | — |
| 8 | `draft-v1.md:367, 375, 391, 399` | comment | `WITH` replacements that would render 1.869502 J as **the issued result** | two-shared-edge floor | a5 | anchor-v2; n=19 |
| 9 | `draft-v1.md:404/407` | comment | swap pair for site 5/6 | — | — | — |

---

## 2. Era and admissibility trace

1. **Non-claim at birth.** The custody record tags every instance `NON-CLAIM`
   (§1). D-124's registration conditions (`decision_log.md:~7970`) make the
   estimator a *candidate* until pre-registered in pack bytes — which happened
   for the **identity**, not the value.
2. **Barred by pre-registration.** `docs/paper/results-fill-registry.md` preamble:
   "**No historical result is a supplier for this registry.** Under D-117, claim
   authority can arise only from prospective alpha, beta, and gamma evidence."
   a5 (2026-07-23) is historical.
3. **Permanently barred by instrument era.** `runs_window_a5_20260723` is
   anchor-v2. **D-146** (`decision_log.md:169`) installs the mechanical
   `CLAIM_BEARING_ANCHOR_METHODS` barrier with reason
   `capture_pipeline_superseded`, and "**NO re-derivation retrofit lane**".
   **D-148 cl.7** (`decision_log.md:171`): the stored anchor-v2 population (748
   repo-tree bundles) is "**permanently non-claim-bearing on estimator
   grounds**" and gets a registered-limitation paragraph.
4. **Also stale against the live calibration generation.** The replay ran
   against acceptance `d079_v2` (n=19, screen 10.818 ms, drift ceiling
   12.093166 ms). The live default is **r6** (n=17, screen **9.724 ms**, ceiling
   **10.164835 ms**) — `draft-v1.md:64` and `joulewise/calibration_bracketing.py:172`
   `ACTIVE_ACCEPTANCE_ID`. Since both floors are **screen-dominated**
   (COMMONMODE-REPLAY `:62`), both values move under r6. Direction is
   indeterminate — the r6 screen is tighter (shrinks) while anchor-v3 widens the
   member bounds (+0.311 ms mean, `draft-v1.md:78`) — and per D-146 there is no
   lane to find out. **The current-instrument value of this cell is unknown and
   unobtainable.** The published "4.6×" ratio is therefore an anchor-v2/n=19
   artifact quoted as a present-tense property.
5. **The paper's own era disclosure does not cover it.** `draft-v1.md:260`
   ("A corrected clock anchor retires every corpus collected before it") names
   only "**The retained a9 and a10 characterization** quoted in Sections 3 and 7."
   **a5 is never mentioned anywhere in the paper** (`grep -n 'a5' draft-v1.md` →
   zero hits). The floor-regime numbers are the one quantitative family in the
   draft with no era label attached.

---

## 3. Registry status — hand-written, not registered fills

- `docs/paper/results-fill-registry.md` contains **no** occurrence of either
  number. Its vocabulary is bracket tokens (`[F_1p5B_decode_cmp_J]`,
  `[F_7B_decode_cmp_J]`, …), all **`KEY_FROZEN / VALUE_UNISSUED`**, fill rules
  `MEASURED` / `DERIVE` / `STOP_FILL`. Numeric characters appear "only inside
  binding identifiers, model names, source locators, and the required census;
  **no measured result or demonstration value appears**."
- `docs/process_traces/2026-08-19-prep-sprint/paper-staging/registry-audit.md:3-8`:
  registry authored `0e35990` (2026-08-09), **never revised**; draft revised 14
  times since. **0 of 34** draft-site rows verdict `OK` (25 `STALE-REF`,
  8 `ORPHANED`, 1 `SHIFTED`).
- **Verdict: all six live occurrences are hand-written literals outside the
  registry's control surface.** No `MEASURED`/`DERIVE` row authorizes them; no
  `STOP_FILL` can stop them; the linter
  (`lint_results_prose_template.py`) never sees them.

---

## 4. What the PENDING discipline says these lines should look like

The draft's own two rules:

- `draft-v1.md:145` — operative floor values and decompositions "are withheld
  until issued artifacts are available: **[RESULT PENDING ISSUED ARTIFACTS]**".
- `draft-v1.md:230` — "**[RESULT PENDING ISSUED ARTIFACTS — tables below are
  structural placeholders; no energy value from superseded artifacts is carried
  into this draft.]**"

The trailing clause of `:230` is written **unqualified — "into this draft"**, not
"into these tables". 8.611855 J and 1.869502 J are energy values from a
superseded artifact, carried into the draft at six sites. Under either reading
(scoped-to-§6, or draft-wide) the pair `:230` vs `:124/:157/:226/:258/:272` is a
self-contradiction on the project's top-priority artifact; under D-119
conservative-by-default the draft-wide reading is the one a reader takes.

Compounding, two sentences assert issuance that has not occurred:
- `:124` "**All comparative results issued in this cycle** use the worst-case
  composition above" — no comparative result has been issued this cycle (`:230`).
- `:272` "**Results in this cycle's retained corpus were issued under** the
  conservative 8.611855 J composition" — "issued" here means an a5 non-claim
  replay ran under that composition. The word does unpaid work and a reader
  takes it as published results.

---

## 5. VERDICT

**Per-occurrence:**

| Site | Verdict |
|---|---|
| `:124` | **Illustrative-needs-labeling + false-issuance wording.** Non-claim a5 value presented as the composition of "all comparative results issued in this cycle". Worst of the six. |
| `:157` | **Illustrative-needs-labeling.** Feeds the sizing disclosure with no provenance or era tag. |
| `:226` | **Best-hedged; needs era tag only.** "only as a prospective scale", and the preceding paragraph (`:224`) says "Earlier captures were analysed for diagnosis only — nothing in them can support a claim". Missing: that the *floor number itself* is one of those earlier captures. |
| `:258` | **Illustrative-needs-labeling.** Present-tense "**has** an 8.611855 J floor" in the limitations section — the one place the era caveat belongs and is absent. |
| `:272` (8.611855 ×2, 1.869502 ×2) | **Illustrative-needs-labeling + false-issuance wording.** The relationship *is* correctly stated (B7 as filed = cured); the provenance is not. |
| `:364–:407` (comment block) | **Not a live claim — but a latent forbidden-by-D-119 landmine.** See below. |

**Consolidated verdict: NOT stale (the two numbers are mutually consistent and
their relationship is correctly stated), NOT forbidden outright (prospective-
sizing use of a non-claim diagnostic is legitimate and D-124 explicitly
contemplates it) — but ILLUSTRATIVE-NEEDS-LABELING at all six live sites, and
the labeling is mandatory rather than stylistic**, because (i) `:230` states a
blanket no-superseded-energy-values rule the sites violate; (ii) D-148 cl.7
requires the anchor-v2 population to be disclosed as permanently non-claim-
bearing and `:260` discloses only a9/a10; (iii) the numbers are additionally
n=19-generation-stale against live r6 with no recomputation lane. No located
ruling distinguishes prospective-sizing use from claim use for this cell —
`OPEN-ITEMS.md:829-833` reached the same open question and stopped there. **That
ruling is the magistrate's to make and is the actual adjudication B7 needs.**

**Sharpest single finding (new, not in any prior sweep):** the commented swap
block at `:367`, `:375`, `:391`, `:399` hard-codes **1.869502 J — an a5,
anchor-v2, n=19 number — into sentences that read "Comparative results issued in
this cycle use the pre-registered two-shared-edge calculation … the resulting
comparative false-effect floor is 1.869502 J."** When
`CONDITIONAL-INSERT-TIGHTER-FLOOR` fires at the first post-freeze mint, the mint
produces a *new* floor from prospective alpha/beta/gamma evidence; the a5 number
is not it. `TASK_QUEUE.md:247` does instruct "verify every replacement against
the minted artifact", so process covers it — but the artifact itself is armed
with the wrong number, and the queue row also says "**Do not apply a partial
swap**", which pressures the operator toward mechanical application.

---

## 6. Minimal correct fix, per occurrence, with authority

**Authority for all wording changes: D-119** (`decision_log.md:7777`) — claim
*language* is magistrate-delegated, conservative-by-default, no Ed gate. None of
these change what the project claims to have **done**, so none reach the
not-delegated list. **No number changes anywhere** — the numbers are arithmetically
correct for what they are.

**F1 — one first-use provenance clause at `:124`** (authority: D-119; D-148 cl.7;
D-124 NON-CLAIM record; global writing standard "first-use test"). Replace the
lead sentence and tag the value once:

> ~~All comparative results issued in this cycle use~~ → *The comparative
> composition registered for this cycle's floor cells is the worst-case
> composition above. Replaying it on the retained a5 decode contrast corpus —
> a non-claim diagnostic captured under the superseded pipeline of Section 2 and
> computed against a superseded calibration-acceptance generation — gives
> 8.611855 J. That value is quoted throughout as a scale, never as a result.*

This is the only site needing full prose; it discharges first-use for the other five.

**F2 — `:157`, `:226`, `:258`: short-form tag** (authority: D-119 conservative-
by-default). Append four words at each: "…8.611855 J **(the non-claim a5
diagnostic of Section 3)**". `:226` and `:258` additionally lose the present-tense
"has an … floor" → "gave … as a diagnostic".

**F3 — `:272`: strike the false issuance** (authority: D-119; `:230`). "Results
in this cycle's retained corpus **were issued under** the conservative 8.611855 J
composition" → "*No comparative result has been issued this cycle; the retained
a5 diagnostic was replayed under the conservative 8.611855 J composition.*"
Keep the correct estimator-not-number pre-registration sentence from `c0ee784`
verbatim.

**F4 — extend the era disclosure at `:260`** (authority: **D-148 cl.7**, which
requires the registered-limitation paragraph, and D-146's no-retrofit ruling).
"The retained a9 and a10 characterization quoted in Sections 3 and 7" →
"*The retained a9 and a10 characterization and the retained a5 floor-regime
diagnostic quoted in Sections 3, 6, and 7*". Add one sentence: "*Because those
values were computed against a superseded calibration-acceptance generation and
there is no re-derivation lane, their value under the present instrument is not
recoverable; they are retained as order-of-magnitude scale only.*" **This is the
load-bearing fix — it is what makes F1–F3 true rather than decorative.**

**F5 — reconcile `:230`** (authority: D-119). Either scope the clause honestly —
"no energy value from superseded artifacts is carried into **these tables**" —
or, preferred, keep it draft-wide and add "…**except the explicitly labelled
non-claim diagnostics of Sections 3 and 7**". Do not silently leave both.

**F6 — disarm the swap block** (authority: `TASK_QUEUE.md:247`
CONDITIONAL-INSERT-TIGHTER-FLOOR, live P1, owner Lead; results-fill-registry
`STOP_FILL` discipline). Replace the literal `1.869502 J` at `:367`, `:375`,
`:391`, `:399` with registry-style markers (e.g.
`[F_tokgen_contrast_cmp_two_edge_J]`) plus a one-line note that the value comes
from the minted artifact, never from this file. Add the token as a
`KEY_FROZEN / VALUE_UNISSUED` row to `docs/paper/results-fill-registry.md`.
This is a change to a **queue-fenced block**, so it is the one item here that
should carry an explicit lead/magistrate authorization rather than riding D-119.

**F7 — registry re-anchor (out of B7's scope, flagged).**
`registry-audit.md` reports 0/34 clean draft-site rows against this head. Until
that is repaired, no `STOP_FILL` mechanism protects any hand-written number in
the draft — this class of defect will recur. Belongs in its own queue row.

---

## 7-APPLIED. Magistrate ruled STRICTER READING (2026-08-20); edits applied, not committed

Both literals removed from `docs/paper/draft-v1.md` (6 live sites + 4 armed sites
in the swap block), from the swap block's anchors, and from `TASK_QUEUE.md:247`.
Registry gained a `Swap-block tokens` subsection with
`[F_decode_contrast_cmp_two_edge_J]` (MEASURED, KEY_FROZEN / VALUE_UNISSUED) and
`[F_decode_contrast_cmp_worst_case_J]` (STOP_FILL, SUPPLIER_UNKNOWN). Two
deviations from the brief are recorded in §8 below.

## 8. Deviations from the ruling's stated expectations

**D1 — `:230`'s blanket clause does NOT become true by removing the a5 numbers.**
The brief predicted it would. Verified otherwise: §3/§7 still carry a9/a10
superseded-era *energies* (`:118`/`:122` 0.98–1.47 J envelopes; `:137` 0.5094 /
0.652 / 0.658 / 0.310 / 0.305 / 0.624 / 0.609 J drift figures; `:118` 1.016 J).
The ruling did not remove those, and D-148 cl.7 requires them disclosed rather
than deleted. Left blanket-and-false, the clause is a second claim-integrity
defect. Minimal honest repair applied instead: "carried into **these tables**,
and none appears anywhere in this paper **except the explicitly labelled
instrument diagnostics of Sections 3 and 7**."

**D2 — `[F_decode_contrast_cmp_worst_case_J]` registered STOP_FILL, not MEASURED.**
The old swap text compared the two estimators on the same cell. The mint issues
one comparative floor per cell under the estimator that cell selected, so no
output field supplies a same-cell worst-case counterpart. Registering it MEASURED
would have re-armed the exact defect just removed — a token that cannot fill,
inviting a hand-written substitute. STOP_FILL makes the clause drop at fill time.

**Also flagged, outside the authorized write scope (not edited):**
- `CLAIMS_STATUS.md:41-42` — "**Issued results in this cycle** remain under the
  conservative 8.611855 J composition." Same false-issuance defect the ruling just
  struck from the paper, in a claim-status document. Highest-priority follow-up.
- `docs/site/decision_log_archive_4.html:1` — a **published** site artifact
  carrying the literal.
- `docs/strategy/2026-08-14-70h-plan.md:131` — the plan's definition of
  DEFENSIBLE gates every comparative claim on "its 1.869502 J floor". That
  definition is now unsatisfiable as written and needs re-anchoring to the
  estimator identity.
- `docs/paper/results-fill-registry.md` remains unrevised since `0e35990` apart
  from this addition; `registry-audit.md` still reports 0/34 clean draft-site rows.

## 9. Residual open question for the magistrate

Is prospective-sizing use of a permanently non-claim-bearing, era-superseded
floor value **admissible at all** in the published paper, even fully labelled?
F1–F5 assume yes-with-labels (the conservative-but-usable reading, consistent
with D-124's "material for D-117" framing and `:224`'s "diagnosis only" posture).
The stricter reading — that D-148 cl.7 plus `:230` mean these numbers leave the
draft entirely and the thin-margin warning at `:226` is re-stated qualitatively
("the projected contrast is thin against the conservative composition") —
survives every rule cited here and costs only precision the project cannot
currently substantiate. **No located ruling decides between them.**
