# Record 37 — gate row 10 fresh-eyes on the record-36 cure commit

- Reviewer: Opus 5 (1M context), read-only seat.
- Target: single commit `4cb214ad` ("Paper-N follow-up (fresh-eyes 36 F1) …").
- Worktree: `/Users/edr/code/JouleWise-wt-paper-n`, branch `fix/2026-09-12-paper-n-binary64-gloss`,
  HEAD `4cb214ada271141ccc9b5c107af4a6fb4cac6684` (verified this session with `git rev-parse HEAD`).
- Session date: 2026-09-12 PDT. Python 3.14.7 (`main`, Aug 5 2026, Clang 21.0.0).
- Write scope honoured: this file only. `git status --porcelain --untracked-files=no` is empty at the
  end of the seat. Every probe wrote to the session scratchpad
  (`/private/tmp/claude-501/.../scratchpad`), never into `docs/` or `tests/`. `python3 -B` throughout;
  the full suite was not run.

## 0. Contamination disclosure

Heavier than record 36's. Two separate channels:

1. **The launch brief told me the hypothesis before I opened anything** — that record 36 found the
   guard vacuous, that it prescribed `assertNotIn("(", header_match.group(1), ...)` before `listed`
   is built, and that the commit did exactly that plus a disposition reword.
2. **`git show 4cb214ad` put the entire body of record 36 in front of me** (the record is itself one
   of the three files the commit adds, all 249 lines). So I read F1's argument, its own probe output,
   its N-a/N-b/N-c residue list, and its same-signature section *before* forming any verdict. I am
   not a blind reviewer of the prior round in any sense.

What is nevertheless independent: the verification mechanism. Record 36 probed by applying guard
logic to header *strings* held in a script. I probed **end-to-end through the real test method**,
using the module's `PAPER_FIRST_USE_DRAFT` override with a composed audit text (see §1), and I ran
three mutants record 36 did not: a gloss whose parenthetical contains a comma, a gloss written with
no parentheses at all, and a LaTeX-bearing term as a false-positive probe. Findings F1 and N-a below
come from those, not from re-reading record 36's list. I also verified the reworded ledger
disposition against the draft prose myself, which record 36 could not have done (it predates the
reword).

## 1. The counterfactual — how it was run

The brief asked whether the module exposes a path override. It does, partially, and the partial
override turns out to be enough.

`tests/test_paper_first_use_ledger.py:11-23` fixes the ledger path as a module constant with **no**
environment hook:

```python
REPO = Path(__file__).resolve().parents[1]
DRAFT = Path(os.environ.get("PAPER_FIRST_USE_DRAFT", DEFAULT_DRAFT))
...
LEDGER = REPO / "docs/paper/protocol/first-use-audit-ledger.md"
```

So `PAPER_FIRST_USE_DRAFT` alone cannot redirect the ledger. The lever is `_audit_text`
(`:439-447`):

```python
if LEDGER_HEADING in text:
    return text
return text + "\n" + PROTOCOL.read_text(...) + "\n" + LEDGER.read_text(...)
```

If the overridden draft **already contains** `## First-use audit ledger`, the loader returns it
verbatim and never reads the repo's protocol or ledger at all. That gives a clean, zero-write
counterfactual: compose `draft + protocol + ledger` into a scratch file, mutate the ledger portion,
and point `PAPER_FIRST_USE_DRAFT` at it. `setUpClass` then builds `cls.text` entirely from the
scratch composition.

Baseline first, to prove the composition is faithful rather than accidentally passing:

```
$ PAPER_FIRST_USE_DRAFT=$S/baseline.md R7F_CORPUS_ROOT=/Users/edr/code/JouleWise \
  PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3 -B -m unittest \
  tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_ledger_shape_statuses_and_count
.
Ran 1 test in 0.003s
OK
```

Then the mutant — a parenthetical gloss inserted into the "that class here is exactly:" list
(`threshold` → `threshold (a numerical cutoff)`), the exact shape record 35 removed by hand:

