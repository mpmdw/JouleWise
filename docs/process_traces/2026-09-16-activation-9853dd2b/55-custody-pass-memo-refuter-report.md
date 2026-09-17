# CUSTODY-PASS-MEMO-01 refuter — Opus 5, read-only, both lenses + mutations, 2026-09-17 08:32–08:52 PDT (cd0a8d2b vs c9589525)

Verbatim report:

# CUSTODY-PASS-MEMO-01 refuter report (Opus 5, read-only, both lenses) — cd0a8d2b vs c9589525

**Verdict: MERGEABLE-WITH-FIXES.** No blocker. The memo's key, arming, invalidation and pass-count wiring are correct and mutation-killed; the three findings are a mis-stated soundness claim, one unenforced clause, and a gate-sizing/prose issue.

## Mutation table (each applied in `/tmp/refute-memo`, reverted after; `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest …`)

| # | Mutation | Site | Suite | Result |
|---|---|---|---|---|
| M1 | drop `clear_custody_memo()` from `_release_writer_lease` | `scripts/validate_powermetrics_fiducial.py:1463` | custody + derivation_only | **SURVIVED** (81 tests OK) |
| M2 | arm the memo before the lease (preflight seeds) | `…fiducial.py` main, after `_configure_writer_crash_authorization` | derivation_only | KILLED (4 failures) |
| M3 | reuse ignores the head digest | `joulewise/calibration_ledger.py:2002` | custody | KILLED (2) |
| M4 | `required <= verified` → `bool(required & verified)` | `calibration_ledger.py:2004` | custody | KILLED (1) |
| M5 | a refused pass records a memo | `calibration_ledger.py:2318-2320` | custody | KILLED (1) |
| M6 | `next_operation()` carries memo + armed flag | `calibration_ledger.py:2034` | custody | KILLED (1) |
| M7 | `WRITER_CUSTODY_PASSES = 4` | `night_agent_install.py:667` | test_run_night | KILLED (1 failure + 1 error) |

## Findings

**1. SHOULD-FIX — the lease does not do what the memo's soundness argument says it does; a stale verdict IS returned in a scenario the lease allows.**
`CalibrationWriterLease` (`joulewise/calibration_ledger.py:3603-3643`) is an advisory `flock` on the ledger's lock sidecar. It excludes *cooperating calibration writers* from the *ledger*; it cannot stop any other process from rewriting a governed artifact file. Three places claim more:
- `docs/phase_2/derivation_night_runbook.md:1257` — "the writer lease, which is what freezes those files against every other process" (false).
- `docs/contracts/calibration_ledger_append.md:704` — "while it is held, no other writer can rewrite the governed bytes or the ledger" (the lease protects the ledger, not the bytes).
- `joulewise/calibration_ledger.py:1958` — "no other process can mutate the governed bytes while this allowance runs" (false). The code comment at `…fiducial.py:1538` ("against other writers") is the accurate one.

Executed (probe P1, real `CustodyFixture`, real custody-worker subprocesses):
```
preflight reasons () passes 1
under-lease reasons () passes 2      <- memo seeded
[corrupt events.jsonl of custody root 0; head digest unchanged]
readiness reasons ()                  slot-validation reasons ()   passes 2
unmemoized pass on the SAME tampered corpus: ('calibration_ledger_custody_invalid',)
```
So the four-pass writer would have refused and the memoized one does not. **Not a blocker**: the window is repair + readiness + slot validation (sub-second on a healthy ledger); nothing in the night's threat model writes those files (D-161); and the miss is fail-closed downstream — the next slot's pre-lease preflight is unmemoized and refuses. Fix (one line each): replace the three overclaims with the true guarantee ("no other calibration writer can append to the ledger"), and add one sentence to the contract stating the accepted trade — corruption arriving after the under-lease sweep is no longer seen by the readiness gate or slot validation. The seat's closing claim ("no window in which a stale memo can be consumed") is true only *after* `_begin_once`; inside it, that is exactly the design.

**2. SHOULD-FIX — the "cleared on release" clause is not enforced on either ordinary exit path (M1 survivor).**
`finalize` (`…fiducial.py:1713`) and non-bracket `abandon` (`:1674`) do `self.custody_deadline = self.custody_deadline.next_operation()` inside `try`, so the `finally: self._release_writer_lease()` (`:1794`, `:1694`) clears a *fresh, disarmed successor*, never the allowance that holds the memo. Probe P7: `preparation deadline still armed after the successor is cleared: True memo present: True`. Nothing today re-acquires the lease or reuses that object, so there is no live exploit — but the contract clause at `calibration_ledger_append.md:706-711` is unbacked and its deletion costs zero tests. Fix: make `CustodyDeadline.next_operation()` call `self.clear_custody_memo()` on the source, and add one regression that builds a `_CaptureLedgerLifecycle` with a stub lease and asserts `_release_writer_lease()` leaves `custody_memo is None` / `custody_memo_armed False`.

