# 159 — READ-ONLY REVIEW of the issue-316 recording (fidelity + pedagogy)

Seat: independent, non-author. Checkout `/Users/edr/code/JouleWise-wt-eq-ruling`,
branch `feat/2026-09-10-equivalence-ruling-316`. Target reviewed:
`git diff bc1d7ef9 12162263 -- configs/calibration/preregistration_d079_epoch_25g83_rev1.md
docs/decision_log.md docs/phase_2/derivation_night_runbook.md`. Authority read in
full this session: `gh issue view 316 --repo mpmdw/JouleWise`. No file was
modified; no git write command was run; this report is the only file written.

**Verdict: no blockers. Three should-fix items, six nits.** Every quoted clause
of issue 316 that the three files present as a quotation is verbatim (checked
mechanically, see below); no paraphrase drops, adds or loosens a condition; the
recording amends no process rule; revision 1 of the pre-registration is
byte-identical; every constant in every constants table is confirmed against the
artifact and the validator.

---

## 0. Mechanical checks, with output

**Scope (rule 11).** `git diff --name-status bc1d7ef9 12162263` = exactly the
three files in scope. `git diff --numstat`: prereg `226 0`, decision log `92 0` —
**zero deletions in both**, so nothing outside the appended sections changed.
The decision-log insertion is ONE hunk (`@@ -6697,6 +6697,98 @@`) at the END of
the D-102 section, immediately before `## D-103` (verified: `docs/decision_log.md:6700`
heading, `:6792` `## D-103`). The D-103 cold-gate text and every other decision's
text are untouched.

**Revision 1 byte-identity.** Compared `git show bc1d7ef9:…prereg…` against the
working file byte-for-byte:

```
old len 21630 new len 34845
new startswith old: True
```

The appended bytes begin `\n---\n\n# Revision 2 (2026-09-10, Ed's ruling by
directive issue 316)\n`. Not one byte of revision 1 moved.

**`preregistration_epoch_pins`.** Its signature is `(text: str) -> tuple[str, str]`
(`scripts/issue_calibration_acceptance_generation.py:814` region) — it takes the
file's TEXT, not a Path. Output over the revised file:

```
('25G83', 'b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5')
```

Exactly one `os_build` and exactly one sampler sha256 still parse. Revision 2
never writes the lexeme `os_build:` with a value, which is what keeps the set
single-valued (the function `set(...)`s its matches and raises on ambiguity).

**Tests.**

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness tests.test_d078_reason_registry
Ran 44 tests in 0.813s

