# U2 cold-gate ruling — cold Fable judge (2026-08-07)

Convened by the magistrate per README.md: Fable subagent, isolated git
worktree, packet + exhibit + decision-log only. Sealed from the Opus
refuter pre-synthesis. Recorded verbatim from the judge's final report.

**Exhibit:** `impl/d117-u2-successor` = `399ffebd` (verified locally).
**Main compared:** `e1a8fc86` (packet's `cdb7896c` verified immaterial —
no intervening commit touches the exhibit files or the writer script).
**Quotation fidelity:** D-102 and D-116 quotations verified verbatim and
complete against `docs/decision_log.md`.

## Rulings

- **Q1 (successor corpus): RATIFY.** Complete content-distinct valid
  same-epoch prefix through cutoff; D-102 pin 2's 19→38 trigger and
  D-116 R2.8 counting ground it; frozen-n=19 reading misapplies the
  issuance-time statement. Builder/test verified (n=31, lineage intact).
- **Q2 (preflight screen): RATIFY-AS-AMENDED.** Amendment: the screen
  derives from the OBSERVED CORPUS MAXIMUM ALONE (quantized
  ROUND_HALF_EVEN 1e-15); the 95% two-draw prediction stays a recorded
  derivation value, never a screen input. The exhibit's
  `max(maximum, prediction_95)` can only RAISE the refusal ceiling —
  loosening systematic classification in exactly the degenerate regime
  the screen polices; the exhibit's own test demonstrates the loosening.
  Caveat recorded: if the max() rule traces to a ratified decision not
  quoted in this packet, that is a packet-completeness problem to
  re-present.
- **Q3 (Student-t method): DEFER.** Structure sound; but the df=18 pin
  short-circuits the algorithm, the only algorithm test asserts the
  pinned literal against itself, and the bisection/incomplete-beta path
  that will mint every future comparator is never compared against any
  reference at any df; ~64 unratified digits extend D-102's 16. To lift:
  independent high-precision cross-check (e.g. mpmath ≥100 digits) over
  a (df, p) grid including df=18 with the pin bypassed, plus a stated
  convergence/error bound.
- **Q4 (count boundary): RATIFY.** Retain pending boundary until
  reached; then 2× the newly issued corpus count. 38 is the only
  ratified number; retention is the more conservative reading.
- **Q5 (new systematic failure): RATIFY.** Persistent automatic-issuance
  refusal pending authority ruling; forecloses the threshold absorbing
  its own challenge; cost is availability, not unsoundness.
- **Q6 (no-content attempts): RATIFY.** Refusal is the only
  non-concealing default given the evidence machinery that exists in the
  exhibit.
- **Q7 (lineage/naming/parents): RATIFY.** Present-in-checkout; one
  authentication path; fail-closed on missing ancestors.
- **Q8 (registry authority): RATIFY.** Every bootstrap pin matches
  D-116's ratified bytes exactly; generalizes the committed-hash-pin
  trust shape.
- **Q9 (publication ordering): RATIFY-AS-AMENDED.** Mechanism ratified;
  amendment (operational contract, no code change): (a) successor
  artifact + registry commit as ONE git commit and no governed
  acceptance evaluation between `publish_successor` returning and that
  commit reaching HEAD; (b) post-commit verification that committed-mode
  loading selects the successor, recorded — the D-116 cold-gate-#2
  precedent for authority transitions.
- **Q10 (probe over open U1 extension): RATIFY.** Narrow authenticated
  exception, read-only advisory probe; issuance and morning verdict sit
  behind terminal committed snapshot assertions.
- **Q11 (parent-judged post evidence): DEFER.** D-102 pin 2's scope
  genuinely underdetermined (acceptance-judgment only vs any later
  bracket-drift evaluation under successor operatives); AND no non-test
  consumer of `POST_SUCCESSOR_POLICY` exists — ratifying a permission
  whose enforcing consumer does not exist licenses future code
  sight-unseen. Lineage-recording machinery itself unobjectionable.
- **Q12 (scope / L4): RATIFY-AS-AMENDED.** Scope acceptable; amendments:
  (a) L4 must NOT be recorded closed/mitigated by U2's landing — open at
  HIGH until writer de-duplication AND §5A/U8 arm-path integration land;
  (b) writer copied-scalar removal is a NAMED BLOCKING UNIT gating any
  live campaign night relying on the writer's systematic classification;
  (c) L4's two mandated review scenarios ride the writer-integration
  review. Live writer still consumes the hardcoded
  `PREFLIGHT_SYSTEMATIC_SCREEN_S` literal with no authentication
  (`scripts/validate_powermetrics_fiducial.py:103`, used ~:913-920).

## Packet defects found

1. Minor: "tags" are code comments, not git tags (all 12 markers exist
   and match).
2. Minor: stale main reference, verified immaterial.
3. No quotation defects WITHIN the quoted entries (D-102/D-116 verbatim,
   adverse clauses present). Caution: Q2's FOR argument inverts the
   refusal-ceiling semantics; AGAINST states it correctly.

## Contamination disclosure (verbatim substance)

Environment not fully cold: harness injected the user's global
CLAUDE.md, project CLAUDE.md, CLAUDE.local.md (including rule 11
itself), and the auto-memory index. Judge states every ruling is
grounded in quoted clause text or verified code. Deliberate in-charter
reads beyond the packet: README.md, D-102/D-116 entries, git metadata.
Did not read task queues, run-state, design brief, D-117 body, U1/U8
records, or traces outside the packet directory. Wrote no files.
