# Magistrate synthesis — CAL-BRACKET B1 rule-11 gate (2026-08-03, late evening)

Instruments: cold Fable judge (`ruling-cold-fable.md`) + Sol contract-lens
refuter at effort HIGH (`ruling-sol-refuter.md`; Ed effort cap in force).
Both ran read-only against `impl/cal-bracket-d079` @ `2e61ff9`; both
worktree-clean verified. Split verdicts synthesized by the lead per
rule 9 (never majority-voted).

## Convergent (adopted as ruled, no synthesis needed)

1. **B1 CONFIRMED, both halves**, independently probed by both
   instruments: the round-1 guard at `whole_window.py:4073-4083` is
   fail-closed before the preparation seam AND fail-open for
   implicit/default minted rows (raw-declaration comparison vs the
   `_row_consumption_semantics_id()` default).
2. **Round 2 LICENSED** — conditioned on the exact shape below.
3. **Repair shape (composed, the two rulings agree on substance):**
   - REMOVE the round-1 pre-flight guard at :4073-4083 entirely; do
     not amend in place; verify not shadowed.
   - ENFORCE in `_validate_row_uncached`, immediately after
     `_current_core_rederivation_reasons()` has had its sole
     preparation opportunity, consolidated with the existing
     normalized post-seam readiness block at :4343-4361: normalized
     `row_semantics == MINTED_CONSUMPTION_SEMANTICS_ID` and
     (`consumption_session is None or not consumption_session.ready`)
     → `whole_window_verdict_provenance_invalid`.
   - Key on the already-computed NORMALIZED `row_semantics` (:4144).
   - PROHIBITED (refuter D1, adopted): placing the check inside
     `_prepare()`; calling `_prepare` from consumers; requiring
     session-semantics == row-semantics (would fail-closed the
     default-constructed sessions in floor_extraction.py:1616-1631
     and inputs.py:2815-2824).
   - Asymmetry (judge b.2, adopted): minted rows may legitimately
     lack `evaluation_basis` — do NOT refuse minted on `basis is None`.
4. **Same-signature trigger pre-armed** (both): if the round-2 delta
   re-audit finds B1 in any placement- or normalization-shaped form,
   rule 11 fires — consult, never round 3. Also (refuter): if the
   consolidation unexpectedly requires consumer-call-site changes,
   STOP — that is new structural evidence, not scope to absorb.
5. **Legacy/implicit rows: fail-closed wins** (judge b.4; refuter's
   covered-paths table concurs). Frozen tests that break get updated
   to supply prepared sessions or explicit non-minted declarations;
   a genuinely frozen contract conflict is a `NEEDS_RULING` early
   return, never a weakened guard.

## Regression contract (UNION of both rulings — all mandatory)

Structural constraint (judge c, verbatim into the implementer prompt):
no B1 regression may call `_prepare()` directly, mock
`_validate_row_uncached`, or otherwise enter below
`whole_window_refusal_reasons` (or a higher production consumer). The
round-1 test pair is REWRITTEN to comply, not deleted.

Five regressions (judge R1-R5; refuter's three are subsumed):
- R1 explicit minted + fresh valid-snapshot session → accepted;
  session became ready as a side effect. RED pre-fix at 2e61ff9.
- R2 same shape, snapshot carries `calibration_ledger_pending` →
  refused, refusal traceable to preparation (refuter: with that
  reason).
- R3 implicit row (no `consumption_semantics_id` anywhere) + None
  session → refused. RED pre-fix at 2e61ff9.
- R4 implicit row + fresh valid session → same outcome as R1.
- R5 explicit minted + None session → refused (round-1 fence widened).

Plus (refuter c, adopted): two mutants — (m1) early-placement (check
moved back before the seam) and (m2) raw-comparison (normalized →
raw) — each must make at least one regression fail. Red-pre-fix for
R1/R3 via the established overlay-on-git-archive method.

## Divergences and lead rulings

**D1 — execution route.** Judge: DELEGATE (deliverable dominated by
tests; contract already written). Refuter: BENCH (rule 9: change
smaller than a restated contract). LEAD RULING: **DELEGATE to Sol.**
The refuter's own premise cuts for delegation — the contract already
exists (these rulings ARE the spec), so the delegation-contract cost
rule 9 weighs is ~zero, while the deliverable (5 regressions through
production entry points + 2 mutants + 2 overlay proofs + round-1 test
rewrite + probable frozen-test updates) is an implementation session,
not a bench wrap. Rule 8 economics and rule 11 altitude both point the
same way. Refuter's bench ruling OVERRULED with this reasoning.

**D2 — implementer effort tier.** Judge ruled xhigh (rule-10
cost-of-error trigger). OVERRIDDEN BY ED's standing directive
(2026-08-03 evening: Sol HIGH only for now). Written dissent recorded
for Ed per rule 11: the magistrate agrees with the judge that this
round is capability-matched to xhigh; it runs at high solely under
Ed's cap. Mitigations: the spec is complete (judgment already spent by
the gate), the delta re-audit conditions are unusually strong, and the
lead TMPDIR replay is mandatory. If the round fails, that is the
"significant decline" datum under Ed's own escape clause and round 2′
re-runs at xhigh after consult.

