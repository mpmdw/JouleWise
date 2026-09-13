# Record 34 — Opus counter-review of the Paper-N follow-up (gate rows 6 and 10)

- **Reviewer:** Opus 5 (1M context), counter-review seat, gate rows 6 and 10.
- **Branch:** `fix/2026-09-12-paper-n-binary64-gloss`, worktree `/Users/edr/code/JouleWise-wt-paper-n`.
- **Head at review:** `d0884550`. **Code diff under review:** `git diff 76a2f2a7..ff3b59b9 -- docs/paper README.md` (3 files, +4/−4). `ff3b59b9..d0884550` adds only records 32/33; no code.
- **Inputs read before forming a view:** record 31 (post-merge review, F1/F2) and record 33 (Astra refuter). Also read the same-signature sections of records 16, 21, and 28 for the signature comparison this brief requires.

## Contamination disclosure

This is **not a blind review**. I read record 31's findings F1/F2 and record 33's clean verdict
before examining the diff, as the brief directed; my agenda for items (1)–(4) is therefore shaped by
F1's four-part minimal cure. Mitigation: every claim below is re-derived from primary text in this
worktree at `ff3b59b9`/`d0884550` — I quote the draft, the protocol, the ledger header, and
`tests/test_paper_first_use_ledger.py` directly rather than relying on either record's assertions,
and two of my three should-fix findings are things neither prior record reports.

Other contamination facts: I ran **no** test suite and **not** the build script, per the brief. I ran
three read-only `grep`/`sed` passes and one `python3 -B` script that only shelled `git show` and
counted numeral tokens; no repository state was modified. The worktree carries six untracked
`*-report.manifest.jsonl` files under this trace directory (seat manifests), none of them in the
diff. My only write is this file.

## Per-item table

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | binary64 gloss at draft ~740 correct, minimal, consistent with the appendix definition at ~979 | **PASS** | Draft 740 is the *first* occurrence of `binary64` in `draft-v2-skeleton.md` (grep: 740, 742, 979, 1004, 1029, …). The gloss is "(the usual 64-bit floating-point format)" — 6 words, no new term of art. Appendix 979: "\"binary64\" means the IEEE-754 double-precision floating-point format that Python floats use." Double-precision *is* 64-bit; no contradiction. The inserted wording is **verbatim** the gloss the draft already carries at 1369 ("In **binary64**, the usual 64-bit floating-point format"), so the draft now glosses the term identically at its first main-text use and at A.3.10. |
| 2 | The two ledger rows' new statuses match the header's definitions and the prose | **PASS on the status word for both rows; one disposition cell FAILS (S1)** | Quoted below. |
| 3 | README line 12 reads correctly after the edit | **PASS** | Quoted below. |
| 4 | Member-envelope integral sum built in A.3.10 before its only use, as the row claims | **FAIL as stated (S1)** — it *is* built before first use, but "its only use" is false and "built" is the wrong class word | Draft 1370–1377 builds it; 1378 and 1399 use it. |
| 5 | First-use check of the one edited sentence | **PASS for the inserted text; one pre-existing un-inventoried term (N1)** | `event-duration statistic` occurs once in all of `docs/paper/` and has no ledger row. |
| 6 | No numeral changed | **PASS** | Mechanical token census below. |

### Item 2 — quoted

Ledger header definitions (`docs/paper/protocol/first-use-audit-ledger.md:4–5`):

> `glossed-at-first-use` means the first named use supplies a plain-word definition or an equivalent calculation in the same sentence or paragraph.
>
> `audience-vocabulary` means a textbook-statistics or plain-English expression the intended metrology/CS professor uses without definition; **that class here is exactly:** repeatability, repetition, random scatter, complete, completeness, sampler cadence, refused, refuses, missing, malformed, corpus range, degrees of freedom, threshold, exact equality, null hypothesis, tail area, quarantine, append-only, run bundle, full-history checkout, third-party dependencies, cumulative counter, linear programme, infeasible, argmin, and detected.

Neither `binary64` nor `resolution bound` appears in that closed list. **Both rows' prior
`audience-vocabulary` status was therefore invalid against the ledger's own exhaustive
enumeration, and the change to `glossed-at-first-use` cures a real contradiction.** That is the
correct direction of travel, and I confirm it independently of record 31.

Row 141 (new): `| binary64 / member-envelope integral sum | Record support in two historical model
stacks | glossed-at-first-use | Binary64 is glossed at its first main-text use as the usual 64-bit
floating-point format; the member-envelope integral sum is built in Appendix A.3.10 before its only
use there. |`

