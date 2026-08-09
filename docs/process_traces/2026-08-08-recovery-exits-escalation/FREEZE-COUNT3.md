# Recovery-exits FROZEN at unexecuted-proof COUNT 3 — cold gate required (2026-08-08 night)

> **RESOLVED (2026-08-08 night) — see COLD-GATE-SYNTHESIS.md.** The cold gate CONFIRMED this freeze and ruled the arming blocker DISCHARGEABLE (ordinary G2/G4/G6 executed-probe fix round + manual arming procedure; witness-integrity rescoped to an out-of-process mutation-kill harness off the critical path; FIX-19 AST-hardening PROHIBITED). Correction to this doc: G2 is a second-occurrence of the lease FAMILY but a first-occurrence MISSED CALL-SITE at the genesis facet (the fixable reading) — the earlier 'first-occurrence' vs 'second occurrence' labels below are reconciled by that distinction.

**Disposition (magistrate, rule 11):** the FIX-14..18 witness-integrity
round is FROZEN. It does NOT get a fix round. A COLD GATE (fresh Fable
instance + Opus contract-lens refuter, mechanically-assembled packet)
owns the resolution. This mirrors the U2 count-3 freeze exactly.

## What delta 2 found (parallel 6-lens fan-out over `bc01908..4495609`)

ALL SIX lenses returned NOT-CLOSED. Reports: DELTA-2-G1..G6-REPORT.md.

| Lens | Verdict | Finding |
|---|---|---|
| G1 (unexecuted-proof CLASS) | **ALIVE count 3, executed** | `EvidenceAlias = PublicExecutionEvidence` fabricated complete-looking writer records past the AST "no direct construction" gate WHILE `_execute_valid_writer` called `calibration_readiness` directly and never launched the writer; both the AST gate and `test_correct_preflight_registry_executes_every_correction_surface` passed with the writer mutated to always-refuse (`Ran 2 tests, OK`). test_calibration_exits.py:543,645-680; owned_process_runner.py:42 |
| G2 (FIX-15 lease) | NOT-CLOSED (inspect) | genesis publication path-based, not bound to the cached parent dirfd — a replaced parent lets two lease handles govern inconsistently. calibration_ledger.py:2951,2972 |
| G3 (FIX-16 preservation) | NOT-CLOSED (executed) | PreservationGuard gate compares stored scalar fingerprint+order, not the actual sample TIME; a deferred-fingerprint guard passes the corpus gate with the manifest-corruption mutation applied. test_calibration_exits.py:94,98,504 |
| G4 (FIX-17 ownership) | NOT-CLOSED | OwnedPublicProcessRunner can block forever before descendant teardown. owned_process_runner.py:308 |
| G5 (FIX-18 analyzer) | 2 should-fix | provenance analyzer laundered by kw-only helper args and nested comprehensions (real delta-1 sites still flagged). |
| G6 (new-defect) | NOT-CLOSED (lead-confirmed) | crash-auth `finally` unlinks any supplied path on ANY successful open (even failed validation) — destructive; must gate unlink on `valid_stage`. validate_powermetrics_fiducial.py:248,279-286; reserve_calibration_window_bracket.py:82-89 |

## Why cold gate, not FIX-19 (rule 11, mandatory)

Two consecutive rounds fail the SAME SIGNATURES, and the failing round
WAS the terminating consult's output:
- unexecuted-proof: gauntlet → delta-1 P1-2 (count 2) → ESC-2 consult
  designed FIX-14 to make it structurally impossible → delta-2 G1
  reproduces it (**count 3**).
- lease identity: delta-1 P1-1 (alias) → FIX-15 "terminal identity" →
  delta-2 G2 (genesis facet) — same family, second occurrence.
- preservation: delta-1 P1-3 (span) → FIX-16 "universal guard" →
  delta-2 G3 (gate doesn't bind sample time) — same family, second
  occurrence.

The ESC-2 consult's designs were called "terminating" and did not
terminate. Rule 11 makes "a second fix round on the same defect" and
"continuing past an escalation trigger" MANDATORY cold-gate triggers.
Spawning FIX-19 would be the sunk-cost continuation the topology exists
to prevent.

## What the freeze costs (unlike U2 — SURFACED TO ED)

Recovery's merge DISCHARGES THE NIGHT-1 ARMING BLOCKER, which gates the
quiet-window captures, which gate the paper's measured numbers. So this
freeze IS on the paper's critical path (U2's was not). This is exactly
why neither barrelling into FIX-19 nor casually freezing is acceptable
— the disposition is consequential and Ed must see it.

## Decomposition the cold gate must rule on (do not pre-commit)

The recovery stream has two layers. The CUSTODY CORE (ledger-resident
intent/finalize/abandon) was ruled CLEAN by the escalation ("no path
admits a control receipt as evidence; the class lives in the
operator/liveness layer"). The WITNESS/EXITS layer
(calibration_exits.py, the witness corpus, the crash matrix) is what
keeps failing. Open question for the cold gate: can the arming blocker
be discharged by landing the clean custody core + the runbook D-117
amendment, with the witness-corpus INTEGRITY question resolved
separately — or is executed-witness integrity load-bearing for arming
such that nothing lands until it holds? The magistrate must NOT decide
this decomposition alone; it is the cold gate's to rule.

## What is sound and must be preserved on resume

The 11 FIX-1..13 closures graded Implemented by delta-1; the
witness-scope tri-state registry (71 rows, census 22/3/46); CH-1 /
PREFLIGHT_SYSTEMATIC_SCREEN_S; the D-117 §5/§6/§10 runbook amendments;
the two-invocation binding-vs-custody classification (G3 confirmed it
correct); FIX-18's real-site flagging (only the laundering evasions
open); FIX-17's real-SIGKILL-at-real-site behavior and inert-ambient
diagnostic (only the unlink-on-failure + runner-hang open).

## Resolution packet (what a cold gate must establish)

1. A witness-integrity contract that a consult-designed gate did NOT
   already fail — i.e. one whose EVASIONS were themselves enumerated
   and closed (aliased evidence classes, direct-readiness shortcuts,
   deferred-fingerprint ordering). The prior failure mode is gates that
   assert on stored artifacts a malicious witness can fabricate; the
   resolution must bind proof to OBSERVED execution the test cannot
   forge.
2. A ruling on the custody-core/witness-layer decomposition above.
3. The four first-occurrence defects (G2 genesis, G4 runner-hang, G6
   crash-unlink, G5 analyzer laundering) folded into whatever lands.

Cold gate schedulable now (design consult for the integrity contract)
or post-window; it is night-critical because it blocks arming.
