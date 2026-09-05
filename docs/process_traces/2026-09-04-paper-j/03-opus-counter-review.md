# 03 — Opus counter-review (gate ledger row 6), seat J

Reviewer: Opus counter-review seat. Date: 2026-09-04.
Worktree: `/Users/edr/code/JouleWise-wt-paper-j`, branch `feat/2026-09-04-paper-j`,
HEAD `89b53af3`. Diff under review: `git diff origin/main...HEAD -- docs/paper`.
Read-only except this file. No commit, no push.

---

## VERDICT

**NOT LANDABLE.**

Two of the three cures introduce a fresh instance of the exact defect class they
were dispatched to remove. Both are single-sentence bench edits; neither
falsifies a claim, changes a number, or breaks a gate. Re-running the two
authorized test modules after the edits is sufficient re-verification.

What is **confirmed correct** and should not be re-litigated:

- **CR-08 is factually TRUE, and it repairs a real numerical inconsistency.**
  `joulewise/powermetrics_fiducial.py:1043` computes
  `b_fiducial_s = max(worst_per_edge) + float(trace_anchor_bound_s)`, and
  Appendix A.3.6 (`docs/paper/draft-v2-skeleton.md:1662-1664`) states
  `B_fiducial = max over the 118 edge excursions + B_anchor`. The pre-cure
  Introduction defined the pulse-derived limit as the displacement term **only**,
  which did not match the number the paper prints for it
  (`0.030067931757111657` s at skeleton lines 241, 1339, 1341 — a value that
  *includes* `B_anchor = 0.0011349971959968978` s). The cure closes a 1.135 ms
  definitional gap, not merely a wording gap.
- **CR-07 honored exactly.** The Abstract block
  (`## Abstract` → `## 1. Introduction`) is byte-identical between
  `origin/main` and HEAD: SHA-256
  `a52064fd715629bc73c1e87aa0534c2dfd455293d01e5c3f44aa20322fc3a9b7` on both.
- **Ledger arithmetic exact.** 266 data rows (header at line 1735, separator
  1736, data 1737–2002); the closing line states `Terms inventoried: 266`.