**WRITE_SCOPE** (judge d, adopted): `joulewise/whole_window.py`,
`tests/test_whole_window_selection.py` — exhaustive. Frozen-test
casualties elsewhere → `NEEDS_SCOPE` with enumerated paths.
`EARLY_RETURN: NEEDS_SCOPE, NEEDS_RULING`.

## Delta re-audit conditions (composed judge e + refuter e)

1. Independent read-only re-audit at the exact final head, implementer-
   distinct, same lane as `streamB-delta.md`.
2. Probes UNMOCKED end-to-end through `whole_window_refusal_reasons`
   with fresh sessions: explicit-valid-fresh → accepted; implicit +
   None session → refused; pending-snapshot fresh → refused.
3. Verify: structural test constraint held; no raw-declaration
   semantics comparison anywhere on the enforcement path; :4073-4083
   guard removed not shadowed; snapshot object identity / no reload on
   every named consumer; B2/S1 fences and round-1 snapshot mechanisms
   (:416-430, :487-494) untouched; both mutants exercised.
4. TMPDIR gap CLOSES THIS ROUND: the re-audit runs focused + canonical
   suites with writable TMPDIR, and the LEAD independently replays the
   focused minted/ledger tests and the full suite at the bench,
   recording exact counts here (rule 1; also retires the packet's §3
   suite-provenance ambiguity flagged by the judge).
5. Same-signature survival → rule-11 consult, no round 3.

## Packet-hygiene erratum (recorded, packet left as-judged)

Refuter P1 (should-fix): the packet's "in full" label was not literally
verbatim (heading converted to a sentence, punctuation normalized);
§5's not-in-dispute summary omitted three retained checks (total-38,
prior-set subtraction, budget boundaries); §4 omitted R1.1
sole-ledger-authority. Judge flagged the fix-1 suite counts as
Sol-sandbox, not bench. Both instruments state the gate result is
unaffected (full D-109 was supplied as authority). The packet is NOT
edited post-judgment; this erratum is the correction of record, and
the "verbatim means verbatim" lesson feeds the packet-assembly
checklist in the charter's validator work.

## Disposition

Round 2 launched per this synthesis (Sol, effort high, worktree
`calbracket`, single commit citing this gate). Gate record complete
when: round-2 report + delta re-audit + lead replay counts are
appended, then PR under D-072.

## Round-2 execution log (appended)

- Round 2 ran delegated Sol HIGH per the D2 deviation (recorded above).
- Report 1 (`round2-report-needsscope.md`): repair COMPLETE in-scope —
  guard removed, normalized post-seam enforcement consolidated, R1-R5 +
  both mutants + both overlay red-pre-fix proofs pass; baseline full
  suite green pre-fix (2453 OK); post-fix canonical failures confined
  to exactly three legacy-fixture files (analysis_integration 39F/4E,
  floor_extraction 4F, whole_window 1F) → NEEDS_SCOPE early return,
  the gate's pre-authorized shape.
- LEAD SCOPE GRANT (2026-08-03 ~23:40): the three enumerated test
  paths added to WRITE_SCOPE (fixture-side only; no enforcement
  weakening; assertion-purpose conflicts return NEEDS_RULING; full
  suite green + single gate-citing commit required). Run resumed on
  the same thread.
- CONTAMINATION ERRATUM (same class as the doctrine-gate judges'
  B1 finding): this gate's cold Fable judge was convened in the main
  checkout pre-charter and received doctrine/memory auto-injection
  without disclosure. Its ruling stands on its verified file:line
  evidence (independently corroborated by the Sol refuter at the same
  head). All future convenings follow the registry clean-launch
  procedure. Full note: t3-doctrine gate synthesis-exhibits SX3.
