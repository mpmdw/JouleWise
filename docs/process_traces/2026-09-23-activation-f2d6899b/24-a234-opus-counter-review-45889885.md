# A234+A212 at 45889885 — Opus 5.5 counter-review, gate-ledger row 6 (condensed verbatim hand-back)

**Verdict:** MERGEABLE. No blocker, no should-fix, three deferrable nits.

## (a) Earlier findings are closed

- **S1 (armed state for an undelivered chain-started refusal):** closed at `magistrate_watchdog.py:952-955`. A mutant that drops the dead-man clause fails `test_undelivered_chain_refusal_keeps_deadman_tail`.
- **S2 (latch key):** closed. The key is `plan_id:custody_root:sha256(result.json)`, at `:894-900`. A mutant that removes the digest from the key fails.
- **S3 (docs):** closed. Every gloss is present, and so is the span bound. The record-23 F2 boundary is stated truthfully.
- **N1:** closed. A mutant that sets the chain-field guard to `if False:` fails `test_result_chain_fields_veto_zero_capture_release`.
- **Record-23 F1 (broken symlinks):** closed. Both paths use `lstat`, and a root that is not a directory counts as a match. The mutant fails 2 tests.
- No new defect found.

## (b) Consumers all fail closed

- `decide()` passes state everywhere.
- If `driver_probe` is missing, the watchdog treats the observation as non-empty and holds.
- The resident supervisor (`:2147`, `:2150`) passes no state and reads `state.json` from disk. The latch is written before the fork.
  - Executed P2: after release, span False, armed False, `relevant_standdown_plan` None.
  - Executed P4: with `state.json` corrupted, span True.
- The sibling lookup in `evidence_night.retained_roots` works.
- `chain_literal` and `probe_payload_kind` raise only `ValueError` or `PlanError`, and both are caught.
- The live `pgrep -lf '[r]un_night\.py'` currently exits 0 because it matches the cold judge's `claude -p` prompt text. It only holds where the agent census already holds, so this is harmless.

## (c) Overbuild

- Nothing needs pruning.
- The delivered chain-started refusal is armed until completion (base: disarmed). Ruling 16 S1 kept this, and it is more conservative than base.
- The `ended_epoch_s` validity check is not required by any ruling (see NIT-2).

## Nits

- **NIT-1:** "One-way" is conditional. The latch holds only while the disk facts still hold. Executed P3: a `*.consumed.json` placed after release with a live census gives HOLD_CENSUS, and the latch is kept. This fails closed, but the prose does not state the condition.
- **NIT-2:** Mutant M10, which drops the `ended > now` check, survives (159 passed). The behaviour is correct (executed P5: FENCED, no latch). Either add a test or prune the check.
- **NIT-3:** My earlier N3 stands: `snapshot.errors` returns before `fenced_checkouts` is refreshed. It is harmless. N2, the HOLD_CENSUS label change, is also only a label difference.

## (d) Tests and mutation probes

- Test run at 45889885 in a scratch worktree: 269 passed, 354 subtests, 700.18 s, exit 0.
- Mutation probes: M1 through M12 were KILLED, except M10, which SURVIVED.

Not executed: live launchd, real custody state, a real driver process.
