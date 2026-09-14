# Record 35 — Fresh-eyes final-head review of `f8e95d2d` (gate row 10)

- **Reviewer:** Opus 5 (1M context), fresh-eyes final-head seat, gate row 10.
- **Worktree:** `/Users/edr/code/JouleWise-wt-paper-n`, branch `fix/2026-09-12-paper-n-binary64-gloss`.
- **Head at review:** `f8e95d2d` (`git rev-parse HEAD` confirmed before any file was opened).
- **Commit under review:** `git show f8e95d2d` — 3 files, +281/−3:
  `docs/paper/protocol/first-use-audit-ledger.md`, `tests/test_paper_first_use_ledger.py`,
  and the new record `34-followup-counter-review-opus.md`.

## Contamination disclosure

**Not blind, unavoidably.** Record 34 is *inside the commit under review*, and the brief frames every
check as "did S1–S3 land." I therefore read record 34 in full before forming a view, and my agenda
for items (1)–(5) is shaped by its three cures. I also read the same-signature sections of records
21 and 28 and the `same_signature` block of record 31 — only those sections, for the comparison this
brief requires. I did **not** read records 31 or 33 in full, and I did not read any fix-round brief.

Mitigation: every claim below is re-derived from primary text in this worktree at `f8e95d2d` — I
quote the draft, the protocol, the ledger, and the test source directly, and **two of my three
substantive findings contradict record 34** (its S2 home proposal would have failed the suite; its
S1 direction was inverted by the commit and the commit's choice is the wrong one).

**What I ran.** `python3 -B -m unittest tests.test_paper_first_use_ledger` once (11 tests, OK,
1.96 s) — one module, not the suite, per the brief. Four read-only mutation probes: composite
draft+protocol+ledger files written to the session scratchpad and fed to the test through
`PAPER_FIRST_USE_DRAFT`, exploiting `_audit_text`'s "embedded ledger keeps its own read order"
branch. **No repository file was read-modified;** the probes mutate scratchpad copies only. My only
write in the repo is this report. The worktree carries six untracked `*-report.manifest.jsonl` seat
manifests under this trace directory, none in the diff.

## Per-item table

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1a | Two new rows' **homes** = section of first occurrence in the draft | **PASS (both)** | Quoted below; and the commit's home for the second row is *more* correct than record 34's proposed cure. |
| 1b | Two new rows' **statuses** match the header definitions | **PASS for `binary64`; FAIL for `member-envelope integral sum` (S1)** | `built-before` is defined as construction *before* the first named use; the construction *is* the first named use. |
| 2 | Membership assertion is non-vacuous | **PASS, proved by mutation** | `listed` = 28 expressions (printed below); probes A and B both go red. |
| 3 | Extending the closed class was legitimate | **PASS for `measurement interval`; FAIL for `deterministic bound` (S2)** | The paper *defines* "deterministic bound" at protocol:357. |
| 4 | Footer count 263 = row count | **PASS** | 263 data rows parsed; the test binds the two. |
| 5 | No draft change in this commit | **PASS** | `git show --name-only` lists three files, none the draft. |

### Item 1 — quoted

**Row 141.** `| binary64 | Record support in two historical model stacks | glossed-at-first-use | Glossed at its first main-text use as the usual 64-bit floating-point format; Appendix A.3 restates the convention. |`

First occurrence of `binary64` in `docs/paper/draft-v2-skeleton.md` is **line 740** (grep: 740, 742,
979, 1004, 1029, …):

> The event-duration statistic subtracts binary64 (the usual 64-bit floating-point format) epoch values before rounding;

The nearest `##`/`###` heading at or above 740 is **line 617, `### Record support in two historical
model stacks`** — exactly the declared home. The gloss is in the same sentence as the first named
use, so `glossed-at-first-use` ("supplies a plain-word definition … in the same sentence or
paragraph") is exactly right. The disposition's second clause is also true: draft 979 restates it as
"the IEEE-754 double-precision floating-point format that Python floats use," and 979 sits under
`### A.3 Formal calibration algorithms` (line 975). **Row 141 is correct in all four cells.**

**Row 142.** `| member-envelope integral sum | A.3 Formal calibration algorithms | built-before | Built in Appendix A.3.10 from the four member integrals with absolute contrast weights before its two uses there. |`

First occurrence is **draft line 1370**, inside `#### A.3.10 Shared-sign rounding and illustration`
(heading at 1366):

> In **binary64**, the usual 64-bit floating-point format, `ulp(1.0)` is the gap between 1 and the next larger representable number. The **member-envelope integral sum** is \(\sum_{m\in\{A_1,B_1,B_2,A_2\}}|c_m|\int_{\mathrm{start}_m-b}^{\mathrm{end}_m+b}P_m(t)\,dt\), where \(c_m=(-1/2,+1/2,+1/2,-1/2)\) …

The two later uses the disposition claims are real: **1378** ("It sets \(M=\max(1,\dots,\text{member-envelope integral sum})\)")
and **1399** ("This member-envelope integral sum exceeds the other scale candidates"). Record 34's
S1 complaint that the cell said "its only use" is therefore **cured**, and "absolute contrast
weights" is faithful to \(|c_m|\) and to line 1383 ("summed with absolute contrast weights of 1/2").

**The home cell is correct, and record 34 was wrong about it.** `SECTION_HEADING =
re.compile(r"^(#{2,3})\s+(.+?)\s*$")` recognises `##` and `###` only; `#### A.3.10 …` matches
neither, so the nearest recognised heading above 1370 is `### A.3 Formal calibration algorithms`
(975). Record 34's S2 cure proposed the home `A.3.10 Shared-sign rounding and illustration`.
Mutation probe **C** applied exactly that cure and the suite went red:

```
AssertionError: 'A.3.10 Shared-sign rounding and illustration' not found in {…}   # unknown home
```

The commit chose the only admissible home. That is a real, unprompted correction of the
counter-review, and it should be recorded as such.

**The status cell is wrong — see S1.**

### Item 2 — the membership assertion is non-vacuous

`listed` parses to **28 expressions** (my own `python3 -B` run of the test's exact regexes over the
ledger text at `f8e95d2d`):

```
append-only, argmin, complete, completeness, corpus range, cumulative counter,
degrees of freedom, detected, deterministic bound, exact equality,
full-history checkout, infeasible, linear programme, malformed, measurement interval,
missing, null hypothesis, quarantine, random scatter, refused, refuses, repeatability,
repetition, run bundle, sampler cadence, tail area, third-party dependencies, threshold
```

The trailing-parenthetical strip (`re.sub(r"\s*\(.*?\)\s*$", "", item)`) does its job: the two new
entries enter the set as bare `measurement interval` and `deterministic bound`. Seventeen rows carry
`audience-vocabulary`; all seventeen match.

Non-vacuity is not argued, it is **demonstrated**:

| Probe | Mutation (scratchpad copy only) | Result |
|---|---|---|
| control | unmutated composite | `rc=0` |
| **A** | flip row 143 `ulp` from `glossed-at-first-use` to `audience-vocabulary` | `rc=1` — `AssertionError: Lists differ: ['ulp'] != []` |
| **B** | delete `, measurement interval (…)` from the header class | `rc=1` — `AssertionError: Lists differ: ['measurement interval'] != []` |
| **C** | retarget row 142's home to the `####` heading | `rc=1` — unknown home |

Probe A answers the brief's question directly: **a row claiming the class for an unlisted term
fails.** Probe B additionally proves the two header extensions are *load-bearing* — without them the
suite is red, which is precisely why the extension route is the one that needs adjudicating (item 3).

### Item 3 — quoted, and my judgment

**`measurement interval` — the extension is legitimate.** Its first occurrence is draft **866**:

> …its associated SPEC methodology requires load-specific analyzer uncertainty, fixed ranges, **minimum measurement intervals**, invalid-sample accounting, clock synchronization, and controlled battery behavior [1] [2].

That line sits in `### Benchmark and metrology lineage` (862), under `## 6. Related work` (845), so
the header's parenthetical "in Section 6" is **factually correct**. The phrase is used here as the
SPECpower/MLPerf-Power literature's own term, inside a citation of that literature, and the paper
never redefines the bare phrase — it defines a *different*, adjacent term (`statistical measurement
interval`, its own row with its own home, pinned in the test's `senses` dict). A metrology professor
reading a related-work paragraph does use "measurement interval" without definition. **PASS.**

**`deterministic bound` — the extension is not legitimate; the row should have been reclassified.**
The decisive fact is that **the paper defines the term itself**, at
`docs/paper/protocol/prospective-comparison-protocol.md:357`:

> **A deterministic bound is a non-random maximum displacement carried in the authenticated block record.**

The header's added parenthetical, "(a non-random maximum displacement)", is a *verbatim excerpt of
the paper's own definition*. An expression that the paper stops to define cannot simultaneously be
"a textbook-statistics or plain-English expression the intended metrology/CS professor uses without
definition." That is a direct contradiction of the header's own class definition, and it is
self-evident on the face of the extended header: the class of undefined words now carries
definitions.

The reading-order problem is the reason it matters. The first use is protocol **273**, eighty-four
lines *before* the definition:

> This empirical allowance samples the registered reference epochs; **it is not a deterministic bound on arbitrary unobserved excursions between them.**

And in the reader-facing draft the term's technical sense arrives earlier still, at **267**, in the
same denial form:

> Under the independent-normal model, the second is a two-sided 95% prediction amount for one further observation; **it is not a deterministic future-error bound.**

(and again at 1228: "It is not a deterministic out-of-sample guarantee.") Every use the reader meets
first is a **denial of a guarantee**. A reader who has not been told what a deterministic bound *is*
cannot evaluate what is being denied — this is exactly the first-use failure the ledger exists to
catch, and exactly the standing writing rule's case ("a term whose meaning arrives only in later
text fails the draft"). The ledger's own disposition cell already concedes the point: it opens with
the definition ("A non-random maximum displacement; the first use denies such a guarantee…"), which
is the prose shape of `glossed-at-first-use`, not of audience vocabulary.

One more internal inconsistency seals it: ledger row **168** carries
`| deterministic-bound kinds / interpolation edge | Directional comparison | glossed-at-first-use | … |`.
The ledger glosses the *derivative* of the term and exempts the *base* term as common knowledge.

**Judgment: the class extension is the wrong instrument for this row.** Record 34's S3 warned that
without a mechanical assertion "this recurs the next time a reviewer wants a row to stop failing."
The commit installed that assertion and, in the same commit, widened the class so the two rows it
would have caught pass anyway. The assertion is a real gain — probes A and B prove it bites — but
these two rows were **grandfathered, not adjudicated**, and one of them fails on the merits.

### Item 4 — count

263 data rows parsed from the table at `f8e95d2d`; the footer reads "Terms inventoried: 263; FAILS:
0." The test binds both (`self.assertEqual(row_count, len(self.rows))` and the FAILS count), so this
cannot silently drift. Status census: 232 `glossed-at-first-use`, 17 `audience-vocabulary`, 12
`built-before`, 2 `forward-pointer-next-paragraph`. **PASS.**

### Item 5 — no draft change, and numeral census

`git show --name-only f8e95d2d` → ledger, test, record 34. **The draft is untouched.** Numeral-token
census over the two non-record files (`python3 -B`, tokens `\d+(?:\.\d+)*`):

```
ADDED   {'6': 1, '64': 2, '3': 2, '3.10': 1, '263': 1, '0': 1, '1': 1}
REMOVED {'64': 3, '3.10': 1, '262': 1, '0': 1}
```

Every token is accounted for by inspection of the seven numeral-bearing changed lines: `6` =
"Section 6" in the header parenthetical; `64` = the two "64-bit" glosses replacing three in the old
grouped row; `3` ×2 = "A.3 Formal calibration algorithms" (home cell) and "Appendix A.3 restates";
`3.10` = the A.3.10 locator, carried over; `1` = `group(1)` in the new test code. **The only
quantity of record that changed is the inventory count 262 → 263, which is required by the split.**

## Findings

**Blocker: none.** The split is correct, the homes are right, the count is right, the assertion is
real, and no draft text and no measured quantity moved.

### S1 (should-fix) — row 142's status `built-before` contradicts the header's own definition

Site: `docs/paper/protocol/first-use-audit-ledger.md:142`.

Header (`:3`): "`built-before` means the body constructs the referent from physical inputs **before
its first named use**." Header (`:4`): "`glossed-at-first-use` means the first named use supplies a
plain-word definition **or an equivalent calculation in the same sentence or paragraph**."

Draft 1370 is one sentence: "The **member-envelope integral sum** is \(\sum…\)". The bolded name
comes *first*; the construction is the predicate of that same sentence. Nothing constructs the sum
before 1370 — the preceding sentence is about `ulp(1.0)`. So the construction is not *before* the
first named use; it *is* the first named use, supplying an equivalent calculation in the same
sentence. That is the second definition, verbatim.

This inverts record 34's S1, which had reached the same conclusion ("The row is in fact
`glossed-at-first-use` on the strictest reading — the first *named* use at 1370 is the sentence that
defines it by formula") and asked for the disposition to stop borrowing the other class's verb. The
commit instead moved the *status* to match the borrowed verb. Nothing mechanical catches this:
`STATUSES` checks the name only, and there is no positional assertion for `built-before` rows.

**Minimal cure (one cell, no draft change, no count change):**

```
| member-envelope integral sum | A.3 Formal calibration algorithms | glossed-at-first-use | Defined by formula at its first named use in Appendix A.3.10 — the sum of the four member integrals under absolute contrast weights — before its two later uses there as a scale candidate. |
```

### S2 (should-fix) — reclassify `deterministic bound` and remove it from the closed class

Site: ledger `:5` (header class) and `:167` (the row); the prose cure is in
`docs/paper/protocol/prospective-comparison-protocol.md:273`.

Argued in item 3. The paper defines the term at protocol 357; a defined term is not audience
vocabulary; every earlier use is a denial the reader cannot evaluate.

**Minimal cure (one clause of prose + two ledger edits, no numerals):** gloss at the first use,
reusing the paper's own words —

> …it is not a **deterministic bound** — a non-random maximum displacement carried in the authenticated block record — on arbitrary unobserved excursions between them.

— then set row 167's status to `glossed-at-first-use` (its disposition text already reads as one)
and delete `, and deterministic bound (a non-random maximum displacement)` from the header class,
leaving `…, argmin, detected, and measurement interval (…)`. Probe B's shape confirms the suite goes
red if the class entry is removed without the reclassification, so the two edits must land together.
This touches the protocol file, which is outside this commit's scope — it belongs in the next
commit, not in a revision of `f8e95d2d`.

### S3 (should-fix) — close the escape route the extension used

Site: `tests/test_paper_first_use_ledger.py`, the new block at `:512–527`.

The commit's own history is the argument: faced with two rows that failed a newly mechanised class,
the round widened the class rather than adjudicating the rows. Nothing stops that from happening
again, and the widening is invisible to every existing assertion. One further assertion makes the
route auditable by forbidding the thing that is definitionally incoherent — a *glossed* entry in a
class of *unglossed* expressions:

```python
self.assertEqual(
    [item for item in re.split(r",\s*(?:and\s+)?", header_match.group(1).replace("\n", " ")) if "(" in item],
    [],
    "audience-vocabulary entries may not carry a gloss: a defined expression is not audience vocabulary",
)
```

With S2 landed, only `measurement interval (…)` remains parenthesised; its parenthetical is a
*disambiguation* against the paper's `statistical measurement interval`, not a definition, so the
honest form is to move that note into the row's disposition cell (where it already lives, verbatim)
and leave the header entry bare. Then the assertion holds, and the next reviewer who wants a row to
stop failing must reclassify it.

### N1 (nit) — the membership assertion uses `any`, so a grouped row can still smuggle an unlisted term

Site: `tests/test_paper_first_use_ledger.py:522` — `and not any(alt.casefold() in listed for alt in
_alternatives(row.term))`.

A row like `null hypothesis / tail area` passes if **either** alternative is listed. Mutation probe
**D** proves it: deleting `tail area` from the header class leaves the suite **green** (`rc=0`).
This is the identical escape-by-grouping hole that this very commit just closed on the home column
(record 34's S2: "Grouping two terms is exactly how a row escapes its own home assertion"), left
open one column to the right. All seventeen rows currently satisfy the stronger form, so the cure is
free.

**Minimal cure:** `not any(...)` → `not all(...)`. One word.

### N2 (nit, no action now) — the class-list parser is comma-fragile

`re.split(r",\s*(?:and\s+)?", …)` will shear any future entry whose parenthetical contains a comma,
silently producing junk members rather than failing. Harmless today (neither new parenthetical has a
comma) and moot if S3 lands, since S3 forbids parentheticals outright. Recording it so the choice is
deliberate.

### N3 (nit, no action) — record 34's own verification narrowing, inherited

Record 34 declined to re-run the suite and recorded the reasoning. I ran one module
(`tests.test_paper_first_use_ledger`, 11 tests, OK) because the commit edits that module and its
data file, and the mutation probes exercise the new code path directly. The commit touches nothing
else that any other module reads. **I do not call for a broader re-run before merge.**

## Same-signature statement vs records 21 / 28 / 31 / 34

The family at issue is **(b): the acceptance instrument certifying more than the text supports or
more than its consumer verifies.** Its history in this series:

- **Record 21** (round 2): ledger row 95 asserted `glossed-at-first-use` at an unbuilt first use — "the ledger row that declared it … was not re-read against the text."
- **Record 28** (round 3): SF-28-1, "an artifact asserting more verification than it performed"; record 28 judged it a single occurrence and declined to escalate.
- **Record 31** (post-merge): `"same_signature": {"answer": "yes", … "an audit disposition certifying more than its consumer verifies"}`, sited at ledger:141.
- **Record 34** (counter-review): family (b) "reproduced, at reduced severity… the **second consecutive round**… **On its face the standing escalation trigger is met**," but declined the consult because the recurrence was fully explained by two un-installed parts of record 31's own cure ("ruled-not-installed"), and set an explicit tripwire: "**If a fourth family-(b) instance appears after the assertion is in the test, that is a genuine structural problem and the escalation should fire then.**"

**Verdict: family (b) is reproduced a third consecutive round, and record 34's own tripwire has
fired.** The assertion *is* now in the test, and two fresh family-(b) instances stand in the same
instrument: **S1**, a status cell certifying a class (`built-before`) the text does not satisfy —
the same cell record 34 had just rewritten — and **S2**, a header class certifying "used without
definition" for a term the paper defines eighty-four lines later. Family **(a)** (a prose edit
leaving live uses of a term whose build it moved) is **not** reproduced: this commit changes no
prose at all.

But the *mechanism* of the recurrence has changed, and that changes the right response. Rounds 1–3
recurred because named cures were **not installed**; this round installed its mechanism (probes A
and B prove it bites) and also, unprompted, corrected the counter-review's home proposal (probe C).
What recurred instead is a pair of **judgment calls made unilaterally to keep the new mechanism
green** — status word, and class membership. That is closer to the lieutenant-forbidden list
("adjudicating severity downward," "self-exempting from a mandatory trigger") than to a missed fix.

So I do not recommend a fourth prose round, and I do not recommend a full council. I recommend the
**one-question cold consult** that the standing rule asks for, run in parallel with the mechanical
cures: *is `deterministic bound` audience vocabulary, given that protocol:357 defines it?* S1, S3
and N1 are mechanical, have unambiguous primary-text answers, and need no adjudication; they should
land regardless of that ruling. If a fifth family-(b) instance appears after S3's assertion is in
the test, the structural problem is proven and the next spend is the topology question, not the
ledger.

## Recommendation

**ADVANCE `f8e95d2d` — the split, the homes, the count and the membership assertion are all correct
and the draft is untouched — and land S1 (one status cell), S2 (one protocol clause + reclassify row
167 + unlist it), S3 (forbid glossed entries in the closed class) and N1 (`any` → `all`) as one
consolidated follow-up commit, with S2's class question put to a single cold-gate ruling in
parallel rather than decided at the bench.**

— Opus 5 (1M context), fresh-eyes final-head seat, gate row 10; head `f8e95d2d`, worktree
`/Users/edr/code/JouleWise-wt-paper-n`.
