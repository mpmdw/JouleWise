# NR adjudication — magistrate synthesis ruling (D-155)

Magistrate: Fable 5, 2026-08-26 early morning. Inputs: the mechanical packet
(`nr-adjudication-packet.md`), and two independent adjudication seats — Opus
(`nr-seat-opus.md`) and Sol gpt-5.6-sol xhigh (`nr-seat-sol.md`), both
recorded verbatim beside this file. Convergence was near-total; both seats
independently discovered and cross-verified two facts the packet missed:
the TWIN terminal-review parser at `scripts/capture_t0_step.py:288-316`
(which would have refused at the first T-0 capture step even after the
obvious NR-11 cure — the "another missed call site" signature caught at the
desk instead of mid-transaction), and the `.claude/settings.local.json`
allow-rules that could suppress or bypass the D-150(1) prompts.

## Adopted rulings (binding; full mechanics in the seat reports)

- **NR-11 → branch D at BOTH parsers** (`arm_readiness_evidence_t0.py` and
  `capture_t0_step.py`): `PASS`/`Tree-Oid` stay exactly-once;
  `Pack-Sha256` becomes non-empty, duplicate-free, membership of the current
  pack's digest. Zero registry cost. Regressions at both sites per the Opus
  seat's five-case list. Producer edit in `window_runbook.md` §5C (three
  trailer lines). The D-151 c7 warning ("do not allowlist the cure") goes in
  the runbook verbatim. Both seats: no zero-code path exists (branch E is
  mechanically empty — verified three times).
- **NR-12 → branch B**: one magistrate-executed (D-150b), tree-preserving
  attestation commit AFTER the mint; `ATTESTATION_HEAD` = published head;
  `PINSET_MINT_HEAD` remains the allowlist-closure/`hS` coordinate; every
  runbook step naming "the head" says which. The Opus seat's finding that
  this makes r4-3's own freeze-span sentence exactly true is recorded as
  independent corroboration.
- **NR-3 → branch A** (push-then-build), with the Phase E reorder
  E1 build → E3 render table → E4 delegated confirmation/`hC` → E2 verify →
  E5 promote (the publication-phase verify REQUIRES the confirmation pair).
  r4-3 amended with a dated marker, never silently.
- **NR-2 → branch A** (pull-into-dev → push origin → fetch-back at the
  measurement checkout), four-way equality asserted by RUNNING
  `reviewed_main` (never by eye); a fetch is licensed inside the freeze
  span, a commit/push/branch-move is not. The runbook's invented `file://`
  form is dropped.
- **NR-1 → branch A**: `/Users/edr/JouleWise-measurement-20260813`,
  fast-forwarded (ancestry verified). Branch B is rejected on three grounds
  including the blanket allow-rule that would suppress the D-150 prompts.
  Branch C (fresh checkout) is the NAMED FALLBACK if the relock cannot
  reach the lock (e.g. `mlx-metal==0.31.2` wheel unavailable) — discovered
  at W-1, never at the bench.
- **NR-4 → branch A**: marker build AND verify `--phase publication`; the
  §1.3 candidate manifest is STILL PRODUCED (C9 consumes it for custody-tool
  digests — the Opus seat's explicit guard against over-deleting); only the
  marker stops consuming it.
- **NR-13 → code guard, landing BEFORE Phase C1** (the changed-set window
  is the binding gate, not the freeze span): custody-external sentinel
  (default `/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN`, env
  override), refuse-before-write, out-of-span behaviour byte-identical,
  two-branch regression; kernel row closed with the off-by-two citation
  fixed. D-150a's visibility promise is unaffected (the channel is the
  push notification + locally-written status, not the git push).
- **NR-6 → branch B** (dry-run ceremony ×3, NO real arm; first real `_v4`
  arm is the shakedown, a non-claim window per B-3, where arm-side U11 and
  the V4-delta proof are discharged). The `file-09-probe P1/P2/P3` is
  **struck as specified** (P3 requires the arm B-4 forbids — the Opus
  seat's unsatisfiability proof stands) and replaced by named assertions
  over the dry-run receipts (PASS, `refusals: []`, head binding =
  `ATTESTATION_HEAD`, `dry_run`/`NOT_APPLICABLE`/`evidence: []`), with P3
  recorded as discharged at the shakedown GO receipt. The Sol seat's
  read-only reformulation of P3 is recorded as dissent; it was declined
  because renaming an unsatisfiable ruled property to a satisfiable weaker
  one is the quiet-weakening shape this process exists to refuse.
- **NR-7 → A4 governs; condition 5 re-scoped, not struck**, using the Opus
  seat's two-sub-interval restatement verbatim (mint → first consuming arm:
  no arms; first consuming arm → fixation: the campaign's claim-bearing
  arms under marker + table). Amendment markers in
  `MAGISTRATE-RULING-O1.md` and the D-151 index row.