```
$ PAPER_FIRST_USE_DRAFT=$S/mutant.md ... python3 -B -m unittest \
  tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_ledger_shape_statuses_and_count
Traceback (most recent call last):
  File ".../tests/test_paper_first_use_ledger.py", line 517, in test_ledger_shape_statuses_and_count
    self.assertNotIn(
        "(", header_match.group(1), "the audience class must list bare expressions, never glosses"
    )
AssertionError: '(' unexpectedly found in 'repeatability, repetition, random scatter, complete,
completeness, sampler cadence, refused, refuses, missing, malformed, corpus range, degrees of
freedom, threshold (a numerical cutoff), exact equality, null hypothesis, tail area, quarantine,
append-only, run bundle, full-history checkout, third-party dependencies, cumulative counter,
linear programme, infeasible, argmin, detected, and measurement interval' : the audience class must
list bare expressions, never glosses
Ran 1 test in 0.003s
FAILED (failures=1)
```

**The guard inspects the raw class text and a glossed entry now fails the test.** Item (1) of the
brief is met, end-to-end, not by reasoning.

Second probe — old guard versus new guard over five header variants, including the **real**
pre-record-35 header recovered with `git show 92ada005^:docs/paper/protocol/first-use-audit-ledger.md`:

```
case                                  old fires  new fires
pre-record-35 REAL header                 False       True
current header (post-4cb214ad)            False      False
mutant: trailing paren gloss              False       True
mutant: gloss containing a comma           True       True
mutant: em-dash gloss, no parens          False      False
LaTeX term (false-positive probe)         False       True
```

Row 1 is the one that matters: the removed guard did **not** fire on the actual defect that sat in
the file, and the new guard does. Record 36's F1 is confirmed against the real historical text, and
the cure is load-bearing rather than cosmetic. Row 4 confirms record 36's account of *why* the old
guard ever seemed to work — a comma inside the parenthetical leaves an unbalanced `(` in a split
fragment; that accident is the only case it caught.

## 2. Item (2) — nothing else changed

```
$ git show --numstat --format= 4cb214ad
1	1	docs/paper/protocol/first-use-audit-ledger.md
249	0	docs/process_traces/2026-09-12-paper-n/36-followup-increment-fresh-eyes-opus.md
3	2	tests/test_paper_first_use_ledger.py
```

Three files: one ledger line reworded, the record-36 report added, the test guard moved. The draft
(`docs/paper/draft-v2-skeleton.md`) is untouched — no prose, no number, no claim moved. The test
change is exactly the prescribed line inserted before `listed` is built plus deletion of the two dead
lines; `grep -rn "glossed_in_class" tests/ scripts/ docs/` (excluding process traces) returns nothing,
so the removal left no dangling reference.

The reworded ledger row (`first-use-audit-ledger.md:142`) I checked against the prose rather than
taking on trust:

> | member-envelope integral sum | A.3 Formal calibration algorithms | glossed-at-first-use | Named and defined in one sentence of Appendix A.3.10 as the four member integrals summed with absolute contrast weights; used twice after that sentence. |

- Nearest heading above the first use is `#### A.3.10 Shared-sign rounding and illustration`
  (`draft-v2-skeleton.md:1366`), so "Appendix A.3.10" is right.
- Name and defining sum are in one sentence at `:1370-1376`, so `glossed-at-first-use` and "named and
  defined in one sentence" are both right.