- **`[FILL]` count unchanged:** 140 markers at `origin/main`, 140 at HEAD.
- **Ledger homes of the added/re-homed rows are the true first reader-facing
  use in selected-A order.** `short-input diagnostic records` → first occurrence
  selected-A line 1345 (§10); `clock-anchor bound` → selected-A line 62 (§1);
  `phase boundary / phase edge` → selected-A line 38 (§1). The Abstract uses
  plain-language paraphrase ("dividing time", "earlier measurements of short
  requests") and does not contain any of these terms, so §1/§10 homes are right.
- **Row removals justified.** `point-only component bounds` and
  `point-only unguarded bound` no longer appear in the prose (see B2 for the
  residue the second removal left behind).
- **Tests.** `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest
  tests.test_paper_first_use_ledger tests.test_paper_terms_lint` → `Ran 13
  tests ... OK`. Matches the seat's reported 10 + 3.
- **`pulse-derived limit` is now fully canonical** in the body: 9 occurrences,
  zero survivors of `pulse-derived bound` / `pulse-derived timing bound`.
- **`phase edge` is fully retired** from the body: one occurrence, the alias
  declaration itself.

Both Sol refuters returned zero findings. The two blockers below are the
sentence-granularity misses.

---

## BLOCKERS

### B1 — the CR-08 cure sentence uses `wall-clock time` eight lines before the paper builds the two-clock distinction

`docs/paper/draft-v2-skeleton.md:79-81` (selected-A 61-63):

> The largest displacement between the commanded times and every edge position
> allowed by the pulse records, plus the **clock-anchor bound**—the uncertainty in
> placing the power record on wall-clock time—is the **pulse-derived limit**.

The build of `wall clock` arrives at `draft-v2-skeleton.md:89`:

> …does not assume that the computer's wall clock and its monotonic clock—a counter
> that advances but is never corrected to civil time—advance at exactly the same rate.

This is a late-arriving term **inside a cure sentence** — the one construction
the binding standard names outright. It is not a stylistic quibble: the physical
fact that makes "uncertainty in placing the power record on wall-clock time"
mean anything is that this machine carries *two* clocks that need not agree, and
the reader does not yet have that fact. Until line 89 the gloss is words, not a
mechanism, and a reader cannot replicate what `B_anchor` prices.

The paper treats `wall clock` as a term of art elsewhere — Appendix A.3 opens
with a conventions paragraph pinning it (`"Wall clock" means the controller's
Unix-epoch UTC clock (time.time())`, skeleton line 1437) — and the ledger homes
`monotonic clock` at `1. Introduction` (line 89). There is **no ledger row for
`wall clock` / `wall-clock time` at all**, so the term the cure now leads with is
unregistered.

Cure shape (one of):

1. Gloss in place inside the appositive: "…—the uncertainty in placing the power
   record on wall-clock time, the machine's civil clock, whose rate need not match
   the never-corrected counter introduced below—…"; or
2. Move the first clause of the line-88 paragraph (wall clock vs monotonic
   clock) ahead of the pulse paragraph so the contrast precedes the appositive.

Either way, add a ledger row for `wall clock / monotonic clock` homed at
`1. Introduction`, or extend the existing `monotonic clock` row (line 1790) to
cover the pair.

Secondary, same sentence: the previous ledger description for `clock-anchor
bound` ended "and points to the construction next"; the re-homed row (line 1787)
drops the pointer, and the Introduction sentence gives none. At first use the
reader has no route to where the bound is built. Add "constructed in Section 2
and Appendix A.3.3" to the sentence or the row.

### B2 — the CR-06 rename orphans the `"Unguarded"` gloss: it now unpacks a word that is not in the term it purports to define

`docs/paper/draft-v2-skeleton.md:505-509` (selected-A 487-490). The cure changed
`first calculate a **point-only unguarded bound**` to `first calculate its
**point-only value**`, but left the two-part unpacking that followed it intact:

> For either component, first calculate its **point-only value**. An
> **admitted energy** is an energy from a run that passed the Section 5 entry
> checks and may therefore bear a claim. "Point only" means using each admitted
> energy at its recorded value. **"Unguarded" means before the later
> small-sample multiplier**, the factor that widens a result to allow for
> limited repetition, and before the whole-window allowance.

A reader hits a scare-quoted word being defined, looks back for it in the term
just introduced, and does not find it. That is the same first-use failure CR-06
was dispatched to remove, newly created by the cure.

It is not a dangling gloss that can simply be deleted: `unguarded` remains
load-bearing at four later sites — selected-A 555 ("the same complete unguarded
formula"), 653 ("the complete comparative unguarded formula"), 710 ("its
unguarded value"), 741 ("unguarded corner values 1.6656 J absolute and 1.7656 J
comparative", which feeds the worked cell-floor example).

Compounding it: deleting the `point-only unguarded bound` ledger row removed the
**only** ledger coverage of `unguarded`. Grep of the ledger returns zero rows
containing the string. The adjective is now used four times with no registered
first-use home.

Cure shape (one of):

1. Restore the compound as the calculated object's name — `first calculate its
   **point-only unguarded value**` — and restore a ledger row for it homed at
   `Comparing the boundary-moved and point-only values`; or
2. Keep `point-only value` and re-anchor the adjective explicitly:
   `"Unguarded", used below for any value taken before the later
   **small-sample multiplier** … and before the whole-window allowance.` — plus a
   ledger row for `unguarded` homed at the same section.

Option 1 is the smaller diff and keeps the §4 name aligned with the §1 build.

---

## SHOULD-FIX

### S1 — `point value` survives at `draft-v2-skeleton.md:591` as an undeclared fourth name for U_point

> Under the retired guarded calculation, the same multiplier was applied to each
> corner value and its matching **point value**, so it cancels from their
> quotient. The three **corner/point pairs** are \(3.153/0.2888=10.92\),
> \(2.922/0.4934=5.92\), and \(2.184/0.3113=7.02\)…

`0.2888`, `0.4934`, `0.3113` are exactly the point-only values printed at
skeleton line 424. So `point value` here *is* U_point, under a name the cure did
not canonicalize — the residue CR-06 was written to eliminate.

Cure shape: `…applied to each corner value and its matching point-only value…
The three corner-to-point-only pairs are…`.

(`point value` at `draft-v2-skeleton.md:300` reads as generic "a single number
rather than an interval" in the null-ladder containment discussion, and
`draft-v2-skeleton.md:1487` is the appendix's interval midpoint — neither is
U_point. Leave both.)

### S2 — CR-06 canonicalized the denominator and left the numerator with six names

U_point is now one canonical name plus one declared alias. U_corner, the thing it
is divided into, still surfaces as:

| Surface form | selected-A line | Skeleton line |
|---|---:|---:|
| `moved-edge limit` (the §1 canonical, used **once** in the whole body) | 101 | 119 |
| `edge-moved corner maximum` | 417 | 435 |
| `boundary-moved bound` (and the §4 heading) | 463, 466 | 481, 484 |
| `independent-edge corner bound` (the operational definition, symbols \(U_{\mathrm{abs,corner}}\) / \(U_{\mathrm{cmp,corner}}\)) | 541 | 559 |
| `corner value` | 573, 741 | 591, 759 |
| `unguarded corner values` | 741 | 759 |

A metrology reader who has just been taught that the denominator has exactly one
name will read the asymmetry as significance and hunt for a distinction that is
not there. This is out of CR-06's stated scope (which named U_point only), so it
is not a blocker for this landing — but it is the same defect, and leaving it
means the next pedagogy pass re-opens the file.

Cure shape: elect `moved-edge limit` as the §1 canonical, keep
`independent-edge corner bound` as the explicit operational alias declared at
skeleton line 559, and reduce the remaining four to those two.

### S3 — `at the phase boundary` (singular) at `draft-v2-skeleton.md:279-280` contradicts the plural used for the same object in §4

> Each of the four member energies has its recorded value **at the phase
> boundary** and an edge-moved allowance \([A_1^L,A_1^U]\), …

A member energy is a phase energy delimited by *two* boundaries; §4 says so
explicitly at skeleton line 557: "moving its **phase boundaries** through every
position allowed by the session calibration." The singular tells the reader the
allowance is one-sided, which is the wrong physical picture for the
\([\,\cdot^L,\cdot^U]\) intervals in the same sentence.

Cure shape: `…has its recorded value at its phase boundaries and an edge-moved
allowance…`.

---

## NITS

### N1 — two aliases declared and never used again

`recorded-edge limit` (`draft-v2-skeleton.md:115-116`) and `phase edge`
(`draft-v2-skeleton.md:56`) are each introduced as an explicit alias and then
appear **nowhere else in the body** — `recorded-edge` survives only in ledger
rows 1741 and 1857, `phase edge` only in ledger row 1746. The standard says a
term is built, glossed, or **deleted**; an alias that never returns is reader
load with no payoff.

This is defensible if the alias is retained deliberately because the advisor's
vocabulary uses it (plausible for `recorded-edge limit`, the earlier canonical).
If so it should be stated as such; otherwise drop both alias clauses.

### N2 — ledger row 1857 still describes the ratio in the retired vocabulary

> `| shared-error ratio | 1. Introduction | … | The **moved-edge to
> recorded-edge** division when one timing error moves across the four-run
> comparison. |`

After canonicalization the denominator's name in prose is `point-only value`.
Cure shape: `The moved-edge to point-only division…`.

### N3 — the CR-05 cure introduces `brief prompt processing` where §6 says `short prompt processing`

`draft-v2-skeleton.md:1389`, `:1395`, `:1401` (all three Conclusion branches) and
ledger row 1770:

> The retained **short-input diagnostic records** are the earlier measurements of
> requests with **brief prompt processing**.

§6's subsection heading and body use `short prompt processing`
(`draft-v2-skeleton.md:997`, `:424`). `brief` vs `short` is a one-word synonym
drift created by a CR-06-adjacent cure.

Cure shape: `…requests with short prompt processing`, in all three branches and
in ledger row 1770.

---

## Method and evidence

- Selected outcome A produced with
  `python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source
  docs/paper/draft-v2-skeleton.md --output /private/tmp/pj-64281-A.md --outcome A`
  → `selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4,
  refusal_reason_slots=1, abstract_words=200`. Sections 1–4 and 10 read in order.
  Temp file removed at the end of this review.
- CR-08 fact check against `joulewise/powermetrics_fiducial.py` (line 1043 and
  its comment: "The capture's own trace anchor is an independent causal shift of
  every fitted trace interval. It is additive to the estimator's worst residual
  excursion and can never shrink the old bound.") and against the registered
  `B_fiducial` definition in Appendix A.3.6.
- Synonym sweep run over the whole body (selected-A lines 1–1665, i.e. everything
  before `## First-use audit ledger`) for the `phase edge`/`phase boundary`,
  `point-only`/`recorded-edge`/`point value`, `pulse-derived`, and
  `corner`/`moved-edge`/`boundary-moved` families.
- Ledger row count taken structurally from the table (`| Term |` header, `|---|`
  separator, 266 data rows) rather than from the seat's stated figure.
- Tests: only `tests.test_paper_first_use_ledger` and `tests.test_paper_terms_lint`,
  with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`. `Ran 13 tests ... OK`.