Prose it must match (draft 740): "The event-duration statistic subtracts binary64 (the usual 64-bit
floating-point format) epoch values before rounding". The first named use supplies a plain-word
definition in the same sentence → `glossed-at-first-use` is exactly right for `binary64`.

Row 149 (new): `| resolution bound | Adding publication safeguards after the ratio |
glossed-at-first-use | Registered operational resolution guard for assigned-energy differences in
one cell; its first use in the protocol supplies that definition. |`

Prose it must match — `resolution bound` does **not** occur in `draft-v2-skeleton.md` at all; its
first and defining occurrence in the reading order is `docs/paper/protocol/prospective-comparison-protocol.md:241`:

> The ratio is calculated before the safeguards used to publish the final resolution bound, **the registered operational guard for assigned-energy differences in this cell.**

Appositive definition in the same sentence → `glossed-at-first-use` is exactly right, and the home
cell "Adding publication safeguards after the ratio" is the `###` heading at protocol line 238 that
contains line 241. The disposition's wording ("operational **resolution** guard") inserts one word
the prose does not have; harmless, not a finding.

### Item 3 — quoted

README line 12 now ends:

> **Next:** harvest the night on 2026-09-13 and apply the pre-registered equivalence rule.

Reads correctly. The definite reference "the night" resolves to the antecedent that opens the same
line ("the first epoch-equivalence measurement night is armed for 02:56 PDT on 2026-09-13"), so the
sentence stands alone. The removed clause ("merge the paper pass under the twelve-row gate, then")
was indeed stale at `76a2f2a7`, which is the merge of PR #331. Two observations, neither a finding:
the date now appears twice in the line (harmless), and the line no longer names any next step for
the paper itself — defensible, since this follow-up is a two-line prose cure rather than a
programme.

### Item 6 — mechanical numeral census

`python3 -B`, numeral tokens `\d+(\.\d+)?([eE][-+]?\d+)?`, `76a2f2a7` → `ff3b59b9`, per file:

```
README.md                                      ADDED {}          REMOVED {}
docs/paper/draft-v2-skeleton.md                ADDED {'64': 1}   REMOVED {}
docs/paper/protocol/first-use-audit-ledger.md  ADDED {'3.10': 1} REMOVED {'3': 1}
```

**No measured value, registry-bound quantity, or reported numeral changed.** The `64` is the new
gloss. The `A.3` → `A.3.10` is a section locator, and I verified A.3.10 is the correct section:
`#### A.3.10 Shared-sign rounding and illustration` at draft line 1366 is where the member-envelope
integral sum is defined. One precision note the record should carry: the README's deleted clause
contained the number **word** "twelve-row", which a numeral-token census cannot see; I confirmed by
reading the deleted text that it was a gate-count reference, not a quantity of record.

## Findings

**Blocker: none.** The three edits are correct, minimal, and land where record 31 said they should.

### S1 (should-fix) — ledger row 141's disposition misstates the draft on two counts

Site: `docs/paper/protocol/first-use-audit-ledger.md:141`.

The cell claims the member-envelope integral sum "is built in Appendix A.3.10 **before its only use**
there." Primary text:

- **1370–1377 (the build):** "The **member-envelope integral sum** is \(\sum_{m\in\{A_1,B_1,B_2,A_2\}}|c_m|\int…\) … This nonnegative joule sum supplies a scale large enough to cover all four member integrals before their signed contrast is formed."
- **1378 (use 1):** "It sets \(M=\max(1,|\delta_j|,|z_j|,…,\text{member-envelope integral sum})\)"
- **1399 (use 2):** "This member-envelope integral sum exceeds the other scale candidates, so M₂=102.95961680584864 J."
- (1383 carries the variant "member-envelope integral contributions".)

So (i) **"its only use" is false** — the term is used at least twice after the build; and (ii) **"built …
before its use" names the header's `built-before` class while the row's Status cell says
`glossed-at-first-use`.** The row is in fact `glossed-at-first-use` on the strictest reading — the
first *named* use at 1370 is the sentence that defines it by formula, which is "an equivalent
calculation in the same sentence." The disposition should say that, not borrow the other class's verb.

This matters because the ledger is the acceptance instrument: a cell that describes the wrong
mechanism is the defect class this series has now hit repeatedly (see same-signature below).

**Minimal cure (one cell, no draft change):** replace the second clause with — "the member-envelope
integral sum's first named use is the Appendix A.3.10 sentence that defines it by formula, before it
is used as a scale candidate in M."