- "Used twice after that sentence": exact-term occurrences after the definition are `:1378`
  (`\text{member-envelope integral sum}` inside the `\max`) and `:1399` ("This member-envelope
  integral sum exceeds"). `:1383` reads "the four member-envelope integral contributions" — a
  different noun phrase, not the term. **Two is correct.**
- The disposition no longer uses `built-before` vocabulary ("Built … before its two uses"), which was
  record 36's N-a. Cured.

## 3. Item (3) — named test module

```
$ cd /Users/edr/code/JouleWise-wt-paper-n && R7F_CORPUS_ROOT=/Users/edr/code/JouleWise \
  PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= \
  python3 -B -m unittest tests.test_paper_first_use_ledger
...........
----------------------------------------------------------------------
Ran 11 tests in 1.973s

OK
```

Six untracked `*-report.manifest.jsonl` files from earlier seats sit in
`docs/process_traces/2026-09-12-paper-n/`; none were touched by me and none are mine.

**Concurrency note.** An untracked `99b-magistrate-terminal-review-followup.md` (mtime 17:14:58)
appeared in `git status` at the end of my seat but was **not** present in the `git status` I ran at
its start. Another seat is writing into this worktree concurrently. It is not mine, I did not read or
touch it, and it does not affect any verdict above — but a second writer in the tree during a row-10
gate is worth the lieutenant's attention before this branch is pushed or merged.

## 4. Findings

### Tier 1 — blockers

**None.** The guard is real, the prose claim is true, the draft is untouched, the module is green.

### Tier 2 — should fix before landing

**None.** Nothing here needs a bench edit before this commit lands.

### Tier 3 — nits, no blocking force

**N-a. The guard's own message still overclaims, narrowly.** The assertion says "must list bare
expressions, **never glosses**", but it tests for one character. Probe row 5: a gloss written without
parentheses —

```
..., detected, threshold - a numerical cutoff, and measurement interval.
```

— passes the guard cleanly. That shape is not hypothetical for this file: record 36's own N-c
recommended em-dashes for exactly this kind of inline gloss elsewhere in the protocol, so the house
style that would evade the guard is one a future editor has already been told to prefer. The
property the message names is "no glosses"; the property enforced is "no parentheses". Minimal cure,
if anyone wants it later: assert the list matches a bare-expression grammar (`^[a-z0-9 /-]+$` per
split item after stripping "and ") rather than blacklisting one delimiter. **Not worth a round now** —
see §5.

**N-b. The guard can false-positive on a LaTeX audience term.** Probe row 6: adding `\(\sigma\)` to
the class list trips the guard, because `\(` contains `(`. The ledger already carries LaTeX terms
elsewhere (`\(U_{\mathrm{point}}\)` at the `GLOSS_REQUIREMENTS` site), so the collision is reachable
in principle. It is very unlikely in practice — the class is defined as textbook-statistics and
plain-English *words* the professor reads without definition, which is close to a definition of "not
LaTeX". Record only; do not pre-emptively complicate the guard.

**N-c. Record 36's residue is still open and correctly deferred.** Its N-b (the header declares
`threshold` and `exact equality` as audience vocabulary while ledger row `:135` gives them a
`glossed-at-first-use` row — the test checks rows ⊆ list but never list ⊆ rows) and its N-c (the
109-character line 273) are both untouched by this commit, which is right: neither is in scope for an
F1 cure. They should be carried forward explicitly rather than being allowed to age out of the trace.

## 5. Same-signature statement vs records 34 / 35 / 36

The family is **"the new mechanical guard is weaker than the invariant it advertises, and no
counterfactual probe was run against it before landing."** It ran three consecutive rounds:

- **Record 34** installed the closed-class check with `any(...)` where the invariant needed `all(...)`
  — a partly-listed grouped row passed. Caught in 35.
- **Record 35** installed `glossed_in_class` over the already-stripped `listed` set — probe row 1
  above proves it did not fire on the very header it shipped alongside. Caught in 36.
- **Record 36** diagnosed the pattern and, per its §3, refused to write a third guard without a probe.

**This commit breaks the streak, and it breaks it for the right reason.** The cure kills the real
mutant (probe rows 1 and 3), which neither predecessor did, and it was landed with a probe recorded
in the commit subject ("probe: a glossed entry now fails"). That is the first round in four whose
guard is not vacuous.

The honest qualifier: the signature is **attenuated, not extinguished**. N-a is the same shape one
more time in miniature — message says "glosses", code says "parentheses". The difference in degree is
large enough that I do not treat it as a fourth repeat: records 34 and 35 shipped guards that killed
**nothing**, while this one kills the entire defect class that actually occurred, twice, in this
file. A guard that is narrower than its prose is a different and much smaller failure than a guard
that is empty.

**Therefore I do not fire the standing escalation trigger**, and I recommend against opening a
fourth guard-writing round to close N-a. Doing so would re-enter precisely the loop record 36 warned
about, at a point where the marginal defect caught is a gloss delimiter nobody has yet written. What
record 36 flagged for magistrate/cold-gate territory still stands and is unaffected by my verdict:
the process rule *"every new ledger-test guard lands with a recorded counterfactual probe showing it
fires on the defect that motivated it"* is a process rule, this commit is its first voluntary
instance, and ratifying it is not a bench decision and not mine.

## 6. Recommendation

**Land as-is.** All three brief items verified: the guard inspects the raw class text and a glossed
entry now fails (end-to-end, through the real test method); nothing but the test guard, one ledger
disposition, and the record-36 report changed; `tests.test_paper_first_use_ledger` is 11/11 green.
N-a/N-b/N-c are trace residue for a later pass, not a fix round.
