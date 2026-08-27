# The "ruled but never installed" sweep (S9, T26, 2026-08-27)

## What this is

A read-only audit of every decision the project made between **D-117 and
D-157**, asking one question of each: *the thing that was ruled — is it actually
in the code?*

Not "was it written down." Not "did someone say it landed." Is there, today, at
a line number you can open, an artifact that does the ruled thing — and a check
that refuses the wrong value at the place where the bytes are made.

## Why it was run

Three times in the single session of 2026-08-26/27, a ruled contract turned out
to have **no route or no check in code**:

1. **CONSUME-CONFIRMATION-SUPPLY-01** — the launcher had no supply line for the
   step-6 confirmation table the ceremony required.
2. **The launcher runbook arguments** — the code required arguments no runbook
   passed.
3. **D-157** — on 2026-08-17, ruling D-139 clause A2 fixed a Holm multiplicity
   family at m=2 and said those values "enter the gamma prospective manifest's
   `families` block at the production freeze." Ten days and eighteen decisions
   later the generator still emitted `m=1` with a "contingent on unresolved
   ratification" note, no `families` block at all, and the freeze path never ran
   the prospective validator. The clone proof passed end to end **while minting
   bytes the consumption edge would refuse.** Cost, had it not been caught by a
   reader: a 168-hour campaign ending in a dead claim edge.

Each of the three was found by a person reading, not by the instrument. That is
the defect this sweep exists to size: **how many more of these are there.**

## The answer, in one line

Enough that the transaction night should not be scheduled on the assumption that
"ruled" means "installed." The sweep found a second end-to-end instance of the
D-157 shape — this one on the collector, downstream of D-157 and **not cured by
it** — plus a scope correction that the in-flight W-10 cure needs before it can
succeed.

## How to read the files here

| File | What it holds |
| --- | --- |
| `SHORTLIST.md` | **Read this first.** The transaction-blocking findings, ranked, each with the concrete cure and whether that cure is a code change, a runbook change, or a W-list entry. |
| `FINDINGS-TABLE.md` | Every implementation clause the sweep enumerated, with its status and evidence. The full census. |
| `METHOD.md` | What was swept, against what baseline, what the four statuses mean, and how the seats were run and refuted. Read this before disputing a status. |
| `raw/` | Verbatim per-group seat output and the refuter reports, preserved as custody. `raw/SHARED-BRIEF.md` is the binding brief every enumeration seat ran under. |

## The status codes in brief

**A** — installed and checked at the producer. **B** — the rule exists somewhere
but nothing enforces it where the bytes are produced; a consumer refuses instead.
**C** — not installed at all. **D** — superseded by a later ruling.

**B is the D-157 shape**, and it is the category that costs campaign nights,
because a B failure is invisible until after the spend. The single test that
separates B from A: *does the validator have any caller outside its own module
and its tests?* `validate_prospective_analysis_manifest_v3` did not — it was
correct, complete, and called by nothing on the freeze path, for ten days.

## What this sweep feeds

The unratified process proposal at
`../process-proposals/ruling-status-semantics.md` argues that a ruling with an
implementation clause should be recorded as `decided`, not `done`, until its
index row cites the commit that installed it **and** names the producer-side
check that refuses its absence. That proposal routes to a cold gate, and this
sweep is the evidence packet for it. The census below is what "we do not
currently know which rulings are installed" costs, measured.

## Standing caveat

This audit can miss things — a clause whose installation lives somewhere no seat
looked. It is built not to invent things: every finding on the shortlist survived
an independent seat whose instructions were to prove it installed. Read the
counts as a floor, not a census.