### S2 (should-fix) — F1's "split its grouped row" cure was not applied, leaving the home column wrong for the second term

Record 31 F1's minimal cure was four parts: *(a)* gloss binary64 at 740, *(b)* **split its grouped
ledger row**, *(c)* classify resolution bound at its protocol definition, *(d)* **enforce
audience-category membership in the audit test**. Parts (a) and (c) landed. Part (b) did not: row 141
still groups two terms whose first homes differ. `binary64` first occurs at draft 740, inside
`### Record support in two historical model stacks` (heading at line 617) — which is the row's home
cell. `member-envelope integral sum` first occurs at draft 1370, inside `#### A.3.10 Shared-sign
rounding and illustration`. **The "First reader-facing home" column is therefore silently wrong for
the row's second term.**

The audit test does not catch this: `test_first_occurrence_is_in_exact_home_section`
(`tests/test_paper_first_use_ledger.py:541`) takes `_first_occurrence(_alternatives(row.term), …)`,
i.e. the *earliest* occurrence of *any* alternative in the grouped term string — which is
`binary64` at 740 — and that matches the declared home, so the test passes while the second term
goes unchecked. Grouping two terms is exactly how a row escapes its own home assertion.

**Minimal cure:** split row 141 into `| binary64 | Record support in two historical model stacks |
glossed-at-first-use | The usual 64-bit floating-point format; Appendix A.3 restates it as IEEE-754
double precision. |` and `| member-envelope integral sum | A.3.10 Shared-sign rounding and
illustration | glossed-at-first-use | <S1's wording> |`, and bump the mechanical count sentence at
ledger line 296 from "Terms inventoried: 262" to 263. (I verified 262 data rows at this head, so the
count sentence is currently correct and the split must move it.)

### S3 (should-fix) — the audience-vocabulary enforcement was not installed, and two rows still violate the header's closed class

Part (d) of F1's cure did not land. `tests/test_paper_first_use_ledger.py:26–34` validates only that
a row's status is one of five *names*:

```python
STATUSES = frozenset({"built-before", "glossed-at-first-use", "audience-vocabulary",
                      "forward-pointer-next-paragraph", "FAILS"})
```

Nothing checks membership in the header's exhaustive `audience-vocabulary` class. Consequence,
verified at this head: of the 17 surviving `audience-vocabulary` rows, **two are not in the header's
closed list**:

- line 163 `| measurement interval | Benchmark and metrology lineage | audience-vocabulary | Analyzer reporting duration in the benchmark methodology; distinct from the statistical measurement interval defined in protocol P.3. |`
- line 166 `| deterministic bound | Adding publication safeguards after the ratio | audience-vocabulary | A non-random maximum displacement; the first use denies such a guarantee for unobserved between-reference excursions. … |`

Both were already `audience-vocabulary` at the base `76a2f2a7` and the header's list is unchanged by
this diff, so this is **pre-existing, not introduced here** — but it is the identical defect the
follow-up just cured twice, so the fix is 2-of-4 complete. Worse, the test's `senses` dict at
lines 522–536 *pins* both rows' home and meaning, so the suite actively blesses them. Note also that
each disposition cell above already reads as a plain-word definition at first use, which is the class
they should carry.

**Minimal cure (pick one, both are one commit):** reclassify rows 163 and 166 to
`glossed-at-first-use` (their disposition text already supports it), **and** add to the ledger test —

```python
AUDIENCE_CLASS = frozenset({...the header's 26 listed expressions...})
# in the invariants test:
for row in self.rows:
    if row.status == "audience-vocabulary":
        self.assertTrue(set(_alternatives(row.term)) & AUDIENCE_CLASS,
                        f"audience-vocabulary outside the header's closed class: {row.term}")
```

Without the assertion this recurs the next time a reviewer wants a row to stop failing.

### N1 (nit) — the edited sentence's own term of art is un-inventoried

Draft 740: "**The event-duration statistic** subtracts binary64 (the usual 64-bit floating-point
format) epoch values before rounding". `event-duration statistic` occurs **once in all of
`docs/paper/`** — this line — and has **no ledger row**. The sentence says what the statistic *does*
arithmetically but never says what it *is* (the duration between the two event-log stamps of a
phase). A charitable read is that it is compositional plain English rather than a term of art, which
is why I grade it a nit and not a should-fix; against the ledger's claim of "Terms inventoried: 262;
FAILS: 0" it is nevertheless a small completeness gap in the audit instrument, in the same sentence
the round just edited. **Minimal cure:** either rename to "the event-log duration" at 740, or add a
row `| event-duration statistic | Record support in two historical model stacks |
glossed-at-first-use | The duration between a phase's two event-log stamps, subtracted as binary64
epoch values. |` and gloss it inline. The inserted parenthetical itself introduces nothing needing
definition, so **item 5 passes for the edit**.

