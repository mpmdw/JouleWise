# S9 sweep — method of record

## What was swept, and against what baseline

**Corpus.** Every decision in `docs/decision_log.md` from **D-117 through
D-157** — both the one-line index rows (lines 142-184) and the tail sections
that carry each decision's full text — plus the twenty-six **unattributed tail
sections** of the same era. Those unattributed sections carry a `WO-…` or
`R-N RULED` heading instead of a D-number (for example "WO-CONSUMPTION-EDGE
contract ADOPTED", `:9112-9159`), but they are rulings with implementation
clauses exactly like the numbered ones, and excluding them would have skipped
the consumption-edge and launch-binding contracts — two of the three areas the
sweep was called to examine.

**Baseline.** `origin/main` at `0dd3b6dc` ("MLX-ACID-SIGABRT-01 +
CALEXITS-FOURTH-SHAPE-01 + PLANTEST-RGLOB-RACE-01 closed", merged 2026-08-26).
Every `file:line` citation in this trace was read at that commit. Work in flight
on other branches — notably the S8 stream on `fix/d139-a2-gamma-families`, which
implements D-157's W-10 cure — is NOT baseline; where a finding is already cured
on an unmerged branch, the table says so.

## What counts as an implementation clause

An **implementation clause** is any sentence in a ruling that asserts a value,
rule, check, refusal, emission, schema key, threshold, or documentation change
is (or will be) realized in an artifact — code, a config, generated pack bytes,
a schema, a runbook, a script, or a test. The signal verbs the sweep keyed on:
*enters, is installed, the code refuses, lands as, the generator emits, the
runbook says, at the production freeze, must, shall, gains, is added, is
stamped, regressions:, the validator requires.*

Pure authority rulings were excluded — "delegated to the magistrate", "Ed signed
off", "recorded as D-1xx" — unless they also specified a mechanical check or a
required document.

## The four statuses

| Code | Meaning |
| --- | --- |
| **A** | Installed AND checked at the producer. The artifact that *writes* the bytes enforces the ruled thing, and a check refuses the wrong value at write time. |
| **B** | Installed, but with NO producer-side check. The value or rule exists somewhere — a consumer refuses it, a validator function exists, a doc says it — but nothing enforces it where the bytes are produced. **This is the D-157 shape.** |
| **C** | Not installed. No code, config, pack byte, runbook, or test realizes the clause. |
| **D** | Superseded by a later ruling (cited). |

The decisive rule, applied throughout: **a validator function with no callers
outside its own module and tests is a B, not an A.** That single test is what
separates "the rule exists" from "the rule is enforced," and it is the test that
D-157 failed for ten days — `validate_prospective_analysis_manifest_v3` existed,
was correct, and was called by nothing on the freeze path.

Seats were instructed to prefer B over A whenever torn, on the ground that a
false A is the worst outcome this sweep can produce: it is exactly the error
that let D-157 live.

## How the sweep was run

**Enumeration — ten parallel seats, one group each.** Seven Opus 5 agents took
the numbered decisions (D-117..D-121, D-122..D-125, D-126..D-132, D-133..D-134,
D-135..D-141, D-142..D-149, D-150..D-157); three Sol xhigh seats took the
unattributed tail sections. Every seat ran under the same binding brief
(`raw/SHARED-BRIEF.md`), read its assigned line ranges verbatim before extracting
anything, and was required to produce a `file:line` it had personally opened for
every status assigned. Raw per-group output is preserved under `raw/`.

**Refutation — independent seats, distinct lenses.** Per the C-028 gauntlet,
each transaction-relevant B and C finding was handed to seats whose instructions
were to PROVE IT INSTALLED, not to confirm it. Blocker-severity findings got two
refuters with distinct lenses — **contract** (what was ruled, what the governing
document says, what a later ruling superseded) and **execution** (what actually
runs, in order, on the night). A finding appears in the confirmed table only if
its refuters failed to break it; refuted and partially-refuted findings are
recorded with the refutation, because a finding that dies to a good refutation is
still evidence about where the instrument is weak.

## Standing bias of this method

The sweep can produce false negatives — a clause whose installation lives
somewhere no seat looked. It is designed not to produce false positives: every
confirmed finding survived an adversary with the opposite brief. Read the counts
as a floor, not a census.
