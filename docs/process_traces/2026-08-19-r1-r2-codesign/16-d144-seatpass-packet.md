# D-144 PRE-MERGE SEAT PASS — packet (BIG designs D-146 + D-147, implemented artifact)

Fires at pool return (23:34 PST). Seats: terra (xhigh, fresh session,
read-only worktree at the merge head) + Opus (fresh agent, read-only).
Shape: each seat independently reviews the IMPLEMENTED artifact against
the ratified-and-amended specs; one bounded debate round over each
other's findings; Fable rules on the findings (merge gate 3 of 4).

## Scope (the implemented artifact, code+config only)

Diff: `git diff 7d4454e..MERGE_HEAD -- joulewise/ scripts/ configs/ tests/`
(docs/ and RUN_STATE excluded — covered by the fresh-pass gate). The
merge head at packet-assembly time is d10881b; use the live head.

## Authorities (in the worktree, read in order)

1. docs/process_traces/2026-08-19-r1-r2-codesign/13-r1-ruling.md (S1–S10)
2. …/14-r2-ruling.md (S1–S9) **as amended by** …/15-amendment-r6.md
3. The executed-refutation records the implementation must not contradict:
   …/04-r1-design-opus.md §(d) A1–A9, …/06-r2-design-opus.md §(d)+(g),
   the debate docs 08/09/11/12.
4. Execution custody: docs/process_traces/2026-08-19-refreeze-execution/
   (lens reports + delta audits already run DURING implementation — the
   seat pass is the post-hoc whole-artifact view those stage-local
   audits could not take).

## What this pass uniquely owes (not a re-run of the stage audits)

- WHOLE-ARTIFACT coherence: do S0–S5 compose? (era system ⟂ resolver ⟂
  pack lineage ⟂ r6 pins — any seam the stage-local lenses could not see
  because each saw one stage.)
- Spec-vs-implementation drift ACCUMULATED across fix rounds (the
  r5→r6 class: design-time verifications falsified by later rounds —
  one instance is known and amended; hunt for others).
- The frozen surfaces: _v1/_v2 byte-identity at the merge head
  (recompute committed tree digests vs the T10 table), r2–r5 acceptance
  artifacts byte-identical, freeze-0003 receipts vs their sidecars.
- The claim barrier end-to-end: one adversarial walk from a stored v2
  bundle through every claim-side surface at the MERGE HEAD.
- Anything either seat judges MERGE-BLOCKING with the D-119/soundness
  lens: this artifact feeds claim-bearing measurement.

## Debate agenda seed (magistrate; extend with your own findings)

1. Findings the other seat missed or overgraded (severity discipline:
   blocker = wrong behavior or broken frozen surface; should-fix =
   correct but fragile; nit).
2. Any deviation from a ruled clause that lacks a recorded amendment.
3. The GO/NO-GO recommendation for the merge wave, per seat, with the
   single strongest reason.

## Outputs

Each seat: a findings report (severity-tiered, file:line, executed
evidence where possible) to the session scratchpad. Debate: one response
each. Fable: ruling (merge gate 3 verdict) custodied to
docs/process_traces/ with the packet.