**3. SHOULD-FIX — `CUSTODY_HEADROOM_FACTOR` is now double-booked; the worst case has zero margin at the admission boundary.**
`night_agent_install.py:665-672` and `runbook:1274-1277` keep the old justification (corpus growth, uneven pass cost) *and* add "at two passes that slack is exactly the repaired-ledger third pass". It cannot be both. Arithmetic: gate admits `T ≤ B/(2×1.5)` = 40 s at B = 120. A repaired ledger costs 3 honest passes = 120 s = the whole allowance. A *corrupt* corpus also costs 3 (preflight + refused under-lease + refusing re-read — the seat's own `test_a_pre_lease_pass_never_feeds_an_under_lease_pass` asserts `custody_passes == 3`), so at the boundary the typed `calibration_ledger_custody_invalid` can be replaced by `calibration_ledger_custody_timeout`. Before this diff the worst case was 4T at T ≤ 20 = 80 s, with 40 s spare. Fix: `WRITER_CUSTODY_PASSES = 3` (T ≤ 26.6 s) or `CUSTODY_HEADROOM_FACTOR = 2.0` (T ≤ 30 s), restoring a growth margin. Note record 44 §3(c) explicitly ruled 2 × 1.5, so changing it is a magistrate call, not the seat's error.

**4. NIT — first-use test on the new contract section (`calibration_ledger_append.md:665-772`).** "custody pass", "T", "entry", "physical head digest", "armed" are all built — but **armed** is *used* at `:693` ("the memo is **armed** (below)") and defined at `:700`; per the standing rule a forward pointer fails the draft — move the paragraph above the numbered list or gloss it inline. "custody-bearing observation" (`:668`) is a term of art doing technical work and is never built anywhere in the contract (only other use is `:755`). Two mechanisms are in code but absent from the contract, so the section is not replicable from: `record_custody_memo` **unions** entries at the same digest (`calibration_ledger.py:2016-2018`), and a memo with no head digest is never recorded (`:2012-2015`).

**5. NIT (outside the seat's WRITE_SCOPE, owner = magistrate).** `TASK_QUEUE.md` row A223 and `docs/process/state_kernel.json:1415`/`:1421` still read "WRITER_CUSTODY_PASSES = 4 … T ≤ 20 s … not started". Must move with the merge or the tracked docs contradict the constant.

## Traced, no finding
- **Receipt key-set pins (item 3).** No consumer validates the writer's stdout receipt key set: the night chain does not parse it; `run_night.py:646` only hashes `chain.stdout.log`; `test_run_night.py:2726` is a *subset* assertion on the probe receipt; `test_corpus_strict_validation.py:247` and `test_scheduler_gates.py:145` pin other receipts. `custody_passes` is purely additive.
- **Head-digest freshness.** `bounded_custody_reasons` is reachable only from `load_calibration_ledger_snapshot`, which sets `custody_deadline.ledger_head_sha256 = physical_digest` from the just-parsed bytes at `calibration_ledger.py:2622`, immediately before the pass — no pass can test the memo against a stale key.
- **Memo purity.** `observation_custody_reasons` (`calibration_custody_worker.py:27-42`) is exactly `sha256(bytes at root/relative) == expected`, so (attempt_id, absolute locator, sorted artifact pairs) is the complete input; nothing else is cached. The `custody_backup_roots_disabled` check runs on every call *before* the memo (`calibration_ledger.py:2298-2304`).
- **Discarded under-lease snapshot.** The under-lease pass's verdict is thrown away (`…fiducial.py:1550`), but only a pass with zero reasons memoizes, so a corrupt corpus forces the enforcing readiness gate to re-read and refuse — verified.
- **Release + re-acquire in one process (P4):** clear then re-arm does not resurrect the memo — corruption injected while unleased is caught, `passes 1→2`.
- **Concurrent reservation append (P3):** real second-process append moves the head, memo dies, `passes 1→2`, reasons `head_mismatch`.
- **Gate arithmetic vs prose:** code `elapsed * 2 * 1.5 > budget` (`night_agent_install.py:820`) ⇒ T ≤ 40 s at B = 120; runbook `:1276`, `:1952`, handback `:530`, contract `:727` all agree; `test_run_night.py:2828` pins 40.0 admitted / ×1.001 refused (green). The contract's "90 × 3 = 270 s" and the runbook's "180 s" are the gate product and the honest-pass cost respectively — both correct.
- **`next_operation()` inherits nothing** (M6 killed, P7).

## Suites (final unmutated tree)
`tests.test_calibration_ledger_custody` 58 in 38.6 s OK · `tests.test_validate_powermetrics_fiducial_derivation_only` 23 in 156.9 s OK · `tests.test_run_night` 128 in 36.9 s OK · `tests.test_authentication_io` 22 in 0.9 s OK ("KILLED 3 renderer AST mutations") · `compileall -q scripts joulewise` rc 0 · `/tmp/refute-memo` and `/Users/edr/code/JouleWise-wt-memo-ref` both `git status --short` empty. No writes outside `/tmp`.
