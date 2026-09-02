# Coverage consult (Sol 250) — magistrate ruling and fix-round-3 shape (2026-09-02)

Consult seat: Sol xhigh, read-only, detached worktree at `8ab397b5`, brief
file 24, report custodied as file 25 (envelope 6077 bytes; clean/complete).

## Ruling

Adopted, as the shape of fix round 3 (implementer: luna xhigh, for a third
model family on the same producer):

1. **Primary — one hand-derived golden bundle** (Sol §Q3, used verbatim:
   eight records, fixture sha256 `cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f`,
   rebuilt and re-hashed at the bench below) with a
   full-`build_payload` equality assertion minus the two provenance keys,
   plus an exact projection of the Markdown field lines and the two stdout
   lines (Sol lists CLI stdout as a not-killed class; it costs one
   assertion to pin).
2. **Secondary — fixed-seed differential** against a ≤ 30-line reference
   implementation inside the test module (Sol §Q1: worth its maintenance
   because a computation mutant can agree on every fixed case, including the
   retained bundle).
3. **Not adopted:** a per-field census test (indirect; the equality assertion
   already fails on any key drift), Hypothesis or a mutation framework (none
   exists in the repo — Sol ran `ls scripts | grep -i mut`: nothing — and
   adding one for a 400-line producer is overbuild).
4. The existing one-refusal-one-test suite stays; the golden does not expand
   refusal coverage (Sol §Q2, row "refusal-guard deletion").

Why the golden is credible: the only derived material is two sorted lists,
three type-7 positions each, and the renderings (Sol §Q1); the magistrate
re-derived every number from the CSV literals with an independent script
(below) before dictating them into the brief, and the brief forbids the seat
from computing any expected value with a producer helper.

## Process note

Sol §Q5 agrees the same-signature reading (file 23) is correct and that the
instrument was a consult, not a cold gate: the failure class is test
adequacy, which a design consult resolves in one round, whereas the cold
gate adjudicates verdicts and irreversible steps. The consult also did what
round three could not: it enumerated the not-killed classes (Sol §Q2) so
the residual is named instead of discovered by a fourth reviewer.

Fix round 3 also carries Opus 249 C-3/C-4/C-10 (glosses, dictated in the
brief) and C-6 (prune), so the artifact is re-issued once.

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-paper-d
$ python3 docs/process_traces/2026-09-02-paper-d-dg071/26a-golden-check.py <scratchpad>/golden-check
sha cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f
gaps [Decimal('2.0E-7'), Decimal('-3.0E-7'), Decimal('0E-8'), Decimal('5.0E-7'), Decimal('-4.0E-7'), Decimal('7.0E-7'), Decimal('-0.00000100')] max 0.00000100 nonzero 6
dg071 8 0.1000000400 0.100500050 0.1010000900 0.0010000500 | 100.0000 100.5000 101.0001 1.0000 diffRendered 1.0001
dg075 7 0.0999998100 0.10059905 0.1010003900 0.0010005800 | 99.9998 100.5990 101.0004 1.0006 diffRendered 1.0006
exit=0
```