### N2 (nit) — record 33's numeral attestation is scoped to the draft, not the diff

Record 33 reports `added_tokens {"64": 1}`, `removed_tokens {}`, with the qualification "The sole
draft-line replacement adds …". The ledger's `Appendix A.3` → `Appendix A.3.10` is also a numeral
token change and is unreported. It is correct (verified against the A.3.10 heading at line 1366) and
is a locator rather than a quantity, so the refuter's substantive claim holds — but a numerals block
that says `existing_numerals_changed: false` should be run over every file in the pathspec, not one
line. No cure needed to the code; worth one sentence in the next refuter brief.

### N3 (nit, no action) — verification narrowed between the two heads

Record 31 ran 10 test modules / 244 tests plus `gen_state.py --check` on the base; record 33 ran 5
modules / 79 tests on the fix head, dropping `test_check_paper_replay_fence`,
`test_paper_round7_artifacts`, `test_gen_state`, `test_paper_successor_migration`, and
`test_build_site_parsers` while the diff edits `README.md`. I checked the one exposure that worried
me — `scripts/gen_state.py` contains no reference to `README` (grep: no hits) — and
`tests.test_docs_freshness` did run and pass on the fix head. **I therefore do not call for a
re-run.** Recording it so the gate row shows the narrowing was considered, not missed.

## Same-signature statement vs records 16 / 21 / 28 / 31

Two signature families run through this series:

- **(a) a prose edit leaving live uses of a term whose build it moved or removed** — record 16 §5 class 1 (NB-1, NB-2, "resolution bound" orphaned at 866), record 21 §5 (NB2-1), record 28: not reproduced.
- **(b) the acceptance instrument certifying more than the text supports or more than its consumer verifies** — record 21 §5 ("the ledger row that declared it … was not re-read against the text"; row 95 asserting `glossed-at-first-use` at an unbuilt first use), record 28 SF-28-1 ("an artifact asserting more verification than it performed"), record 31 F1 ("an audit disposition certifying more than its consumer verifies").

**Family (a): not reproduced.** The gloss at 740 is the *cure* for a family-(a) defect (the padding
paragraph's move to A.3.10 orphaned the term), and it creates no new orphan: `binary64` is glossed at
740 and re-glossed identically at 1369, `resolution bound` still resolves at protocol 241, and the
numeral census shows no build text was moved or deleted.

**Family (b): reproduced, at reduced severity.** S1 is a ledger cell that describes the wrong
mechanism (asserting `built-before` language under a `glossed-at-first-use` status, and asserting
"its only use" where the draft has two). S2 and S3 are the same family seen from the other side — the
row that escapes its own home assertion by grouping, and the class assertion with no consumer. This
is the **second consecutive round** in which family (b) fires, and the **second time in the same
instrument** (row 95 in round 2, row 141 now). **On its face the standing escalation trigger is met.**

But the diagnosis is unusually clean, so I do not recommend a consult: the recurrence is fully
explained by the two dropped parts of record 31's own four-part cure. F1 named the structural fix
(*split the grouped row*, *enforce audience-category membership in the audit test*), the round applied
only the two prose parts, and the two mechanisms that would have blocked S1/S2/S3 are exactly the two
that were not installed. This is the **"ruled-not-installed"** pattern, not a new blind spot: the next
spend is installing the enforcement (S3's assertion + S2's split), which is mechanical and testable,
not a third prose round and not another review lens. If a *fourth* family-(b) instance appears after
the assertion is in the test, that is a genuine structural problem and the escalation should fire then.

## Recommendation

**ADVANCE `ff3b59b9` as correct and minimal — all six checks pass on substance and no numeral of
record changed — and land S1 (one ledger cell), S2 (split row 141, count 262→263) and S3 (reclassify
ledger rows 163/166 plus the audience-class assertion in `tests/test_paper_first_use_ledger.py`) as a
single consolidated commit that completes record 31's F1 cure, rather than opening another prose round.**

— Opus 5 (1M context), counter-review seat, gate rows 6 and 10; head `d0884550`, code-final `ff3b59b9`, base `76a2f2a7`.