OK
```

**Constants — every number confirmed against BOTH sources.**

| Quantity | Recorded | `_D102_N17_DERIVATION["operatives"]` | `calibration_acceptance_d079_v2_n17_r6.json` | verdict |
|---|---|---|---|---|
| Operative level screen | `0.032898493715362` | `preflight_level_screen_s = "0.032898493715362"` | `ratified_operatives.preflight_level_screen_s` = same; `rounding.preflight_level_screen` `quantum_s 0.000000000000001`, `numeric_role operative_comparator` | ✅ |
| Operative bracket screen | `0.009724` | `bracket_screen_s = "0.009724"` | `ratified_operatives.bracket_screen_s` = same; `rounding.operative_bracket_screen` `quantum_s 0.000001`, `numeric_role operative_comparator` | ✅ |
| Budget ceiling | `0.010164834757777545` | `maximum_budgetable_drift_s` = same | `ratified_operatives.maximum_budgetable_drift_s` = same; `source_statistics.prediction_99_two_draw_s` = same lexeme | ✅ |
| Max budgetable excess | `0.000440834757777545` | `max_budgetable_excess_s` = same | `ratified_operatives.max_budgetable_excess_s` = same | ✅ |
| Raw corpus maximum | `0.03289849371536248` | — | `source_statistics.maximum_s` | ✅ |
| Raw corpus range | `0.00972358928879385` | — | `source_statistics.range_s` (= `maximum_s − minimum_s 0.02317490442656863`) | ✅ |
| n | `17` | `corpus_n = 17` | `derivation_corpus.n = 17` | ✅ |

**"No floor in force here" — TRUE.** `_D102_N17_DERIVATION["screen_rule"]` is
`range_equals_screen`. In `joulewise/calibration_bracketing.py:1066-1070`,
`range_equals_screen` checks `quantized_range == screen` with no floor term,
while `floored_range_envelope_screen` is the branch that applies
`D125_SCREEN_FLOOR_S = Decimal("0.010818")` (`:240`). Revision 1 of the
pre-registration (lines 233–239 of the sealed text) registers the floored rule
for the SUCCESSOR corpus and says in its own words that the six issued
generations register the other name. The recording's claim is exact, and its
scoping ("for this comparison") is what keeps it true — the `0.010818` value
also lives in D-102 clause 3 as the never-zero drift ALLOWANCE, which is
untouched and irrelevant to this comparison. Correctly not conflated anywhere.

**Quotation verbatim check, run mechanically.** Whitespace-normalised
containment of every blockquote block in revision 2 against the issue body:

```
--- block 1..9  VERBATIM=True   (all nine)
```

The same check over the decision-log addendum's and runbook §2.5's inline
quoted strings: all substantive quotes verbatim, with two cosmetic exceptions
recorded as nits N-2 and N-3 below.

---

## 1. Fidelity table (issue clause → where recorded → verbatim?)

| Issue 316 clause | Recorded at | Verbatim? |
|---|---|---|
| Provenance line (Gmail id, filed-on-behalf, "The ruling is Ed's; the wording is Fable's") | prereg `:307-312` (blockquote); declog `:6702-6710` (inline) | y (prereg); y word-for-word in declog, inner `"…"` rendered `'…'` (nit N-3) |
| Decision 1: NO as default path, incl. "is acting for an adversary that doesn't exist" | prereg `:321-328`; declog `:6715-6721`; runbook §0.5 `:529-538`, §6 item 7 `:2046-2049` | y (prereg blockquote + declog inline quote); runbook paraphrase, condition-preserving |
| Clause 1 — one derivation-kind session, 12 slots, merged chain as built, arm/chain/settle/census/dead-man unchanged, handback unchanged, rehearsal untouched | prereg `:360-366` (blockquote) | y |
| Clause 2 lead — "After the night closes, the magistrate READS … applies this rule, written now" | prereg `:425-426` | y |
| Reference envelope (r6 id, corpus max, corpus range, n=17, budget ceiling as the validator computes it) | prereg constants table `:388-396` + declog `:6731-6745` + runbook §2.5 constants table | Paraphrase into a two-column (operative / raw) table. Both the issue's raw numbers and the operatives are printed; no condition dropped. See I-1 for the one interpretive extension. |
| "…if the validator's operative screen differs from the raw range (the never-zero floor), the operative value is the one used" | prereg `:379-382`; declog `:6740-6742`; runbook §2.5 inputs | y in all three |
| Retained m definition | prereg `:428-429`; declog `:6746-6747`; runbook §2.5 | y |
| `m < 6` → INCONCLUSIVE, "run one more equivalence night before deciding. No other action." | prereg `:430-431`; declog `:6747-6749`; runbook §2.5 rule + outcome table | y |
| PASS (two inequalities, level screen AND range ≤ operative bracket screen) | prereg `:432-434`; declog `:6750-6752`; runbook §2.5 | y |
| FAIL = "anything else." | prereg `:435`; declog `:6752`; runbook §2.5 | y |
| Clause 3 — continuation on PASS, dated D-102 addendum, cites session id + twelve slot outcomes + m values, pre-registration stays on file, code change through the normal PR gate, never worked around by hand | prereg `:445-462` (full blockquote) + four numbered consequences; declog `:6754-6770`; runbook §2.5 PASS row + §6 item 12 | y (prereg blockquote); declog quote of the PR-gate phrase drops one word — nit N-2 |
| Clause 4 — FAIL route, V3 AFFIRMED (three nights, 12 slots, n ≥ 19 or exactly 17 with a written ruling), night one COUNTS, blindness clarification, "does not run a fourth night to satisfy the guard" | prereg `:474-482` (full blockquote); declog `:6771-6778`; runbook §2.5 FAIL row, §0.5, §6 items 7 and 11, Terms `Blind` | y |
| Blindness clarification ("every rule fixed before data", not "no one may look") | prereg `:484-496`; declog `:6779-6782`; runbook Terms `Blind` `:160-172`, §2.3 | y |
| Clause 5 — record as prereg revision 2 + dated D-102 addendum; not a magistrate amendment (rule 11 intact) | prereg STATUS line `:290-291`; declog `:6708-6712` | Faithful paraphrase; the STATUS line reads "Ed's ruling by directive issue 316; recorded by the magistrate; not a magistrate amendment (rule 11)" |
| Decisions 2, 3 and 4 unchanged; veto windows stand as the email wrote them | prereg `:500-501`; declog `:6784-6786` | y |
| Timing (earliest 2026-09-12, subject to PR #316 landing / handback rewrite / standing gates; objective = real G2-a on the first quiet slot after a PASS) | prereg `:503-506` (verbatim blockquote); declog `:6786-6789` | y in prereg; declog substitutes "the recording landing" for "PR #316 landing" — same condition, volatile literal avoided; acceptable |
| "While reading this" (side threads DOCS-THIN-01 / CI-TRIM-01, do not adopt/rebase/delete) | not recorded in any of the three files | Correct — it is session guidance to the magistrate, not a registration or decision rule |

---

## 2. Findings

### Blockers

None.

### Should-fix

**S-1 — misattributed quotation inside the pre-registration.**
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:493-496`:

> Revision 1's own reason for blindness — "so that nothing can be chosen after
> seeing values" — is satisfied by fixing the rule, which is what this section
> does.

That quoted string does **not** appear in revision 1. Whitespace-normalised
search of the sealed revision-1 bytes: `ABSENT`. It is the RUNBOOK's wording
(`docs/phase_2/derivation_night_runbook.md` §2.3, present since revision 5:
"…so that nothing can be chosen after seeing values"). Revision 1's actual
sentence is:

> every rule that could otherwise be chosen after seeing values is fixed here
> first.

The meaning is identical, so nothing shifts — but this is a pre-registration,
the one document whose citations a reader is expected to check against sealed
bytes months later, and the quotation marks assert a byte-level claim that
fails. Fix: quote revision 1's real sentence, or drop the quotation marks and
attribute the phrasing to the runbook.

**S-2 — "the m values" is an unglossed term doing load-bearing work in the one
action table the operator executes from.**
`docs/phase_2/derivation_night_runbook.md:1689` (§2.5 PASS row), and the same
phrase at prereg `:449` and `docs/decision_log.md:6759`:

> The addendum cites this night's session id, the twelve slot outcomes and the
> m values verbatim, and moves no threshold.

In the prereg and the decision log the phrase sits inside a blockquote of the
issue, where verbatim is correct. In §2.5 it is presented unquoted as an
INSTRUCTION, and the operator cannot replicate it: "the m values" could mean
`m` itself, the m retained `b_fiducial_s` values, or both. The issue's own
phrase is ambiguous; the runbook is the place that must resolve it, and per the
writing standard the resolution belongs at first use. Fix: in §2.5's PASS row,
write what the addendum must carry (e.g. "the retained count `m` and each of
the m retained values, each with its slot and attempt id") and footnote that the
issue's phrase was "the m values".

**S-3 — the decision-log addendum names the part of D-102 clause 2 it
PRESERVES, but never names the part the ruling DISPLACES.**
`docs/decision_log.md:6766-6770`:

> Clause 2's rule that a trigger observation is judged under the PRIOR artifact
> and never incorporated into a threshold that judges itself is preserved
> exactly: the equivalence night's values are compared against r6 and enter no
> statistic.

True, and the right thing to say. But the same clause 2 also reads (decision log,
D-102 clause 2): "**Mandatory prospective re-derivation triggers: any
identity-field change**…". The continuation route Ed authorizes is precisely a
carve-out from that sentence — an identity-field change that, on a same-envelope
night, does NOT force re-derivation. Ed's authority for it is explicit in the
issue, so this is not a fidelity defect against the ruling; it is a
completeness defect in the record. A reader of D-102 who reaches only clause 2
still reads an unqualified mandatory trigger. Fix: add one sentence stating that
on the PASS route the continuation addendum qualifies clause 2's
identity-field re-derivation trigger, by Ed's authorization in issue 316, and
leaves the other listed triggers untouched.

### Nits

**N-1** — `docs/phase_2/derivation_night_runbook.md:2009` (§5 failure table) still
reads "Expected after nights 1 and 2." for `check --session-ids …` rc 5, while
the rc-0 row one line above was scoped to the FAIL route. On the PASS route
there are no nights 1 and 2. Scope it the same way.

**N-2** — `docs/decision_log.md:6764` quotes "lands through the normal PR gate as
the smallest possible change"; the issue reads "lands **it** through…". A
one-word grammatical splice inside quotation marks.

**N-3** — `docs/decision_log.md:6702-6710` renders the issue's inner `"…"` as
`'…'` inside its own quotation. Conventional and harmless; recorded for
completeness since the brief asks for verbatim.

**N-4** — `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:361` and
`:504` carry `PR #315` and `PR #316`. Both are inside verbatim blockquotes of
the issue, so removing them would break the quote, and `tests/test_docs_freshness.py`
does not scan `configs/` (its `_current_sections()` covers README, PROJECT_STATUS
and two regions of `docs/orchestration.md`) — the suite passes. Still, `PR #316`
is a self-reference that stops resolving once the file is read as an archived
registration. Suggest a bracketed editorial gloss immediately after the quote
naming the landed commit. No volatile literal (`PR #`, test count, model name)
appears in any UNQUOTED added text in any of the three files; the runbook's
pre-existing `claude`/`codex` hits are census-substring code blocks, untouched.

**N-5** — the pre-registration's constants table (`:388-396`) lists the budget
ceiling and the maximum budgetable excess without the runbook's clarifier
("Carried for the record: the check itself compares against the two screens
only"). §"The rule" resolves it two paragraphs later, but a reader consulting
the table alone could take the ceiling for a third comparator. Copy the
runbook's one-clause note into the prereg table.

**N-6** — `docs/decision_log.md:6790-6791`: two consecutive blank lines before
`## D-103`.

### Informational (no action)

**I-0** — At the reviewed commit, §2.5 `:1700` carries `[UNVERIFIED: at this
revision no committed tool extracts the retained values…]`. That is correct AS
OF 12162263 (`git ls-tree 12162263 scripts/` contains no
`epoch_equivalence_check.py`). Two later commits on this branch (`631cd207`,
`08ccdb4a`) replace that note with the committed tool's invocation, exit codes
(0 PASS / 4 FAIL / 5 INCONCLUSIVE / 3 refusal) and the two-checkout comparison.
Nothing to fix in the reviewed commit; noted so the lead does not re-raise it.

---

## 3. Interpretive extensions the recording makes — all disclosed, all judged sound

**I-1 — the operative-preference rule applied to the LEVEL screen, not only the
range.** Issue 316's resolving sentence is literally scoped to the range: "if the
validator's operative screen differs from **the raw range**…, the operative value
is the one used." Its PASS clause says "the r6 level screen" unqualified but
"the r6 **operative** bracket screen" for the other. The recording uses the
operative value for BOTH. Supporting authority in the same issue: "The magistrate
confirms **these operative constants** from the artifact and the validator's own
code path" — plural, covering the level screen. Effect, bench-confirmed this
session: the operative level screen is SMALLER than the raw maximum by
`4.8e-16 s`, i.e. marginally STRICTER, at a margin fifteen decimal places below
anything the instrument resolves. All three files state the direction and the
magnitude explicitly (prereg fact 2 `:404-410`, runbook §2.5 fact 2). Sound, and
disclosed rather than silent. No action.

**I-2 — ordering `m < 6` before PASS/FAIL.** Read literally, "FAIL = anything
else" would swallow the `m < 6` case, since a five-value night that fails the
range test is "anything else". The only coherent reading is INCONCLUSIVE first,
and §2.5 states it as an instruction — "Evaluate the `m < 6` branch FIRST" — with
the reason (a one-value night has range zero and would pass on the level screen
alone). The prereg carries the same ordering. Correct interpretive work; it is
also the reading that protects the campaign, not the one that eases it.

**I-3 — "anchor-v3 replay resolved" operationalised.** §2.5 defines it as: the
capture's stored `clock_anchor` record was written by the anchor-v3 estimator and
is not `affine_clock_fit_empty`. Verified against
`joulewise/calibration_bracketing.py:263` —
`REGISTERED_CORPUS_EXCLUSION_REASONS = frozenset({"affine_clock_fit_empty"})` —
and `joulewise/uncertainty_evidence.py:1100`, where that is the only unresolved
class the estimator emits. Correct.

**I-4 — an added safeguard.** §2.5 requires reading the value from BOTH the
ledger row's `exact_bound_lexeme_s` and the capture's authenticated
`instrument_evidence.json`, and refusing the night's numbers if they differ.
Not in the issue; it can only make the check stricter, never admit a night the
issue would refuse. Fine.

**I-5 — beyond-the-brief runbook repairs.** Three edits sit outside a literal
transcription but are forced by the ruling and are inside the one file:
§0.5's V3 precondition (`:529-538`, which as written would have FORBIDDEN arming
the equivalence night), §3's and §4's FAIL-route gating leads, and §5's rc-0 row.
Each is necessary for internal consistency; N-1 is the one such repair that was
missed.

---

## 4. Pedagogy — first-use table for the terms revision 6 and revision 2 introduce

Test applied as the brief specifies: a reader who starts at §2.5 the morning
after the night, not at §0.

| Term | First use in §2.5 / revision 2 | Built, glossed at first use, or neither? | Verdict |
|---|---|---|---|
| epoch-equivalence check | runbook §2.5 title `:1593`; prereg `:334-339` | Prereg BUILDS it in one sentence before any use. §2.5 gives its QUESTION and its negations ("builds no corpus, computes no successor statistic, issues nothing") but never the one-sentence "what it is"; the definition lives in §"What night one is for" and in §8. | Nit (N-7, below) |
| reference envelope | runbook §2.5 third input; prereg `:341-344` | Built at first use in both, then tabulated with sources before the rule uses it. | ✅ |
| retained value | runbook §2.5 first input; prereg `:346-350` | Built at first use, with the exclusion cases named (`ordinary-invalid`, `slot_refused`, `window_exhausted`) and the field coordinates given. | ✅ |
| retained m | runbook §2.5 second input | Built ("how many retained values this night produced") immediately after `retained value`, then the issue's own words quoted. | ✅ |
| "the m values" | §2.5 PASS row `:1689` | Neither built nor glossed, and it is an instruction. | **S-2** |
| continuation / "epoch continuation on evidence" | §2.5 PASS row; prereg `:351-355` | Glossed AT first use in both ("an identity-field change followed by a same-envelope night CONTINUES the acceptance in force rather than voiding it"), plus the licensing consequence. | ✅ |
| operative constant | §2.5 constants preamble; prereg `:375-382` | Built at first use: "the raw statistic rounded to the fixed decimal place the artifact registers for it", with both forms printed side by side. | ✅ |
| judged | runbook §"What night one is for" `:94`; §8 row `acceptance` | Glossed by construction ("judged against thresholds that live in one JSON artifact called the **acceptance**"). Does no unexplained work. | ✅ |
| acknowledged / affirmative written acknowledgment | runbook §0.5 `:529-532`; §6 item 7; prereg `:484-487` | Glossed in place: V3 is named (night count, slots, retained-corpus minimum) and the acknowledgment requirement is stated and then discharged. | ✅ |
| blind / blindness fence | Terms `:160-172`, `:201-210`; §2.3 `:1484-1515` | Both REBUILT, and the near-name collision is called out explicitly ("a different object under a confusingly similar name"). §2.3's rewrite from a blanket prohibition into three time-ordered rules is the strongest pedagogy in the diff. | ✅ |
| INCONCLUSIVE / PASS / FAIL | §2.5 rule + outcome table | Defined by the quoted rule, then each given exactly one next action. | ✅ |

**N-7 (nit)** — add one sentence at the head of §2.5 saying what the check IS,
not only what it asks and what it is not, e.g. "The check compares this night's
retained values against the thresholds the acceptance in force already carries,
under the rule below, and returns exactly one of three outcomes." A reader
entering at §2.5 currently has to infer the definition from the inputs.

### Replication test: can an operator execute the desk decision from §2.5 alone?

**Yes, with one cross-reference.** §2.5 supplies: (a) the three inputs, each with
its field coordinates — ledger disposition `valid`, `clock_anchor` not
`affine_clock_fit_empty`, value read from `exact_bound_lexeme_s` and
cross-checked against `instrument_evidence.json`; (b) the constants, with both
forms and both sources, and the three facts that change what a comparison means;
(c) the ordering, stated as an instruction ("Evaluate the `m < 6` branch FIRST");
(d) the two inequalities written out against the literal numbers ("every retained
value ≤ `0.032898493715362` s, and (largest − smallest) ≤ `0.009724` s"); and (e)
a three-row table giving the one exact next action per outcome, each closed
against improvisation ("No top-up of this night, no partial decision, no other
action"; "§3 and §4 do not run"; "never run a fourth night to satisfy the
guard"). The single cross-reference is §2.1 for WHERE the ledger rows and
bundles live; §2.5 names the files but not their paths. That is acceptable —
§2.1 is in the same harvest section the operator has just executed — and §2.1's
new row explicitly forward-points to §2.5.

Two open items are RECORDED rather than decided, both bracketed in §2.5: no
committed tool at this revision (superseded on the branch, see I-0), and the
unanswered INCONCLUSIVE-then-FAIL night count, which §2.5 correctly routes to Ed
rather than to the desk. Recording an open question in the operating text,
where the operator meets it, is the right disposal.

### Unpaid words

I found none in the added text beyond S-2. Every term the brief named is built
or glossed at its first use; `converge`-class vocabulary ("admissible",
"terminal", "retained", "screen", "fence") is either pre-existing with a §8 row
or rebuilt in this diff. The three §8 rows whose meaning MOVED (`blind`,
`blindness fence`, `screen`) were repaired rather than left stale — that is the
failure mode this standard exists to catch, and the author caught it.

---

## 5. Summary for the lead

Fidelity: clean. Nine blockquotes verbatim, every inline quote verbatim but for
one dropped word and one quote-style conversion, no condition added, dropped or
shifted, rule 11 intact (zero deletions, one appended hunk per file, revision 1
byte-identical, no cold-gate text touched), every constant confirmed against
both the validator and the artifact, `preregistration_epoch_pins` still
single-valued, 44 tests OK.

Pedagogy: strong. §2.5 is replicable from itself. The one real defect is S-2
("the m values" as an unglossed instruction); S-1 is a citation that does not
resolve; S-3 is a missing sentence about which half of D-102 clause 2 the ruling
displaces. None of the three blocks landing; all three are cheap.
