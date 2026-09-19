# Exhibit B — the contract text (verbatim): D-109 R1 (decision log) and the append contract §head pin

## docs/decision_log.md lines 7505–7530 at `2f79e633`

```
   writer creates capture state pre-receipt and has pre-manifest
   failure exits — a publish-on-return receipt misses exactly the
   crash/interrupt cases a completeness mechanism exists to catch.)
3. Receipts are immutable and hash-chained: sequence, predecessor,
   attempt id, content id, artifact hashes, six-field epoch, full T1,
   capture time, exact bound lexeme, disposition, custody locator.
4. The acceptance artifact pins its baseline ledger head. Evaluation
   ALSO requires the independent current-head pin (clause below),
   verifies one complete non-forked chain extension from baseline to
   current, and threads ONE immutable ledger snapshot through every
   consumer path (session, direct runner path, secondary verifier) —
   repeated independent loads are a refusal-grade defect.
   Anti-rollback authority: a REPO-COMMITTED head-pin file
   `{sequence, head_digest, ledger_schema}` (existing checked-in
   byte-pin trust model; no second trusted latest-sequence store).
   Rotation is epoch-bounded — at most one lead-controlled
   quiet-machine collection session — and NO claim evaluation may
   occur between ledger advancement and pin commit; a physical head
   differing from the committed pin refuses.
5. Ledger history is retained permanently. Referenced evidence remains
   in authenticated custody; missing or unverifiable required bytes
   cause refusal, never silent omission.
6. Version 1 is single-authority, single-machine. Remote/other-machine
   captures are invalid until imported through an authenticated ledger
   transaction; direct multi-machine append requires a new ruling.
7. Threat model, stated honestly and to be stated wherever A-min is
```

## docs/contracts/calibration_ledger_append.md lines 270–300 at `2f79e633`

```

A bracket claim ID is the domain-separated canonical SHA-256 of policy
revision plus `(session_id, slot, attempt_id)`. It is stable across processes.
A per-process UUID never participates in durable equality. At retry, the
stable operation key and target commitment distinguish exact completion from
semantic conflict; the writer lease independently distinguishes a live holder
from a dead predecessor.

The machine gate reports one typed pin relation:

- `exact`: physical and committed heads match;
- `physical_ahead`: the committed head is an authenticated prefix and desk
  work is required;
- `physical_behind`: rollback; or
- `diverged`: the committed pin is not on the physical chain.

Only `scripts/recover_calibration_ledger.py advance-head-pin` may advance the
pin. It requires the exact authenticated candidate, operator identity,
attestation reason, a clean physical protocol with no legacy journal, and a
terminal session (or a sessionless recovery-only abandonment control head).
Any pending/open/refusal business state beyond that authenticated control tail
blocks advancement. Execution is
desk-only: review the candidate and diff, run with `--execute`, commit the pin,
restore a clean checkout, and repeat readiness. There is no night-path
uncommitted-head override.

## Composite readiness gate

`inspection.state == "clean"` is diagnostic, never ARM authorization. The
machine readiness predicate additionally enforces absence of a legacy journal,
intent, residue, incompatible operation target, and live writer, plus the
```

## docs/phase_2/derivation_night_runbook.md lines 2788–2802 at `2f79e633`

```
   written into it (§0.8), and the §1.2 arithmetic recomputed for that night's
   dead-man. Never re-arm a published plan and never silently edit one.
3. **Distinct calendar days.** The registration requires three windows on
   distinct calendar days.
4. **The terminal pin candidate is reviewed and committed at the desk before
   the next night opens.** The night itself never commits Git. Each night opens
   at head-equals-pin, so an uncommitted terminal pin candidate blocks the next
   night's session open. The pre-registration's `[SEQ]`/`[DIGEST]` fields stay
   as the FIRST night's pin; they are the registration's baseline, not a
   per-night field.
5. **A `check` dry run precedes EVERY arm**, not just the first (§0.3 plus
   §2.2). This is the T38j lesson stated as a rule: the OS-build mismatch that
   voided the previous acceptance was found only because a dry run was run.
   Never skip it because last night's passed.
6. **Every arm goes through email-then-arm** (§1.4), every time. Ed's NO on any
```
