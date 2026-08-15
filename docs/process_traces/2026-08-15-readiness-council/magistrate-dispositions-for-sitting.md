# MAGISTRATE DISPOSITIONS FOR THE READINESS SITTING — 2026-08-14 (T7 successor session)

Both items below were raised by the C-058 drafting mechanic (⚑ OPEN flags,
c058-draft.md). They are MANDATORY CONTENTS of the sealed sitting packet:
the cold pairing adjudicates both. Written before fleet harvest; the fleet
(run wf_29eee330-1db) was NOT stopped over either — rationale below is the
thing under review.

## Disposition 1 — Baseline drift (manifest head ac3fe1d vs fleet worktrees at 8937dec)

Claim under review: charter amendment 2/12 says any drift from the
baseline manifest invalidates affected lens results; the eleven fleet
worktrees are checked out at 8937dec, three commits past the manifest's
head_commit ac3fe1d.

Magistrate disposition: ZERO lens results are affected, by direct
mechanical application of the rule — not by reinterpretation.

Mechanical facts (verify with `git diff --stat ac3fe1d..8937dec` and
`git show --stat` per commit):
1. Commits after head_commit: 694442c (adds
   docs/process/audit-baseline-manifest.json — the manifest itself),
   d279a7c (README.md + RUN_STATE.md), 8937dec (RUN_STATE.md).
2. Total changed files vs the pinned head: README.md, RUN_STATE.md,
   audit-baseline-manifest.json. No code, no chain artifact, no pack
   byte, no runbook, no contract, no decision-log text.
3. The invalidation rule's own scope is "voids AFFECTED lens results."
   README.md and RUN_STATE.md are session-state surfaces in no lens's
   evidence universe (L1 control plane, L2-L5 chain code/artifacts,
   L6/L7 producer-consumer artifact classes, L8 runbook+packet+scripts,
   L9 hazard register, L10 pipeline, L11 a9/a10 corpus). The manifest is
   cited by every lens but is the REFERENCE, not an audited artifact.
4. Manifest-after-its-own-head is charter-BY-CONSTRUCTION (amendment 2:
   the manifest is "committed before any lens launches, binding HEAD" —
   a worktree at head_commit exactly would not contain the manifest the
   lens must cite). The charter therefore anticipates lens trees at
   manifest-commit-or-later; the drift rule governs changes AFTER the
   manifest, of which there are exactly two, both confined to the two
   session-state files above.
5. RUN_STATE's own T7 instruction ("verify main = baseline head + this
   checkpoint commit; re-pin if doc-only commits landed after") is
   satisfied: nothing landed after 8937dec (verified `git status -sb`:
   main == origin/main == 8937dec at fleet launch).

Standing consequence accepted by this disposition: the COMMIT FREEZE —
no commit of any kind lands on main between fleet launch and harvest, so
the set {README.md, RUN_STATE.md, manifest} remains the complete and
final post-baseline delta for the fleet's whole run. Any commit before
harvest voids this disposition and the affected seats re-run.

If the cold pairing REJECTS this disposition, the remedy is: re-pin the
manifest at the current head and re-run every seat whose universe the
pairing judges touched (worst case: full fleet re-run; windows are not
scarce, per the charter preamble).

## Disposition 2 — M-2 retroactive cold review (rule-11 trigger missed)

Fact pattern (decision log, "M-2 RULED (magistrate)", 2026-08-14): M-2
ruled the frozen packs' draft_status/"not armable" text generator-owned
and OVERRODE the §5C gate's placeholder-text NO-GO reading for exactly
that field, transitional until the chain-fix batch landed freeze-aware
generator text (it landed in #149).

The mechanic's finding, CONFIRMED by the magistrate: rule 11 lists "any
reversal or reinterpretation of a stop signal or verdict" as a MANDATORY
cold-pairing trigger. M-2 overrode a NO-GO reading. No cold-gate
artifact exists for it. The trigger was missed — this is acknowledged as
a process defect, not argued around.

Disposition: M-2 is submitted for RETROACTIVE adjudication by this
sitting's cold pairing (which has exactly the rule-11 required shape:
fresh Fable adjudicator + Opus contract refuter). Scope for the pairing:
(a) was the override sound on the merits; (b) is the landed remedy
(freeze-aware generator status text, #149) sound — note lens L5 is
independently auditing the frozen packs' current text; (c) does any
consumption that relied on the transitional override need re-review.
Exposure is bounded: the override was scoped to one field, transitional,
and is now moot in operation — but a rejected M-2 would void the packs'
regenerated status text and route back through the generator gate.

Process follow-up regardless of outcome: the C-058 entry records the
zero-cold-gates-in-span anomaly; the miss pattern (magistrate ruling
under time pressure at packet-finalization) goes to the council entry's
process-findings section.

## Packet routing

Both dispositions + the c058-draft ⚑ items + the mechanic's record
anomalies (span correction, manifest-gap widening 3→6 concentrated in
review-class runs, #149 body staleness, CLOSED-not-merged PR counts)
are packet inputs. Nothing here lands on main before harvest.