- **NR-8 → mechanical close with an Ed escape**: the magistrate declares
  campaign close when the executed arm set equals the published plan
  (both coordinates named: last consuming arm id closes the changed-set
  window per A6; window-consume completion permits the commit-freeze
  close per A1); early termination/waivers/abandonment are Ed's. Canonical
  `campaign-close.json` in transaction custody (Sol seat's shape) and the
  STRICT record order (declaration → freeze-off → notification → THE
  FIXATION COMMIT FIRST → only then any bookkeeping) per the Opus seat.
- **NR-10 → six ruled prompts + a pre-window prompt inventory** delivered
  to Ed as an ALLOW/ASK/DENY table with exact command strings and cwd
  spelling (the `python3` vs `python` trap noted); if the broad allows
  would swallow a licensed command, ED narrows them — no agent
  self-modification of settings, and any tracked permission edit lands
  before evidence derivation.
- **NR-9 part 3 (cadence) → Ed's one-word question**, presented with both
  seats' options: immediate ping per desk event (Sol: only two events
  exist; visibility after the irreversible step matters) vs batched to
  phase boundaries with immediate mismatch pings (Opus). Recommendation:
  immediate — the saving from batching is literally one ping.

## Operator fixes (adopted shapes)

- **Venv relock**: the Sol seat's FRESH-VENV method (preserve `.venv` as
  `.venv.pre-v4`, rebuild from the lock's canonical constraints form),
  verified by the Opus seat's empty-diff acceptance (full freeze vs the
  37-line lock; version print is a smoke check, the diff is the gate);
  wheel-unavailability falls back to NR-1 branch C.
- **Step-6 contract edit**: the Opus seat's replacement text for
  `d117_step6_confirmation_table.md:37-41` (+`:7-8`, `:79` exemplar),
  recording the D-150b standing delegation with independent recomputation
  of `hM`/`hS`, `authority: ED` / `decision: YES` unchanged, mismatch =
  refusal + ping.

## Pre-window worklist (adopted: Opus W-0..W-8, extended)

W-0 this ruling (ratified here; NR-9 cadence to Ed). W-1 Ed's relock +
magistrate verification (runs first, in parallel). W-2 ONE code PR:
NR-11 both parsers + regressions, NR-13 sentinel guard + regressions —
full C-028 gauntlet + delta re-audit. W-3 ONE docs PR: every doc
reconciliation both seats enumerate (contract, r4-3 amendments, runbooks,
condition-5 restatement, ceremony redefinition, NR-8 procedure, phase
reorder, ruling records, decision-log row D-155). W-4 declare the
reviewed head by CI `conclusion`. W-5 fast-forward + four-way predicate +
§1.1/anchor gates at the measurement checkout. W-6 prompt inventory to
Ed. W-7 measure the full suite once on a scratch checkout (the budget's
only unknown). W-8 §1.5 preflight + D-150a "freeze ON" notification.
**W-9 (pre-SHAKEDOWN, not pre-transaction, parallel):** the Sol seat's
standing blockers (CONSUME-CONFIRMATION-SUPPLY-01, T0-UNATTENDED-01,
UNATTENDED-LAUNCH-01), the WINDOW-COUNCIL-GATE reconvene, and the Opus
seat's flagged V-5 scheduler-gate check.

## Window shape and date

Transaction night per the Opus budget (~2.5–6 h machine, Ed present
~1 h 15 m across two sittings); the shakedown follows council clearance,
never same-night by default. Earliest credible transaction night:
**2026-08-28**, gated on W-2 clearing its gauntlet first-pass; a
same-signature second fix round on W-2 is a consult per the standing
trigger. The 168-hour campaign clock starts at the evidence commit —
the night is chosen only ahead of a week whose nights are available.
