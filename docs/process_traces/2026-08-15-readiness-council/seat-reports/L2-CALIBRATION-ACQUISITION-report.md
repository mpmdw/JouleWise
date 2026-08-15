# L2 CALIBRATION ACQUISITION — instrument-readiness audit (xhigh seat)

**Baseline:** `docs/process/audit-baseline-manifest.json` — manifest head `ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b`; worktree HEAD `8937dec` differs from it only in `README.md`, `RUN_STATE.md`, and the manifest itself (verified by `git diff --stat`), so **no artifact in this seat's scope drifted**; results valid under amendment 12. Verified against the manifest: runbook sha `25a4e809…` ✓, acceptance artifact sha `31611396…` ✓, committed head pin at sequence 76 ✓. Worktree left byte-identical (`git status --porcelain` empty at exit); no stray probe processes.

**Verdict: READY** — full packet below; two should-fix work orders (non-gating: neither can corrupt or launder a claim-bearing output; both are availability/taxonomy defects on refusal paths), two nits, two ED-QUALIFICATION rows.

## 1. Evidence universe (16 items)

| # | Artifact | Disposition |
|---|---|---|
| E1 | `scripts/validate_powermetrics_fiducial.py` (1642 ln) | read in full; executed 4 ways |
| E2 | `scripts/reserve_calibration_window_bracket.py` (249 ln) | read in full; executed 3 ways |
| E3 | `scripts/recover_calibration_ledger.py` (504 ln) | read in full; executed 7 subcommands |
| E4 | `joulewise/calibration_ledger.py` (5567 ln) | ~1200 ln read (lease, locked-append, reservation/claim/finalize/abort, terminal pin, session-status, readiness, resume-finalize, abort-session, constants); historical-import block behaviorally via green tests |
| E5 | `joulewise/calibration_bracketing.py` — acceptance-authentication half (44–576) | read; executed incl. forgery (evaluation half → seat L4) |
| E6 | `joulewise/powermetrics_fiducial.py` — evidence assembly + detection core | read; executed via writer runs + 46 module tests |
| E7 | `joulewise/calibration_exits.py` refusal registry | exercised by every refusal probe + registry-congruence test |
| E8 | `joulewise/authentication_io.py` | executed green (its suite + every authenticated read here) |
| E9 | acceptance artifact `calibration_acceptance_d079_v2.json` | manifest-hash ✓, authenticated, tampered (falsifier) |
| E10 | `protocol_v3.json` frozen protocol | verified by every writer invocation |
| E11 | committed head pin (seq 76) | live-audited |
| E12 | **production ledger** `runs/calibration_observation_ledger.jsonl` (untracked, main checkout) | read-only live audit |
| E13 | runbook §§5/5B/5C/6 (+§10 anchors) | read; compared to code; sha ✓ |
| E14 | `docs/contracts/calibration_ledger_append.md` generated registry | congruence EXECUTED (exits suite test) |
| E15 | fast test corpus (5 modules + exits) | 215 tests executed green |
| E16 | writer crash matrix (16 tests) | **partial**: 6 executed locally; full module blocked on-host by finding L2-1; CI exclusive job green at baseline head (#149) |

**Coverage: 15/16 examined fully; E16 partial** (see unexecuted obligations).

## 2. Executed positive probes

- **P1 — CH-1 comparator (two-way check, executed):** `_derive_preflight_systematic_screen_s()` → `0.033558756679900` == the chain literal `PRE_CAL_FIDUCIAL_MAX_S` in runbook §6; module-level `PREFLIGHT_SYSTEMATIC_SCREEN_S` identical; wrong identity epoch → named `acceptance_artifact_epoch_mismatch{stale_fields:[os_build]}`.
- **P2 — 215 tests green on this host:** bracketing+authentication_io+custody_store (67), calibration_ledger (72), powermetrics_fiducial (46), calibration_exits (30 in 314 s — includes the generated refusal-registry ↔ contract ↔ runbook-§10 congruence test, which is the executed §10-vs-code check).
- **P3 — Runbook E-8/E-9 replay (literal argv):** readiness pre-reserve → `ready` + exact frozen-plan sha echoed; reservation superset `--execute` → `calibration_pre_reserve_authorized` + `status: reserved` + deferred terminal pin; `session-status` → `next_slot: pre` and the chain's exact `jq` dispatch path resolves; pre-slot early warning → `ready` at `physical_ahead`.
- **P4 — Degenerate live-writer lifecycle fails closed end-to-end:** unresolved clock anchor → evidence `invalid`, `b_fiducial_s: null`, exit 1, pre-slot finalized non-valid → automatic session abort + terminal pin candidate + `claim_evaluation_blocked_until_pin_commit: true`.
- **P5 — Live production ledger:** worktree code, read-only: `audit` → `audit_clean` @ seq 76 = committed pin; `audit-observations` at the acceptance cutoff → `observations_classified`.
- **P6 — Recovery positive control + idempotency:** resume-finalize on clean custody → `finalized/valid/operation_completed`; identical re-reservation → byte-identical ledger (5678→5678), exit 0; conflicting re-reservation → `reservation_identity_conflict`.
- **P7 — Targeted crash-matrix green:** two-process lease contention → fresh resume; crash-capability trio (invalid preserved/valid consumed; ambient stage inert; swapped pathname fails link-count check closed).

## 3. Executed falsifiers (negative probes)

- **N1 (mandated) — tampered acceptance through the full preflight:** built a **self-consistent forgery** (level screen loosened to `0.0995…`, statistics/rounding/operatives aligned, `derivation_sha256` recomputed) in a byte-copy of the tree; ran the full live writer CLI with bracket args. **Refused**: exit 2, `calibration_frozen_protocol_invalid` / `acceptance_artifact_unauthenticated`, `arm_blocked: true` — before mlx import, ledger touch, or capture. Only the code-pinned exact-byte sha catches it, which is the design. Same tree, `resume-finalize` → `acceptance_artifact_underivable` (**None-comparator guard fired**).
- **N2 (mandated) — recovery the ledger must refuse (7 scenarios):** tampered `power_trace.csv` → `custody_unreadable`; partial custody → `custody_partial`; abort-on-complete → `custody_complete_use_resume`; post-before-pre → `slot_order_conflict`; wrong plan bytes → `plan_hash_mismatch`; binding swap (self-consistently re-hashed) → `finalization_binding_conflict`; forged 0.9 s bound in valid-status evidence → **`systematic-invalid` + session abort — never `valid`**. All exact registered codes.
- **N3 — non-termination witness (found L2-1):** crash-stage degenerate run ground **>600 s** (3 observations) inside `_accepted_region_projection`; SIGABRT stack captured at `_pulse_loss_cell_lower_bound`; identical no-crash setup finished in 10.7 s and failed closed correctly.
- **N4 — missing-parent traceback (found L2-2):** readiness with a ledger path whose parent doesn't exist → raw `FileNotFoundError` traceback, no refusal envelope; `inspect` handles the same state cleanly; E-9 then succeeds because the lease `mkdir`s the parent — i.e., the documented E-8→E-9 order crashes at E-8 on a fresh checkout.

## 4. Findings

**L2-1 (should-fix)** — `joulewise/powermetrics_fiducial.py:554` (`_accepted_region_projection`; constants :70/:73). No work budget in the interval branch-and-bound: 1.5 s × 1.5 s bisected to 0.1 ms cells is ~2.25e8 cells/pulse × 59 pulses when the loss surface doesn't prune (degenerate unanchored traces). *Failure scenario:* pre-calibration hits `clock_anchor_unresolved` (recorded real condition, §10/§13.1) with a flat loss surface; the writer computes for hours **holding the writer lease**, the chain has no watchdog, the operator may not touch the Mac (§5C) — the funded window and its one-launch consumed arm capability burn with no governed exit. Consumption soundness unaffected (evidence forced invalid; SIGKILL leaves fail-closed pending state — witness-proven). Also prevents the crash-matrix suite from completing on this host. → **WO-L2-1**: rigorous cell/wall budget → fail-closed `detection_nonconvergent`; and/or skip full-resolution projection when the anchor is unresolved.

**L2-2 (should-fix)** — `joulewise/calibration_ledger.py:2885` via `writer_lease_is_live`, uncaught at `scripts/recover_calibration_ledger.py:412/:321`. Missing ledger **parent directory** → raw traceback (exit 1) on the diagnostic readiness/session-status surfaces instead of a registered refusal — an unmapped failure ends the night per §5C rule 4 where a governed `physical_ledger_unreadable`-family refusal (with its §10 row) should. *Bounded:* the frozen plan pins `CALIBRATION_LEDGER` to `/Users/edr/code/JouleWise/runs/...` which exists (verified live), so the documented night path is unaffected; trigger requires a mis-pointed path. → **WO-L2-2**.

**L2-3 (nit)** — runbook :421–423 vs `calibration_ledger.py:4949`: "needs_pin_commit: true ends a 2 a.m. attempt" is unscoped, but pre-slot readiness reports `needs_pin_commit: true` whenever ready (PHYSICAL_AHEAD is the required mid-bracket relation). Mechanical reading aborts every legitimate resume. → **WO-L2-3** (scope the bullet).

**L2-4 (nit)** — `reserve_calibration_window_bracket.py:172–201`: idempotent resume returns `status: reserved` without re-printing `calibration_pre_reserve_authorized`; §5C requires both markers. Harmless (byte-identical ledger, executed), but document the resume shape. → **WO-L2-4**.

**Notes, not findings:** (a) resume-finalize trusts complete hash-consistent custody without a writer signature — within the recorded cold-gate L1 limitation (§5C) and the human entry gate; (b) `status:"valid"` structurally requires a numeric bound (`instrument_evidence`, :1226–1235), so the defensive `bound is not None` branch in resume-finalize cannot launder a boundless-valid disposition from writer-produced custody; (c) zsh float compare in the chain's §5B screen is valid zsh arithmetic; the writer's own `systematic-invalid` disposition + pre-slot abort double-fences the screen.

## 5. Unexecuted obligations
1. Full crash-matrix module on this host — blocked by L2-1's degenerate-cost case (600 s harness ceiling); CI runs it as a dedicated exclusive job (`ci.yml:115`) and the baseline-head PR #149 merged green.
2. Two documented skips needing lead-reviewed D-079 import fixtures at `/private/tmp` (absent here).
3. `calibration_ledger.py` historical-import/bootstrap internals read behaviorally (green tests), not line-by-line.
4. Bracketing evaluation half → seat L4. 5. Real-scale live writer + sudo powermetrics → ED rows / seat L3.

## 6. ED-QUALIFICATION rows
- **EDQ-L2-1**: run `tests.test_calibration_writer_crash_matrix` to completion on the quiet bench at the baseline head; record pass + wall time (CI-corroborated; locally blocked by L2-1).
- **EDQ-L2-2**: the §5C non-delegable lead live verification on the exact reviewed measurement checkout — literal readiness validator + complete under-lease synthetic rehearsal (`--execute`, both slots) + D-134 dry-run receipt `PASS`. Replayed equivalently in scratch here; the runbook requires it on the production checkout with the frozen plan.

## 7. Verdict reasoning
The council question — does every required output either trace through a claim consumer or fail closed against consumption — is answered YES for this component **by execution**: the authenticated-acceptance path refuses a maximally self-consistent forgery at the exact-byte pin; the None-comparator guard refuses by name; the recovery surface refuses every tampered/partial/mis-ordered/mis-bound scenario with its registered code and can never upgrade an out-of-family bound to `valid`; the live production ledger authenticates clean against the committed pin; the degenerate live-writer lifecycle fails closed end-to-end. The two should-fix findings are availability/taxonomy defects on refusal paths — neither can produce a consumable false output — so they attach as work orders, not launch blocks. READY.